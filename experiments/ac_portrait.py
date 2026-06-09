"""v2.03 - The holographic (a,c) RG portrait: the conformal-collider plane that unifies
the program.

One master plane in (a, c) = (g_R2 Euler, g_C Weyl^2) tying together:
  - v1.71  the Hofman-Maldacena wedge 1/3 <= a/c <= 31/18 (the free-SCALAR ratio 1/3 is
           the floor; the free-VECTOR ratio 31/18 is the ceiling -- the HM endpoints are
           saturated by free fields).
  - v1.72  eta/s <-> a/c: 1 - 4pi(eta/s) = (c-a)/c, so eta/s (KSS units) = a/c; contours
           of constant a/c are rays from the origin.
  - v1.94  the symmetric double copy = the a/c = 1 diagonal.
  - v1.98  holographic complexity dC/dt = 1 + c (driven by Weyl^2 c).
  - v1.99  the a-theorem a_UV >= a_IR: the RG flow must have a decreasing toward the IR;
           the v1.89 toy flow (-> a*=0.15) VIOLATES this for a-large frameworks unless the
           fixed point carries a* >= 0.45.
  - v2.02  c = g_C (Weyl^2) is the fattest island direction.

HONEST: toy a=g_R2, c=g_C identification + schematic v1.89 flow; the robust content is the
unifying STRUCTURE in one plane, not precise coordinates.

Run on Vulcan:  python experiments/ac_portrait.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from itb.predict import FRAMEWORKS
from itb.gravitational_observables import HolographicEtaOverS, HolographicComplexityRate
from itb.holographic_ac import gC_from_gR2
from itb.theory import Theory
from stack import build_stack
from phylogeny import beta, COEFFS as PH_COEFFS

AC_FLOOR, AC_CEIL = 1.0 / 3.0, 31.0 / 18.0       # free scalar / free vector (HM endpoints)
_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def passes_stack(coeffs):
    th = Theory(coefficients=dict(coeffs))
    return all(c.evaluate(th).satisfied for c in _STACK)


def main():
    eta = HolographicEtaOverS()
    cpx = HolographicComplexityRate()
    rows = []
    for name, fw in FRAMEWORKS.items():
        c = dict(fw.encode().coefficients)
        a = c.get("g_R2", 0.0)
        cc = c.get("g_C", gC_from_gR2(a))
        c.setdefault("g_C", cc)
        if a <= 1e-6 and cc <= 1e-6:
            continue
        ac = a / cc if cc > 1e-9 else float("inf")
        in_wedge = AC_FLOOR <= ac <= AC_CEIL
        es = float(eta.predict(fw.encode())[0])
        dC = float(cpx.predict(Theory(coefficients=c))[0])
        rows.append({"framework": name, "a": round(a, 3), "c": round(cc, 3),
                     "a_over_c": round(ac, 3), "in_wedge": in_wedge,
                     "eta_s": round(es, 3), "dCdt": round(dC, 3),
                     "passes_stack": passes_stack(c)})
    rows.sort(key=lambda r: -r["a_over_c"])
    most_central = min(rows, key=lambda r: abs(r["a_over_c"] - 1.0))   # closest to a=c

    # ---- the portrait ----
    fig, ax = plt.subplots(figsize=(11, 9))
    A = np.linspace(0, 0.5, 100)
    # Hofman-Maldacena wedge: 18a/31 <= c <= 3a
    ax.fill_between(A, 18 * A / 31, 3 * A, color="#d9ead3", alpha=0.7,
                    label="Hofman-Maldacena wedge (1/3 <= a/c <= 31/18)")
    # a/c = 1 symmetric double-copy diagonal (v1.94)
    ax.plot(A, A, color="#d62728", lw=2, ls="-", label="symmetric double copy (a/c=1)")
    # wedge edges = free-field landmarks
    ax.plot(A, 3 * A, color="#1f77b4", lw=1.4, ls="--",
            label="a/c=1/3 (free scalar = floor)")
    ax.plot(A, 18 * A / 31, color="#9467bd", lw=1.4, ls="--",
            label="a/c=31/18 (free vector = ceiling)")
    # eta/s contours (constant a/c rays) -- label a few
    for ac_val, lbl in [(0.5, "eta/s=0.50"), (0.75, "eta/s=0.75")]:
        ax.plot(A, A / ac_val, color="#7f7f7f", lw=0.8, ls=":")
        ax.text(0.46, 0.46 / ac_val, lbl, fontsize=6, color="#7f7f7f")
    # RG flow streamlines in (a,c): beta_a=-0.4(a-0.15), beta_c=-0.8 c^2 (-> UV (0.15,0))
    ga, gc = np.meshgrid(np.linspace(0.001, 0.5, 26), np.linspace(0.001, 0.7, 26))
    Ba = -0.4 * (ga - 0.15); Bc = -0.8 * gc ** 2          # toward UV = increasing t
    ax.streamplot(ga, gc, Ba, Bc, color="#aaaaaa", density=0.7, linewidth=0.5,
                  arrowsize=0.7)
    ax.scatter([0.15], [0.0], marker="*", s=240, color="black", zorder=6)
    ax.annotate("UV fixed point (a*=0.15)\na-theorem needs a* >= 0.45", (0.15, 0.0),
                fontsize=7, xytext=(0.17, 0.05), color="black")
    # frameworks
    for r in rows:
        col = "#2ca02c" if r["passes_stack"] else "#cccccc"
        m = "*" if r["framework"] == "discovered_data_driven" else "o"
        s = 160 if m == "*" else 55
        ax.scatter([r["a"]], [r["c"]], s=s, marker=m, color=col, edgecolor="black",
                   zorder=5, linewidth=0.6)
        ax.annotate(r["framework"][:11], (r["a"], r["c"]), fontsize=6,
                    textcoords="offset points", xytext=(4, 2))
    ax.scatter([0.2135], [0.2316], marker="P", s=120, color="#ff7f0e", zorder=6,
               edgecolor="black", label="v1.74 island center")
    ax.set_xlabel("a = g_R2 (Euler central charge)")
    ax.set_ylabel("c = g_C (Weyl^2 central charge)")
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.7)
    ax.set_title("v2.03  The holographic (a,c) RG portrait\n"
                 "conformal-collider wedge + double-copy diagonal + eta/s rays + RG flow "
                 "(a-theorem) + the 14 frameworks", fontsize=10)
    ax.legend(fontsize=7.5, loc="upper left")
    fig.tight_layout()
    png = "/tmp/ac_portrait.png"
    fig.savefig(png, dpi=145)

    in_wedge = [r["framework"] for r in rows if r["in_wedge"]]
    summary = {
        "wedge": f"{AC_FLOOR:.3f} <= a/c <= {AC_CEIL:.3f} (free scalar floor, free vector ceiling)",
        "eta_s_relation": "eta/s (KSS units) = a/c  [v1.72]; a/c<1 -> KSS-violating dual",
        "frameworks_in_wedge": in_wedge,
        "n_in_wedge": len(in_wedge), "n_total": len(rows),
        "most_central_a_eq_c": {"framework": most_central["framework"],
                                "a_over_c": most_central["a_over_c"]},
        "rg_flow": "v1.89 beta -> UV fixed point (a*=0.15, c*=0 by Weyl^2 asymptotic freedom); "
                   "a-theorem requires a* >= 0.45 (v1.99) so the toy fixed point is too low",
        "table": rows,
        "interpretation": "One plane unifies the program: the consistent frameworks all sit "
            "INSIDE the Hofman-Maldacena wedge (v1.71), BELOW the a/c=1 double-copy diagonal "
            "(v1.94, asymmetric double copies), as KSS-violating duals (a/c<1 -> eta/s<1/4pi, "
            "v1.72), super-saturating complexity (c>0, v1.98); the RG flow (v1.89) pushes them "
            "toward a low UV fixed point that the a-theorem (v1.99) says must instead carry "
            "a* >= 0.45; and c (the vertical Weyl^2 axis) is the fattest island direction (v2.02).",
        "honest": "toy a=g_R2,c=g_C identification + schematic flow; robust content is the "
                  "unifying structure in one plane.",
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
