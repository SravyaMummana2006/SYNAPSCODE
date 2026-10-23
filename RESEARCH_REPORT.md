# Research Report: Detecting Code Plagiarism and AI-Generated Code with Fingerprinting and Pattern Matching

**Project Specification:** P10  
**Authors:** Advanced Agentic AI & Systems Engineering Group  
**Dataset Format:** CodeNet / SOCO / IR-Plag Benchmark Suite  
**Date:** October 2026  

---

## 1. Abstract & Executive Summary

Plagiarism detection systems in academia and competitive programming (e.g., **MOSS**, **JPlag**) rely on $k$-gram fingerprinting through the **Winnowing algorithm** and **Rabin–Karp rolling hashes**. While resilient to identifier renaming and superficial formatting changes, these token-based systems are vulnerable to modern Large Language Models (LLMs). Generative AI can effortlessly re-architect source code—substituting loop paradigms, extracting helper functions, inverting control-flow branches, and wrapping procedures in dummy object-oriented abstractions—while preserving identical input/output semantics.

This research study presents:
1. An exact, mathematically verified implementation of classical **Token-Level Winnowing** following Schleimer et al. (*ACM SIGMOD 2003*) and Karp-Rabin (*IBM J. Res. Dev. 1987*).
2. A curated benchmark dataset of **5 algorithmic problems**, **35 programs**, and **60 labeled evaluation pairs** verified with **175 functional test cases**.
3. An improved **AST-Normalized Structural Winnowing Engine** incorporating commutative operation canonicalization, relational inequality inversion, augmented assignment unification, and OOP wrapper neutralization.
4. An empirical evaluation strictly measuring **Precision, Recall, F1-Score, ROC-AUC**, and **Pairwise Comparison Time**.

### Key Empirical Findings
* **Vulnerability of Baseline:** Under adversarial LLM code paraphrasing, classical token-level winnowing experienced a catastrophic collapse: mean Jaccard similarity dropped to **$6.06\%$**, rendering AI-rewritten code indistinguishable from non-plagiarized independent solutions ($5.36\%$).
* **Recovery via AST Normalization:** The proposed AST-normalized detector recovered an average similarity of **$40.71\%$** on the same adversarial LLM rewrites, lifting overall ROC-AUC from **$85.49\%$** to **$92.80\%$** ($+7.31\%$), and LLM-subset ROC-AUC from **$84.29\%$** to **$93.43\%$** ($+9.14\%$).
* **Computational Efficiency:** The proposed AST approach proved **$2.1\times$ faster** ($0.930\text{ ms}$ vs. $1.983\text{ ms}$ per comparison) due to compact structural token representations.

---

## 2. Theoretical Formulation

```mermaid
flowchart TD
    subgraph S1["Source Code Pair (A & B)"]
        CA["Code A"]
        CB["Code B"]
    end

    subgraph MOSS["Baseline Pipeline (MOSS-Style)"]
        T1["Lexer & Tokenizer<br/>(Strip comments, docstrings)"]
        T2["Identifier Abstraction<br/>(Map to 'ID', literals to 'LIT')"]
        RK1["Rabin-Karp Rolling Hashes<br/>(k-gram windowing, mod 2^31-1)"]
        W1["Local Winnowing<br/>(Window size w, rightmost tie-break)"]
    end

    subgraph AST["Proposed Pipeline (AST-Normalized)"]
        A1["AST Parsing<br/>(Python native AST)"]
        A2["Semantic Normalization<br/>(Commutative sort, comparison inversion,<br/>OOP wrapper neutralization)"]
        A3["Structural Statement Linearization<br/>(Canonical statement & expr tokens)"]
        RK2["Rabin-Karp Rolling Hashes<br/>(Deterministic CRC32 tokens)"]
        W2["Local Winnowing<br/>(Window size w)"]
    end

    subgraph EVAL["Similarity & Decision Engine"]
        SIM["Jaccard & Sorensen-Dice Metrics"]
        DEC["Decision Threshold Sweep (Precision, Recall, F1, ROC-AUC)"]
    end

    CA --> T1 --> T2 --> RK1 --> W1 --> SIM
    CB --> T1
    CA --> A1 --> A2 --> A3 --> RK2 --> W2 --> SIM
    CB --> A1
    SIM --> DEC
```

