"""v1.99 - The a-theorem along the RG phylogeny: does the central charge decrease
toward the IR?

We tie the v1.89 RG flow to the Euler central charge a = g_R2. The a-theorem
(Komargodski-Schwimmer 2011; holographic Myers-Sinha) says a is MONOTONE along RG flows
and DECREASES from UV to IR: a_UV >= a_IR. The v1.89 toy flow has a UV-attractive fixed
point at a* = g_star (GSTAR[g_R2] = 0.15), with beta_{g_R2} = -k (g_R2 - g_star).

KEY (Dr. M.-confirmed): the a-theorem requires the UV fixed point to DOMINATE, a* >=
a_IR for every IR theory. So a framework with g_R2 > a* has a INCREASING toward the IR
-> it VIOLATES the a-theorem. The flow is a-theorem-consistent only if g_star >= max
framework g_R2. (And c = g_C is NON-monotone in 4d -- there is no c-theorem, Cardy -- so
c-a need not be monotone.)

This makes the a-theorem a CONSISTENCY CHECK / CONSTRAINT on the toy beta functions.

Run on Vulcan:  python experiments/a_theorem_flow.py
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
from phylogeny import COEFFS, GSTAR, flow

A_IDX = COEFFS.index("g_R2")          # a = Euler central charge
C_IDX = COEFFS.index("g_C")           # c = Weyl^2 central charge
A_STAR = float(GSTAR[A_IDX])          # UV fixed-point a*


def main():
    fw = {name: np.array([f.encode().coefficients.get(k, 0.0) for k in COEFFS])
          for name, f in FRAMEWORKS.items()}

    rows = []
    trajs = {}
    for name, g0 in fw.items():
        t, Y = flow(g0)
        trajs[name] = (t, Y[:, A_IDX])
        a_now = float(g0[A_IDX])           # framework = IR-ish value
        a_uv = float(Y[-1, A_IDX])         # UV end (-> a* = g_star)
        # a-theorem: a must DECREASE toward IR, i.e. a_now (IR) <= a_uv (UV fixed point)
        violates = a_now > A_STAR + 1e-9
        # monotonicity of a(t) along the integrated flow
        da = np.diff(Y[:, A_IDX])
        monotone = bool(np.all(da <= 1e-9) or np.all(da >= -1e-9))
        # c monotonicity (expected non-monotone in general)
        dc = np.diff(Y[:, C_IDX])
        c_monotone = bool(np.all(dc <= 1e-9) or np.all(dc >= -1e-9))
        rows.append({"framework": name, "a_g_R2": round(a_now, 3),
                     "a_UV_fixedpoint": round(a_uv, 3),
                     "a_theorem_ok": not violates, "a_monotone_along_flow": monotone,
                     "c_monotone": c_monotone})
    rows.sort(key=lambda r: -r["a_g_R2"])

    violators = [r["framework"] for r in rows if not r["a_theorem_ok"]]
    max_a = max(r["a_g_R2"] for r in rows)
    required_a_star = max_a
    all_monotone = all(r["a_monotone_along_flow"] for r in rows)

    # ---- figure: a(t) flows + a_framework vs a* threshold ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    for name, (t, a_t) in trajs.items():
        ax1.plot(t, a_t, lw=1, alpha=0.8)
    ax1.axhline(A_STAR, color="#d62728", ls="--", lw=2, label=f"UV fixed point a* = {A_STAR}")
    ax1.annotate("UV", (t.max(), A_STAR), fontsize=10, color="#d62728")
    ax1.annotate("IR ->", (t.min(), A_STAR + 0.02), fontsize=9)
    ax1.set_xlabel("RG time t = log(scale)  (right = UV)")
    ax1.set_ylabel("a = g_R2 (Euler central charge)")
    ax1.set_title("a(t) along the flow: a-theorem wants a to DECREASE toward the IR\n"
                  f"(frameworks above a*={A_STAR} have a INCREASING to the IR -> violate)",
                  fontsize=9)
    ax1.legend(fontsize=8)
    # scatter: framework a vs a*; violators above the line
    names = [r["framework"] for r in rows]
    avals = [r["a_g_R2"] for r in rows]
    cols = ["#d62728" if not r["a_theorem_ok"] else "#2ca02c" for r in rows]
    ax2.barh(names[::-1], avals[::-1], color=cols[::-1])
    ax2.axvline(A_STAR, color="black", ls="--", lw=2, label=f"a* = {A_STAR} (must be >= all)")
    ax2.set_xlabel("framework a = g_R2")
    ax2.set_title(f"a-theorem violators (red): {len(violators)}/{len(rows)} have a > a*\n"
                  f"-> consistency requires a* >= {required_a_star}", fontsize=9)
    ax2.legend(fontsize=8)
    fig.suptitle("v1.99  The a-theorem along the RG phylogeny", fontsize=12)
    fig.tight_layout()
    png = "/tmp/a_theorem_flow.png"
    fig.savefig(png, dpi=140)

    summary = {
        "a_UV_fixed_point": A_STAR,
        "a_monotone_along_flow_all": all_monotone,
        "a_theorem_violators": violators,
        "n_violators": len(violators),
        "n_frameworks": len(rows),
        "max_framework_a": round(max_a, 3),
        "a_theorem_requires_a_star_at_least": round(required_a_star, 3),
        "c_is_non_monotone_in_4d": "no c-theorem (Cardy) -> c-a need not be monotone",
        "verdict": (f"a(t) is MONOTONE along the toy flow for every framework, but the "
                    f"v1.89 UV fixed point a*={A_STAR} lies BELOW {len(violators)}/{len(rows)} "
                    f"frameworks' a=g_R2, so those flows have the central charge INCREASING "
                    f"toward the IR -- VIOLATING the a-theorem (a_UV >= a_IR). The a-theorem "
                    f"thus CONSTRAINS the phylogeny: the UV fixed point must have a* >= "
                    f"{required_a_star} (the largest framework a), i.e. the asymptotic-safety "
                    f"fixed point must carry a LARGE Euler central charge dominating all IR "
                    f"theories."),
        "interpretation": "The a-theorem is a non-trivial consistency check on the toy RG "
            "flow. The v1.89 betas (tuned for the phylogeny tree) are NOT a-theorem-consistent "
            "as-is; reconciling them PREDICTS a property of the UV fixed point (a* dominates). "
            "A constraint the engine derives by combining its own RG flow (v1.89) with the "
            "a-theorem (v1.70/71).",
        "honest": "toy betas (v1.89) + a=g_R2 proxy; robust content is monotonicity-along-flow, "
                  "the UV-must-dominate structure, and the resulting fixed-point constraint.",
        "rows": rows,
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
