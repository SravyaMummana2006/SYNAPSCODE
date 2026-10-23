"""
Experimental Evaluation and Benchmarking Suite.
Computes all required metrics:
1. Precision
2. Recall
3. F1-Score
4. ROC-AUC (Area Under the Receiver Operating Characteristic Curve)
5. Pairwise Comparison Time (latency per comparison)

Evaluates:
- Baseline (Classical Token-Level Winnowing)
- Improved (AST-Normalized Structural Winnowing)
across the benchmark dataset and generates publication-grade plots and metrics.
"""

import os
import sys
import json
import time
import numpy as np
from typing import Dict, List, Tuple
from sklearn.metrics import roc_curve, auc, roc_auc_score, precision_recall_curve, f1_score

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from baseline.detector import TokenWinnowingDetector
from ast_engine.detector import ASTWinnowingDetector

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

RESULTS_DIR = os.path.join(BASE_DIR, "results")
BENCHMARKS_DIR = os.path.join(BASE_DIR, "dataset", "benchmarks")
MANIFEST_PATH = os.path.join(BASE_DIR, "dataset", "ground_truth.json")

def load_ground_truth() -> List[Dict]:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run_evaluation():
    print("=" * 80)
    print("  RUNNING COMPREHENSIVE EXPERIMENTAL EVALUATION")
    print("=" * 80)

    pairs = load_ground_truth()
    y_true = np.array([p["is_plagiarism"] for p in pairs])
    categories = [p["category"] for p in pairs]

    baseline_detector = TokenWinnowingDetector(k=10, w=5)
    ast_detector = ASTWinnowingDetector(k=1, w=2)

    # 1. Collect pairwise predictions and runtimes
    baseline_scores = []
    baseline_times = []

    ast_scores = []
    ast_times = []

    for p in pairs:
        f1_path = os.path.join(BENCHMARKS_DIR, p["file1"])
        f2_path = os.path.join(BENCHMARKS_DIR, p["file2"])

        # Baseline
        res_b = baseline_detector.compare_files(f1_path, f2_path)
        baseline_scores.append(res_b.jaccard)
        baseline_times.append(res_b.execution_time_sec)

        # AST
        res_a = ast_detector.compare_files(f1_path, f2_path)
        ast_scores.append(res_a.jaccard)
        ast_times.append(res_a.execution_time_sec)

    baseline_scores = np.array(baseline_scores)
    ast_scores = np.array(ast_scores)

    baseline_times = np.array(baseline_times) * 1000.0  # ms
    ast_times = np.array(ast_times) * 1000.0            # ms

    # 2. Compute ROC-AUC
    baseline_auc = roc_auc_score(y_true, baseline_scores)
    ast_auc = roc_auc_score(y_true, ast_scores)

    # 3. Find Optimal Decision Thresholds (maximizing F1)
    def compute_optimal_metrics(scores, y):
        thresholds = np.linspace(0.01, 0.99, 1000)
        best_f1 = -1.0
        best_thresh = 0.5
        best_prec = 0.0
        best_rec = 0.0

        for t in thresholds:
            y_pred = (scores >= t).astype(int)
            tp = np.sum((y_pred == 1) & (y == 1))
            fp = np.sum((y_pred == 1) & (y == 0))
            fn = np.sum((y_pred == 0) & (y == 1))

            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2.0 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0

            if f1 > best_f1:
                best_f1 = f1
                best_thresh = t
                best_prec = prec
                best_rec = rec

        return {
            "optimal_threshold": float(best_thresh),
            "precision": float(best_prec),
            "recall": float(best_rec),
            "f1_score": float(best_f1)
        }

    baseline_opt = compute_optimal_metrics(baseline_scores, y_true)
    ast_opt = compute_optimal_metrics(ast_scores, y_true)

    # 4. Subset Evaluation: Performance on AI-Generated / LLM Paraphrased Code
    llm_mask = np.array([("llm" in cat) or (y_val == 0) for cat, y_val in zip(categories, y_true)])
    y_llm = y_true[llm_mask]
    base_llm_scores = baseline_scores[llm_mask]
    ast_llm_scores = ast_scores[llm_mask]

    baseline_llm_auc = roc_auc_score(y_llm, base_llm_scores)
    ast_llm_auc = roc_auc_score(y_llm, ast_llm_scores)
    baseline_llm_opt = compute_optimal_metrics(base_llm_scores, y_llm)
    ast_llm_opt = compute_optimal_metrics(ast_llm_scores, y_llm)

    # 5. Runtime Metrics
    baseline_latency_mean = float(np.mean(baseline_times))
    baseline_latency_std = float(np.std(baseline_times))
    ast_latency_mean = float(np.mean(ast_times))
    ast_latency_std = float(np.std(ast_times))

    # Print Summary Table
    print("\n" + "=" * 80)
    print("                    OVERALL BENCHMARK EVALUATION RESULTS")
    print("=" * 80)
    print(f"{'Metric':30s} | {'Baseline (Token Winnowing)':26s} | {'Proposed (AST Winnowing)':24s}")
    print("-" * 86)
    print(f"{'ROC-AUC (Overall)':30s} | {baseline_auc*100:24.2f}% | {ast_auc*100:22.2f}%")
    print(f"{'Optimal Threshold':30s} | {baseline_opt['optimal_threshold']:24.4f} | {ast_opt['optimal_threshold']:22.4f}")
    print(f"{'Precision (at optimal)':30s} | {baseline_opt['precision']*100:24.2f}% | {ast_opt['precision']*100:22.2f}%")
    print(f"{'Recall (at optimal)':30s} | {baseline_opt['recall']*100:24.2f}% | {ast_opt['recall']*100:22.2f}%")
    print(f"{'F1-Score (at optimal)':30s} | {baseline_opt['f1_score']*100:24.2f}% | {ast_opt['f1_score']*100:22.2f}%")
    print(f"{'Mean Pairwise Time':30s} | {baseline_latency_mean:19.3f} ms | {ast_latency_mean:17.3f} ms")
    print(f"{'Std Pairwise Time':30s} | {baseline_latency_std:19.3f} ms | {ast_latency_std:17.3f} ms")
    print("=" * 86)

    print("\n" + "=" * 80)
    print("          AI-OBFUSCATION / LLM REWRITE SUBSET (Robustness Study)")
    print("=" * 80)
    print(f"{'Metric (LLM Subset)':30s} | {'Baseline (Token Winnowing)':26s} | {'Proposed (AST Winnowing)':24s}")
    print("-" * 86)
    print(f"{'ROC-AUC (against LLM)':30s} | {baseline_llm_auc*100:24.2f}% | {ast_llm_auc*100:22.2f}%")
    print(f"{'Precision (against LLM)':30s} | {baseline_llm_opt['precision']*100:24.2f}% | {ast_llm_opt['precision']*100:22.2f}%")
    print(f"{'Recall (against LLM)':30s} | {baseline_llm_opt['recall']*100:24.2f}% | {ast_llm_opt['recall']*100:22.2f}%")
    print(f"{'F1-Score (against LLM)':30s} | {baseline_llm_opt['f1_score']*100:24.2f}% | {ast_llm_opt['f1_score']*100:22.2f}%")
    print("=" * 86)

    # 6. Generate ROC Curve Plots
    fpr_b, tpr_b, _ = roc_curve(y_true, baseline_scores)
    fpr_a, tpr_a, _ = roc_curve(y_true, ast_scores)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr_b, tpr_b, color="#d9534f", lw=2.5, label=f"Baseline Token-Winnowing (AUC = {baseline_auc:.3f})")
    plt.plot(fpr_a, tpr_a, color="#2b8a3e", lw=2.5, label=f"Proposed AST-Winnowing (AUC = {ast_auc:.3f})")
    plt.plot([0, 1], [0, 1], color="#868e96", lw=1.5, linestyle="--", label="Random Classifier (AUC = 0.500)")

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
    plt.ylabel("True Positive Rate (Recall / Sensitivity)", fontsize=12)
    plt.title("ROC Curves: Baseline vs. AST-Normalized Plagiarism Detection", fontsize=13, fontweight="bold")
    plt.legend(loc="lower right", fontsize=11)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()

    roc_plot_path = os.path.join(RESULTS_DIR, "roc_curves.png")
    plt.savefig(roc_plot_path, dpi=300)
    plt.close()
    print(f"\nSaved ROC curves plot to: {roc_plot_path}")

    # 7. Category Bar Chart
    cat_order = [
        "plagiarism_manual_rename",
        "plagiarism_manual_structure",
        "plagiarism_llm_light",
        "plagiarism_llm_heavy",
        "plagiarism_cross_transformed",
        "independent_same_problem",
        "independent_diff_problem"
    ]
    labels_short = [
        "Manual\nRename",
        "Manual\nStructure",
        "LLM\nLight",
        "LLM\nHeavy",
        "Cross\nTransformed",
        "Same-Prob\nIndep.",
        "Diff-Prob\nIndep."
    ]

    base_cat_means = [np.mean(baseline_scores[np.array(categories) == c]) * 100 for c in cat_order]
    ast_cat_means = [np.mean(ast_scores[np.array(categories) == c]) * 100 for c in cat_order]

    x = np.arange(len(cat_order))
    width = 0.35

    plt.figure(figsize=(10, 5.5))
    plt.bar(x - width/2, base_cat_means, width, label="Baseline (Token)", color="#e03131", alpha=0.85)
    plt.bar(x + width/2, ast_cat_means, width, label="Proposed (AST)", color="#2f9e44", alpha=0.85)

    plt.ylabel("Mean Jaccard Similarity (%)", fontsize=12)
    plt.title("Similarity Score Breakdown by Obfuscation & Paraphrase Category", fontsize=13, fontweight="bold")
    plt.xticks(x, labels_short, fontsize=10)
    plt.ylim([0, 105])
    plt.axhline(0, color="black", linewidth=0.8)
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()

    barchart_path = os.path.join(RESULTS_DIR, "category_similarity_barchart.png")
    plt.savefig(barchart_path, dpi=300)
    plt.close()
    print(f"Saved category similarity breakdown chart to: {barchart_path}")

    # 8. Save structured metrics JSON
    summary_data = {
        "overall_evaluation": {
            "baseline": {
                "roc_auc": float(baseline_auc),
                "optimal_threshold": baseline_opt["optimal_threshold"],
                "precision": baseline_opt["precision"],
                "recall": baseline_opt["recall"],
                "f1_score": baseline_opt["f1_score"],
                "mean_pairwise_time_ms": baseline_latency_mean,
                "std_pairwise_time_ms": baseline_latency_std
            },
            "ast_winnowing": {
                "roc_auc": float(ast_auc),
                "optimal_threshold": ast_opt["optimal_threshold"],
                "precision": ast_opt["precision"],
                "recall": ast_opt["recall"],
                "f1_score": ast_opt["f1_score"],
                "mean_pairwise_time_ms": ast_latency_mean,
                "std_pairwise_time_ms": ast_latency_std
            }
        },
        "llm_robustness_study": {
            "baseline": {
                "roc_auc": float(baseline_llm_auc),
                "precision": baseline_llm_opt["precision"],
                "recall": baseline_llm_opt["recall"],
                "f1_score": baseline_llm_opt["f1_score"]
            },
            "ast_winnowing": {
                "roc_auc": float(ast_llm_auc),
                "precision": ast_llm_opt["precision"],
                "recall": ast_llm_opt["recall"],
                "f1_score": ast_llm_opt["f1_score"]
            }
        },
        "category_breakdown": {
            cat: {
                "baseline_mean_jaccard": float(b_mean / 100.0),
                "ast_mean_jaccard": float(a_mean / 100.0)
            }
            for cat, b_mean, a_mean in zip(cat_order, base_cat_means, ast_cat_means)
        }
    }

    json_path = os.path.join(RESULTS_DIR, "evaluation_metrics.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"Saved structured metrics to: {json_path}")
    print("\nEVALUATION COMPLETE.")

if __name__ == "__main__":
    run_evaluation()
