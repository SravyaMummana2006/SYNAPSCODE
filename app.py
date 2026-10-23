"""
SynapsCode Web Application & REST API Server.
Serves the modern React 19 + Tailwind CSS + Lucide frontend from dist/
and powers live AST & Token Winnowing plagiarism detection.
"""

import os
import sys
import json
import ast
from flask import Flask, request, jsonify, send_from_directory, send_file

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector
from ast_engine.normalizer import normalize_expr
from baseline.tokenizer import tokenize_code, tokens_to_stream
from baseline.rabin_karp import compute_rolling_hashes
from baseline.winnowing import winnow

DIST_DIR = os.path.join(BASE_DIR, "dist")
BENCHMARKS_DIR = os.path.join(BASE_DIR, "dataset", "benchmarks")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

app = Flask(__name__, static_folder=DIST_DIR)

# Initialize engines
base_detector = TokenWinnowingDetector(k=10, w=5)
ast_detector = ASTWinnowingDetector(k=1, w=2)

PRESETS = {
    "binary_search_llm": {
        "title": "Binary Search: Canonical vs. Adversarial LLM Rewrite",
        "file1": "p01_binary_search/orig_1.py",
        "file2": "p01_binary_search/llm_paraphrase_heavy.py"
    },
    "knapsack_llm_oop": {
        "title": "0/1 Knapsack: Canonical DP vs. LLM Class-Wrapped Evasion",
        "file1": "p03_knapsack/orig_1.py",
        "file2": "p03_knapsack/llm_paraphrase_heavy.py"
    },
    "merge_intervals_rename": {
        "title": "Merge Intervals: Original vs. Variable Renaming",
        "file1": "p02_merge_intervals/orig_1.py",
        "file2": "p02_merge_intervals/manual_rename.py"
    },
    "bfs_independent": {
        "title": "BFS Graph: Canonical vs. Independent Student Implementation (True Negative)",
        "file1": "p04_bfs_shortest_path/orig_1.py",
        "file2": "p04_bfs_shortest_path/orig_2.py"
    },
    "lcs_diff_paradigm": {
        "title": "LCS: Table DP vs. Independent Recursive Memoization (True Negative)",
        "file1": "p05_lcs/orig_1.py",
        "file2": "p05_lcs/orig_3.py"
    }
}

def read_bench_file(rel_path):
    full_p = os.path.join(BENCHMARKS_DIR, rel_path)
    if os.path.exists(full_p):
        with open(full_p, "r", encoding="utf-8") as f:
            return f.read()
    return ""

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_spa(path):
    if path and os.path.exists(os.path.join(DIST_DIR, path)):
        return send_from_directory(DIST_DIR, path)
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index_file):
        return send_file(index_file)
    return "SynapsCode UI dist not found. Please build the frontend.", 404

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    assets_dir = os.path.join(DIST_DIR, "assets")
    return send_from_directory(assets_dir, filename)

@app.route("/results/<path:filename>")
def serve_results(filename):
    return send_from_directory(RESULTS_DIR, filename)

@app.route("/api/presets", methods=["GET"])
def api_presets():
    presets_with_code = {}
    for k, p in PRESETS.items():
        presets_with_code[k] = {
            "title": p["title"],
            "code1": read_bench_file(p["file1"]),
            "code2": read_bench_file(p["file2"]),
        }
    return jsonify(presets_with_code)

