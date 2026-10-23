"""
Side-by-Side Visual Match Highlighter and Interactive HTML Report Generator.
Renders synchronized side-by-side source code with line-numbered panels,
highlighted matching fingerprints, similarity gauges, and detailed AST metadata.
"""

import os
import sys
import html
from typing import Dict, List, Set, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from baseline.tokenizer import tokenize_code, tokens_to_stream, CodeToken
from baseline.rabin_karp import compute_rolling_hashes
from baseline.winnowing import winnow, Fingerprint
from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector

def generate_side_by_side_html(
    file_a: str,
    file_b: str,
    output_html_path: str = "visualizer/comparison_report.html",
    threshold: float = 0.25
) -> str:
    with open(file_a, "r", encoding="utf-8") as fa:
        code_a = fa.read()
    with open(file_b, "r", encoding="utf-8") as fb:
        code_b = fb.read()

    lines_a = code_a.splitlines()
    lines_b = code_b.splitlines()

    # Run detectors
    base_det = TokenWinnowingDetector(k=10, w=5)
    ast_det = ASTWinnowingDetector(k=1, w=2)

    res_base = base_det.compare_codes(code_a, code_b)
    res_ast = ast_det.compare_codes(code_a, code_b)

    # Extract tokens and find matching line numbers
    toks_a = tokenize_code(code_a, abstract_identifiers=True, abstract_literals=True)
    toks_b = tokenize_code(code_b, abstract_identifiers=True, abstract_literals=True)

    stream_a = tokens_to_stream(toks_a)
    stream_b = tokens_to_stream(toks_b)

    hashes_a = compute_rolling_hashes(stream_a, k=base_det.k)
    hashes_b = compute_rolling_hashes(stream_b, k=base_det.k)

    fps_a = winnow(hashes_a, base_det.w)
    fps_b = winnow(hashes_b, base_det.w)

    set_h_a = {fp.hash_value for fp in fps_a}
    set_h_b = {fp.hash_value for fp in fps_b}
    shared_hashes = set_h_a.intersection(set_h_b)

    # Map shared hashes to matching lines in both files
    matched_lines_a = set()
    for fp in fps_a:
        if fp.hash_value in shared_hashes:
            # Token index where k-gram begins
            start_tok_idx = fp.position
            end_tok_idx = min(len(toks_a) - 1, start_tok_idx + base_det.k)
            for t_idx in range(start_tok_idx, end_tok_idx + 1):
                matched_lines_a.add(toks_a[t_idx].start_line)

    matched_lines_b = set()
    for fp in fps_b:
        if fp.hash_value in shared_hashes:
            start_tok_idx = fp.position
            end_tok_idx = min(len(toks_b) - 1, start_tok_idx + base_det.k)
            for t_idx in range(start_tok_idx, end_tok_idx + 1):
                matched_lines_b.add(toks_b[t_idx].start_line)

    # Format lines for side-by-side rendering
    def render_code_rows(lines, matched_lines):
        rows = []
        for idx, line in enumerate(lines, 1):
            is_match = idx in matched_lines
            bg_class = "match-row" if is_match else ""
            badge = '<span class="match-badge">MATCH</span>' if is_match else ''
            safe_code = html.escape(line) if line else "&nbsp;"
            rows.append(
                f'<tr class="{bg_class}"><td class="lineno">{idx}</td><td class="code-col">{safe_code} {badge}</td></tr>'
            )
        return "\n".join(rows)

    rows_a_html = render_code_rows(lines_a, matched_lines_a)
    rows_b_html = render_code_rows(lines_b, matched_lines_b)

    verdict_class = "verdict-plag" if res_ast.jaccard >= threshold else "verdict-indep"
    verdict_text = "SUSPECTED PLAGIARISM" if res_ast.jaccard >= threshold else "INDEPENDENT IMPLEMENTATION"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Plagiarism Visual Inspection: {os.path.basename(file_a)} vs {os.path.basename(file_b)}</title>
