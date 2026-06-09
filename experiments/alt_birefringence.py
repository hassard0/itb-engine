"""v2.08 - The alternative-birefringence EFTs: how the favored quantum gravity pivots on
the birefringence interpretation.

v2.04 found the data-driven EFT is a 'one-observable theory' -- its whole case rests on
cosmic birefringence beta=0.34+/-0.09 (a ~3.6sigma HINT). Here we make that concrete: we
re-derive the engine's FAVORED framework (Bayesian posterior over the 14 frameworks) as a
function of the ASSUMED beta, and over 5 scenarios:
  A canonical (beta=0.34+/-0.09, Minami-Komatsu),
  B null/parity-even (beta=0+/-0.09, the hint was a systematic),
  C tightened-confirmed (beta=0.34+/-0.03, LiteBIRD era),
  D half-value (beta=0.17+/-0.09),
  E higher (beta=0.45+/-0.09).

Map: beta = 3.4 * g_R2_parity. The favored data-driven EFT has g_R2_parity = beta/3.4 by
construction; the catalogued frameworks predict beta=0. We compute the posterior of
discovered_data_driven vs the best parity-even framework across beta in [0, 0.45].

HONEST: the favored EFT is CONTINGENT on the birefringence reading -- a null collapses it.
Robust content is the PIVOT structure (parity-even wins at beta~0, data-driven wins at
beta >~ 0.15).

Run on Vulcan:  python experiments/alt_birefringence.py
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
from stack import build_stack

KAPPA_BETA = 3.4
_STACK = build_stack(bnossw_mean="geometric", rfc_form="convex_hull")


def beta_of(name):
    g = FRAMEWORKS[name].encode().coefficients.get("g_R2_parity", 0.0)
    return KAPPA_BETA * g


# the cleanest contest: the engine's data-driven EFT (consistent, g_R2_parity = beta/3.4,
# tracks the assumed signal) vs the best CONSISTENT PARITY-EVEN framework (beta=0). The
# catalogued parity-violating frameworks (horava, the discovered_parity_violating branch)
# are separately excluded -- infeasible or wrong-sign parity (v1.78) -- so they are not the
# relevant competitor; the real pivot is parity-violating-EFT vs parity-even-survivor.
PARITY_EVEN_SURVIVOR = "string_tree_eft"      # canonical consistent, beta=0


def posterior_data_driven(beta_obs, sigma):
    """2-hypothesis posterior: data-driven EFT (matches beta) vs the parity-even survivor
    (beta=0). Returns P(data-driven), the parity-even competitor, and a 'decisively favored'
    flag (Bayes factor > 10)."""
    L_dd = 1.0                                            # matches the assumed beta exactly
    L_even = np.exp(-0.5 * (beta_obs / sigma) ** 2)       # parity-even survivor predicts 0
    Z = L_dd + L_even
    p_dd = L_dd / Z
    return {"discovered_data_driven": p_dd, PARITY_EVEN_SURVIVOR: L_even / Z}, PARITY_EVEN_SURVIVOR


def main():
    scenarios = [
        ("A canonical (MK hint)", 0.34, 0.09),
        ("B null / parity-even", 0.0, 0.09),
        ("C tightened (LiteBIRD)", 0.34, 0.03),
        ("D half-value", 0.17, 0.09),
        ("E higher", 0.45, 0.09),
    ]
    scen_rows = []
    for lbl, b, s in scenarios:
        post, best_even = posterior_data_driven(b, s)
        p_dd = post["discovered_data_driven"]
        # winner: parity-even by PARSIMONY at a tie (beta~0 adds no needed parameter)
        winner = "discovered_data_driven" if p_dd > 0.5 + 1e-9 else best_even
        scen_rows.append({"scenario": lbl, "beta": b, "sigma": s,
                          "data_driven_posterior": round(p_dd, 4),
                          "best_parity_even": best_even,
                          "best_parity_even_posterior": round(post[best_even], 4),
                          "winner": winner, "decisively_favored_BF>10": bool(p_dd > 10 / 11),
                          "g_R2_parity_favored": round(b / KAPPA_BETA, 4)})

    # sweep beta at the hint sigma and the LiteBIRD sigma
    betas = np.linspace(0.0, 0.45, 60)
    pdd_hint = [posterior_data_driven(b, 0.09)[0]["discovered_data_driven"] for b in betas]
    pdd_lb = [posterior_data_driven(b, 0.03)[0]["discovered_data_driven"] for b in betas]
    # pivot beta: where the data-driven EFT becomes DECISIVELY favored (BF>10 -> p=0.909)
    pivot = float(np.interp(10 / 11, pdd_hint, betas)) if pdd_hint[-1] > 10 / 11 else None
    pivot_lb = float(np.interp(10 / 11, pdd_lb, betas)) if pdd_lb[-1] > 10 / 11 else None

    # ---- figure ----
    fig, ax = plt.subplots(figsize=(10.5, 6.5))
    ax.plot(betas, pdd_hint, lw=2, color="#1f77b4", label="data-driven posterior (sigma=0.09, hint)")
    ax.plot(betas, pdd_lb, lw=2, ls="--", color="#2ca02c", label="data-driven posterior (sigma=0.03, LiteBIRD)")
    ax.axhline(0.5, color="grey", lw=0.8, ls=":")
    ax.axhline(10 / 11, color="purple", lw=0.8, ls=":", label="decisive (BF=10)")
    for lbl, b, s in scenarios:
        ax.axvline(b, color="#d62728", lw=0.7, alpha=0.5)
        ax.annotate(lbl.split("(")[0], (b, 0.05), rotation=90, fontsize=6.5, color="#d62728")
    if pivot:
        ax.scatter([pivot], [0.5], s=80, color="black", zorder=5)
        ax.annotate(f"pivot beta~{pivot:.2f}", (pivot, 0.5), fontsize=8, xytext=(5, 5),
                    textcoords="offset points")
    ax.set_xlabel("assumed cosmic-birefringence beta (deg)")
    ax.set_ylabel("posterior P(data-driven EFT | beta)")
    ax.set_title("v2.08  The favored quantum gravity pivots on the birefringence reading\n"
                 "parity-even frameworks win at beta~0; the data-driven EFT wins at beta >~ pivot",
                 fontsize=10)
    ax.legend(fontsize=8, loc="center right"); ax.set_ylim(0, 1.02)
    fig.tight_layout()
    png = "/tmp/alt_birefringence.png"
    fig.savefig(png, dpi=140)

    summary = {
        "map": "beta = 3.4 * g_R2_parity",
        "contest": "data-driven EFT (matches beta) vs the consistent PARITY-EVEN survivor "
                   "(string tree-EFT, beta=0); parity-even wins at a tie by parsimony",
        "scenarios": scen_rows,
        "decisive_pivot_beta_hint_sigma": round(pivot, 3) if pivot else None,
        "decisive_pivot_beta_LiteBIRD_sigma": round(pivot_lb, 3) if pivot_lb else None,
        "null_scenario_winner": scen_rows[1]["winner"],
        "null_scenario_data_driven_posterior": scen_rows[1]["data_driven_posterior"],
        "canonical_decisively_favored": scen_rows[0]["decisively_favored_BF>10"],
        "interpretation": "The engine's favored quantum gravity PIVOTS on the birefringence "
            "interpretation. Under the NULL (beta=0) scenario the data-driven EFT ties the "
            "parity-even survivor (posterior 0.5) -- so by PARSIMONY the parity-even framework "
            "wins (the data-driven EFT adds an unneeded parity coupling): it was a creature of "
            "the hint. The data-driven EFT becomes DECISIVELY favored (Bayes factor > 10) only "
            "for beta above ~{:.2f} at the current hint precision (sigma=0.09), tightening to "
            "~{:.2f} at LiteBIRD precision (sigma=0.03). The canonical beta=0.34 is well above "
            "both -> decisively favored today; a tightened null would collapse it. This makes "
            "v2.04's 'one-observable theory' concrete: the conclusion is CONTINGENT on the "
            "~3.6sigma birefringence reading.".format(pivot or 0.0, pivot_lb or 0.0),
        "honest": "toy Gaussian likelihoods + the beta=3.4*g_R2_parity map; the data-driven EFT "
                  "tracks the assumed beta by construction, so this measures CONTINGENCY, not "
                  "confirmation. Robust content is the pivot structure.",
        "relates_to": ["v2.01 Bayesian comparison", "v2.04 minimal falsifier", "v1.78/79"],
        "png": png,
    }
    print(json.dumps(summary, indent=2,
                     default=lambda o: o.item() if hasattr(o, "item") else str(o)))


if __name__ == "__main__":
    main()
