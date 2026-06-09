"""v1.69 - 2-D feasibility-region slice in the graviton-curvature plane.

Sweep g_R2 (x) vs g_R3 (y) over [0, 0.5]^2, fixing the matter sector at a
string-like survivor point (g_4=0.5, g_6=0.4, g_8=0.4, parity=0). At each cell
evaluate the *corrected* stack (geometric BNOSSW + convex_hull RFC) and record:

  - feasible (all constraints pass), or
  - the BINDING constraint: the single most-violated constraint (most negative
    margin) at that infeasible cell.

This makes the engine's allowed region in the (g_R2, g_R3) plane visible as a
shape, and shows WHICH physics walls it off where. Framework points overlaid.

Run on Vulcan from the repo root:
    python experiments/slice_gR2_gR3.py
writes /tmp/slice_gR2_gR3.png and prints a JSON summary.
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.theory import Theory

# Fixed matter-sector survivor point (string-like), parity off.
BASE = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4,
        "g_R2_parity": 0.0, "g_R3_parity": 0.0}

# Framework points to overlay (g_R2, g_R3, label).
FRAMEWORKS = [
    (0.20, 0.15, "string-EFT"),
    (0.15, 0.10, "asymp-safety"),
    (0.30, 0.30, "LQG-induced"),
    (0.22, 0.15, "CDT"),
]

N = 121               # grid resolution per axis
LO, HI = 0.0, 0.5


def main():
    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    # stable constraint ordering / index -> name
    names = [c.name for c in stack]
    name_to_idx = {n: i for i, n in enumerate(names)}

    xs = np.linspace(LO, HI, N)   # g_R2
    ys = np.linspace(LO, HI, N)   # g_R3

    # grid[j, i]: -1 feasible, else index of binding constraint
    grid = np.full((N, N), -1, dtype=int)
    binding_counts = {}

    for j, gR3 in enumerate(ys):
        for i, gR2 in enumerate(xs):
            coeffs = dict(BASE)
            coeffs["g_R2"] = float(gR2)
            coeffs["g_R3"] = float(gR3)
            th = Theory(coefficients=coeffs)
            worst_margin = np.inf
            worst_name = None
            for c in stack:
                r = c.evaluate(th)
                if not r.satisfied and r.margin < worst_margin:
                    worst_margin = r.margin
                    worst_name = c.name
            if worst_name is None:
                grid[j, i] = -1
            else:
                grid[j, i] = name_to_idx[worst_name]
                binding_counts[worst_name] = binding_counts.get(worst_name, 0) + 1

    feasible_cells = int((grid == -1).sum())
    feasible_frac = feasible_cells / (N * N)

    # which constraints actually bind anywhere -> assign distinct colors
    active = sorted(binding_counts, key=lambda n: -binding_counts[n])
    # palette: feasible = green, then distinct NON-green colors for the walls
    # (deliberately avoid green so binding regions never collide with feasible)
    palette = ["#2ca02c"]  # feasible = green
    wall_colors = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78",
                   "#9467bd", "#d62728", "#8c564b", "#e377c2",
                   "#7f7f7f", "#17becf"]
    palette += [wall_colors[k % len(wall_colors)] for k in range(len(active))]
    cmap = ListedColormap(palette)

    # remap grid -> 0 feasible, 1..K binding (in `active` order)
    remap = {name_to_idx[n]: (k + 1) for k, n in enumerate(active)}
    disp = np.zeros_like(grid)
    for j in range(N):
        for i in range(N):
            disp[j, i] = 0 if grid[j, i] == -1 else remap[grid[j, i]]

    bounds = np.arange(-0.5, len(palette) + 0.5, 1)
    norm = BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    ax.imshow(disp, origin="lower", extent=[LO, HI, LO, HI],
              aspect="auto", cmap=cmap, norm=norm, interpolation="nearest")

    # overlay framework points
    for gR2, gR3, lab in FRAMEWORKS:
        inside = (LO <= gR2 <= HI) and (LO <= gR3 <= HI)
        feas = False
        if inside:
            ii = int(round((gR2 - LO) / (HI - LO) * (N - 1)))
            jj = int(round((gR3 - LO) / (HI - LO) * (N - 1)))
            feas = grid[jj, ii] == -1
        ax.scatter([gR2], [gR3], s=90, marker="o",
                   facecolor="white", edgecolor="black", zorder=5)
        ax.annotate(f"{lab}{' ✓' if feas else ' ✗'}",
                    (gR2, gR3), textcoords="offset points", xytext=(8, 4),
                    fontsize=9, fontweight="bold",
                    color="black",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", alpha=0.7,
                              ec="none"))

    # legend
    handles = [Line2D([0], [0], marker="s", linestyle="", markersize=11,
                      markerfacecolor=palette[0], markeredgecolor="none",
                      label=f"feasible ({feasible_frac*100:.0f}%)")]
    for k, n in enumerate(active):
        handles.append(Line2D([0], [0], marker="s", linestyle="", markersize=11,
                              markerfacecolor=palette[k + 1], markeredgecolor="none",
                              label=f"{n} ({binding_counts[n]})"))
    ax.legend(handles=handles, loc="upper left", fontsize=8,
              framealpha=0.92, title="binding constraint (cells)")

    ax.set_xlabel(r"$g_{R^2}$  (leading curvature coupling)", fontsize=12)
    ax.set_ylabel(r"$g_{R^3}$  (cubic curvature coupling)", fontsize=12)
    ax.set_title("v1.69  Feasibility region in the graviton-curvature plane\n"
                 "corrected stack (geometric BNOSSW, convex-hull RFC); "
                 f"matter fixed g4=0.5 g6=0.4 g8=0.4, parity=0",
                 fontsize=11)
    fig.tight_layout()
    out = "/tmp/slice_gR2_gR3.png"
    fig.savefig(out, dpi=140)

    summary = {
        "grid": f"{N}x{N}",
        "range": [LO, HI],
        "n_constraints": len(stack),
        "feasible_cells": feasible_cells,
        "feasible_fraction": round(feasible_frac, 4),
        "binding_counts": dict(sorted(binding_counts.items(),
                                       key=lambda kv: -kv[1])),
        "frameworks": [
            {"label": lab, "g_R2": gR2, "g_R3": gR3}
            for gR2, gR3, lab in FRAMEWORKS
        ],
        "png": out,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
