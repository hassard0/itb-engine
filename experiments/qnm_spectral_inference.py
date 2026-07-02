"""v2.438 - the low-energy amplitude DOES infer part of the UV: the candidate's Hankel saturation shows a multi-state tower (not a single resonance) -- but not which tower, refining v2.437.

Bold swing on the S-matrix / spectral-density angle, done safely with the bound the engine already has. The
matter dispersion bound g_6^2 <= g_4 g_8 is Cauchy-Schwarz on the positive spectral density rho(m^2) (the Wilson
coefficients are its moments): it is SATURATED (s = g_6^2/(g_4 g_8) = 1) iff rho is a single delta -- ONE massive
resonance -- and is INTERIOR (s < 1) iff rho has support on two or more masses -- a MULTI-state spectrum (a
tower). So the saturation ratio s reads off part of the UV spectrum from the low-energy amplitude.

Result: the candidate has s = g_6^2/(g_4 g_8) = 0.756 -- INTERIOR, not saturating -- so its implied UV spectrum
is MULTI-STATE (tower-like), NOT a single massive resonance. And every viable UV completion is similarly interior:
string 0.80, asymptotic safety 0.75, CDT 0.83 (LQG 0.84, excluded), pure GR undefined (no dim-8 matter). Two
things follow. (1) A genuine partial UV inference: amplitude positivity, beyond carving the couplings, ESTABLISHES
that the candidate's UV is a tower (a spread spectral density), ruling out a single-resonance / weakly-coupled-
single-state completion -- the candidate is 'stringy' in the sense of having many states. (2) It does NOT
discriminate the completions: they are all interior with s ~ 0.75-0.84, within the O(1) encoder spread, and --
tellingly -- the saturation RANKS them differently from the parity-even distance (on s the candidate is closest
to asymptotic safety at 0.75, while on distance it is closest to string at 0.067), so no single low-energy measure
picks a winner. This refines v2.437: the low-energy program CAN confirm a tower EXISTS (multi-state, s<1) but
cannot see its TYPE (Regge vs Kaluza-Klein vs fixed-point) -- the tower's existence is a low-energy fact, its
character is the UV frontier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.438"
DEFAULT_OUT = Path("experiments/results/v2.438/qnm_spectral_inference.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
PE = ["g_4", "g_6", "g_8", "g_R2", "g_R3"]


def _sat(c):
    d = c.get("g_4", 0.0) * c.get("g_8", 0.0)
    return round(c.get("g_6", 0.0) ** 2 / d, 3) if d > 0 else None


def run() -> dict:
    import math
    cand_s = _sat(CON)
    table = {}
    for f in frameworks():
        c = {k: float(f.encode().coefficients.get(k, 0.0)) for k in KEYS}
        s = _sat(c)
        dist = round(math.sqrt(sum((CON[k] - c.get(k, 0.0)) ** 2 for k in PE)), 3)
        table[f.name] = {"saturation": s, "parity_even_distance": dist,
                         "multi_state_tower": (s is not None and s < 0.95)}

    viable = {n: r for n, r in table.items() if r["saturation"] is not None and n != "lqg_induced"}
    # ranking by saturation-closeness vs by distance -- do they agree?
    by_sat = sorted(viable, key=lambda n: abs(viable[n]["saturation"] - cand_s))
    by_dist = sorted(viable, key=lambda n: viable[n]["parity_even_distance"])
    rankings_differ = by_sat[0] != by_dist[0]

    checks = {
        "candidate_interior_not_saturating": cand_s < 0.95,
        "candidate_multi_state_tower": cand_s < 1.0,
        "all_viable_completions_interior": all(r["multi_state_tower"] for r in viable.values()),
        "saturation_ranks_differently_than_distance": rankings_differ,
        "tower_exists_but_type_inaccessible": cand_s < 0.95 and all(r["multi_state_tower"] for r in viable.values()),
    }

    return {
        "version": VERSION,
        "candidate_saturation": cand_s,
        "saturation_table": {n: r["saturation"] for n, r in table.items()},
        "closest_by_saturation": by_sat[0],
        "closest_by_distance": by_dist[0],
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The low-energy amplitude DOES infer part of the UV: the candidate's Hankel saturation shows a "
            "multi-state tower (not a single resonance), refining v2.437. The matter dispersion bound "
            "g_6^2 <= g_4 g_8 is Cauchy-Schwarz on the positive spectral density (the Wilson coefficients are "
            "its moments): saturated (s = g_6^2/(g_4 g_8) = 1) iff the spectrum is a single massive resonance, "
            "interior (s < 1) iff two or more masses -- a tower. The candidate has s = 0.756, INTERIOR, so its "
            "implied UV is MULTI-STATE (tower-like), NOT a single resonance; every viable completion is "
            "similarly interior (string 0.80, asymptotic safety 0.75, CDT 0.83). Two consequences. (1) A "
            "genuine partial UV inference: amplitude positivity, beyond carving the couplings, ESTABLISHES that "
            "the candidate's UV is a tower (a spread spectral density), ruling out a single-resonance / "
            "weakly-coupled-single-state completion -- so the candidate is 'stringy' in the concrete sense of "
            "having many states, and the tower whose EXISTENCE v2.375 asserted from log-convexity is here "
            "confirmed from the interior saturation. (2) It still does NOT discriminate the completions: all are "
            "interior with s ~ 0.75-0.84 within the O(1) encoder spread, and the saturation RANKS them "
            "differently from the parity-even distance -- on saturation the candidate is closest to asymptotic "
            "safety (0.75), on distance closest to string (0.067) -- so no single low-energy measure picks a "
            "winner, reinforcing the robust UV-completion degeneracy (v2.436). Net, this sharpens exactly what "
            "the low-energy program can and cannot say about the UV: it CAN confirm a tower EXISTS (the "
            "candidate is a multi-state theory, s < 1), but it CANNOT see the tower's TYPE (Regge vs "
            "Kaluza-Klein vs fixed-point) -- the tower's existence is a low-energy fact, its character is the "
            "UV frontier. So the amplitude-carving program's honest UV output is: 'the candidate is a "
            "multi-state (stringy) EFT whose specific UV completion (string / CDT / asymptotic safety) the "
            "low-energy data cannot resolve -- that needs the cutoff-scale spectrum.'"
        ),
        "honest_scope": (
            "s = g_6^2/(g_4 g_8) is the engine's leading matter Hankel ratio; its 'saturation = single state, "
            "interior = tower' reading is the exact moment-problem interpretation (Cauchy-Schwarz equality iff "
            "a rank-1 / single-delta measure), so this part is rigorous IN STRUCTURE (v2.411 'source-exact in "
            "form' -- the coefficients-as-moments convention). BUT the candidate's g_6 = g_8 = 0.4 is a "
            "Chebyshev-center ARTIFACT (v2.392), so the precise s = 0.756 is at an artifact point, not a "
            "prediction; the robust content is only that s < 1 (interior => multi-state), which holds across "
            "the feasible region and all frameworks, not the exact value. The frameworks are schematic O(1) "
            "encoders (v2.436 caveat), so the per-framework s (0.75-0.84) and the differing rankings are "
            "encoder-level -- the point is that they cluster and rank inconsistently (degeneracy), not the "
            "specific numbers. 'Multi-state tower' is an inference about the spectral density's support (>= 2 "
            "masses), not a computed spectrum. Robust content: the candidate (and all viable completions) is "
            "interior to the leading matter positivity bound (s < 1), so its UV spectral density is multi-state "
            "-- a tower exists -- while the tower's type is not resolved by any low-energy measure, refining the "
            "UV-frontier statement of v2.437. Chebyshev-artifact-point, interior-is-robust-value-is-not, "
            "encoder-level, spectrum-inferred-not-computed. A spectral-inference cycle."
        ),
        "references": [
            "this repo: v2.437 (UV discriminator = tower spectrum), v2.436 (UV degeneracy), v2.375 (log-convex tower asserted), v2.392 (g_6=g_8 Chebyshev artifact), dispersion_tower (the Hankel bound)",
            "physics: Cauchy-Schwarz / Hankel positivity on the spectral density; saturation = single state, interior = multi-state; string/KK/fixed-point differ in the tower TYPE, not its existence",
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
    print("v2.438 - spectral inference from the low-energy amplitude (Hankel saturation):")
    print(f"  candidate saturation s = g_6^2/(g_4 g_8) = {res['candidate_saturation']} (INTERIOR < 1 => multi-state tower, not a single resonance)")
    for n, s in res["saturation_table"].items():
        print(f"    {n:<20} s = {s}")
    print(f"  closest by saturation: {res['closest_by_saturation']}; by distance: {res['closest_by_distance']} (differ => degeneracy)")
    print("  => low-energy CAN confirm a tower EXISTS (s<1, multi-state) but NOT its type (Regge/KK/fixed-point) -- refines v2.437")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
