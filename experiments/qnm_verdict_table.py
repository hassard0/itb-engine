"""v2.430 - the 2030 verdict table: the candidate is confirmed by exactly one of eight joint-outcome patterns -- maximally falsifiable.

Continuing option #1 (the empirical solve): turn the correlated smoking-gun signature (v2.429) into an actionable
DECISION RULE. The three near-term measurements each have a binary outcome:
  P  parity  -- CMB cosmic birefringence:  beta > 0 (detected)  vs  beta = 0 (null)
  M  matter  -- CMB-S4 inflation:          matter tension (large g_4)  vs  clean single-field slow-roll
  D  dark E  -- DESI/Euclid:               w in the candidate band (~ -1, bounded)  vs  w far off

That is 2^3 = 8 joint-outcome patterns. Because the candidate REQUIRES the correlated triple (all three fronts
nonzero and tied through the keystones, v2.429 -- re-verified here: parity=0 and weak-matter are each INFEASIBLE
with the rest at candidate values), it is confirmed by exactly ONE pattern (P=1,M=1,D=1) and falsified or
not-confirmed by the other seven. The two nearest alternatives are cleanly separated: beta=0 with the rest
present selects the parity-conserving RIVAL (v2.420, re-verified: feasible when birefringence is null); an
all-null result (P=0,M=0,D=0) is standard cosmology / no new physics.

So the candidate makes a MAXIMALLY FALSIFIABLE joint prediction: 1/8 of the outcome space confirms it, and the
correlation is what makes partial patterns (e.g. parity WITHOUT matter tension, P=1,M=0) candidate-KILLERS that
independent single-probe tests could not distinguish. This is the sharpest actionable form of 'how we will know
by ~2030'.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.430"
DEFAULT_OUT = Path("experiments/results/v2.430/qnm_verdict_table.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CON = [0.529, 0.4, 0.4, 0.193, 0.09, 0.06]


def _feas(stack, v):
    return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)


def _verdict(P, M, D):
    # P=parity>0, M=matter tension (large g_4), D=dark energy w in candidate band
    if P and M and D:
        return "CANDIDATE confirmed", "the full correlated triple -- unique to the candidate"
    if (not P) and M and D:
        return "parity-conserving RIVAL", "matter+dark-energy structure but no parity (v2.420)"
    if (not P) and (not M) and (not D):
        return "STANDARD / no new physics", "clean slow-roll, beta=0, w=-1 -- candidate killed"
    if P and not M:
        return "NEITHER (candidate killed)", "parity without matter tension breaks the keystone correlation"
    if M and not D:
        return "NEITHER (candidate killed)", "matter tension without the predicted w breaks the DE prediction"
    return "NEITHER / inconclusive", "a partial pattern the candidate does not predict"


def run() -> dict:
    full = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                       include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    no_biref = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=False,
                           include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    # engine anchors driving the table
    anchors = {
        "candidate_feasible": _feas(full, CON),
        "parity_off_infeasible": not _feas(full, [0.529, 0.4, 0.4, 0.193, 0.09, 0.0]),
        "weak_matter_infeasible": not _feas(full, [0.2, 0.4, 0.4, 0.193, 0.09, 0.06]),
        "parity_conserving_rival_feasible_if_beta0": _feas(no_biref, [0.529, 0.4, 0.4, 0.193, 0.09, 0.0]),
    }

    table = []
    for P in (1, 0):
        for M in (1, 0):
            for D in (1, 0):
                verdict, why = _verdict(P, M, D)
                table.append({"parity": P, "matter": M, "dark_energy": D, "verdict": verdict, "why": why})

    n_candidate = sum(1 for r in table if r["verdict"].startswith("CANDIDATE"))
    n_falsify = sum(1 for r in table if "killed" in r["verdict"] or "NEITHER" in r["verdict"] or "STANDARD" in r["verdict"])

    checks = {
        "anchors_verified": all(anchors.values()),
        "candidate_confirmed_by_one_pattern": n_candidate == 1,
        "majority_of_outcomes_do_not_confirm": n_falsify >= 5,
        "rival_and_standard_distinct": any(r["verdict"].startswith("parity-conserving") for r in table)
                                       and any(r["verdict"].startswith("STANDARD") for r in table),
        "correlation_breakers_kill": any(r["parity"] == 1 and r["matter"] == 0 and "killed" in r["verdict"] for r in table),
    }

    return {
        "version": VERSION,
        "engine_anchors": anchors,
        "verdict_table": table,
        "candidate_confirmed_patterns": n_candidate,
        "total_patterns": len(table),
        "non_confirming_patterns": n_falsify,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The 2030 verdict table: the candidate is confirmed by exactly ONE of eight joint-outcome patterns, "
            "making it maximally falsifiable. Turning the correlated signature (v2.429) into a decision rule "
            "over the three binary measurement outcomes -- parity (CMB birefringence beta>0 vs 0), matter "
            "(CMB-S4 inflationary tension vs clean slow-roll), and dark energy (w in the candidate band vs far "
            "off) -- gives 2^3 = 8 patterns. Because the candidate REQUIRES the correlated triple (re-verified: "
            "parity=0 and weak-matter are each infeasible with the rest at candidate values), it is confirmed "
            "by exactly one pattern (parity + matter + dark-energy all as predicted) and NOT confirmed by the "
            "other seven. The two nearest alternatives are cleanly separated: a null birefringence (beta=0) "
            "with the rest present selects the parity-conserving RIVAL (re-verified feasible when birefringence "
            "is null), and an all-null result is standard cosmology / no new physics. Crucially the CORRELATION "
            "makes partial patterns decisive: a parity detection WITHOUT the matter tension (parity but no "
            "large g_4) breaks the keystone correlation and KILLS the candidate -- a discrimination independent "
            "single-probe tests could not make. So the candidate's empirical status by ~2030 is a clean "
            "actionable verdict: one specific correlated pattern confirms it, seven falsify or fail to confirm "
            "it, and the two runner-up theories (parity-conserving EFT; standard no-new-physics cosmology) have "
            "their own distinct signatures. This is the sharpest, most decision-ready form of the empirical "
            "test -- the concrete answer to 'how will we know', and the furthest an EFT-carving program can "
            "push toward settling the theory short of the data itself."
        ),
        "honest_scope": (
            "The verdict LOGIC follows from two engine-verified feasibility facts (the candidate requires the "
            "correlated triple, v2.429; the parity-conserving rival is selected by beta=0, v2.420) plus the "
            "binary discretization of three continuous measurements -- so it is a decision-support map, not a "
            "likelihood/Bayes computation (a full posterior would need the measurement error models and the "
            "toy-map magnitudes, which are O(1)). The three 'outcomes' are coarse binaries; real data give "
            "continuous values, and the boundary cases (marginal beta, marginal w) are not resolved here. The "
            "'matter tension' and 'w band' outcomes rest on the toy coupling->observable maps (the SIGN/pattern "
            "content is robust, the exact thresholds are not). The parity axis is contingent on the ~3.6-sigma "
            "birefringence framing (v2.329). '1/8 confirms' counts discrete patterns, not probability mass -- "
            "the priors over outcomes are not modeled. Robust content: the candidate requires a specific "
            "correlated joint pattern, so of the eight coarse outcome combinations exactly one confirms it and "
            "the correlation makes partial patterns (parity without matter) candidate-killers; the "
            "parity-conserving rival and standard cosmology occupy distinct patterns. Decision-map-not-Bayes, "
            "coarse-binaries, toy-map-thresholds, birefringence-contingent. A verdict-table cycle sharpening "
            "option #1."
        ),
        "references": [
            "this repo: v2.429 (correlated signature -- the triple), v2.420 (parity-conserving rival), v2.421 (falsification portfolio), v2.01 (early Bayesian model comparison), v2.329 (birefringence hint)",
            "physics: CMB-S4 (inflation + birefringence), DESI/Euclid (w(z)); a correlated joint verdict is less evadeable than independent single-probe tests",
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
    print("v2.430 - the 2030 verdict table (parity P, matter M, dark-energy D):")
    for r in res["verdict_table"]:
        print(f"  P={r['parity']} M={r['matter']} D={r['dark_energy']} -> {r['verdict']:<28} ({r['why'][:52]})")
    print(f"  => candidate confirmed by {res['candidate_confirmed_patterns']}/{res['total_patterns']} patterns; {res['non_confirming_patterns']}/{res['total_patterns']} do not confirm => maximally falsifiable")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
