"""
Direct comparison of Baseline Token-Winnowing vs Improved AST-Winnowing
across all benchmark categories.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector

def compare_engines():
    baseline = TokenWinnowingDetector(k=10, w=5)
    ast_detector = ASTWinnowingDetector(k=1, w=2)

    manifest_path = os.path.join(BASE_DIR, "dataset", "ground_truth.json")
    benchmarks_dir = os.path.join(BASE_DIR, "dataset", "benchmarks")

    with open(manifest_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    base_cat_scores = {}
    ast_cat_scores = {}
    base_time = 0.0
    ast_time = 0.0

    for p in pairs:
        f1_path = os.path.join(benchmarks_dir, p["file1"])
        f2_path = os.path.join(benchmarks_dir, p["file2"])

        res_b = baseline.compare_files(f1_path, f2_path)
        res_a = ast_detector.compare_files(f1_path, f2_path)

        cat = p["category"]
        if cat not in base_cat_scores:
            base_cat_scores[cat] = []
            ast_cat_scores[cat] = []

        base_cat_scores[cat].append(res_b.jaccard)
        ast_cat_scores[cat].append(res_a.jaccard)

        base_time += res_b.execution_time_sec
        ast_time += res_a.execution_time_sec

    print(f"{'Category':32s} | {'Baseline Jaccard':16s} | {'AST-Winnowing':16s} | {'Delta':8s}")
    print("-" * 80)
    for cat in base_cat_scores.keys():
        b_avg = sum(base_cat_scores[cat]) / len(base_cat_scores[cat])
        a_avg = sum(ast_cat_scores[cat]) / len(ast_cat_scores[cat])
        diff = (a_avg - b_avg) * 100
        sign = "+" if diff >= 0 else ""
        print(f"{cat:32s} | {b_avg*100:14.2f}% | {a_avg*100:14.2f}% | {sign}{diff:6.2f}%")

    print("\nPairwise Execution Time per comparison:")
    print(f"  * Baseline Token-Winnowing : {(base_time / len(pairs)) * 1000:6.3f} ms")
    print(f"  * Improved AST-Winnowing   : {(ast_time / len(pairs)) * 1000:6.3f} ms")

if __name__ == "__main__":
    compare_engines()