@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.json or {}
    code_a = data.get("codeA") or data.get("code_a", "")
    code_b = data.get("codeB") or data.get("code_b", "")

    res_base = base_detector.compare_codes(code_a, code_b)
    res_ast = ast_detector.compare_codes(code_a, code_b)

    # 1. Line-level match extraction using token winnowing (Classical MOSS)
    toks_a = tokenize_code(code_a, abstract_identifiers=True, abstract_literals=True)
    toks_b = tokenize_code(code_b, abstract_identifiers=True, abstract_literals=True)

    stream_a = tokens_to_stream(toks_a)
    stream_b = tokens_to_stream(toks_b)

    hashes_a = compute_rolling_hashes(stream_a, k=base_detector.k)
    hashes_b = compute_rolling_hashes(stream_b, k=base_detector.k)

    fps_a = winnow(hashes_a, base_detector.w)
    fps_b = winnow(hashes_b, base_detector.w)

    set_a = {fp.hash_value for fp in fps_a}
    set_b = {fp.hash_value for fp in fps_b}
    shared = set_a.intersection(set_b)

    matched_a = set()
    for fp in fps_a:
        if fp.hash_value in shared:
            for t_idx in range(fp.position, min(len(toks_a), fp.position + base_detector.k)):
                matched_a.add(toks_a[t_idx].start_line)

    matched_b = set()
    for fp in fps_b:
        if fp.hash_value in shared:
            for t_idx in range(fp.position, min(len(toks_b), fp.position + base_detector.k)):
                matched_b.add(toks_b[t_idx].start_line)

    # 2. Line-level match extraction using AST Normalized Invariants (SynapsCode Engine)
    ast_matched_a = set()
    ast_matched_b = set()
    try:
        tree_a = ast.parse(code_a)
        tree_b = ast.parse(code_b)

        def get_ast_tokens(tree):
            items = []
            for node in ast.walk(tree):
                lineno = getattr(node, 'lineno', None)
                if isinstance(node, ast.Assign):
                    t_str = ','.join(normalize_expr(t) for t in node.targets)
                    items.append((f"ASSIGN:{t_str}={normalize_expr(node.value)}", lineno))
                elif isinstance(node, ast.AugAssign):
                    binop = ast.BinOp(left=node.target, op=node.op, right=node.value)
                    items.append((f"ASSIGN:{normalize_expr(node.target)}={normalize_expr(binop)}", lineno))
                elif isinstance(node, ast.Return):
                    items.append((f"RETURN:{normalize_expr(node.value)}", lineno))
                elif isinstance(node, (ast.While, ast.For)):
                    cond = getattr(node, 'test', None) or getattr(node, 'iter', None)
                    items.append((f"LOOP:{node.__class__.__name__}({normalize_expr(cond)})", lineno))
                elif isinstance(node, ast.If):
                    items.append((f"IF:{normalize_expr(node.test)}", lineno))
                elif isinstance(node, (ast.BinOp, ast.Compare, ast.Call, ast.Subscript)):
                    items.append((f"EXPR:{normalize_expr(node)}", lineno))
            return items

        toks_ast_a = get_ast_tokens(tree_a)
        toks_ast_b = get_ast_tokens(tree_b)

        set_ast_tokens_b = {t[0] for t in toks_ast_b}
        set_ast_tokens_a = {t[0] for t in toks_ast_a}

        for tok, l in toks_ast_a:
            if tok in set_ast_tokens_b and l is not None:
                ast_matched_a.add(l)
        for tok, l in toks_ast_b:
            if tok in set_ast_tokens_a and l is not None:
                ast_matched_b.add(l)
    except Exception:
        pass

    # Combined matches for comprehensive highlight
    combined_a = sorted(list(matched_a.union(ast_matched_a)))
    combined_b = sorted(list(matched_b.union(ast_matched_b)))
    ast_only_a = sorted(list(ast_matched_a - matched_a))
    ast_only_b = sorted(list(ast_matched_b - matched_b))

    return jsonify({
        "baseline": {
            "jaccard": res_base.jaccard,
            "dice": res_base.dice,
            "containment_a": res_base.containment_a,
            "containment_b": res_base.containment_b,
            "execution_time_sec": res_base.execution_time_sec
        },
        "ast": {
            "jaccard": res_ast.jaccard,
            "dice": res_ast.dice,
            "containment_a": res_ast.containment_a,
            "containment_b": res_ast.containment_b,
            "execution_time_sec": res_ast.execution_time_sec
        },
        "lines_a": code_a.splitlines(),
        "lines_b": code_b.splitlines(),
        "matched_a": combined_a,
        "matched_b": combined_b,
        "ast_only_matched_a": ast_only_a,
        "ast_only_matched_b": ast_only_b,
        "token_matched_a": sorted(list(matched_a)),
        "token_matched_b": sorted(list(matched_b))
    })

@app.route("/api/scan", methods=["GET"])
def api_scan():
    problem = request.args.get("problem", "p01_binary_search")
    prob_dir = os.path.join(BENCHMARKS_DIR, problem)
    if not os.path.exists(prob_dir):
        return jsonify({"error": "Problem not found"}), 404

    files = [f for f in os.listdir(prob_dir) if f.endswith(".py")]
    pairs_results = []

    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            f1 = files[i]
            f2 = files[j]
            p1 = os.path.join(prob_dir, f1)
            p2 = os.path.join(prob_dir, f2)

            res_ast = ast_detector.compare_files(p1, p2)
            res_base = base_detector.compare_files(p1, p2)

            pairs_results.append({
                "file1": f1,
                "file2": f2,
                "ast_similarity": res_ast.jaccard,
                "base_similarity": res_base.jaccard
            })

    pairs_results.sort(key=lambda x: x["ast_similarity"], reverse=True)
    return jsonify({
        "problem": problem,
        "total_files": len(files),
        "pairs": pairs_results
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 70)
    print(f"[*] SynapsCode AI Defense Studio running at: http://0.0.0.0:{port}")
    print("=" * 70 + "\n")
    app.run(host="0.0.0.0", port=port, debug=False)
