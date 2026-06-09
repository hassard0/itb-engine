"""v1.72 - Frameworks under the holographic a/c portrait: one coupling, two
observables, and causality strictly inside the Hofman-Maldacena wedge.

For every framework we map its single curvature coupling g_R2 (= a, Euler) to a
Gauss-Bonnet coupling lambda_GB = 0.22*g_R2, then read off BOTH:
  - a/c           (v1.71 conformal-collider wedge axis), and
  - eta/s in KSS units = 1 - 4 lambda  (v1.67 holographic observable),
from the SAME lambda. We check:
  (1) the unification 1 - 4pi(eta/s) = (c-a)/c holds (one coupling),
  (2) each framework's eta/s ordering matches its a/c ordering,
  (3) where each framework sits vs the HM wedge [1/3, 31/18] AND vs the GB
      causality window lambda in [-7/36, 9/100] -> a/c in [~0.561, 1.560],
  (4) the headline: causality is STRICTLY tighter than HM (HM floor a/c=1/3
      needs lambda=1/8 > 9/100), so every causal framework is auto-inside HM.
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

from itb.predict import FRAMEWORKS
from itb.holographic_ac import (
    MU, LAMBDA_CAUSALITY_MAX, LAMBDA_CAUSALITY_MIN, AC_FLOOR, AC_CEIL,
    lambda_GB, ac_ratio, c_minus_a_over_c, eta_over_s_kss, gC_from_gR2,
    unification_residual,
)


def main():
    rows = []
    for name, fw in FRAMEWORKS.items():
        gR2 = fw.encode().coefficients.get("g_R2", 0.0)
        if gR2 <= 0.0:
            rows.append({"framework": name, "g_R2": gR2, "lambda_GB": 0.0,
                         "a_over_c": 1.0, "eta_s_kss": 1.0, "g_C": 0.0,
                         "in_HM_wedge": True, "in_causality": True,
                         "note": "no curvature sector (a=c=0, vacuous)"})
            continue
        lam = lambda_GB(gR2)
        ac = ac_ratio(lam)
        es = eta_over_s_kss(lam)
        gC = gC_from_gR2(gR2)
        in_hm = AC_FLOOR <= ac <= AC_CEIL
        in_caus = LAMBDA_CAUSALITY_MIN <= lam <= LAMBDA_CAUSALITY_MAX
        rows.append({"framework": name, "g_R2": round(gR2, 4),
                     "lambda_GB": round(lam, 4), "a_over_c": round(ac, 4),
                     "eta_s_kss": round(es, 4), "g_C": round(gC, 4),
                     "cma_over_c": round(c_minus_a_over_c(lam), 4),
                     "in_HM_wedge": bool(in_hm), "in_causality": bool(in_caus)})

    # (1) unification residual: tight at small lambda, O(lambda^2) at the edges
    lams = np.linspace(-0.19, 0.09, 29)
    max_resid = float(np.max(np.abs([unification_residual(l) for l in lams])))
    small = np.linspace(-0.05, 0.05, 21)
    small_resid = float(np.max(np.abs([unification_residual(l) for l in small])))

    # (2) ordering check: eta/s and a/c both monotone decreasing in g_R2
    act = [r for r in rows if r["g_R2"] > 0]
    by_g = sorted(act, key=lambda r: r["g_R2"])
    es_seq = [r["eta_s_kss"] for r in by_g]
    ac_seq = [r["a_over_c"] for r in by_g]
    es_monotone = all(es_seq[i] >= es_seq[i + 1] for i in range(len(es_seq) - 1))
    ac_monotone = all(ac_seq[i] >= ac_seq[i + 1] for i in range(len(ac_seq) - 1))

    # (4) thresholds
    lam_hm_floor = 1.0 / 8.0     # a/c = 1/3
    lam_hm_ceil = (AC_CEIL - 1.0) / (2.0 * AC_CEIL - 6.0)  # a/c=31/18 solve
    # a/c=(1-6L)/(1-2L)=31/18 -> 18(1-6L)=31(1-2L) -> 18-108L=31-62L -> L=-13/46
    lam_hm_ceil = -13.0 / 46.0

    # any framework excluded?
    excluded = [r["framework"] for r in rows if not r["in_HM_wedge"]]

    # ---- figure: a/c vs eta/s, frameworks on the unification line ----
    fig, ax = plt.subplots(figsize=(9, 7))
    # HM wedge band (vertical, on a/c axis) and causality band
    ax.axvspan(AC_FLOOR, AC_CEIL, color="#cfe8cf", alpha=0.5,
               label=f"HM wedge  a/c in [1/3, 31/18]")
    ac_caus_lo = ac_ratio(LAMBDA_CAUSALITY_MAX)   # 0.561
    ac_caus_hi = ac_ratio(LAMBDA_CAUSALITY_MIN)   # 1.560
    ax.axvspan(ac_caus_lo, ac_caus_hi, color="#9ecae1", alpha=0.55,
               label=f"GB causality  a/c in [{ac_caus_lo:.2f}, {ac_caus_hi:.2f}]")
    # unification curve: a/c vs eta/s as lambda varies
    lam_line = np.linspace(LAMBDA_CAUSALITY_MIN, LAMBDA_CAUSALITY_MAX, 100)
    ax.plot([ac_ratio(l) for l in lam_line], [eta_over_s_kss(l) for l in lam_line],
            "k-", lw=1.3, label="one-coupling locus (vary lambda_GB)")
    for r in act:
        ax.scatter([r["a_over_c"]], [r["eta_s_kss"]], s=70, zorder=5,
                   edgecolor="black")
        ax.annotate(r["framework"], (r["a_over_c"], r["eta_s_kss"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=7.5)
    ax.axvline(AC_FLOOR, color="green", ls="--", lw=1, alpha=0.7)
    ax.axvline(AC_CEIL, color="green", ls="--", lw=1, alpha=0.7)
    ax.set_xlabel("a / c  (Hofman-Maldacena wedge axis)", fontsize=12)
    ax.set_ylabel(r"$\eta/s$  in KSS units $(1-4\lambda_{GB})$", fontsize=12)
    ax.set_title("v1.72  One coupling, two observables: frameworks under the GB portrait\n"
                 "causality band (blue) sits strictly inside the HM wedge (green)",
                 fontsize=10)
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    out = "/tmp/framework_ac.png"
    fig.savefig(out, dpi=140)

    summary = {
        "map": f"lambda_GB = {MU} * g_R2",
        "unification": {
            "relation_linear_order": "1 - 4pi(eta/s) = (c-a)/c  (both = 4 lambda)",
            "relation_exact": "1 - 4pi(eta/s) = (c-a)/c * (1 - 2 lambda)",
            "max_abs_residual_small_lambda_pm0.05": round(small_resid, 5),
            "max_abs_residual_full_causal_range": round(max_resid, 5),
            "note": ("identity tight at small lambda; O(lambda^2) corrections "
                     "grow to ~0.2 at the causal boundary (exact form above)"),
        },
        "ordering": {"eta_s_monotone_in_gR2": es_monotone,
                     "a_over_c_monotone_in_gR2": ac_monotone,
                     "same_ordering": es_monotone and ac_monotone},
        "causality_vs_HM": {
            "lambda_for_HM_floor_ac_1_3": round(lam_hm_floor, 4),
            "lambda_for_HM_ceil_ac_31_18": round(lam_hm_ceil, 4),
            "lambda_causality_window": [round(LAMBDA_CAUSALITY_MIN, 4),
                                        round(LAMBDA_CAUSALITY_MAX, 4)],
            "a_over_c_causality_window": [round(ac_ratio(LAMBDA_CAUSALITY_MAX), 4),
                                          round(ac_ratio(LAMBDA_CAUSALITY_MIN), 4)],
            "headline": ("causality STRICTLY inside HM wedge: HM floor needs "
                         "lambda=0.125 > causality 0.09; HM ceil needs "
                         "lambda=-0.283 < causality -0.194"),
        },
        "frameworks_excluded_by_HM": excluded,
        "frameworks": rows,
        "png": out,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
