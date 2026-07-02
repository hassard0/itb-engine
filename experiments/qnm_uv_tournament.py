"""v2.436 - other paths to solve: the candidate is a UV-convergence point (string, CDT, asymptotic safety all viable), NOT string-unique -- honestly tempering the v2.434 heterotic call.

The user asked to consider OTHER paths. The whole program (and the v2.433-435 arc) assumed the amplitude-carving
line converges on STRING (heterotic). This cycle runs the full UV-completion tournament: for every framework the
engine encodes, where it sits relative to the candidate's rigorous cage, and whether a parity deformation carries
it to the candidate (as it did for heterotic in v2.433).

Result (parity-even distance to the candidate; 'reaches' = in the rigorous cage AND separated from the candidate
only by cosmic birefringence, i.e. a parity-conserving version of the candidate):
  string_tree_eft    dist 0.067  R2 yes  REACHES   (closest)
  cdt                dist 0.085  R2 yes  REACHES   (near-tie second)
  asymptotic_safety  dist 0.196  R2 yes  REACHES   (competitive)
  pure_gr            dist 0.803  R2 no   REACHES-but-far (no R^2, far from the candidate)
  lqg_induced        --          R2 yes  EXCLUDED  (violates graviton positivity + CFT bootstrap)

So the candidate is NOT string-unique. FOUR paradigms sit in the rigorous cage and are reachable by a parity
deformation; only LQG is rigorously excluded. Among the R^2-bearing ones (which the candidate rigorously
requires, v2.434), string is closest (0.067) but CDT is a near-tie (0.085) and asymptotic safety is genuinely
competitive (0.196). The candidate is a CONVERGENCE POINT of multiple UV completions, and the low-energy EFT the
engine carves CANNOT discriminate string vs CDT vs asymptotic safety -- that needs genuinely UV/quantum-gravity
data (the actual UV behaviour: does gravity hit a string tower, a discrete-spacetime continuum limit, or a UV
fixed point?). This is a genuine broadening -- there ARE other viable solve-paths (CDT and asymptotic safety, not
only string) -- and an honest correction to v2.434: heterotic is the CLOSEST and best-motivated (its
model-independent axion gives the cleanest parity story), but it is NOT the unique UV completion; the bold
'it is heterotic' should read 'heterotic is the leading candidate UV completion among several the low-energy data
cannot yet separate'.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, effective_rigorous_stack, frameworks

VERSION = "v2.436"
DEFAULT_OUT = Path("experiments/results/v2.436/qnm_uv_tournament.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
PE = ["g_4", "g_6", "g_8", "g_R2", "g_R3"]
CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
BK = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
          include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def run() -> dict:
    full = build_stack(**BK)
    eff = effective_rigorous_stack(**BK)

    def viol(st, c):
        return [r.constraint_name for r in check(Theory(coefficients=c, name="x"), st).results if not r.satisfied]

    table = {}
    for f in frameworks():
        c = {k: float(f.encode().coefficients.get(k, 0.0)) for k in KEYS}
        in_cage = len(viol(eff, c)) == 0
        fv = viol(full, c)
        pe = round(math.sqrt(sum((CON[k] - c.get(k, 0.0)) ** 2 for k in PE)), 3)
        has_R2 = c.get("g_R2", 0.0) > 0.02
        reaches = in_cage and (fv == ["cosmic_birefringence_data"] or len(fv) == 0)
        table[f.name] = {"in_rigorous_cage": in_cage, "full_stack_violations": fv[:3],
                         "parity_even_distance": pe, "has_R2": has_R2, "reaches_candidate": reaches}

    reachers = sorted([n for n, r in table.items() if r["reaches_candidate"]],
                      key=lambda n: table[n]["parity_even_distance"])
    excluded = [n for n, r in table.items() if not r["in_rigorous_cage"]]
    R2_reachers = [n for n in reachers if table[n]["has_R2"]]

    checks = {
        "multiple_UV_completions_reach": len(reachers) >= 3,
        "only_lqg_excluded": excluded == ["lqg_induced"],
        "string_closest": reachers and reachers[0] == "string_tree_eft",
        "cdt_and_AS_competitive": ("cdt" in R2_reachers and "asymptotic_safety" in R2_reachers),
        "candidate_not_string_unique": len(R2_reachers) >= 3,
    }

    return {
        "version": VERSION,
        "tournament": table,
        "reachers_ranked_by_distance": [(n, table[n]["parity_even_distance"]) for n in reachers],
        "R2_bearing_reachers": R2_reachers,
        "excluded": excluded,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Other paths exist: the candidate is a UV-convergence point (string, CDT, asymptotic safety all "
            "viable), NOT string-unique -- an honest broadening and a correction to the v2.434 heterotic call. "
            "Running the full UV-completion tournament -- each framework's low-energy point vs the candidate's "
            "rigorous cage, and whether a parity deformation reaches the candidate (as for heterotic in v2.433) "
            "-- FOUR paradigms sit in the rigorous cage and are reachable (each separated from the candidate "
            "only by cosmic birefringence, i.e. a parity-conserving version of it): string tree-EFT (parity-"
            "even distance 0.067, closest), CDT (0.085, a near-tie), asymptotic safety (0.196, competitive), "
            "and pure GR (0.803, far, and lacking the rigorously-required R^2). Only LQG-induced gravity is "
            "rigorously EXCLUDED (it violates graviton positivity + the CFT bootstrap). So among the R^2-bearing "
            "UV completions the candidate requires, string is closest and best-motivated (its model-independent "
            "axion gives the cleanest parity story, v2.434-435), but CDT and asymptotic safety are genuinely "
            "competitive alternatives that the LOW-ENERGY EFT the engine carves CANNOT rule out. The candidate "
            "is a convergence point of multiple UV completions, and discriminating string vs CDT vs asymptotic "
            "safety needs genuinely UV / quantum-gravity data -- the actual UV behaviour (a string tower, a "
            "discrete-spacetime continuum limit, or a UV fixed point) -- which the amplitude-carving of a "
            "low-energy EFT does not access. This is the honest broadening the user asked for: there are OTHER "
            "viable solve-paths (CDT and asymptotic safety, not only string), and the bold 'it is heterotic' "
            "(v2.434) must be tempered to 'heterotic/string is the LEADING candidate UV completion among "
            "several the low-energy data cannot yet separate'. It also sharpens what a genuine QG-solving "
            "measurement must do: not just confirm the candidate (the correlated 2030 signature, v2.430) but "
            "REACH the UV to discriminate the completions -- a distinct, harder observational target than the "
            "low-energy fronts."
        ),
        "honest_scope": (
            "The frameworks are the ENGINE's schematic O(1) encoders of each paradigm's low-energy dim-8 "
            "coefficients, not computed spectra -- so 'CDT reaches the candidate' means the engine's CDT-encoder "
            "point is in the cage and parity-deformation-close, a structural statement about the encoders, not "
            "a proof that a real CDT continuum limit yields the candidate (same caveat as the string "
            "identification, v2.433). Parity-even distance uses the dimensionless O(1) couplings (magnitudes "
            "toy). 'Reaches' requires the framework to be the parity-conserving rival (rejected only by "
            "birefringence) OR already feasible; it is a low-energy-EFT statement and cannot see UV differences. "
            "The ranking (string 0.067 < CDT 0.085 < AS 0.196) is at the encoder level; the string-vs-CDT gap "
            "is small and within the O(1) encoder uncertainty, which is exactly why 'not string-unique' is the "
            "honest reading. This TEMPERS but does not overturn v2.434: heterotic remains the best-motivated "
            "(the axion), and 'not type II' stands (pure-GR's no-R^2 point is far). Robust content: multiple "
            "R^2-bearing UV paradigms (string, CDT, asymptotic safety) sit in the candidate's rigorous cage and "
            "are parity-deformation-reachable, only LQG is excluded, so the candidate is not string-unique and "
            "the low-energy EFT cannot discriminate the UV completion -- other viable solve-paths exist. "
            "Encoder-level, toy-distances, low-energy-cannot-see-UV, tempers-not-overturns. A UV-tournament "
            "broadening cycle."
        ),
        "references": [
            "this repo: v2.434 (heterotic identification -- tempered here), v2.433 (string tree-EFT + parity), v2.431 (rigorous cage), v2.411 (LQG excluded / framework sweep), v2.322 (no framework fits theory+data), v1.89 (framework phylogeny)",
            "physics: string (tower), CDT (discrete-spacetime continuum limit), asymptotic safety (UV fixed point) are distinct UV completions; a low-energy EFT is UV-completion-agnostic among those consistent with it",
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
    print("v2.436 - UV-completion tournament (OTHER paths): the candidate is NOT string-unique")
    for n, r in res["tournament"].items():
        tag = "EXCLUDED" if not r["in_rigorous_cage"] else ("reaches" if r["reaches_candidate"] else "in-cage")
        print(f"  {n:<20} dist={r['parity_even_distance']:<7} R2={r['has_R2']!s:<6} {tag}")
    print(f"  => R^2-bearing UV completions reaching the candidate: {res['R2_bearing_reachers']} (string closest, CDT near-tie, AS competitive)")
    print(f"  => only excluded: {res['excluded']}; low-energy EFT cannot discriminate string vs CDT vs AS -> OTHER viable solve-paths exist")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
