"""
Command Line Interface (CLI) for Code Plagiarism Detection.
Supports:
1. Pairwise comparison of two Python source files (Baseline vs AST Engine).
2. Directory scan across multiple submissions (all-pairs matrix).
"""

import os
import sys
import argparse
from typing import List

# Ensure package root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector

def compare_two_files(file1: str, file2: str, threshold: float = 0.25):
    if not os.path.exists(file1):
        print(f"Error: File not found: {file1}")
        sys.exit(1)
    if not os.path.exists(file2):
        print(f"Error: File not found: {file2}")
        sys.exit(1)

    base_detector = TokenWinnowingDetector(k=10, w=5)
    ast_detector = ASTWinnowingDetector(k=1, w=2)

    res_b = base_detector.compare_files(file1, file2)
    res_a = ast_detector.compare_files(file1, file2)

    print("\n" + "=" * 70)
    print("           PAIRWISE CODE PLAGIARISM COMPARISON REPORT")
    print("=" * 70)
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")
    print("-" * 70)
    print(f"{'Metric':32s} | {'Baseline (Token)':16s} | {'Proposed (AST)':16s}")
    print("-" * 70)
    print(f"{'Jaccard Similarity':32s} | {res_b.jaccard*100:14.2f}% | {res_a.jaccard*100:14.2f}%")
    print(f"{'Dice Similarity':32s} | {res_b.dice*100:14.2f}% | {res_a.dice*100:14.2f}%")
    print(f"{'Containment (File 1 in 2)':32s} | {res_b.containment_a*100:14.2f}% | {res_a.containment_a*100:14.2f}%")
    print(f"{'Containment (File 2 in 1)':32s} | {res_b.containment_b*100:14.2f}% | {res_a.containment_b*100:14.2f}%")
    print(f"{'Execution Time':32s} | {res_b.execution_time_sec*1000:13.3f} ms | {res_a.execution_time_sec*1000:13.3f} ms")
    print("-" * 70)

    is_plag_ast = res_a.jaccard >= threshold
    verdict = "SUSPECTED PLAGIARISM" if is_plag_ast else "INDEPENDENT IMPLEMENTATION"
    print(f"Verdict (AST threshold = {threshold*100:.1f}%): [{verdict}]")
    print("=" * 70 + "\n")

def scan_directory(dir_path: str, threshold: float = 0.25):
    if not os.path.isdir(dir_path):
        print(f"Error: Directory not found: {dir_path}")
        sys.exit(1)

    py_files: List[str] = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    if len(py_files) < 2:
        print(f"Need at least 2 Python files to scan in {dir_path}, found {len(py_files)}")
        sys.exit(1)

    print(f"\nScanning {len(py_files)} Python files in {dir_path}...")
    ast_detector = ASTWinnowingDetector(k=1, w=2)
    flagged = []

    for i in range(len(py_files)):
        for j in range(i + 1, len(py_files)):
            f1 = py_files[i]
            f2 = py_files[j]
            res = ast_detector.compare_files(f1, f2)
            if res.jaccard >= threshold:
                flagged.append((f1, f2, res.jaccard))

    print(f"\nFound {len(flagged)} pairs exceeding similarity threshold >= {threshold*100:.1f}%:")
    print("-" * 75)
    for f1, f2, sim in sorted(flagged, key=lambda x: x[2], reverse=True):
        rel1 = os.path.relpath(f1, dir_path)
        rel2 = os.path.relpath(f2, dir_path)
        print(f"[{sim*100:5.1f}% similarity] {rel1}  <-->  {rel2}")
    print("-" * 75 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Code Plagiarism Detection CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compare command
    p_comp = subparsers.add_parser("compare", help="Compare two source files")
    p_comp.add_argument("file1", help="Path to first python file")
    p_comp.add_argument("file2", help="Path to second python file")
    p_comp.add_argument("--threshold", type=float, default=0.25, help="Plagiarism threshold (default 0.25)")

    # scan command
    p_scan = subparsers.add_parser("scan", help="Scan a directory of source files")
    p_scan.add_argument("dir", help="Directory containing python submissions")
    p_scan.add_argument("--threshold", type=float, default=0.25, help="Plagiarism threshold (default 0.25)")

    # visual command
    p_vis = subparsers.add_parser("visual", help="Generate side-by-side interactive HTML visual report")
    p_vis.add_argument("file1", help="Path to first python file")
    p_vis.add_argument("file2", help="Path to second python file")
    p_vis.add_argument("--out", default="visualizer/comparison_report.html", help="Output HTML path")
    p_vis.add_argument("--threshold", type=float, default=0.25, help="Plagiarism threshold (default 0.25)")

    args = parser.parse_args()

    if args.command == "compare":
        compare_two_files(args.file1, args.file2, args.threshold)
    elif args.command == "scan":
        scan_directory(args.dir, args.threshold)
    elif args.command == "visual":
        from visualizer.visual_highlighter import generate_side_by_side_html
        out_path = generate_side_by_side_html(args.file1, args.file2, args.out, args.threshold)
        print(f"Generated side-by-side visual report at: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    main()
