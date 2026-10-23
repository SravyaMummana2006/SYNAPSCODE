"""
Quick sanity check evaluating baseline Token-Winnowing across the benchmark dataset categories.
"""

import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector

def evaluate_baseline_samples():
    detector = TokenWinnowingDetector(k=10, w=5)
    manifest_path = os.path.join(BASE_DIR, "dataset", "ground_truth.json")
    benchmarks_dir = os.path.join(BASE_DIR, "dataset", "benchmarks")

    with open(manifest_path, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    category_scores = {}
    total_time = 0.0

    for p in pairs:
        f1_path = os.path.join(benchmarks_dir, p["file1"])
        f2_path = os.path.join(benchmarks_dir, p["file2"])

        res = detector.compare_files(f1_path, f2_path)
        cat = p["category"]
        if cat not in category_scores:
            category_scores[cat] = []
        category_scores[cat].append(res.jaccard)
        total_time += res.execution_time_sec

    print("=== Baseline Token-Winnowing Average Jaccard Similarity per Category ===")
    for cat, scores in category_scores.items():
        avg = sum(scores) / len(scores)
        print(f"  * {cat:32s}: {avg * 100:6.2f}% (min: {min(scores)*100:5.1f}%, max: {max(scores)*100:5.1f}%)")

    print(f"\nAverage pairwise comparison time: {(total_time / len(pairs)) * 1000:.3f} ms")

if __name__ == "__main__":
    evaluate_baseline_samples()
