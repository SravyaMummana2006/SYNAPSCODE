# Benchmark Dataset for Code Plagiarism & AI-Evasion

This benchmark follows the methodology of established plagiarism detection competitions (**IR-Plag**, **SOCO**) and competitive programming corpora (**AIZU/CodeNet**), specifically tailored to evaluate classical fingerprinting robustness against modern LLM-driven paraphrasing.

## Structure
- **5 Algorithmic Problems**:
  1. `p01_binary_search`: Sorted array first-occurrence search.
  2. `p02_merge_intervals`: Interval sorting and consolidation.
  3. `p03_knapsack`: 0/1 Knapsack dynamic programming.
  4. `p04_bfs_shortest_path`: Breadth-first graph traversal on unweighted graphs.
  5. `p05_lcs`: Longest Common Subsequence dynamic programming.

## Variants per Problem (7 variants, 35 files total)
- `orig_1.py`: Baseline canonical implementation.
- `orig_2.py`: Independent implementation 1 (different algorithmic design / recursion vs iteration / alternate data structures).
- `orig_3.py`: Independent implementation 2 (alternate paradigm, e.g. two-pointer / bidirectional / memoization).
- `manual_rename.py`: Manual obfuscation (identifier renaming, comment alterations).
- `manual_structure.py`: Manual obfuscation (control flow inversion, loop conversion `for` $\leftrightarrow$ `while`, inlining/extracting).
- `llm_paraphrase_light.py`: LLM rewrite focusing on idiomatic expressions, syntactic alternatives, and functional constructs.
- `llm_paraphrase_heavy.py`: LLM adversarial evasion rewrite (OOP encapsulation, helper methods, restructured branch logic specifically designed to alter token sequence distributions).

## Ground Truth Manifest (`ground_truth.json`)
Contains 60 rigorously labeled pairs:
- **Positives (25 pairs)**:
  - `plagiarism_manual_rename`: 5 pairs
  - `plagiarism_manual_structure`: 5 pairs
  - `plagiarism_llm_light`: 5 pairs
  - `plagiarism_llm_heavy`: 5 pairs
  - `plagiarism_cross_transformed`: 5 pairs
- **Negatives (35 pairs)**:
  - `independent_same_problem`: 25 pairs (Crucial test: solves the exact same problem with identical I/O specifications independently)
  - `independent_diff_problem`: 10 pairs (Solves completely different algorithmic tasks)

## Verification
All variants pass 100% of functional test cases (175 test assertions) via `python dataset/validate_dataset.py`.
