"""v1.82 - Black-hole entropy and the WGC: the engine's coefficients fix the sign
of the extremal-entropy shift.

Cheung-Liu-Remmen / Reall-Santos: Delta S_ext > 0 (the leading higher-derivative
correction to the extremal RN entropy at fixed M,Q) is EQUIVALENT to the WGC. In 4d
the Euler/Gauss-Bonnet term is topological (no shift), so Delta S_ext is driven by
the Weyl^2 coupling g_C and the matter sector g_4. We compute Delta S_ext for all
frameworks + the island center, check the sign, the ordering, and whether it
correlates with the engine's existing WGC margin.

Run on Vulcan:  python experiments/bh_entropy.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
sys.path.insert(0, "experiments")

from stack import build_stack
from itb.predict import FRAMEWORKS
from itb.gravitational_observables import BlackHoleEntropyShift
from itb.constraints.swampland import WeakGravityConjecture
from itb.holographic_ac import gC_from_gR2
from itb.theory import Theory

# island center (v1.74, parity-even): g_4,g_6,g_8,g_R2,g_R3,g_C
ISLAND_CENTER = {"g_4": 0.5216, "g_6": 0.3843, "g_8": 0.4351,
                 "g_R2": 0.2135, "g_R3": 0.0773, "g_C": 0.2316,
                 "g_R2_parity": 0.0, "g_R3_parity": 0.0}


def main():
    obs = BlackHoleEntropyShift()
    wgc = WeakGravityConjecture(alpha=1.0)
    stack = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")

    rows = []
    items = list(FRAMEWORKS.items()) + [("island_center", None)]
    for name, fw in items:
        if fw is None:
            th = Theory(coefficients=dict(ISLAND_CENTER))
        else:
            th = fw.encode()
        c = dict(th.coefficients)
        # ensure g_C present (portrait default) so the BH observable is well-defined
        if "g_C" not in c:
            c["g_C"] = gC_from_gR2(c.get("g_R2", 0.0))
        th = Theory(coefficients=c)
        dS = float(obs.predict(th)[0])
        wgc_margin = float(wgc.evaluate(th).margin)
        feasible = all(cc.evaluate(th).satisfied for cc in stack) if fw is not None else None
        rows.append({"name": name, "g_C": round(c.get("g_C", 0.0), 3),
                     "g_4": round(c.get("g_4", 0.0), 3),
                     "delta_S_ext": round(dS, 4),
                     "wgc_margin": round(wgc_margin, 4),
                     "feasible": feasible})
    rows.sort(key=lambda r: -r["delta_S_ext"])

    all_positive = all(r["delta_S_ext"] > 0 for r in rows)
    # correlation of Delta S with WGC margin across frameworks
    dS_arr = np.array([r["delta_S_ext"] for r in rows])
    wgc_arr = np.array([r["wgc_margin"] for r in rows])
    corr = float(np.corrcoef(dS_arr, wgc_arr)[0, 1]) if len(dS_arr) > 2 else None

    # does WaldEntropyPositivity newly exclude any survivor?
    newly_excluded = []
    for name, fw in FRAMEWORKS.items():
        th = fw.encode()
        c = dict(th.coefficients); c.setdefault("g_C", gC_from_gR2(c.get("g_R2", 0.0)))
        th = Theory(coefficients=c)
        from itb.constraints.bh_entropy_positivity import WaldEntropyPositivity
        wald_ok = WaldEntropyPositivity().evaluate(th).satisfied
        # feasible under the rest of the stack (without wald)?
        rest = [cc for cc in stack if cc.name != "wald_entropy_positivity"]
        rest_ok = all(cc.evaluate(th).satisfied for cc in rest)
        if rest_ok and not wald_ok:
            newly_excluded.append(name)

    # ---- figure ----
    fig, ax = plt.subplots(figsize=(11, 6.5))
    names = [r["name"] for r in rows]
    vals = [r["delta_S_ext"] for r in rows]
    colors = ["#1f77b4" if v > 0 else "#d62728" for v in vals]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    ax.axvline(0, color="black", lw=1.5, label="WGC-consistency line (Delta S_ext = 0)")
    ax.set_xlabel(r"$\Delta S_{\rm ext}$  (extremal BH entropy shift, Wald units) "
                  r"$= g_C + 0.5\,g_4$")
    ax.set_title("v1.82  Black-hole entropy and the WGC\n"
                 "every consistent framework has Delta S_ext > 0 "
                 "(extremal BHs can decay); g_R2 (Euler) drops out (topological)",
                 fontsize=10)
    ax.legend(fontsize=9, loc="lower right")
    ax.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout()
    png = "/tmp/bh_entropy.png"
    fig.savefig(png, dpi=140)

    dd = next(r for r in rows if r["name"] == "discovered_data_driven")
    summary = {
        "mapping": "Delta S_ext = A*g_C + B*g_4 (A=1, B=0.5); g_R2 (Euler) topological -> 0",
        "all_frameworks_positive_delta_S": bool(all_positive),
        "interpretation": "Delta S_ext > 0 for every consistent framework <=> WGC "
                          "(extremal black holes can decay) -- an independent "
                          "thermodynamic restatement of the engine's positivity.",
        "correlation_deltaS_vs_WGC_margin": round(corr, 3) if corr is not None else None,
        "wald_positivity_newly_excludes": newly_excluded,
        "wald_is_redundant_restatement": len(newly_excluded) == 0,
        "data_driven_eft_delta_S": dd["delta_S_ext"],
        "ranking": rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
