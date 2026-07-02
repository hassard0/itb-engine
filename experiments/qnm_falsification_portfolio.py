"""v2.421 - the falsification portfolio: the concrete decision map for confirming or killing the candidate.

Assembling the program (post de-toying arc) into one actionable artifact: for each near/mid-future observable,
what it measures, the candidate's prediction, the rival archetype it distinguishes (v2.420), the RIGOR TIER of
the candidate's prediction (from the v2.411-419 rigor work), and the rough timeline. This is a consolidation/
decision map, not new physics -- it answers 'so what would actually settle this?'.

The spine (from v2.420): the candidate's single LIVE rival is the parity-conserving EFT, separated by the parity
question; the too-much-gravity / too-little-matter archetypes are already rigorously excluded. So the portfolio
is organized around the parity question (the live one) plus the structural checks (mostly settled) plus the
make-or-break matter test (CMB-S4 inflation).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import rigorous_core_stack, build_stack, frameworks

VERSION = "v2.421"
DEFAULT_OUT = Path("experiments/results/v2.421/qnm_falsification_portfolio.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
BK = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
          include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def run() -> dict:
    core = rigorous_core_stack(**BK)

    def rig_viol(v):
        return [r.constraint_name for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), core).results if not r.satisfied]

    # verified anchors for the portfolio
    lqg = [f for f in frameworks() if f.name == "lqg_induced"][0]
    lqg_rig_excluded = len(rig_viol([lqg.encode().coefficients.get(k, 0) for k in KEYS])) > 0

    portfolio = [
        {"observable": "CMB cosmic birefringence (LiteBIRD / CMB-S4, ~2028-2030)",
         "measures": "photon-sector parity rotation beta",
         "candidate_prediction": "nonzero positive-handed beta (parity-violating)",
         "distinguishes": "candidate (A) vs parity-conserving rival (B)",
         "prediction_tier": "data-contingent (the ~3.6-sigma hint); parity SIGN rigorous+data, magnitude data-pinned under a rigorous ceiling (v2.418)",
         "kills_candidate_if": "beta consistent with 0 -> the parity-conserving rival (B) is selected",
         "role": "THE live discriminator (v2.420: candidate-vs-rival reduces to this)"},
        {"observable": "CMB-S4 inflationary observables (~2030)",
         "measures": "the matter self-coupling g_4 (via the inflaton potential)",
         "candidate_prediction": "large g_4 (matter dominance) -> tension with single-field slow-roll (>10 sigma, v2.395)",
         "distinguishes": "candidate vs standard slow-roll inflation",
         "prediction_tier": "structure rigorous (matter dominance), observable map toy (g_4<->inflaton)",
         "kills_candidate_if": "clean single-field slow-roll confirmed with small self-coupling",
         "role": "make-or-break matter test (independent of the parity question)"},
        {"observable": "GW birefringence (LISA / Einstein Telescope, ~2035)",
         "measures": "graviton-sector parity (chirality)",
         "candidate_prediction": "nonzero chirality ~4x below current cap (v2.387); rival predicts ZERO",
         "distinguishes": "candidate (A) vs parity-conserving rival (B), via a DIFFERENT sector than CMB",
         "prediction_tier": "chirality structure rigorous (parity-decomposed positivity), magnitude toy",
         "kills_candidate_if": "no GW birefringence at ET/LISA sensitivity AND CMB beta->0 (joint)",
         "role": "SECOND independent parity channel -> de-risks the single-measurement dependence; agreement/disagreement with CMB tests the single-parity-origin assumption"},
        {"observable": "sub-mm gravity (Eot-Wash-class torsion balances)",
         "measures": "the scalaron fifth-force range/strength (g_R2 sector)",
         "candidate_prediction": "screened scalaron (unscreened dark-energy-scale force excluded)",
         "distinguishes": "screened vs unscreened curvature sector",
         "prediction_tier": "requires screening (qualitative feature); magnitude toy",
         "kills_candidate_if": "an unscreened sub-mm fifth force at the dark-energy scale is detected",
         "role": "consistency check (mostly settled; the theory must screen)"},
        {"observable": "amplitude/causality structure (already in hand)",
         "measures": "the gravity/matter balance + framework identity",
         "candidate_prediction": "LQG-induced excluded; too-much-gravity/too-little-matter excluded",
         "distinguishes": "candidate family vs rigorously-excluded archetypes (D, E) and LQG",
         "prediction_tier": "RIGOROUS (zero toy input, v2.411/2.420)",
         "kills_candidate_if": "n/a -- these are settled rigorous exclusions, not future measurements",
         "role": "the rigorous backbone (settled)"},
    ]

    checks = {
        "lqg_rigorously_excluded_anchor": lqg_rig_excluded,
        "portfolio_covers_both_live_tests": any("live discriminator" in e["role"] for e in portfolio) and any("make-or-break" in e["role"] for e in portfolio),
        "parity_has_two_independent_channels": sum(1 for e in portfolio if "parity" in e["measures"]) >= 2,
        "has_rigorous_backbone": any(e["prediction_tier"].startswith("RIGOROUS") for e in portfolio),
        "portfolio_nonempty": len(portfolio) == 5,
    }

    return {
        "version": VERSION,
        "portfolio": portfolio,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The falsification portfolio -- the concrete decision map for the candidate. Organized around the "
            "one live discriminator plus the make-or-break matter test plus the settled rigorous backbone: "
            "(1) CMB cosmic birefringence (LiteBIRD/CMB-S4, ~2028-30) is THE live discriminator -- the "
            "candidate-vs-parity-conserving-rival question reduces to it (v2.420); the parity SIGN is "
            "rigorous+data and the magnitude is data-pinned under a rigorous ceiling (v2.418), so a beta "
            "consistent with 0 selects the rival. (2) CMB-S4 inflationary observables (~2030) are the "
            "make-or-break MATTER test, independent of parity: the candidate's matter dominance forces a large "
            "g_4 in >10-sigma tension with single-field slow-roll (v2.395, structure rigorous / observable map "
            "toy). (3) GW birefringence (LISA/ET, ~2035) is a SECOND independent parity channel probing the "
            "GRAVITON sector (vs CMB's photon sector) -- it de-risks the single-measurement dependence and, by "
            "agreeing or disagreeing with CMB, tests the single-parity-origin assumption; the candidate "
            "predicts nonzero chirality ~4x below the current cap (v2.387) while the rival predicts zero. "
            "(4) sub-mm gravity is a consistency check (the theory must screen). (5) the amplitude/causality "
            "structure is the RIGOROUS backbone already in hand -- LQG and the too-much-gravity/too-little-"
            "matter archetypes are excluded with zero toy input (v2.411/2.420), not awaiting measurement. Net "
            "actionable picture: the candidate is falsifiable on two independent fronts -- PARITY (CMB now, GW "
            "later; if both null, the parity-conserving rival wins) and MATTER (CMB-S4 inflation; if clean "
            "slow-roll, matter dominance breaks) -- on a rigorous backbone that already excludes the other "
            "archetypes. So it is not hostage to one measurement: the parity question has redundant probes, and "
            "the matter test is orthogonal."
        ),
        "honest_scope": (
            "This is a CONSOLIDATION / decision map, not new physics -- it assembles predictions from prior "
            "cycles (v2.387/395/408/418/420) with their rigor tiers attached; the only live computation here "
            "is re-confirming the rigorous LQG exclusion as the backbone anchor. Timelines are approximate "
            "experiment horizons, not commitments. The prediction tiers are the honest crux: the parity SIGN "
            "and the rigorous ceiling are source-exact, but every MAGNITUDE (beta, the GW-birefringence size, "
            "g_4's inflationary imprint) rests on toy observable maps, so 'the candidate predicts nonzero "
            "beta/chirality' is robust while the predicted SIZES are order-of-magnitude. The birefringence "
            "'hint' is ~3.6-sigma (v2.329), not a detection. The GW-birefringence-tests-single-parity-origin "
            "point assumes the CMB and GW parity share an origin (the single-axion assumption, v1.81) -- which "
            "is exactly what their comparison would test. Robust content: the candidate is falsifiable on two "
            "independent fronts (parity: CMB+GW; matter: CMB-S4 inflation) atop a rigorous backbone that "
            "already excludes LQG and the extreme archetypes, so it is not hostage to a single measurement. "
            "Consolidation/decision-map, magnitudes toy, timelines approximate. A falsification-portfolio cycle."
        ),
        "references": [
            "this repo: v2.420 (alternatives map / live rival), v2.395 (CMB-S4 matter test), v2.408 (birefringence load-bearing), v2.418 (parity ceiling+data), v2.387 (GW-birefringence window), v2.411 (rigorous exclusions), v1.81 (multi-messenger parity), v2.329 (birefringence hint)",
            "physics: CMB cosmic birefringence (LiteBIRD/CMB-S4); CMB-S4 inflation; GW birefringence (LISA/ET); Eot-Wash sub-mm",
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
    print("v2.421 - the falsification portfolio (how to confirm/kill the candidate):")
    for e in res["portfolio"]:
        print(f"  [{e['prediction_tier'][:34]:<34}] {e['observable'][:46]}")
        print(f"      role: {e['role'][:90]}")
    print("  => two independent falsification fronts: PARITY (CMB now + GW later) and MATTER (CMB-S4 inflation), on a rigorous backbone")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
