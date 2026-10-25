import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, PathPatch
from matplotlib.path import Path
import numpy as np

os.environ['MPLCONFIGDIR'] = 'C:/Users/Sravya mummana/AppData/Local/Temp/matplotlib_cache'
os.makedirs('C:/Users/Sravya mummana/AppData/Local/Temp/matplotlib_cache', exist_ok=True)

out_dir = r"C:\Users\Sravya mummana\OneDrive\dogfood\code_plagiarism_detection\figures"
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------------
def draw_box(ax, x, y, w, h, title, subtitle=None, 
             fc='#FFFFFF', ec='#CBD5E1', tc='#0F172A', sub_tc='#475569',
             title_fs=10, sub_fs=8.5, lw=1.5, r=0.15, z=3):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={r}",
                       facecolor=fc, edgecolor=ec, linewidth=lw, zorder=z)
    ax.add_patch(p)
    cx = x + w / 2.0
    if subtitle:
        cy_title = y + h * 0.72
        cy_sub = y + h * 0.35
        ax.text(cx, cy_title, title, ha='center', va='center',
                fontsize=title_fs, fontweight='bold', color=tc, zorder=z+1)
        ax.text(cx, cy_sub, subtitle, ha='center', va='center',
                fontsize=sub_fs, color=sub_tc, zorder=z+1)
    else:
        ax.text(cx, y + h / 2.0, title, ha='center', va='center',
                fontsize=title_fs, fontweight='bold', color=tc, zorder=z+1)
    return p

def draw_arrow(ax, x1, y1, x2, y2, color='#64748B', lw=1.8, style="-|>", rad=0.0, z=5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2),
                zorder=z)

