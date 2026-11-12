
"""
FactoryGuard AI — Architecture Diagram
Generates docs/architecture.png using Matplotlib.

Run from the project root:
    python docs/architecture.py
"""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


OUTPUT = Path(__file__).resolve().parent / "architecture.png"

# Canvas
fig, ax = plt.subplots(figsize=(18, 12))
fig.patch.set_facecolor("#F7F9FC")
ax.set_facecolor("#F7F9FC")
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis("off")

# Colors
NAVY = "#172B4D"
BLUE = "#2563EB"
BLUE_LIGHT = "#EAF2FF"
PURPLE = "#7547C8"
PURPLE_LIGHT = "#F1EBFF"
GREEN = "#16805D"
GREEN_LIGHT = "#E7F7F0"
RED = "#C24141"
GRAY = "#52627A"
BORDER = "#D6DFEA"


def rounded_box(x, y, w, h, text, fill, edge, fontsize=10.5):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.035,rounding_size=0.15",
        linewidth=1.5,
        edgecolor=edge,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=NAVY,
        fontweight="semibold",
        linespacing=1.35,
        zorder=4,
    )


def arrow(start, end, color=GRAY, label=None, style="-|>", lw=1.8):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=15,
        linewidth=lw,
        color=color,
        connectionstyle="arc3",
        zorder=5,
    )
    ax.add_patch(patch)
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        ax.text(
            mx,
            my + 0.10,
            label,
            ha="center",
            fontsize=8.5,
            color=color,
            bbox=dict(facecolor="#F7F9FC", edgecolor="none", pad=1),
            zorder=6,
        )


def layer_background(y, h, title, subtitle, fill, accent):
    bg = FancyBboxPatch(
        (0.55, y),
        16.9,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.22",
        linewidth=1.2,
        edgecolor=BORDER,
        facecolor=fill,
        zorder=0,
    )
    ax.add_patch(bg)
    ax.text(
        0.9,
        y + h - 0.35,
        title,
        fontsize=14,
        fontweight="bold",
        color=accent,
        va="center",
    )
    ax.text(
        0.9,
        y + h - 0.68,
        subtitle,
        fontsize=9,
        color=GRAY,
        va="center",
    )


# Header
ax.text(
    0.65,
    11.55,
    "FactoryGuard AI",
    fontsize=27,
    fontweight="bold",
    color=NAVY,
)
ax.text(
    0.68,
    11.15,
    "Offline industrial diagnostics | AI advisory intelligence | Deterministic safety",
    fontsize=12,
    color=GRAY,
)

# Three architecture layers
layer_background(
    8.1,
    2.65,
    "01  MACHINE & SAFETY",
    "Simulated machine state and independent deterministic enforcement",
    BLUE_LIGHT,
    BLUE,
)

layer_background(
    4.55,
    3.15,
    "02  AI ADVISORY INTELLIGENCE",
    "Local inference and maintenance guidance; no machine-control authority",
    PURPLE_LIGHT,
    PURPLE,
)

layer_background(
    1.05,
    3.05,
    "03  CONTROLLED RECOVERY & AUDIT",
    "Operator-controlled simulated actions subject to deterministic authorization",
    GREEN_LIGHT,
    GREEN,
)

# Layer 1 nodes
rounded_box(1.0, 8.55, 3.3, 0.9, "Simulated machine\n& sensor readings", "#FFFFFF", BLUE)
rounded_box(5.1, 8.55, 3.3, 0.9, "Fault detection\n& latched state", "#FFFFFF", BLUE)
rounded_box(9.2, 8.55, 3.3, 0.9, "Deterministic\nsafety controller", "#FFFFFF", RED)
rounded_box(13.35, 8.55, 3.25, 0.9, "Safety stop\n& interlocks", "#FFFFFF", RED)

arrow((4.3, 9.0), (5.1, 9.0), BLUE)
arrow((8.4, 9.0), (9.2, 9.0), BLUE)
arrow((12.5, 9.0), (13.35, 9.0), RED)

# Layer 2 nodes
rounded_box(0.95, 5.15, 3.05, 1.0, "LangGraph\nworkflow", "#FFFFFF", PURPLE)
rounded_box(4.55, 5.15, 3.05, 1.0, "Local Gemma 3\nvision analysis", "#FFFFFF", PURPLE)
rounded_box(8.15, 5.15, 3.05, 1.0, "Maintenance RAG\n& local advisor", "#FFFFFF", PURPLE)
rounded_box(11.75, 5.15, 4.7, 1.0, "Structured diagnostic report\n& grounded recommendations", "#FFFFFF", PURPLE)

arrow((4.0, 5.65), (4.55, 5.65), PURPLE)
arrow((7.6, 5.65), (8.15, 5.65), PURPLE)
arrow((11.2, 5.65), (11.75, 5.65), PURPLE)

# Sensor context to AI
arrow((2.65, 8.55), (2.65, 6.15), BLUE, "Sensor and scene context")

# Deterministic fault state informs diagnostic report
arrow((10.85, 8.55), (13.6, 6.15), RED)

# Layer 3 nodes
rounded_box(0.95, 1.65, 3.1, 0.95, "Operator review\n& approval", "#FFFFFF", GREEN)
rounded_box(4.65, 1.65, 3.1, 0.95, "Recovery\nbehavior tree", "#FFFFFF", GREEN)
rounded_box(8.35, 1.65, 3.1, 0.95, "Deterministic\nsafety gate", "#FFFFFF", RED)
rounded_box(12.05, 1.65, 4.25, 0.95, "Simulated recovery\n& SQLite audit", "#FFFFFF", GREEN)

arrow((4.05, 2.12), (4.65, 2.12), GREEN)
arrow((7.75, 2.12), (8.35, 2.12), GREEN)
arrow((11.45, 2.12), (12.05, 2.12), GREEN)

# Diagnostic report to operator
arrow((13.65, 5.15), (2.5, 2.60), PURPLE)

# Safety controller authorizes recovery gate independently of AI
arrow((10.85, 8.55), (10.0, 2.60), RED)

# Feedback path: simulated recovery -> machine
arrow((14.2, 2.60), (15.5, 8.55), GREEN)

# Key principle
ax.text(
    9,
    0.45,
    "SAFETY BOUNDARY: AI recommends. The deterministic controller and operator authorize simulated recovery.",
    ha="center",
    fontsize=11,
    fontweight="bold",
    color=RED,
)

plt.savefig(
    OUTPUT,
    dpi=200,
    bbox_inches="tight",
    facecolor=fig.get_facecolor(),
)
plt.close(fig)

print(f"Architecture diagram saved: {OUTPUT}")