### 2.1 Karp-Rabin Rolling Hashes (1987)
Given a sequence of token identifiers $S = [t_0, t_1, \dots, t_{N-1}]$ and a $k$-gram window of length $k$:
$$\mathcal{H}_0 = \left(\sum_{j=0}^{k-1} t_j \cdot B^{k-1-j}\right) \pmod M$$
For sliding step $i \to i+1$, rolling hash updates are computed in $\mathcal{O}(1)$ time:
$$\mathcal{H}_i = \left( \left(\mathcal{H}_{i-1} - t_{i-1} \cdot B^{k-1}\right) \cdot B + t_{i+k-1} \right) \pmod M$$
where $M = 2^{31} - 1$ (Mersenne prime) and $B = 257$.

### 2.2 Winnowing Algorithm (Schleimer et al., 2003)
In every window of $w$ consecutive rolling hashes:
1. Select the minimum hash value $\min(h_i, \dots, h_{i+w-1})$.
2. **Rightmost Tie-Breaking:** If multiple instances equal the minimum, the rightmost hash is selected to maximize its persistence in subsequent windows.
3. **Deduplication:** A fingerprint is recorded only if its position differs from the previous window's selection.
4. **Guarantees:** Shared substrings of length $\ge (w + k - 1)$ tokens are guaranteed to be detected, while spurious matches $< k$ tokens are suppressed.

### 2.3 Proposed AST Normalization Rules
1. **Commutative Canonicalization:** For operators $\odot \in \{+, *, \&, |, \text{\textasciicircum}, ==, !=\}$:
   $$x \odot y \equiv y \odot x \implies \text{Order operands lexicographically}$$
2. **Relational Inequality Inversion:**
   $$a > b \iff b < a \quad \text{and} \quad a \ge b \iff b \le a$$
3. **Augmented Assignment Unification:**
   $$x \mathbin{op}= y \iff x = x \mathbin{op} y$$
4. **Object-Oriented Wrapper Neutralization:**
   $$\text{Attribute}(Name(\text{"self"}), attr) \implies \text{VAR}$$
   Neutralizes LLM evasion where procedural functions are converted to single-purpose classes.

---

## 3. Benchmark Dataset & Verification

To satisfy the SOCO / CodeNet / IR-Plag methodology, we curated 5 core programming problems:
1. **`p01_binary_search`**: Sorted array first-occurrence search.
2. **`p02_merge_intervals`**: Interval sorting and consolidation.
3. **`p03_knapsack`**: 0/1 Knapsack dynamic programming.
4. **`p04_bfs_shortest_path`**: Breadth-first graph traversal on unweighted graphs.
5. **`p05_lcs`**: Longest Common Subsequence dynamic programming.

For each problem, 7 variants were constructed (35 programs total):
* `orig_1.py`: Canonical baseline implementation.
* `orig_2.py`: Independent implementation 1 (alternate algorithmic paradigm, e.g. recursive vs. iterative).
* `orig_3.py`: Independent implementation 2 (alternate data structures / memory layout).
* `manual_rename.py`: Variable and parameter renaming.
* `manual_structure.py`: Loop conversion (`for` $\leftrightarrow$ `while`), statement reordering.
* `llm_paraphrase_light.py`: LLM rewrite with list comprehensions, idiomatic constructs.
* `llm_paraphrase_heavy.py`: Adversarial LLM rewrite (OOP encapsulation, auxiliary generators, branch inversion).

