"""v2.344 - How robust is the data-pinned parity window to the anomaly-inflow prefactor?

The program's single most load-bearing AND most-caveated result is the parity prediction: the constructed
theory needs g_R2_parity > 0 (parity violation), pinned into a narrow window by the cosmic-birefringence
DATA from below and the gravitational anomaly-inflow budget from above. The lower edge is data
(birefringence beta = 0.34 +/- 0.09 deg, 2-sigma band [0.0471, 0.1529] in g_R2_parity). The UPPER edge is
the anomaly budget g_R2_parity^2 + 2 g_R3_parity^2 <= rho_inflow * g_4 * g_R2, whose prefactor rho_inflow is
an O(1) CHOICE. So the natural stress test: does the parity result survive across the engine's OWN declared
plausible band for that prefactor, anomaly_rho in [0.03, 0.12]?

Closed form (constructed g_4=0.529, g_R2=0.193, g_R3_parity=0): the anomaly upper edge on g_R2_parity is
sqrt(rho * g_4 * g_R2) = sqrt(rho * 0.10210). The joint (birefringence AND anomaly) window is
[0.0471, min(0.1529, sqrt(rho*0.10210))].

Two thresholds fall out:
  * window non-empty   iff  rho >= 0.0471^2 / 0.10210 = 0.0217   (well below the declared band)
  * constructed 0.06 survives  iff  rho >= 0.06^2 / 0.10210 = 0.0353

So the QUALITATIVE headline (a positive parity window exists -> parity is required) is robust across the
entire declared band, but the SPECIFIC value 0.06 is prefactor-contingent: in the lowest ~17% of the band
[0.03, 0.0353) the constructed 0.06 would violate the anomaly budget and the window center shifts down. An
honest, quantified fragility threshold on the one load-bearing prefactor.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.constraints.anomaly_flow import GeneralizedAnomalyInflow
from itb.constraints.cosmic_birefringence import CosmicBirefringenceData
from itb.theory import Theory

VERSION = "v2.344"
DEFAULT_OUT = Path("experiments/results/v2.344/qnm_parity_prefactor_robustness.json")

CONSTRUCTED = {
    "g_4": 0.529, "g_6": 0.4, "g_8": 0.4,
    "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06, "g_R3_parity": 0.0,
}
DECLARED_BAND = (0.03, 0.12)          # the engine's own plausible band for anomaly_rho (experiments/stack.py)
G4, GR2 = CONSTRUCTED["g_4"], CONSTRUCTED["g_R2"]
PROD = G4 * GR2                        # 0.10210
CONSTRUCTED_PARITY = CONSTRUCTED["g_R2_parity"]


def anomaly_upper(rho: float) -> float:
    """Closed-form upper edge on g_R2_parity from the anomaly budget (g_R3_parity = 0)."""
    return math.sqrt(rho * PROD)


def theory_with_parity(p: float) -> Theory:
    c = dict(CONSTRUCTED)
    c["g_R2_parity"] = p
    return Theory(coefficients=c, name=f"parity_{p:.4f}")


def run() -> dict:
    bire = CosmicBirefringenceData(n_sigma=2.0)
    bire_lo, bire_hi = bire.preferred_band
    bire_lo, bire_hi = round(bire_lo, 4), round(bire_hi, 4)

    # thresholds (closed form)
    rho_window_open = bire_lo ** 2 / PROD
    rho_constructed_survives = CONSTRUCTED_PARITY ** 2 / PROD

    # scan across the declared band (incl. the default 0.06), cross-checking against the actual constraint
    grid = sorted(set(
        [DECLARED_BAND[0] + i * (DECLARED_BAND[1] - DECLARED_BAND[0]) / 8 for i in range(9)] + [0.06]))
    rows = []
    closed_form_matches_engine = True
    for rho in grid:
        up = anomaly_upper(rho)
        win_lo = bire_lo
        win_hi = min(bire_hi, up)
        nonempty = win_hi > win_lo
        constructed_in = win_lo <= CONSTRUCTED_PARITY <= win_hi

        # engine cross-check 1: the constructed theory's anomaly satisfaction at this rho
        anom = GeneralizedAnomalyInflow(rho=rho)
        eng_satisfied = anom.evaluate(theory_with_parity(CONSTRUCTED_PARITY)).satisfied
        # engine cross-check 2: a theory exactly AT the closed-form edge has anomaly margin ~ 0
        edge_margin = anom.evaluate(theory_with_parity(up)).margin
        if abs(edge_margin) > 1e-9 or eng_satisfied != constructed_in:
            closed_form_matches_engine = False

        rows.append({
            "anomaly_rho": round(rho, 4),
            "anomaly_upper_edge": round(up, 4),
            "joint_window": [round(win_lo, 4), round(win_hi, 4)],
            "window_width": round(max(0.0, win_hi - win_lo), 4),
            "window_nonempty": bool(nonempty),
            "constructed_0p06_survives": bool(constructed_in),
            "engine_anomaly_satisfied": bool(eng_satisfied),
        })

    window_nonempty_across_band = all(r["window_nonempty"] for r in rows)
    parity_required_positive = all(r["joint_window"][0] > 0.0 for r in rows)
    constructed_survives_at_default = bire_lo <= CONSTRUCTED_PARITY <= anomaly_upper(0.06)
    constructed_excluded_at_band_bottom = not rows[0]["constructed_0p06_survives"]

    checks = {
        "window_nonempty_across_declared_band": window_nonempty_across_band,
        "parity_required_positive_across_band": parity_required_positive,
        "constructed_survives_at_default_rho": constructed_survives_at_default,
        "constructed_excluded_at_band_bottom": constructed_excluded_at_band_bottom,  # the honest fragility
        "closed_form_matches_engine_constraint": closed_form_matches_engine,
    }

    return {
        "version": VERSION,
        "declared_anomaly_rho_band": list(DECLARED_BAND),
        "birefringence_2sigma_band": [bire_lo, bire_hi],
        "g4_times_gR2": round(PROD, 5),
        "threshold_rho_window_opens": round(rho_window_open, 4),
        "threshold_rho_constructed_survives": round(rho_constructed_survives, 4),
        "scan": rows,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The parity prediction's QUALITATIVE core is robust to the one load-bearing prefactor, but its "
            "specific magnitude is not -- and the threshold is quantified. The constructed theory needs a "
            "positive parity coupling g_R2_parity, pinned from below by the cosmic-birefringence data "
            "(2-sigma band [0.0471, 0.1529]) and from above by the gravitational anomaly-inflow budget "
            "whose prefactor anomaly_rho is an O(1) choice. Stress-testing across the engine's OWN declared "
            "plausible band anomaly_rho in [0.03, 0.12]: the joint (data AND anomaly) window for "
            "g_R2_parity stays NON-EMPTY and strictly positive at every rho in the band (it would only "
            "close below rho = 0.0217, well outside the declared band), so 'parity violation is required, "
            "beta = 0 excluded' holds regardless of the prefactor -- the headline is robust. What is NOT "
            "robust is the specific constructed VALUE 0.06: it survives the anomaly budget only for "
            "rho >= 0.0353, so in the lowest ~17% of the declared band, [0.03, 0.0353), the constructed "
            "0.06 would VIOLATE the budget and the window center shifts down to ~0.051. So the EXISTENCE "
            "and SIGN of the parity prediction are prefactor-robust; its precise MAGNITUDE tracks the "
            "prefactor and is contingent on anomaly_rho being near its default 0.06 rather than its floor. "
            "The closed-form window edges match the engine's actual GeneralizedAnomalyInflow constraint "
            "exactly at every grid point (a theory placed at the sqrt(rho g_4 g_R2) edge has anomaly margin "
            "0). This is the honest sensitivity of the program's most load-bearing result: the parity "
            "headline you should trust is 'g_R2_parity > 0, in [0.047, ~0.08]', not the single digit 0.06."
        ),
        "honest_scope": (
            "This is a sensitivity analysis of two specific constraints (cosmic_birefringence + "
            "generalized_anomaly_inflow), not the full stack -- other constraints could in principle tighten "
            "the window further, so the windows here are UPPER bounds on the feasible parity range (the true "
            "joint-with-everything window is a subset). The anomaly budget's FORM (g_R2_parity^2 + 2 "
            "g_R3_parity^2 <= rho g_4 g_R2) and the birefringence map (beta = 3.4 deg * g_R2_parity) are the "
            "engine's toy encodings; the threshold values (0.0217, 0.0353) are exact arithmetic GIVEN those "
            "forms, but inherit the toy-basis and O(1)-prefactor caveats. The [0.03, 0.12] band is the "
            "engine's own declared range for anomaly_rho (experiments/stack.py), itself a convention -- a "
            "wider band would widen the fragility region. The whole result still rests on the "
            "cosmic-birefringence data being real (the ~3.6-sigma hint, v2.329 caveat); if it is a "
            "systematic, the lower edge vanishes and parity becomes a soft direction with no positivity "
            "requirement. Robust content: across the declared prefactor band the parity window is non-empty "
            "and positive (the sign/existence is prefactor-robust), and the specific 0.06 requires rho >= "
            "0.0353. Toy basis. A robustness audit of the load-bearing parity result, reported with its "
            "fragility."
        ),
        "references": [
            "this repo: experiments/stack.py (anomaly_rho default 0.06, declared band [0.03,0.12]); src/itb/constraints/anomaly_flow.py; src/itb/constraints/cosmic_birefringence.py (beta=0.34+/-0.09 deg)",
            "this repo: v2.329 (birefringence is the single point of failure), v2.335 (anomaly budget couples the parity couplings), v2.321 (birefringence pins parity)",
            "Minami & Komatsu PRL 125,221301 (2020); Eskilt & Komatsu 2022; Alvarez-Gaume-Witten 1984 (anomaly inflow)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("parity window vs anomaly_rho (declared band [0.03, 0.12]):")
    print(f"  birefringence 2-sigma lower edge: {res['birefringence_2sigma_band'][0]}")
    print(f"  {'rho':>6}  {'anom_upper':>10}  {'window':>18}  width   0.06?")
    for r in res["scan"]:
        print(f"  {r['anomaly_rho']:>6}  {r['anomaly_upper_edge']:>10}  "
              f"{str(r['joint_window']):>18}  {r['window_width']:.4f}  {r['constructed_0p06_survives']}")
    print(f"  threshold rho window opens:        {res['threshold_rho_window_opens']}")
    print(f"  threshold rho constructed survives: {res['threshold_rho_constructed_survives']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
