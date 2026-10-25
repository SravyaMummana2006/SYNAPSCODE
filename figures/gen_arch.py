import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

os.environ['MPLCONFIGDIR'] = 'C:/Users/Sravya mummana/AppData/Local/Temp/matplotlib_cache'
os.makedirs('C:/Users/Sravya mummana/AppData/Local/Temp/matplotlib_cache', exist_ok=True)

out_dir = r"C:\Users\Sravya mummana\OneDrive\dogfood\code_plagiarism_detection\figures"
os.makedirs(out_dir, exist_ok=True)

def draw_rounded_box(ax, xy, width, height, text, title=None, 
                     box_color='#E0F2FE', edge_color='#0284C7', text_color='#0F172A',
                     fontsize=10, boxstyle="round,pad=0.4,rounding_size=0.15", linewidth=1.5):
    x, y = xy
    p = FancyBboxPatch((x, y), width, height,
                       boxstyle=boxstyle,
                       facecolor=box_color, edgecolor=edge_color,
                       linewidth=linewidth, zorder=3)
    ax.add_patch(p)
    cx = x + width / 2.0
    cy = y + height / 2.0
    if title:
        ax.text(cx, y + height - 0.12, title, ha='center', va='top',
                fontsize=fontsize, fontweight='bold', color=text_color, zorder=4)
        ax.text(cx, cy - 0.05, text, ha='center', va='center',
                fontsize=fontsize - 1.5, color=text_color, zorder=4)
    else:
        ax.text(cx, cy, text, ha='center', va='center',
                fontsize=fontsize, color=text_color, zorder=4)
    return p

def draw_arrow(ax, start, end, color='#0284C7', lw=1.8, style="-|>", rad=0.0):
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=4, shrinkB=4),
                zorder=5)