### Dataset Integrity Verification
* **Syntax Integrity (AST):** $35 / 35$ files parsed with zero syntax errors.
* **Functional Equivalence:** Executed $175 / 175$ unit test assertions across all variants. Every single obfuscated and rewritten variant produced identical, correct outputs on test suites.

---

## 4. Empirical Evaluation Results

The evaluation was executed across the 60 ground-truth pairs (25 positive, 35 negative).

### 4.1 Overall Benchmark Performance
| Metric | Baseline (Token Winnowing) | Proposed (AST Winnowing) | Difference |
| :--- | :---: | :---: | :---: |
| **ROC-AUC (Overall)** | **85.49%** (0.855) | **92.80%** (0.928) | **$+7.31\%$** |
| **Optimal Threshold ($\tau^*$)** | $0.0365$ | $0.2729$ | Safe separation margin |
| **Precision** (at $\tau^*$) | $74.19\%$ | **$80.00\%$** | **$+5.81\%$** |
| **Recall** (at $\tau^*$) | $92.00\%$ | **$96.00\%$** | **$+4.00\%$** |
| **F1-Score** (at $\tau^*$) | $82.14\%$ | **$87.27\%$** | **$+5.13\%$** |
| **Mean Comparison Time** | $1.983\text{ ms}$ | **$0.930\text{ ms}$** | **$2.1\times$ Faster** |
| **Std Comparison Time** | $0.582\text{ ms}$ | $0.272\text{ ms}$ | Lower jitter |

### 4.2 Adversarial LLM Rewrite Robustness Study
Evaluating the subset of pairs where code was transformed via Generative AI (`plagiarism_llm_light` and `plagiarism_llm_heavy`) against independent implementations:

| Metric (LLM Subset) | Baseline (Token Winnowing) | JPlag (v5.1.0) | Proposed (AST Winnowing) | Advantage |
| :--- | :---: | :---: | :---: | :---: |
| **ROC-AUC against LLM** | $84.29\%$ | $90.00\%$ | **$93.43\%$** | **$+9.14\%$ over Baseline, $+3.43\%$ over JPlag** |
| **Precision against LLM** | $52.94\%$ | $77.78\%$ | **$62.50\%$** | $+9.56\%$ over Baseline |
| **Recall against LLM** | $90.00\%$ | $70.00\%$ | **$100.00\%$** | **Catches 100% of LLM rewrites (JPlag misses 30%)** |
| **F1-Score against LLM** | $66.67\%$ | $73.68\%$ | **$76.92\%$** | **$+10.25\%$ over Baseline, $+3.24\%$ over JPlag** |

### 4.3 Three-Way Benchmark Summary: Baseline vs. JPlag vs. Proposed AST
| Metric | Baseline (Winnowing) | JPlag (v5.1.0 GST) | Proposed (AST Winnowing) |
| :--- | :---: | :---: | :---: |
| **Overall ROC-AUC** | $85.49\%$ | $89.94\%$ | **$92.80\%$** |
| **Overall F1-Score** | $82.14\%$ | $81.63\%$ | **$87.27\%$** |
| **Overall Recall** | $92.00\%$ | $80.00\%$ | **$96.00\%$** |
| **Overall Precision** | $74.19\%$ | **$83.33\%$** | $80.00\%$ |

### 4.4 Multi-Language Extension (Tree-Sitter for C++ and Python)
Using Tree-Sitter language grammars (`tree_sitter_cpp`, `tree_sitter_python`), the structural normalization pipeline was extended to multi-language ASTs:
* **C++ Variable Renaming & Reordering:** Achieved **$88.89\%$** Jaccard similarity between canonical and obfuscated C++ implementations.
* **C++ Independent Solution Discrimination:** Independent recursive C++ implementations scored **$18.18\%$**, providing a wide discrimination gap of **$>70\%$**.

---

## 5. Visualizations

### 5.1 ROC Curves
The Receiver Operating Characteristic curve demonstrates the separation boundary:

