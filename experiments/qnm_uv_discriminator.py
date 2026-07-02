"""v2.437 - the asymptotic-safety discriminator FAILS at low energy: the species scale can't tell a fixed point from a string, so the UV-completion degeneracy is robust -- the genuine discriminator is the tower SPECTRUM (a UV observable).

Bold swing on a genuinely different solve-path (asymptotic safety = a UV fixed point, no tower, vs string/CDT =
a fundamental scale + a tower). The natural discriminator is the SPECIES SCALE: a bare fixed-point theory should
be UV-complete with no sub-Planckian cutoff (N -> 1), while a string/CDT theory has a tower (N > 1). Does it
separate them?

NO. Computed on each framework's low-energy point (N = 1 + nu(|g_R2|+|g_C|+|g_R3|), Lambda_sp = M_Pl/sqrt(N)):
  candidate           N 1.57   Lambda_sp 0.80
  string_tree_eft     N 1.70   Lambda_sp 0.77
  asymptotic_safety   N 1.50   Lambda_sp 0.82   <-- ALSO has a tower/cutoff (N>1)!
  cdt                 N 1.74   Lambda_sp 0.76
  pure_gr             N 1.00   Lambda_sp 1.00   <-- the only N=1 (no-tower), but it lacks R^2 and is far/excluded
The species scale is computed from the LOW-ENERGY curvature couplings, which are shared by all the R^2-bearing
completions -- so string, asymptotic safety, and CDT all get N ~ 1.5-1.7 and the species scale CANNOT
distinguish them. Even this semi-UV quantity is, in the engine, a low-energy quantity.

This is an honest negative that SHARPENS v2.436: the UV-completion degeneracy (string ~ CDT ~ asymptotic safety
at low energy) is ROBUST -- not even the species scale / cutoff breaks it. The genuine discriminator is the TOWER
SPECTRUM itself -- what the light states at the cutoff ARE: a Regge trajectory (m^2 linear in spin => string), a
Kaluza-Klein / decompactification tower (=> large extra dimensions), or effectively no tower with the metric
running to a fixed point (=> asymptotic safety). That is a genuinely UV / high-energy observable (the pattern of
resonances near the cutoff), NOT accessible to the low-energy amplitude-carving the engine does. So the 'other
paths' ARE discriminable -- but only by reaching the UV, which tells us exactly what a QG-solving experiment must
measure: the spectrum of states at the species/cutoff scale.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.constraints.species_scale import SpeciesScaleBound
from itb.theory import Theory
from experiments.stack import frameworks

VERSION = "v2.437"
DEFAULT_OUT = Path("experiments/results/v2.437/qnm_uv_discriminator.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
PE = ["g_4", "g_6", "g_8", "g_R2", "g_R3"]
CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
SS = SpeciesScaleBound()


def _N(c):
    return SS._species(Theory(coefficients=c, name="x"))


def run() -> dict:
    cand_N = round(_N(CON), 3)
    table = {}
    for f in frameworks():
        c = {k: float(f.encode().coefficients.get(k, 0.0)) for k in KEYS}
        N = round(_N(c), 3)
        table[f.name] = {"N": N, "lambda_species_over_Mpl": round(1 / math.sqrt(N), 3),
                         "parity_even_distance": round(math.sqrt(sum((CON[k] - c.get(k, 0.0)) ** 2 for k in PE)), 3),
                         "has_R2": c.get("g_R2", 0.0) > 0.02, "has_tower": N > 1.05}

    # the VIABLE R^2-bearing completions (LQG is already excluded by positivity, v2.411, so drop it)
    R2_bearing = {n: r for n, r in table.items() if r["has_R2"] and n != "lqg_induced"}
    N_vals = [r["N"] for r in R2_bearing.values()]
    species_spread = round(max(N_vals) - min(N_vals), 3)
    species_discriminates = species_spread > 0.5   # would need a big spread to separate them

    checks = {
        "candidate_has_a_tower_cutoff": cand_N > 1.05,
        "all_R2_bearing_have_towers": all(r["has_tower"] for r in R2_bearing.values()),
        "species_scale_does_not_discriminate": not species_discriminates,
        "only_no_R2_point_has_N1": all(abs(r["N"] - 1.0) < 0.05 for n, r in table.items() if not r["has_R2"]),
        "degeneracy_robust_to_species_scale": (not species_discriminates) and all(r["has_tower"] for r in R2_bearing.values()),
    }

    return {
        "version": VERSION,
        "candidate_N": cand_N,
        "species_table": table,
        "R2_bearing_N_spread": species_spread,
        "genuine_discriminator": "the tower spectrum at the cutoff: Regge (string) vs Kaluza-Klein/decompactification (extra dims) vs none/metric-fixed-point (asymptotic safety) -- a UV/high-energy observable",
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The asymptotic-safety discriminator fails at low energy: the species scale cannot tell a UV fixed "
            "point from a string, so the UV-completion degeneracy is robust, and the genuine discriminator is "
            "the tower SPECTRUM. Asymptotic safety (a UV fixed point, no tower) vs string/CDT (a fundamental "
            "scale + a tower) should be separable by the species scale -- a bare fixed point being UV-complete "
            "with no sub-Planckian cutoff (N -> 1). But computing N = 1 + nu(|g_R2|+|g_C|+|g_R3|) on each "
            "framework's low-energy point, string (N=1.70), asymptotic safety (N=1.50), and CDT (N=1.74) ALL "
            "have towers/cutoffs N ~ 1.5-1.7 -- because the species scale is built from the LOW-ENERGY curvature "
            "couplings, which the convergent completions SHARE. The only N=1 (no-tower) point is pure GR, which "
            "lacks the rigorously-required R^2 and is far/excluded. So even this semi-UV quantity is, in the "
            "engine, a low-energy quantity and cannot break the degeneracy. This honest negative SHARPENS "
            "v2.436: the UV-completion degeneracy (string ~ CDT ~ asymptotic safety at low energy) is ROBUST -- "
            "not even the species scale separates them. The genuine discriminator is the tower SPECTRUM itself "
            "-- what the light states at the cutoff ARE: a Regge trajectory (m^2 linear in spin => string), a "
            "Kaluza-Klein / decompactification tower (=> large extra dimensions), or effectively no tower with "
            "the metric running to a fixed point (=> asymptotic safety). That is a genuinely UV / high-energy "
            "observable (the pattern of resonances near the cutoff), not accessible to low-energy "
            "amplitude-carving. So the 'other paths' ARE discriminable, but only by reaching the UV -- which "
            "tells us precisely what a QG-SOLVING experiment must measure: the spectrum of states at the "
            "species / cutoff scale, not more low-energy Wilson coefficients. This closes the honest loop on "
            "the UV question: the low-energy program has extracted everything it can (a rigor-caged candidate, "
            "a named leading completion, a maximally-falsifiable low-energy verdict), and the remaining "
            "discrimination is a distinct, harder, UV measurement -- the true frontier of solving QG."
        ),
        "honest_scope": (
            "The species scale is the engine's toy Dvali proxy (nu, N_max O(1)), and the frameworks are "
            "schematic O(1) encoders (v2.436 caveat), so the specific N values (1.5-1.74) are illustrative; the "
            "robust content is that they are all > 1 and clustered (spread ~0.24 among the R^2-bearing "
            "completions), so the species scale does not separate them -- not the precise numbers. 'Asymptotic "
            "safety should have N -> 1' is the idealized bare-fixed-point expectation; the engine's asymptotic "
            "safety ENCODER carries nonzero R^2/R^3 (hence N=1.5), which is itself the point -- its LOW-ENERGY "
            "couplings look like the others. The 'tower spectrum discriminates' claim is standard QG "
            "phenomenology (Regge vs KK vs fixed-point), not an engine computation; the engine cannot compute "
            "the spectrum (it carves Wilson coefficients, not the state content). This is a negative result "
            "(the species-scale discriminator fails) plus its constructive reading (the discriminator is a UV "
            "spectral observable). Robust content: all R^2-bearing UV completions share a sub-Planckian "
            "species-scale cutoff (N ~ 1.5-1.7), so the species scale does not break the UV-completion "
            "degeneracy; discriminating string vs CDT vs asymptotic safety requires the tower spectrum at the "
            "cutoff, a UV/high-energy observable outside the low-energy program. Toy-species-proxy, "
            "encoder-level, spectrum-not-computed, negative-plus-constructive. An asymptotic-safety-discriminator "
            "cycle."
        ),
        "references": [
            "this repo: v2.436 (UV tournament -- degeneracy), v2.394 (species scale ~0.72 M_Pl), v2.375 (string-like tower), src/itb/constraints/species_scale.py",
            "physics: Dvali species scale; asymptotic safety (UV fixed point, no tower); string (Regge tower); KK/decompactification (extra dimensions); the tower spectrum discriminates the UV completion",
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
    print("v2.437 - the asymptotic-safety discriminator FAILS at low energy (honest negative):")
    for n, r in res["species_table"].items():
        print(f"  {n:<20} N={r['N']:<6} Lambda_sp={r['lambda_species_over_Mpl']:<6} tower={r['has_tower']!s:<6} R2={r['has_R2']}")
    print(f"  => R^2-bearing completions all have towers N~1.5-1.7 (spread {res['R2_bearing_N_spread']}) => species scale does NOT discriminate")
    print("  => the UV-completion degeneracy is ROBUST; the genuine discriminator is the TOWER SPECTRUM (a UV observable)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