# =========================================================================
# 1. ACADEMIC PAPER SYSTEM ARCHITECTURE (White background, high DPI)
# =========================================================================
def generate_system_architecture_paper():
    fig, ax = plt.subplots(figsize=(13, 7.5), dpi=300)
    ax.set_facecolor('#FFFFFF')
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8)
    ax.axis('off')

    # Title
    ax.text(6.5, 7.6, "SynapsCode: Dual-Engine Code Plagiarism & LLM Paraphrase Detection Pipeline",
            ha='center', va='center', fontsize=14, fontweight='bold', color='#0F172A')
    ax.text(6.5, 7.25, "Structural AST Canonicalization vs. Classical Lexical Token Winnowing",
            ha='center', va='center', fontsize=10.5, color='#475569', style='italic')

    # Input Box
    draw_rounded_box(ax, (0.5, 3.2), 1.8, 1.6, "Code A & Code B\n(Python / C++ / Java)",
                     title="Source Programs", box_color='#F1F5F9', edge_color='#64748B',
                     text_color='#0F172A', fontsize=10)

    # Subgraph 1: Classical Token Pipeline (Top)
    p_base = FancyBboxPatch((2.7, 4.3), 7.5, 2.5, boxstyle="round,pad=0.3,rounding_size=0.1",
                            facecolor='#FEF2F2', edgecolor='#EF4444', linewidth=1.2, linestyle='--', zorder=1)
    ax.add_patch(p_base)
    ax.text(2.9, 6.55, "Baseline Path: Classical MOSS Token Winnowing", fontsize=10, fontweight='bold', color='#991B1B')

    draw_rounded_box(ax, (3.0, 4.6), 1.9, 1.5, "Comments & docstrings\nwhitespace removal",
                     title="Lexer / Tokenizer", box_color='#FFFFFF', edge_color='#F87171', fontsize=9)
    draw_rounded_box(ax, (5.2, 4.6), 2.2, 1.5, "Map identifiers → VAR\nLiterals → CONST",
                     title="Identifier Masking", box_color='#FFFFFF', edge_color='#F87171', fontsize=9)
    draw_rounded_box(ax, (7.7, 4.6), 2.2, 1.5, "k-gram sliding window\nHash mod 2^31-1",
                     title="Rabin-Karp Hashes", box_color='#FFFFFF', edge_color='#F87171', fontsize=9)

    # Subgraph 2: Proposed AST Pipeline (Bottom)
    p_ast = FancyBboxPatch((2.7, 0.8), 7.5, 3.1, boxstyle="round,pad=0.3,rounding_size=0.1",
                           facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=1.5, zorder=1)
    ax.add_patch(p_ast)
    ax.text(2.9, 3.65, "Proposed Path: AST-Normalized Structural Winnowing Engine", fontsize=10, fontweight='bold', color='#166534')

    draw_rounded_box(ax, (3.0, 1.1), 1.9, 2.2, "Generate syntax tree\nLanguage grammar\n(Python/Tree-Sitter)",
                     title="AST Parsing", box_color='#FFFFFF', edge_color='#4ADE80', fontsize=9)
    draw_rounded_box(ax, (5.2, 1.1), 2.2, 2.2, "• Commutative sort (x+y)\n• Invert ops (a>b ↔ b<a)\n• Neutralize OOP classes\n• Augmented assign unify",
                     title="Semantic Normalizer", box_color='#FFFFFF', edge_color='#4ADE80', fontsize=8.5)
    draw_rounded_box(ax, (7.7, 1.1), 2.2, 2.2, "Canonical expression &\nstatement linearization\nStructural k-grams (k=5)",
                     title="Structural Linearizer", box_color='#FFFFFF', edge_color='#4ADE80', fontsize=9)

    # Fingerprinting & Winnowing Stage
    draw_rounded_box(ax, (10.6, 2.5), 2.0, 3.0, "Sliding window (w=4)\nRightmost tie-break\nFingerprint deduplication\nJaccard / Sorensen-Dice",
                     title="Winnowing Engine", box_color='#EFF6FF', edge_color='#2563EB', fontsize=9)

    # Arrows
    draw_arrow(ax, (2.3, 4.4), (2.7, 5.35), color='#EF4444', lw=1.5)
    draw_arrow(ax, (2.3, 3.6), (2.7, 2.35), color='#16A34A', lw=1.5)

    # Within Baseline
    draw_arrow(ax, (4.9, 5.35), (5.2, 5.35), color='#EF4444')
    draw_arrow(ax, (7.4, 5.35), (7.7, 5.35), color='#EF4444')
    draw_arrow(ax, (9.9, 5.35), (10.6, 4.5), color='#EF4444')

    # Within AST
    draw_arrow(ax, (4.9, 2.2), (5.2, 2.2), color='#16A34A')
    draw_arrow(ax, (7.4, 2.2), (7.7, 2.2), color='#16A34A')
    draw_arrow(ax, (9.9, 2.2), (10.6, 3.5), color='#16A34A')

    # Output Decision Arrow
    ax.text(11.6, 1.8, "Plagiarism Verdict\nSimilarity Score (0–100%)\nROC-AUC: 92.8%",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1E293B',
            bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7", ec="#F59E0B", lw=1.2))
    draw_arrow(ax, (11.6, 2.5), (11.6, 2.15), color='#D97706')

    plt.tight_layout()
    out_path = os.path.join(out_dir, "fig1_system_architecture_paper.png")
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

# =========================================================================
# 2. SLIDE 4 SYSTEM ARCHITECTURE (Dark teal/cyan theme for presentation)
# =========================================================================
def generate_system_architecture_slide():
    # 16:9 slide format
    fig, ax = plt.subplots(figsize=(16, 9), dpi=200)
    ax.set_facecolor('#09282D')
    fig.patch.set_facecolor('#09282D')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # Title & Badge
    ax.text(8.0, 8.4, "SYSTEM ARCHITECTURE OVERVIEW",
            ha='center', va='center', fontsize=22, fontweight='bold', color='#2DD4BF')
    ax.text(8.0, 7.9, "Dual-Engine Pipeline: Classical Token Winnowing vs. AST Structural Normalization",
            ha='center', va='center', fontsize=13, color='#94A3B8')

    # Source Code Box
    draw_rounded_box(ax, (0.8, 3.2), 2.2, 2.2, "Code A & Code B\nSource Files\n(Raw Input)",
                     title="INPUT CODE", box_color='#0D3B43', edge_color='#2DD4BF',
                     text_color='#FFFFFF', fontsize=12, linewidth=2.0)

    # Subgraph 1: Classical Baseline (Top)
    p1 = FancyBboxPatch((3.5, 4.7), 8.4, 2.7, boxstyle="round,pad=0.3,rounding_size=0.15",
                        facecolor='#0F1E24', edgecolor='#EF4444', linewidth=1.8, linestyle='--', zorder=1)
    ax.add_patch(p1)
    ax.text(3.8, 7.1, "BASELINE: Classical Token-Level Winnowing (MOSS Style)", fontsize=11, fontweight='bold', color='#F87171')

    draw_rounded_box(ax, (3.8, 5.0), 2.4, 1.8, "Strip Comments\n& Docstrings",
                     title="1. Lexer", box_color='#09282D', edge_color='#EF4444', text_color='#FFFFFF', fontsize=10.5)
    draw_rounded_box(ax, (6.5, 5.0), 2.4, 1.8, "Identifiers → 'ID'\nLiterals → 'LIT'",
                     title="2. Masking", box_color='#09282D', edge_color='#EF4444', text_color='#FFFFFF', fontsize=10.5)
    draw_rounded_box(ax, (9.2, 5.0), 2.4, 1.8, "k-gram Hashes\nRolling Hash Mod 2^31-1",
                     title="3. Rabin-Karp", box_color='#09282D', edge_color='#EF4444', text_color='#FFFFFF', fontsize=10.5)

    # Subgraph 2: Proposed AST Engine (Bottom)
    p2 = FancyBboxPatch((3.5, 1.1), 8.4, 3.2, boxstyle="round,pad=0.3,rounding_size=0.15",
                        facecolor='#08252A', edgecolor='#2DD4BF', linewidth=2.0, zorder=1)
    ax.add_patch(p2)
    ax.text(3.8, 3.95, "PROPOSED: Structural AST Normalization Engine (SynapsCode)", fontsize=11.5, fontweight='bold', color='#2DD4BF')

    draw_rounded_box(ax, (3.8, 1.4), 2.4, 2.2, "Language AST\nSyntax Hierarchy\n(Python/Tree-Sitter)",
                     title="1. AST Parser", box_color='#0D3B43', edge_color='#2DD4BF', text_color='#FFFFFF', fontsize=10.5)
    draw_rounded_box(ax, (6.5, 1.4), 2.4, 2.2, "• Commutative sort\n• Invert relational ops\n• Strip OOP wrappers\n• Unify assignments",
                     title="2. Semantic Rules", box_color='#0D3B43', edge_color='#2DD4BF', text_color='#FFFFFF', fontsize=10)
    draw_rounded_box(ax, (9.2, 1.4), 2.4, 2.2, "Canonical Tree Walk\nLinear Statement Tokens\nCompact Sequence",
                     title="3. Structural Tokens", box_color='#0D3B43', edge_color='#2DD4BF', text_color='#FFFFFF', fontsize=10.5)

    # Decision Engine (Right)
    draw_rounded_box(ax, (12.4, 2.8), 2.8, 3.2, "Window (w=4)\nTie-breaking\nFingerprint Hashes\n\nJaccard Index\nROC-AUC: 92.80%",
                     title="4. WINNOWING & SIMILARITY", box_color='#0D3B43', edge_color='#38BDF8',
                     text_color='#FFFFFF', fontsize=11, linewidth=2.0)

    # Arrows
    draw_arrow(ax, (3.0, 4.6), (3.5, 5.9), color='#F87171', lw=2.0)
    draw_arrow(ax, (3.0, 3.8), (3.5, 2.7), color='#2DD4BF', lw=2.0)

    draw_arrow(ax, (6.2, 5.9), (6.5, 5.9), color='#F87171', lw=2.0)
    draw_arrow(ax, (8.9, 5.9), (9.2, 5.9), color='#F87171', lw=2.0)
    draw_arrow(ax, (11.6, 5.9), (12.4, 4.9), color='#F87171', lw=2.0)

    draw_arrow(ax, (6.2, 2.5), (6.5, 2.5), color='#2DD4BF', lw=2.0)
    draw_arrow(ax, (8.9, 2.5), (9.2, 2.5), color='#2DD4BF', lw=2.0)
    draw_arrow(ax, (11.6, 2.5), (12.4, 3.9), color='#2DD4BF', lw=2.0)

    out_path = os.path.join(out_dir, "slide4_system_architecture_diagram.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print("Saved:", out_path)

if __name__ == '__main__':
    generate_system_architecture_paper()
    generate_system_architecture_slide()
