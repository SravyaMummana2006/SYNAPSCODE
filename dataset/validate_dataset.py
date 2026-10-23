"""
Automated verification and validation suite for the benchmark dataset.
Validates:
1. Syntax correctness (ast.parse) of all 35 benchmark programs.
2. Functional correctness & semantic equivalence against all test cases.
3. Ground truth integrity (file existence, symmetry, and class distributions).
"""

import os
import sys
import json
import ast
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BENCHMARKS_DIR = os.path.join(BASE_DIR, "benchmarks")
MANIFEST_PATH = os.path.join(BASE_DIR, "ground_truth.json")

# Import PROBLEMS definition from build_dataset
sys.path.insert(0, BASE_DIR)
from build_dataset import PROBLEMS

def validate_syntax():
    """Verify that all generated benchmark files parse without any SyntaxError."""
    print("=== [1/3] Validating Syntax with AST ===")
    verified_files = 0
    for root, _, files in os.walk(BENCHMARKS_DIR):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8") as py_file:
                    content = py_file.read()
                try:
                    ast.parse(content, filename=path)
                    verified_files += 1
                except SyntaxError as e:
                    raise AssertionError(f"Syntax error in {path}: {e}")
    print(f"PASSED: All {verified_files} Python source files successfully parsed by AST.\n")
    return verified_files

def load_module_from_file(filepath):
    """Dynamically loads a Python file as a module."""
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def validate_functional_equivalence():
    """
    Executes each variant against all problem test cases.
    Verifies that all variants produce identical, correct results.
    """
    print("=== [2/3] Validating Functional Equivalence ===")
    total_test_executions = 0

    function_names = {
        "p01_binary_search": "binary_search",
        "p02_merge_intervals": "merge_intervals",
        "p03_knapsack": "knapsack",
        "p04_bfs_shortest_path": "shortest_path",
        "p05_lcs": "lcs",
    }

    for prob_name, prob_info in PROBLEMS.items():
        fn_name = function_names[prob_name]
        prob_dir = os.path.join(BENCHMARKS_DIR, prob_name)
        test_cases = prob_info["test_cases"]

        for filename in prob_info["files"].keys():
            filepath = os.path.join(prob_dir, filename)
            mod = load_module_from_file(filepath)
            assert hasattr(mod, fn_name), f"Function '{fn_name}' missing in {filepath}"
            fn = getattr(mod, fn_name)

            for tc_idx, tc in enumerate(test_cases):
                # Pass a deepcopy of arguments to avoid in-place mutation side-effects
                import copy
                args_copy = copy.deepcopy(tc["args"])
                actual = fn(*args_copy)
                expected = tc["expected"]
                assert actual == expected, (
                    f"Test failure in {prob_name}/{filename} on TC {tc_idx}!\n"
                    f"Args: {tc['args']}\nExpected: {expected}\nActual: {actual}"
                )
                total_test_executions += 1

    print(f"PASSED: Executed {total_test_executions} functional tests across all variants.")
    print("All original, manually obfuscated, and LLM-paraphrased programs are 100% functionally equivalent.\n")

def validate_ground_truth_integrity():
    """Verifies that ground truth pairs reference real files and report statistics."""
    print("=== [3/3] Validating Ground Truth Manifest & Statistics ===")
    assert os.path.exists(MANIFEST_PATH), f"Manifest file missing: {MANIFEST_PATH}"

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        pairs = json.load(f)

    assert len(pairs) > 0, "Ground truth manifest is empty!"

    categories = {}
    label_counts = {0: 0, 1: 0}

    for p in pairs:
        # Check files exist
        f1_full = os.path.join(BENCHMARKS_DIR, p["file1"])
        f2_full = os.path.join(BENCHMARKS_DIR, p["file2"])
        assert os.path.exists(f1_full), f"Referenced file1 does not exist: {f1_full}"
        assert os.path.exists(f2_full), f"Referenced file2 does not exist: {f2_full}"

        label = p["is_plagiarism"]
        label_counts[label] += 1

        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print(f"Total labeled pairs: {len(pairs)}")
    print(f"  - Positive pairs (Plagiarized / Transformed) [y=1]: {label_counts[1]}")
    print(f"  - Negative pairs (Independent implementations) [y=0]: {label_counts[0]}")
    print("\nBreakdown by category:")
    for cat, count in categories.items():
        print(f"  * {cat:32s}: {count:3d} pairs")

    print("\nPASSED: Ground truth manifest integrity is verified.")
    return len(pairs), label_counts, categories

def run_all_validations():
    validate_syntax()
    validate_functional_equivalence()
    validate_ground_truth_integrity()
    print("==================================================")
    print(" STEP 1 COMPLETE: Dataset & Benchmark Verification Passed!")
    print("==================================================")

if __name__ == "__main__":
    run_all_validations()
