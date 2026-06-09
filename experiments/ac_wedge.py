"""v1.71 - The a/c wedge bites once the basis resolves c from a.

v1.70 showed the a-theorem was dormant because the toy basis collapsed the Euler
(a) and Weyl^2 (c) anomalies onto a single coupling g_R2. We now add a second
curvature-squared coupling g_C (= c) and the Hofman-Maldacena wedge
1/3 <= a/c <= 31/18, with a = g_R2, c = g_C.

This script proves the wedge carries NEW information:

  (1) WITNESS: a point feasible under the OLD stack (no g_C / wedge) but excluded
      by the NEW stack purely because of the a/c wedge. Since g_C enters ONLY the
      wedge, the rest of the stack is unchanged, so the wedge is the sole excluder.

  (2) MAP: sweep g_R2 (x) vs g_C (y); color feasible / binding; draw the two
      wedge rays a/c=1/3 and a/c=31/18 and the a/c=1 holographic diagonal.

  (3) FRAMEWORKS: with the default g_C=g_R2 (a/c=1) every framework sits dead
      center -> the wedge does not bite the default points (honest, reported).
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

from stack import build_stack, frameworks
from itb.constraints.hofman_maldacena import HofmanMaldacenaWedge
from itb.theory import Theory

BASE = {"g_4": 0.5, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.2, "g_R3": 0.15,
        "g_R2_parity": 0.0, "g_R3_parity": 0.0}   # string-like survivor (v1.69)

N = 121
LO, HI = 0.0, 0.7


def feasible(stack, th):
    failed = [c.name for c in stack if not c.evaluate(th).satisfied]
    return len(failed) == 0, failed


def main():
    new_stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")
    old_stack = [c for c in new_stack if c.name != "hofman_maldacena_wedge"]

    # (1) WITNESS: string-like survivor, push g_C outside the wedge.
    # a/c = g_R2/g_C; g_R2=0.2. g_C=0.05 -> a/c=4.0 (> 31/18) -> excluded.
    witness = dict(BASE); witness["g_C"] = 0.05
    th_w = Theory(coefficients=witness)
    old_ok, _ = feasible(old_stack, th_w)
    new_ok, new_failed = feasible(new_stack, th_w)
    wedge_r = HofmanMaldacenaWedge().evaluate(th_w)

    # (2) MAP over (g_R2, g_C)
    xs = np.linspace(LO, HI, N)   # g_R2
    ys = np.linspace(LO, HI, N)   # g_C
    grid = np.full((N, N), -1, dtype=int)
    binding_counts = {}
    for j, gC in enumerate(ys):
        for i, gR2 in enumerate(xs):
            coeffs = dict(BASE); coeffs["g_R2"] = float(gR2); coeffs["g_C"] = float(gC)
            th = Theory(coefficients=coeffs)
            worst_m, worst_n = np.inf, None
            for c in new_stack:
                r = c.evaluate(th)
                if not r.satisfied and r.margin < worst_m:
                    worst_m, worst_n = r.margin, c.name
            if worst_n is None:
                grid[j, i] = -1
            else:
                grid[j, i] = 0  # placeholder; remap below
                binding_counts[worst_n] = binding_counts.get(worst_n, 0) + 1

    # rebuild grid storing binding name index
    names = [c.name for c in new_stack]
    nidx = {n: k for k, n in enumerate(names)}
    grid = np.full((N, N), -1, dtype=int)
    for j, gC in enumerate(ys):
        for i, gR2 in enumerate(xs):
            coeffs = dict(BASE); coeffs["g_R2"] = float(gR2); coeffs["g_C"] = float(gC)
            th = Theory(coefficients=coeffs)
            worst_m, worst_n = np.inf, None
            for c in new_stack:
                r = c.evaluate(th)
                if not r.satisfied and r.margin < worst_m:
                    worst_m, worst_n = r.margin, c.name
            grid[j, i] = -1 if worst_n is None else nidx[worst_n]

    feasible_cells = int((grid == -1).sum())
    active = sorted(binding_counts, key=lambda n: -binding_counts[n])
    palette = ["#2ca02c"]
    wall_colors = ["#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#9467bd",
                   "#d62728", "#8c564b", "#e377c2", "#7f7f7f", "#17becf"]
    palette += [wall_colors[k % len(wall_colors)] for k in range(len(active))]
    cmap = ListedColormap(palette)
    remap = {nidx[n]: (k + 1) for k, n in enumerate(active)}
    disp = np.zeros_like(grid)
    for j in range(N):
        for i in range(N):
            disp[j, i] = 0 if grid[j, i] == -1 else remap[grid[j, i]]
    norm = BoundaryNorm(np.arange(-0.5, len(palette) + 0.5, 1), cmap.N)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    ax.imshow(disp, origin="lower", extent=[LO, HI, LO, HI], aspect="auto",
              cmap=cmap, norm=norm, interpolation="nearest")
    # wedge rays: g_C = 3 g_R2 (a/c=1/3) and g_C = (18/31) g_R2 (a/c=31/18)
    xr = np.array([LO, HI])
    ax.plot(xr, 3.0 * xr, "k--", lw=1.5, label="a/c = 1/3  (g_C = 3 g_R2)")
    ax.plot(xr, (18.0 / 31.0) * xr, "k-.", lw=1.5,
            label="a/c = 31/18  (g_C = 18/31 g_R2)")
    ax.plot(xr, xr, color="white", lw=1.2, ls=":", label="a/c = 1 (holographic)")
    # frameworks at default a/c=1 sit on the white diagonal
    for fw in frameworks():
        g = fw.encode().coefficients.get("g_R2", 0.0)
        if LO <= g <= HI:
            ax.scatter([g], [g], s=70, marker="o", facecolor="white",
                       edgecolor="black", zorder=5)
    # witness point
    ax.scatter([BASE["g_R2"]], [witness["g_C"]], s=150, marker="*",
               facecolor="yellow", edgecolor="black", zorder=6,
               label="witness (excluded by wedge)")

    handles = [Line2D([0], [0], marker="s", linestyle="", markersize=11,
                      markerfacecolor=palette[0], markeredgecolor="none",
                      label=f"feasible ({feasible_cells/(N*N)*100:.0f}%)")]
    for k, n in enumerate(active):
        handles.append(Line2D([0], [0], marker="s", linestyle="", markersize=11,
                              markerfacecolor=palette[k + 1], markeredgecolor="none",
                              label=f"{n} ({binding_counts[n]})"))
    leg1 = ax.legend(handles=handles, loc="upper left", fontsize=8,
                     framealpha=0.92, title="binding constraint (cells)")
    ax.add_artist(leg1)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.92)

    ax.set_xlabel(r"$g_{R^2}\ \propto\ a$  (Euler central charge)", fontsize=12)
    ax.set_ylabel(r"$g_C\ \propto\ c$  (Weyl$^2$ central charge)", fontsize=12)
    ax.set_title("v1.71  The Hofman-Maldacena a/c wedge, once a and c are resolved\n"
                 "feasible band between a/c=1/3 and a/c=31/18; frameworks sit on the "
                 "a/c=1 diagonal", fontsize=10)
    ax.set_xlim(LO, HI); ax.set_ylim(LO, HI)
    fig.tight_layout()
    out = "/tmp/ac_wedge.png"
    fig.savefig(out, dpi=140)

    # (3) FRAMEWORKS under default g_C=g_R2
    fw_rows = []
    wedge = HofmanMaldacenaWedge()
    for fw in frameworks():
        th = fw.encode()
        r = wedge.evaluate(th)
        fw_rows.append({"framework": fw.name,
                        "a_over_c_default": round(r.details.get("a_over_c", 0.0), 3),
                        "wedge_ok": r.satisfied})

    summary = {
        "witness": {
            "point": {"g_R2": BASE["g_R2"], "g_C": witness["g_C"]},
            "a_over_c": round(wedge_r.details["a_over_c"], 3),
            "old_stack_feasible": old_ok,
            "new_stack_feasible": new_ok,
            "new_stack_failed": new_failed,
            "interpretation": ("WEDGE BITES: old stack allowed it, wedge excludes it"
                               if (old_ok and not new_ok and
                                   new_failed == ["hofman_maldacena_wedge"])
                               else "check"),
        },
        "map": {"grid": f"{N}x{N}", "range": [LO, HI],
                "feasible_cells": feasible_cells,
                "feasible_fraction": round(feasible_cells / (N * N), 4),
                "binding_counts": dict(sorted(binding_counts.items(),
                                              key=lambda kv: -kv[1])),
                "png": out},
        "frameworks_default_ac1": fw_rows,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