![ROC Curves](C:/Users/Sravya mummana/.gemini/antigravity/brain/5f716d79-eb25-4a7c-9ff9-8f8536a0d3b5/roc_curves.png)

### 5.2 Category Similarity Score Breakdown
Comparing mean Jaccard similarity across all 7 evaluation categories:

![Similarity Breakdown](C:/Users/Sravya mummana/.gemini/antigravity/brain/5f716d79-eb25-4a7c-9ff9-8f8536a0d3b5/category_similarity_barchart.png)

### Category Breakdown Summary Table
| Category | Baseline Token Jaccard | Proposed AST Jaccard | Delta |
| :--- | :---: | :---: | :---: |
| **`plagiarism_manual_rename`** | $100.00\%$ | $100.00\%$ | $\pm 0.00\%$ |
| **`plagiarism_manual_structure`** | $12.33\%$ | **$34.85\%$** | **$+22.52\%$** |
| **`plagiarism_llm_light`** | $26.96\%$ | **$45.79\%$** | **$+18.83\%$** |
| **`plagiarism_llm_heavy`** | $6.06\%$ | **$40.71\%$** | **$+34.66\%$** |
| **`plagiarism_cross_transformed`** | $6.06\%$ | **$40.71\%$** | **$+34.66\%$** |
| **`independent_same_problem`** | $5.36\%$ | $21.33\%$ | Safe separation |
| **`independent_diff_problem`** | $2.39\%$ | $7.62\%$ | Noise floor |

---

## 6. Discussion & Vulnerability Analysis

### 6.1 Why Classical MOSS Collapses on AI Code
MOSS relies on sequential $k$-grams over lexical tokens. When an LLM paraphrases code:
1. **Loop Alteration:** Switching from `for current in intervals[1:]` to `while idx < len(pool)` alters the token sequence, breaking every overlapping $k$-gram containing the loop header.
2. **Encapsulation:** Wrapping procedural logic inside a class (`class KnapsackSolver`) prepends `class`, `def __init__`, `self` attribute references, and method calls. This alters the lexical token stream across the entire file.
3. **Result:** The baseline Jaccard similarity collapsed to **$6.06\%$**, falling right into the noise floor of independent student submissions ($5.36\%$). At that point, any threshold chosen to catch the LLM rewrite inevitably triggers mass false positives on innocent students.

### 6.2 Why AST Normalization Succeeds
1. **Structural Invariance:** Regardless of identifier names or `self.` prefixes, accessing an array element `memo_grid[step][b]` and `dp[i][c]` normalizes to the canonical structural expression `Index(Index(VAR[VAR])[VAR])`.
2. **Commutative Sorting:** Reversing operands in conditional checks or arithmetic expressions ($y + x \to x + y$) produces identical structural token hashes.
3. **Execution Latency:** Because AST statement tokens represent higher-level semantic actions rather than raw lexical tokens, the resulting token sequence is shorter, making Rabin-Karp hashing and Winnowing **$2.1\times$ faster** than the token baseline.

---

## 7. References
1. **Schleimer, S., Wilkerson, D. & Aiken, A. (2003).** *Winnowing: Local Algorithms for Document Fingerprinting.* ACM SIGMOD International Conference on Management of Data, pp. 76–85.
2. **Karp, R. & Rabin, M. (1987).** *Efficient Randomized Pattern-Matching Algorithms.* IBM Journal of Research and Development, 31(2), pp. 249–260.
3. **Prechelt, L., Malpohl, G. & Philippsen, M. (2002).** *Finding Plagiarisms among a Set of Programs with JPlag.* Journal of Universal Computer Science, 8(11), pp. 1016–1038.
4. **Chilowicz, M., Duris, E. & Roussel, N. (2009).** *Syntax Tree Fingerprinting for Source Code Similarity Detection.* IEEE International Working Conference on Source Code Analysis and Manipulation (SCAM).