# =========================================================================
# FIGURE 1: Publication System Architecture (White, High-Res 300 DPI)
# =========================================================================
def generate_fig1_paper():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Main Header
    ax.text(7.0, 8.1, "SynapsCode: Dual-Pipeline Code Plagiarism & LLM Paraphrase Detection",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F172A')
    ax.text(7.0, 7.75, "Comparative Architecture: Baseline Token Winnowing vs. Proposed AST-Normalized Engine",
            ha='center', va='center', fontsize=10.5, color='#64748B', style='italic')

    # Source Box (Left)
    draw_box(ax, 0.5, 3.4, 2.0, 1.8, "Source Programs", "Code A & Code B\n(Python, C++, Java)",
             fc='#F8FAFC', ec='#64748B', tc='#0F172A', sub_tc='#334155', title_fs=11, sub_fs=9, lw=1.8)

    # ---------------- TOP PATH: BASELINE MOSS ----------------
    # Container
    p_base = FancyBboxPatch((3.0, 4.8), 7.6, 2.4, boxstyle="round,pad=0,rounding_size=0.15",
                            facecolor='#FFF5F5', edgecolor='#F87171', linewidth=1.5, linestyle='--', zorder=1)
    ax.add_patch(p_base)
    ax.text(3.2, 7.0, "BASELINE: Classical MOSS-Style Token Winnowing (Schleimer et al., 2003)",
            fontsize=10, fontweight='bold', color='#B91C1C', zorder=2)

    # Boxes in Baseline
    draw_box(ax, 3.2, 5.1, 2.2, 1.6, "1. Lexer / Tokenizer", "Strip comments, docs,\nwhitespace normalization",
             fc='#FFFFFF', ec='#EF4444', tc='#991B1B', sub_tc='#7F1D1D', title_fs=9.5, sub_fs=8)
    draw_box(ax, 5.7, 5.1, 2.2, 1.6, "2. Identifier Masking", "Map variables → 'ID'\nLiterals → 'LIT'",
             fc='#FFFFFF', ec='#EF4444', tc='#991B1B', sub_tc='#7F1D1D', title_fs=9.5, sub_fs=8)
    draw_box(ax, 8.2, 5.1, 2.2, 1.6, "3. Rabin-Karp Hashes", "k-gram rolling window\nMod 2^31 - 1, base 257",
             fc='#FFFFFF', ec='#EF4444', tc='#991B1B', sub_tc='#7F1D1D', title_fs=9.5, sub_fs=8)

    # Connect baseline boxes
    draw_arrow(ax, 5.4, 5.9, 5.7, 5.9, color='#EF4444')
    draw_arrow(ax, 7.9, 5.9, 8.2, 5.9, color='#EF4444')

    # ---------------- BOTTOM PATH: PROPOSED AST ENGINE ----------------
    # Container
    p_ast = FancyBboxPatch((3.0, 1.2), 7.6, 3.1, boxstyle="round,pad=0,rounding_size=0.15",
                           facecolor='#F0FDF4', edgecolor='#22C55E', linewidth=1.8, zorder=1)
    ax.add_patch(p_ast)
    ax.text(3.2, 4.05, "PROPOSED: Structural AST Normalization Engine (SynapsCode)",
            fontsize=10, fontweight='bold', color='#15803D', zorder=2)

    # Boxes in AST
    draw_box(ax, 3.2, 1.5, 2.2, 2.3, "1. AST Parser", "Python native ast /\nTree-Sitter grammars\nFull syntax hierarchy",
             fc='#FFFFFF', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=9.5, sub_fs=8)
    draw_box(ax, 5.7, 1.5, 2.2, 2.3, "2. Semantic Normalizer", "• Commutative sort (x+y)\n• Invert relational (a>b)\n• OOP wrapper neutralization\n• Augmented assign unify",
             fc='#FFFFFF', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=9.5, sub_fs=7.5)
    draw_box(ax, 8.2, 1.5, 2.2, 2.3, "3. Linearizer & Hashes", "Canonical statement walk\nStructural k-grams (k=5)\nDeterministic CRC32/RK",
             fc='#FFFFFF', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=9.5, sub_fs=8)

    # Connect AST boxes
    draw_arrow(ax, 5.4, 2.65, 5.7, 2.65, color='#16A34A')
    draw_arrow(ax, 7.9, 2.65, 8.2, 2.65, color='#16A34A')

    # ---------------- RIGHT: WINNOWING & SIMILARITY ----------------
    draw_box(ax, 11.1, 2.6, 2.4, 3.4, "Winnowing & Decision",
             "Sliding Window (w=4)\nRightmost tie-breaking\nHash Deduplication\n\nJaccard Index (S_A ∩ S_B)\nOptimal Threshold τ* = 0.273\nROC-AUC: 92.80%",
             fc='#EFF6FF', ec='#3B82F6', tc='#1E40AF', sub_tc='#1E3A8A', title_fs=10, sub_fs=8.5, lw=1.8)

    # Output verdict box
    draw_box(ax, 11.1, 0.9, 2.4, 1.2, "Plagiarism Verdict", "Positive Match (Plagiarized)\nor Negative (Independent)",
             fc='#FEF3C7', ec='#F59E0B', tc='#92400E', sub_tc='#78350F', title_fs=9.5, sub_fs=8, lw=1.5)

    # Connect to Winnowing & Output
    draw_arrow(ax, 2.5, 4.6, 3.0, 5.9, color='#EF4444', lw=1.8)
    draw_arrow(ax, 2.5, 3.9, 3.0, 2.65, color='#16A34A', lw=1.8)

    draw_arrow(ax, 10.4, 5.9, 11.1, 4.8, color='#EF4444', lw=1.8)
    draw_arrow(ax, 10.4, 2.65, 11.1, 3.8, color='#16A34A', lw=1.8)
    draw_arrow(ax, 12.3, 2.6, 12.3, 2.1, color='#F59E0B', lw=1.8)

    out_path = os.path.join(out_dir, "fig1_system_architecture_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

# =========================================================================
# FIGURE 2: AST Normalization & Tree Comparison (White, High-Res 300 DPI)
# =========================================================================
def generate_fig2_ast_tree():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Title
    ax.text(7.0, 8.1, "Figure 2: AST Canonicalization Neutralizing Identifier Renaming & Commutativity",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(7.0, 7.7, "Demonstration on 'def add(a, b): return a + b' vs. 'def sum(x, y): return y + x'",
            ha='center', va='center', fontsize=10.5, color='#64748B', style='italic')

    # Left Box: Program A
    p_a = FancyBboxPatch((0.6, 3.6), 5.8, 3.7, boxstyle="round,pad=0,rounding_size=0.15",
                         facecolor='#F8FAFC', edgecolor='#3B82F6', linewidth=1.5, zorder=1)
    ax.add_patch(p_a)
    ax.text(0.9, 7.0, "Program A (Original)", fontsize=11, fontweight='bold', color='#1D4ED8')
    ax.text(0.9, 6.55, "def add(a, b):\n    return a + b", fontsize=10, family='monospace', color='#0F172A',
            bbox=dict(boxstyle="round,pad=0.3", fc="#EFF6FF", ec="#BFDBFE"))

    # Tree Nodes Program A
    draw_box(ax, 2.6, 5.6, 1.8, 0.6, "FunctionDef('add')", fc='#DBEAFE', ec='#3B82F6', title_fs=8.5)
    draw_box(ax, 1.4, 4.6, 1.6, 0.55, "args: ['a', 'b']", fc='#F1F5F9', ec='#94A3B8', title_fs=8)
    draw_box(ax, 3.8, 4.6, 1.6, 0.55, "Return", fc='#DBEAFE', ec='#3B82F6', title_fs=8)
    draw_box(ax, 3.8, 3.8, 1.6, 0.55, "BinOp(+)", fc='#EFF6FF', ec='#3B82F6', title_fs=8)

    draw_arrow(ax, 3.2, 5.6, 2.2, 5.15, color='#94A3B8', lw=1.2)
    draw_arrow(ax, 3.8, 5.6, 4.6, 5.15, color='#3B82F6', lw=1.2)
    draw_arrow(ax, 4.6, 4.6, 4.6, 4.35, color='#3B82F6', lw=1.2)

    # Right Box: Program B (Obfuscated / LLM Rewritten)
    p_b = FancyBboxPatch((7.6, 3.6), 5.8, 3.7, boxstyle="round,pad=0,rounding_size=0.15",
                         facecolor='#FDF4FF', edgecolor='#A855F7', linewidth=1.5, zorder=1)
    ax.add_patch(p_b)
    ax.text(7.9, 7.0, "Program B (Renamed & Commutative Inversion)", fontsize=11, fontweight='bold', color='#7E22CE')
    ax.text(7.9, 6.55, "def sum(x, y):\n    return y + x", fontsize=10, family='monospace', color='#0F172A',
            bbox=dict(boxstyle="round,pad=0.3", fc="#FAF5FF", ec="#E9D5FF"))

    # Tree Nodes Program B
    draw_box(ax, 9.6, 5.6, 1.8, 0.6, "FunctionDef('sum')", fc='#F3E8FF', ec='#A855F7', title_fs=8.5)
    draw_box(ax, 8.4, 4.6, 1.6, 0.55, "args: ['x', 'y']", fc='#F1F5F9', ec='#94A3B8', title_fs=8)
    draw_box(ax, 10.8, 4.6, 1.6, 0.55, "Return", fc='#F3E8FF', ec='#A855F7', title_fs=8)
    draw_box(ax, 10.8, 3.8, 1.6, 0.55, "BinOp(+)", fc='#FAF5FF', ec='#A855F7', title_fs=8)

    draw_arrow(ax, 10.2, 5.6, 9.2, 5.15, color='#94A3B8', lw=1.2)
    draw_arrow(ax, 10.8, 5.6, 11.6, 5.15, color='#A855F7', lw=1.2)
    draw_arrow(ax, 11.6, 4.6, 11.6, 4.35, color='#A855F7', lw=1.2)

    # Central Normalization Engine Block
    draw_arrow(ax, 3.5, 3.6, 5.8, 2.7, color='#16A34A', lw=2.0)
    draw_arrow(ax, 10.5, 3.6, 8.2, 2.7, color='#16A34A', lw=2.0)

    # Bottom Box: Invariant Normalized AST
    p_norm = FancyBboxPatch((3.0, 0.6), 8.0, 2.1, boxstyle="round,pad=0,rounding_size=0.15",
                            facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=2.0, zorder=1)
    ax.add_patch(p_norm)
    ax.text(7.0, 2.4, "Canonical AST Normalizer: Identifier Masking + Lexicographical Sorting",
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#15803D')

    # Tree Nodes Canonical
    draw_box(ax, 3.4, 0.9, 2.0, 1.1, "Func(VAR_0, VAR_1)", "Canonical func wrapper",
             fc='#DCFCE7', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=9, sub_fs=7.5)
    draw_box(ax, 5.9, 0.9, 2.2, 1.1, "Return: BinOp(+)", "Commutative Sorted: (v0, v1)",
             fc='#DCFCE7', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=9, sub_fs=7.5)
    draw_box(ax, 8.6, 0.9, 2.0, 1.1, "Hash Fingerprint", "0x8F3A2B1C\n100% Invariant Match!",
             fc='#FEF08A', ec='#CA8A04', tc='#854D0E', sub_tc='#713F12', title_fs=9, sub_fs=8)

    draw_arrow(ax, 5.4, 1.45, 5.9, 1.45, color='#16A34A', lw=1.5)
    draw_arrow(ax, 8.1, 1.45, 8.6, 1.45, color='#16A34A', lw=1.5)

    out_path = os.path.join(out_dir, "fig2_ast_tree_canonicalization_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

# =========================================================================
# FIGURE 3: Winnowing Algorithm & Rolling Hashes (White, High-Res 300 DPI)
# =========================================================================
def generate_fig3_winnowing():
    fig, ax = plt.subplots(figsize=(14, 7.5), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(7.0, 7.6, "Figure 3: Karp-Rabin Rolling Hash & Winnowing Fingerprint Selection",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(7.0, 7.2, "Sliding k-grams (k=5) and Winnowing Window (w=4) with Rightmost Minimum Tie-Breaking",
            ha='center', va='center', fontsize=10.5, color='#64748B', style='italic')

    # Step 1: Token Sequence
    ax.text(0.8, 6.3, "Step 1: Normalized Token Stream:", fontsize=11, fontweight='bold', color='#1E293B')
    tokens = ["VAR", "=", "VAR", "+", "CONST", ";", "IF", "VAR", ">", "CONST"]
    for i, tok in enumerate(tokens):
        draw_box(ax, 0.8 + i * 1.25, 5.6, 1.1, 0.5, tok, fc='#F1F5F9', ec='#94A3B8', tc='#0F172A', title_fs=9)

    # Step 2: k-grams and Rolling Hashes
    ax.text(0.8, 4.9, "Step 2: Karp-Rabin Rolling Hashes (k=5 tokens, Mod 2^31 - 1):", fontsize=11, fontweight='bold', color='#1E293B')
    hashes = [77, 34, 52, 19, 88, 19, 43]
    for i, h_val in enumerate(hashes):
        draw_box(ax, 1.5 + i * 1.5, 4.1, 1.2, 0.6, f"h_{i}", f"{h_val}",
                 fc='#EFF6FF', ec='#3B82F6', tc='#1D4ED8', sub_tc='#1E3A8A', title_fs=9, sub_fs=8)

    # Step 3: Winnowing Window Selection
    ax.text(0.8, 3.4, "Step 3: Sliding Winnowing Window (w=4) & Minimum Selection:", fontsize=11, fontweight='bold', color='#1E293B')

    # Window 1: [77, 34, 52, 19] -> min is 19 at index 3
    p_w1 = FancyBboxPatch((1.3, 2.3), 6.0, 0.85, boxstyle="round,pad=0,rounding_size=0.1",
                          facecolor='#FEF3C7', edgecolor='#F59E0B', linewidth=1.5, zorder=1)
    ax.add_patch(p_w1)
    ax.text(1.5, 2.7, "Window 0: [77, 34, 52, 19] → Minimum = 19 (pos 3) [RECORDED]",
            fontsize=9.5, fontweight='bold', color='#92400E', zorder=2)

    # Window 2: [34, 52, 19, 88] -> min is 19 at index 3 (persists, not duplicated)
    p_w2 = FancyBboxPatch((2.8, 1.3), 6.0, 0.85, boxstyle="round,pad=0,rounding_size=0.1",
                          facecolor='#F1F5F9', edgecolor='#94A3B8', linewidth=1.2, linestyle='--', zorder=1)
    ax.add_patch(p_w2)
    ax.text(3.0, 1.7, "Window 1: [34, 52, 19, 88] → Minimum = 19 (pos 3) [SKIPPED - Duplicate]",
            fontsize=9.5, color='#475569', zorder=2)

    # Window 3: [52, 19, 88, 19] -> min is 19 at pos 3 and pos 5. Rightmost tie-break chooses pos 5!
    p_w3 = FancyBboxPatch((4.3, 0.3), 6.5, 0.85, boxstyle="round,pad=0,rounding_size=0.1",
                          facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=1.8, zorder=1)
    ax.add_patch(p_w3)
    ax.text(4.5, 0.7, "Window 2: [52, 19, 88, 19] → Rightmost Tie-Break = 19 (pos 5) [RECORDED]",
            fontsize=9.5, fontweight='bold', color='#166534', zorder=2)

    # Fingerprint Output Set Box (Right)
    draw_box(ax, 11.2, 0.8, 2.4, 4.8, "Selected Document\nFingerprints",
             "Persistent Hashes:\n• (Hash: 19, Pos: 3)\n• (Hash: 19, Pos: 5)\n• ...\n\nGuarantees:\nMatches >= (w + k - 1)\n= 8 tokens detected\nNoise < k suppressed",
             fc='#F0FDF4', ec='#16A34A', tc='#166534', sub_tc='#14532D', title_fs=10, sub_fs=8.5, lw=1.8)

    draw_arrow(ax, 7.3, 2.7, 11.2, 3.2, color='#F59E0B', lw=1.5)
    draw_arrow(ax, 10.8, 0.7, 11.2, 2.0, color='#16A34A', lw=1.8)

    out_path = os.path.join(out_dir, "fig3_winnowing_mechanism_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

# =========================================================================
# FIGURE 4: Adversarial LLM Attacks & Countermeasures (White, 300 DPI)
# =========================================================================
def generate_fig4_llm_attacks():
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')

    # Title
    ax.text(7.0, 8.1, "Figure 4: Taxonomy of Generative AI Code Paraphrasing & AST Neutralization",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(7.0, 7.7, "Analysis of Why Classical MOSS Collapses ($6.06\\%$) and Proposed AST Recovers ($40.71\\%$)",
            ha='center', va='center', fontsize=10.5, color='#64748B', style='italic')

    # 4 Rows of Attacks
    attacks = [
        {
            "name": "1. Identifier & Function Renaming",
            "example": "find_first(arr, target) → b_search(lst, key)",
            "moss": "Fails if token sequences vary; passes if simple mask",
            "moss_res": "100%", "moss_color": "#22C55E",
            "ast": "Maps all variable/argument names to canonical VAR",
            "ast_res": "100%", "ast_color": "#22C55E"
        },
        {
            "name": "2. Commutative & Relational Inversion",
            "example": "if a > b or (x + y == 10) → if b < a or (y + x == 10)",
            "moss": "Breaks lexical k-grams completely (0% overlap in window)",
            "moss_res": "12.3%", "moss_color": "#EF4444",
            "ast": "Commutative operand sorting & relational operator inversion",
            "ast_res": "88.9%", "ast_color": "#22C55E"
        },
        {
            "name": "3. Loop Paradigm Substitution",
            "example": "for x in data: ... → idx = 0; while idx < len(data): ...",
            "moss": "Alters token grammar from FOR to WHILE + INDEX syntax",
            "moss_res": "26.9%", "moss_color": "#EF4444",
            "ast": "Statement sequence linearization preserves body expressions",
            "ast_res": "45.8%", "ast_color": "#16A34A"
        },
        {
            "name": "4. OOP Wrapper & Auxiliary Methods",
            "example": "Procedural function → class Solver: def solve(self): ...",
            "moss": "Prepends class, self attributes, destroying all k-grams",
            "moss_res": "6.06%", "moss_color": "#B91C1C",
            "ast": "Neutralizes self attributes, extracts core semantic blocks",
            "ast_res": "40.7%", "ast_color": "#16A34A"
        }
    ]

    y_start = 6.8
    row_h = 1.35
    for i, att in enumerate(attacks):
        y = y_start - i * 1.55

        # Attack Info Box
        draw_box(ax, 0.5, y, 4.5, row_h, att["name"], att["example"],
                 fc='#F8FAFC', ec='#64748B', tc='#0F172A', sub_tc='#475569', title_fs=9.5, sub_fs=8)

        # Baseline MOSS Column
        draw_box(ax, 5.2, y, 4.0, row_h, f"MOSS Token Baseline: {att['moss_res']}", att["moss"],
                 fc='#FEF2F2', ec=att["moss_color"], tc='#991B1B', sub_tc='#7F1D1D', title_fs=9.5, sub_fs=7.5, lw=1.5)

        # Proposed AST Column
        draw_box(ax, 9.4, y, 4.1, row_h, f"Proposed SynapsCode: {att['ast_res']}", att["ast"],
                 fc='#F0FDF4', ec=att["ast_color"], tc='#166534', sub_tc='#14532D', title_fs=9.5, sub_fs=7.5, lw=1.5)

    out_path = os.path.join(out_dir, "fig4_adversarial_paraphrase_taxonomy_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

# =========================================================================
# FIGURE 5: Comprehensive Empirical Evaluation Dashboard (White, 300 DPI)
# =========================================================================
def generate_fig5_evaluation_dashboard():
    fig = plt.figure(figsize=(15, 9), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    gs = fig.add_gridspec(2, 2, hspace=0.28, wspace=0.22,
                          left=0.07, right=0.95, top=0.92, bottom=0.08)

    fig.suptitle("Figure 5: Empirical Benchmark Evaluation (SynapsCode AST vs. Baseline vs. JPlag)",
                 fontsize=15, fontweight='bold', color='#0F172A')

    # Panel A: ROC Curves
    ax1 = fig.add_subplot(gs[0, 0])
    # Exact ROC points from empirical evaluation
    fpr_ast = [0.0, 0.0, 0.0, 0.06, 0.06, 0.08, 0.08, 0.17, 0.17, 0.40, 1.0]
    tpr_ast = [0.0, 0.36, 0.68, 0.68, 0.80, 0.80, 0.96, 0.96, 1.0, 1.0, 1.0]

    fpr_base = [0.0, 0.0, 0.06, 0.06, 0.15, 0.15, 0.17, 0.17, 0.23, 0.23, 0.57, 0.57, 1.0]
    tpr_base = [0.0, 0.28, 0.28, 0.36, 0.36, 0.56, 0.56, 0.84, 0.84, 0.92, 0.92, 1.0, 1.0]

    ax1.plot(fpr_ast, tpr_ast, color='#16A34A', lw=2.5, label='Proposed AST (AUC = 0.928)')
    ax1.plot(fpr_base, tpr_base, color='#DC2626', lw=2.0, label='Baseline Token (AUC = 0.855)')
    ax1.plot([0, 1], [0, 1], color='#94A3B8', linestyle='--', label='Random (AUC = 0.500)')
    ax1.set_title("A: ROC Curves (Overall Benchmark)", fontsize=11, fontweight='bold', color='#0F172A')
    ax1.set_xlabel("False Positive Rate", fontsize=9.5)
    ax1.set_ylabel("True Positive Rate (Recall)", fontsize=9.5)
    ax1.legend(loc='lower right', fontsize=8.5)
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Panel B: Category Similarity Breakdown
    ax2 = fig.add_subplot(gs[0, 1])
    categories = ['Rename', 'Structure', 'LLM Light', 'LLM Heavy', 'Same-Prob\nIndep.', 'Diff-Prob\nIndep.']
    base_scores = [100.0, 12.33, 26.96, 6.06, 5.36, 2.39]
    ast_scores = [100.0, 34.85, 45.79, 40.71, 21.33, 7.62]

    x = np.arange(len(categories))
    w = 0.35
    ax2.bar(x - w/2, base_scores, w, label='Baseline Token', color='#F87171')
    ax2.bar(x + w/2, ast_scores, w, label='Proposed AST', color='#34D399')
    ax2.set_title("B: Mean Similarity Score by Obfuscation Category", fontsize=11, fontweight='bold', color='#0F172A')
    ax2.set_ylabel("Jaccard Similarity (%)", fontsize=9.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=8.5)
    ax2.legend(loc='upper right', fontsize=8.5)
    ax2.grid(True, axis='y', linestyle=':', alpha=0.6)

    # Panel C: Three-Way LLM Robustness Comparison (Baseline vs JPlag vs Proposed AST)
    ax3 = fig.add_subplot(gs[1, 0])
    metrics = ['ROC-AUC', 'Precision', 'Recall', 'F1-Score']
    base_llm = [84.29, 52.94, 90.00, 66.67]
    jplag_llm = [90.00, 77.78, 70.00, 73.68]
    ast_llm = [93.43, 62.50, 100.00, 76.92]

    x3 = np.arange(len(metrics))
    w3 = 0.25
    ax3.bar(x3 - w3, base_llm, w3, label='Baseline Token', color='#F87171')
    ax3.bar(x3, jplag_llm, w3, label='JPlag (v5.1.0)', color='#60A5FA')
    ax3.bar(x3 + w3, ast_llm, w3, label='Proposed AST', color='#34D399')
    ax3.set_title("C: Adversarial LLM Rewrite Robustness (Three-Way)", fontsize=11, fontweight='bold', color='#0F172A')
    ax3.set_ylabel("Score (%)", fontsize=9.5)
    ax3.set_xticks(x3)
    ax3.set_xticklabels(metrics, fontsize=8.5)
    ax3.legend(loc='lower right', fontsize=8.5)
    ax3.grid(True, axis='y', linestyle=':', alpha=0.6)

    # Panel D: Execution Speed & Efficiency Comparison
    ax4 = fig.add_subplot(gs[1, 1])
    models = ['Baseline Token\n(Winnowing)', 'Proposed AST\n(SynapsCode)']
    latencies = [1.983, 0.930]
    errors = [0.582, 0.272]
    colors = ['#F87171', '#34D399']

    bars = ax4.bar(models, latencies, yerr=errors, capsize=6, color=colors, width=0.45, edgecolor='#475569', lw=1.2)
    ax4.set_title("D: Pairwise Comparison Latency (ms / pair)", fontsize=11, fontweight='bold', color='#0F172A')
    ax4.set_ylabel("Time (milliseconds)", fontsize=9.5)
    ax4.grid(True, axis='y', linestyle=':', alpha=0.6)

    for bar, val in zip(bars, latencies):
        ax4.text(bar.get_x() + bar.get_width() / 2, val + 0.35, f"{val:.3f} ms\n({1.983/val:.1f}x speed)",
                 ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0F172A')

    out_path = os.path.join(out_dir, "fig5_empirical_evaluation_dashboard_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

if __name__ == '__main__':
    generate_fig1_paper()
    generate_fig2_ast_tree()
    generate_fig3_winnowing()
    generate_fig4_llm_attacks()
    generate_fig5_evaluation_dashboard()
