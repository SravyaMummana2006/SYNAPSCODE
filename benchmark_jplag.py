"""
Automated JPlag Benchmarking and Comparative Runner.
Prepares submissions, executes official JPlag (v5.1.0) on the benchmark suite,
extracts pairwise similarity scores, and computes 3-way metrics:
1. Baseline (Token Winnowing)
2. JPlag (Greedy String Tiling on Python AST/tokens)
3. Proposed (AST-Normalized Winnowing)
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
import numpy as np
from sklearn.metrics import roc_auc_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector

BENCHMARKS_DIR = os.path.join(BASE_DIR, "dataset", "benchmarks")
MANIFEST_PATH = os.path.join(BASE_DIR, "dataset", "ground_truth.json")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
JPLAG_DIR = os.path.join(BASE_DIR, "jplag_runs")
JAR_PATH = os.path.join(BASE_DIR, "jplag.jar")

def prepare_jplag_directory():
    """Formats 35 benchmark programs into separate submission directories for JPlag."""
    if os.path.exists(JPLAG_DIR):
        shutil.rmtree(JPLAG_DIR)
    os.makedirs(JPLAG_DIR, exist_ok=True)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    # Collect unique files referenced
    unique_files = set()
    for p in pairs:
        unique_files.add(p["file1"])
        unique_files.add(p["file2"])

    # Map each file (e.g. p01_binary_search/orig_1.py) to a submission folder (e.g. p01_binary_search__orig_1)
    file_to_sub = {}
    for rel_path in unique_files:
        prob, fname = rel_path.split("/")
        sub_id = f"{prob}__{fname.replace('.py', '')}"
        file_to_sub[rel_path] = sub_id

        sub_path = os.path.join(JPLAG_DIR, sub_id)
        os.makedirs(sub_path, exist_ok=True)
        src_path = os.path.join(BENCHMARKS_DIR, rel_path)
        shutil.copy(src_path, os.path.join(sub_path, fname))

    return file_to_sub

def run_jplag(file_to_sub) -> dict:
    """Executes JPlag and parses the resulting overview.json from the zip archive."""
    if not os.path.exists(JAR_PATH):
        print("Downloading official JPlag v5.1.0 release...")
        import urllib.request
        urllib.request.urlretrieve("https://github.com/jplag/JPlag/releases/download/v5.1.0/jplag-5.1.0-jar-with-dependencies.jar", JAR_PATH)

    zip_out = os.path.join(BASE_DIR, "jplag_benchmark_out.zip")
    if os.path.exists(zip_out):
        os.remove(zip_out)

    cmd = [
        "java", "-jar", JAR_PATH,
        "-l", "python3",
        "-t", "6",                # Sensitive token threshold
        "-m", "0.0",              # Save all comparisons
        "-r", zip_out,
        JPLAG_DIR
    ]

    print("Executing JPlag v5.1.0 across benchmark submissions...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print("JPlag stderr:", res.stderr)
        raise RuntimeError("JPlag execution failed!")

    # Extract overview.json from zip_out
    with zipfile.ZipFile(zip_out, "r") as z:
        overview_data = json.loads(z.read("overview.json").decode("utf-8"))

    # Build similarity lookup: (subA, subB) -> similarity (0.0 to 1.0)
    jplag_sims = {}
    for comp in overview_data.get("top_comparisons", []):
        s1 = comp["first_submission"]
        s2 = comp["second_submission"]
        # JPlag provides AVG and MAX similarity (percentage 0 - 100 or 0 - 1.0)
        sim_val = comp["similarities"]["AVG"]
        # Normalize to 0.0 - 1.0 if JPlag outputs 0 - 100
        if sim_val > 1.0:
            sim_val = sim_val / 100.0
        jplag_sims[(s1, s2)] = sim_val
        jplag_sims[(s2, s1)] = sim_val

    # Cleanup temporary directories
    shutil.rmtree(JPLAG_DIR, ignore_errors=True)
    if os.path.exists(zip_out):
        os.remove(zip_out)

    return jplag_sims

def evaluate_three_way():
    file_to_sub = prepare_jplag_directory()
    jplag_sims = run_jplag(file_to_sub)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    y_true = np.array([p["is_plagiarism"] for p in pairs])
    categories = [p["category"] for p in pairs]

    base_detector = TokenWinnowingDetector(k=10, w=5)
    ast_detector = ASTWinnowingDetector(k=1, w=2)

    base_scores = []
    ast_scores = []
    jplag_scores = []

    for p in pairs:
        f1_rel = p["file1"]
        f2_rel = p["file2"]
        f1_path = os.path.join(BENCHMARKS_DIR, f1_rel)
        f2_path = os.path.join(BENCHMARKS_DIR, f2_rel)

        # Baseline & AST
        base_scores.append(base_detector.compare_files(f1_path, f2_path).jaccard)
        ast_scores.append(ast_detector.compare_files(f1_path, f2_path).jaccard)

        # JPlag
        sub1 = file_to_sub[f1_rel]
        sub2 = file_to_sub[f2_rel]
        j_score = jplag_sims.get((sub1, sub2), 0.0)
        jplag_scores.append(j_score)

    base_scores = np.array(base_scores)
    ast_scores = np.array(ast_scores)
    jplag_scores = np.array(jplag_scores)

    # Compute optimal metrics helper
    def get_metrics(scores, y):
        auc = roc_auc_score(y, scores)
        thresholds = np.linspace(0.01, 0.99, 1000)
        best_f1, best_t, best_p, best_r = -1.0, 0.5, 0.0, 0.0
        for t in thresholds:
            pred = (scores >= t).astype(int)
            tp = np.sum((pred == 1) & (y == 1))
            fp = np.sum((pred == 1) & (y == 0))
            fn = np.sum((pred == 0) & (y == 1))
            p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2.0 * p * r / (p + r)) if (p + r) > 0 else 0.0
            if f1 > best_f1:
                best_f1, best_t, best_p, best_r = f1, t, p, r
        return {"auc": float(auc), "precision": float(best_p), "recall": float(best_r), "f1": float(best_f1), "threshold": float(best_t)}

    overall_base = get_metrics(base_scores, y_true)
    overall_jplag = get_metrics(jplag_scores, y_true)
    overall_ast = get_metrics(ast_scores, y_true)

    # LLM Subset
    llm_mask = np.array([("llm" in c) or (y == 0) for c, y in zip(categories, y_true)])
    y_llm = y_true[llm_mask]
    llm_base = get_metrics(base_scores[llm_mask], y_llm)
    llm_jplag = get_metrics(jplag_scores[llm_mask], y_llm)
    llm_ast = get_metrics(ast_scores[llm_mask], y_llm)

    # Print 3-way comparison table
    print("\n" + "=" * 88)
    print("      THREE-WAY BENCHMARK COMPARISON: BASELINE vs. JPLAG (v5.1.0) vs. PROPOSED AST")
    print("=" * 88)
    print(f"{'Metric':28s} | {'Baseline (Winnowing)':20s} | {'JPlag (v5.1.0)':16s} | {'Proposed (AST)':16s}")
    print("-" * 88)
    print(f"{'Overall ROC-AUC':28s} | {overall_base['auc']*100:18.2f}% | {overall_jplag['auc']*100:14.2f}% | {overall_ast['auc']*100:14.2f}%")
    print(f"{'Overall Precision':28s} | {overall_base['precision']*100:18.2f}% | {overall_jplag['precision']*100:14.2f}% | {overall_ast['precision']*100:14.2f}%")
    print(f"{'Overall Recall':28s} | {overall_base['recall']*100:18.2f}% | {overall_jplag['recall']*100:14.2f}% | {overall_ast['recall']*100:14.2f}%")
    print(f"{'Overall F1-Score':28s} | {overall_base['f1']*100:18.2f}% | {overall_jplag['f1']*100:14.2f}% | {overall_ast['f1']*100:14.2f}%")
    print("-" * 88)
    print(f"{'AI / LLM Subset ROC-AUC':28s} | {llm_base['auc']*100:18.2f}% | {llm_jplag['auc']*100:14.2f}% | {llm_ast['auc']*100:14.2f}%")
    print(f"{'AI / LLM Subset Precision':28s} | {llm_base['precision']*100:18.2f}% | {llm_jplag['precision']*100:14.2f}% | {llm_ast['precision']*100:14.2f}%")
    print(f"{'AI / LLM Subset Recall':28s} | {llm_base['recall']*100:18.2f}% | {llm_jplag['recall']*100:14.2f}% | {llm_ast['recall']*100:14.2f}%")
    print(f"{'AI / LLM Subset F1-Score':28s} | {llm_base['f1']*100:18.2f}% | {llm_jplag['f1']*100:14.2f}% | {llm_ast['f1']*100:14.2f}%")
    print("=" * 88)

    # Save to json
    results_path = os.path.join(RESULTS_DIR, "three_way_jplag_comparison.json")
    with open(results_path, "w", encoding="utf-8") as out:
        json.dump({
            "overall": {
                "baseline_token": overall_base,
                "jplag_v5": overall_jplag,
                "proposed_ast": overall_ast
            },
            "llm_subset": {
                "baseline_token": llm_base,
                "jplag_v5": llm_jplag,
                "proposed_ast": llm_ast
            }
        }, out, indent=2)
    print(f"\nSaved 3-way evaluation results to: {results_path}")

if __name__ == "__main__":
    evaluate_three_way()