<style>
  :root {{
    --bg: #0f172a;
    --card: #1e293b;
    --text: #f1f5f9;
    --accent: #38bdf8;
    --match: rgba(234, 179, 8, 0.25);
    --match-border: #eab308;
    --danger: #ef4444;
    --success: #22c55e;
  }}
  body {{
    margin: 0; padding: 24px;
    background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
  }}
  .header {{
    background: var(--card); border-radius: 12px; padding: 20px 28px;
    margin-bottom: 24px; border: 1px solid #334155; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  }}
  h1 {{ margin: 0 0 10px 0; font-size: 22px; color: var(--accent); }}
  .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 14px; }}
  .card {{ background: #0b1120; padding: 14px; border-radius: 8px; border: 1px solid #1e293b; }}
  .card .label {{ font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.5px; }}
  .card .val {{ font-size: 20px; font-weight: bold; margin-top: 4px; }}
  .verdict-plag {{ color: var(--danger); }}
  .verdict-indep {{ color: var(--success); }}
  .panels {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .panel {{
    background: var(--card); border-radius: 12px; border: 1px solid #334155;
    overflow: hidden; display: flex; flex-direction: column;
  }}
  .panel-header {{
    background: #1e293b; padding: 12px 18px; font-weight: bold; font-size: 14px;
    border-bottom: 1px solid #334155; color: #e2e8f0; display: flex; justify-content: space-between;
  }}
  .code-table {{ width: 100%; border-collapse: collapse; font-family: 'Consolas', 'Fira Code', monospace; font-size: 13px; }}
  .lineno {{
    width: 44px; text-align: right; padding: 2px 10px; color: #64748b;
    background: #111827; user-select: none; border-right: 1px solid #334155;
  }}
  .code-col {{ padding: 2px 12px; white-space: pre; color: #e2e8f0; }}
  .match-row {{ background: var(--match); border-left: 3px solid var(--match-border); }}
  .match-badge {{
    font-size: 9px; background: var(--match-border); color: #000;
    padding: 1px 5px; border-radius: 4px; font-weight: bold; margin-left: 8px; vertical-align: middle;
  }}
</style>
</head>
<body>

<div class="header">
  <h1>🔍 Code Plagiarism Pairwise Visual Inspection</h1>
  <div style="font-size: 13px; color: #94a3b8;">
    Comparing <code>{html.escape(file_a)}</code> vs <code>{html.escape(file_b)}</code>
  </div>

  <div class="meta-grid">
    <div class="card">
      <div class="label">Proposed AST Similarity</div>
      <div class="val" style="color: var(--accent);">{res_ast.jaccard * 100:.2f}%</div>
    </div>
    <div class="card">
      <div class="label">Baseline Token Similarity</div>
      <div class="val" style="color: #cbd5e1;">{res_base.jaccard * 100:.2f}%</div>
    </div>
    <div class="card">
      <div class="label">AST Containment (A in B)</div>
      <div class="val" style="color: #cbd5e1;">{res_ast.containment_a * 100:.1f}%</div>
    </div>
    <div class="card">
      <div class="label">Execution Time</div>
      <div class="val" style="color: #a7f3d0;">{res_ast.execution_time_sec * 1000:.2f} ms</div>
    </div>
    <div class="card">
      <div class="label">Verdict (Threshold = {threshold * 100:.1f}%)</div>
      <div class="val {verdict_class}">{verdict_text}</div>
    </div>
  </div>
</div>

<div class="panels">
  <div class="panel">
    <div class="panel-header">
      <span>File 1: {os.path.basename(file_a)}</span>
      <span style="font-size: 12px; color: #94a3b8;">{len(lines_a)} lines | {len(matched_lines_a)} matched lines</span>
    </div>
    <div style="overflow-x: auto; max-height: 75vh;">
      <table class="code-table">
        <tbody>
          {rows_a_html}
        </tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <div class="panel-header">
      <span>File 2: {os.path.basename(file_b)}</span>
      <span style="font-size: 12px; color: #94a3b8;">{len(lines_b)} lines | {len(matched_lines_b)} matched lines</span>
    </div>
    <div style="overflow-x: auto; max-height: 75vh;">
      <table class="code-table">
        <tbody>
          {rows_b_html}
        </tbody>
      </table>
    </div>
  </div>
</div>

</body>
</html>
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as out:
        out.write(html_content)

    return output_html_path

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate side-by-side match visualizer")
    parser.add_argument("file_a", help="First source file")
    parser.add_argument("file_b", help="Second source file")
    parser.add_argument("--out", default="visualizer/comparison_report.html", help="Output HTML file path")
    args = parser.parse_args()

    out_file = generate_side_by_side_html(args.file_a, args.file_b, args.out)
    print(f"Generated side-by-side visualization at: {out_file}")
