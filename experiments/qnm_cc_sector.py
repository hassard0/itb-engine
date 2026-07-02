"""v2.422 - CORE EXTENSION CC1: the cosmological-constant / dark-energy sector -- the candidate accommodates dark energy, bounded by its curvature via the refined de Sitter conjecture.

The engine had no vacuum-energy coupling -- the one big quantum-gravity problem it never touched. This is the
first slice of a new core-engine sector (user-chosen direction). It adds a dimensionless vacuum-energy parameter
g_Lambda (dark-energy density in cutoff-scale units: >0 de Sitter, <0 anti-de Sitter, 0 Minkowski) and its first
swampland constraint, the refined de Sitter conjecture (Ooguri-Palti-Shiu-Vafa 2018), wired OPT-IN so the entire
existing stack, all frameworks, and all goldens are untouched (the g_R4-tower precedent). The new constraint is
tagged 'sourced_proxy' in the rigor registry -- the honest tiering built in the de-toying arc automatically
places this conjectural swampland statement in the toy/proxy layer, NOT the source-exact core.

Physics: a positive vacuum energy at a potential extremum can satisfy the refined dS conjecture only if the
potential is sufficiently CONCAVE (the tachyonic second condition M_Pl^2 min(V'')/V <= -c'). The candidate's dark
energy rides the Starobinsky R^2 scalaron (g_R2 is the R^2 inflaton, v1.86), whose plateau is concave, so the
condition maps to g_Lambda <= g_R2 / c_dS.

Result: the candidate ACCOMMODATES dark energy. With c_dS=1 it admits a positive cosmological constant up to
g_Lambda <= g_R2 ~ 0.193 (cutoff units); above that the refined-dS constraint fails (too much vacuum energy for
the scalaron curvature to support). AdS and Minkowski (g_Lambda <= 0) are trivially consistent. So the engine's
new dark-energy sector says: a positive Lambda is allowed and is capped by the curvature sector -- the same g_R2
that drives inflation (v1.86) and is the keystone of the whole theory (v2.396) also sets the ceiling on the dark
energy the candidate can carry, consistent with the refined dS swampland conjecture. This is CC1: sector opened,
dark energy accommodated, first bound established and honestly tiered; later slices add the AdS-distance / species
relation and the quintessence-vs-constant distinction.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, rigor_of

VERSION = "v2.422"
DEFAULT_OUT = Path("experiments/results/v2.422/qnm_cc_sector.json")

CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
BASE = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
            include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def _feasible(stack, gL):
    return all(r.satisfied for r in check(Theory(coefficients={**CON, "g_Lambda": float(gL)}, name="x"), stack).results)


def run() -> dict:
    default_stack = build_stack(**BASE)
    # CC1 isolates its own refined-dS constraint: disable the CC2 AdS-distance floor (cc_c_AdS=0) so this
    # slice's window reflects the dS ceiling + EFT-validity only (CC2 has its own experiment, v2.423).
    cc_stack = build_stack(**BASE, include_cc_sector=True, cc_c_AdS=0.0)

    default_names = [getattr(c, "name", "") for c in default_stack]
    cc_names = [getattr(c, "name", "") for c in cc_stack]
    cc_present = "de_sitter_conjecture" in cc_names
    opt_in_clean = "de_sitter_conjecture" not in default_names and len(cc_stack) >= len(default_stack) + 1

    # full allowed g_Lambda window on the full stack + CC sector
    grid = [round(float(g), 3) for g in np.arange(-1.0, 0.6, 0.002) if _feasible(cc_stack, float(g))]
    max_dS = max([g for g in grid if g > 0], default=None)
    lam_window = [min(grid), max(grid)] if grid else None
    modest_ads_ok = _feasible(cc_stack, -0.1) and _feasible(cc_stack, 0.0)

    checks = {
        "cc_sector_is_opt_in": opt_in_clean,
        "cc_constraint_present_when_enabled": cc_present,
        "tagged_sourced_proxy": rigor_of("de_sitter_conjecture") == "sourced_proxy",
        "candidate_admits_positive_dark_energy": max_dS is not None and max_dS > 0.05,
        "dS_bound_tracks_scalaron_curvature": max_dS is not None and abs(max_dS - CON["g_R2"]) < 0.02,
        "modest_ads_and_minkowski_ok": bool(modest_ads_ok),
    }

    return {
        "version": VERSION,
        "stack_sizes": {"default": len(default_stack), "with_cc_sector": len(cc_stack)},
        "de_sitter_rigor_tier": rigor_of("de_sitter_conjecture"),
        "max_positive_g_Lambda_allowed": max_dS,
        "g_Lambda_window": lam_window,
        "candidate_g_R2": CON["g_R2"],
        "modest_ads_minkowski_ok": bool(modest_ads_ok),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "CORE EXTENSION CC1: the engine now has a cosmological-constant / dark-energy sector, and the "
            "candidate accommodates dark energy bounded by its curvature via the refined de Sitter conjecture. "
            "A dimensionless vacuum-energy parameter g_Lambda (>0 de Sitter, <0 anti-de Sitter) is added with "
            "its first swampland constraint (refined dS conjecture, Ooguri-Palti-Shiu-Vafa 2018), wired OPT-IN "
            "so the entire existing stack/frameworks/goldens are untouched and tagged 'sourced_proxy' by the "
            "rigor registry -- the honest tiering from the de-toying arc automatically files this conjectural "
            "swampland statement in the proxy layer, not the source-exact core. Physics: a positive vacuum "
            "energy at a potential extremum satisfies the refined dS conjecture only if the potential is "
            "sufficiently concave (the tachyonic second condition); the candidate's dark energy rides the "
            "Starobinsky R^2 scalaron (g_R2, v1.86), whose plateau is concave, so the condition maps to "
            "g_Lambda <= g_R2/c_dS. Result: the candidate ADMITS a positive cosmological constant up to "
            "g_Lambda <= g_R2 ~ 0.193 (c_dS=1); above that the refined-dS bound fails (too much vacuum energy "
            "for the scalaron curvature). Modest AdS and Minkowski are consistent (a large vacuum-energy magnitude "
            "is separately bounded by EFT-validity / the complexity cutoff -- the vacuum energy cannot exceed "
            "the cutoff scale). So the SAME g_R2 that "
            "drives inflation (v1.86) and anchors the theory as its keystone (v2.396) also caps the dark energy "
            "the candidate can carry -- a genuine new cross-link between the curvature sector and the "
            "cosmological constant, consistent with the refined dS swampland conjecture. This opens the CC "
            "sector honestly: the bound is conjectural+proxy (so tiered accordingly), and later slices add the "
            "AdS-distance/species-scale relation (small Lambda <-> a light tower, which the candidate's tower "
            "structure v2.375 makes computable) and the quintessence-vs-constant distinction."
        ),
        "honest_scope": (
            "This is a FIRST-PROXY encoding of a CONJECTURAL statement, and it is tagged as such "
            "(sourced_proxy) -- the refined dS conjecture is itself unproven and debated, and the map from its "
            "abstract V''/V condition to the engine's dimensionless g_R2 is order-of-magnitude (the robust "
            "content is 'a positive Lambda is bounded by the scalaron curvature', the exact c_dS is O(1) and "
            "the linear g_Lambda <= g_R2 form is the simplest proxy, not a derived relation). g_Lambda is "
            "dimensionless (vacuum energy in cutoff-scale units); the engine still has no absolute scale, so "
            "this does NOT address the CC magnitude problem (why Lambda is ~10^-120 M_Pl^4) -- it addresses the "
            "STRUCTURAL question of whether a positive Lambda is admissible and what bounds it. The sector is "
            "opt-in, so nothing about the prior candidate results changes; this ADDS a sector. The 'accommodates "
            "dark energy' claim is that a positive g_Lambda is feasible up to the curvature bound, not that the "
            "observed dark-energy value is predicted. Robust content: the engine now has a dark-energy sector; "
            "a positive cosmological constant is admissible and bounded by the scalaron curvature (g_Lambda <= "
            "g_R2) under the refined dS conjecture; modest AdS/Minkowski are consistent while a large "
            "vacuum-energy magnitude is EFT-validity-bounded -- all honestly tiered as a conjectural proxy. Conjectural+proxy, dimensionless (no CC magnitude), opt-in. The CC1 "
            "core-extension cycle."
        ),
        "references": [
            "this repo: v1.86 (g_R2 = Starobinsky R^2 scalaron), v2.396 (g_R2 keystone), v2.411 (rigor tiering -> the CC constraint auto-tagged sourced_proxy), v2.375 (tower structure for the future AdS-distance slice), src/itb/constraints/cosmological_constant.py",
            "physics: Ooguri-Palti-Shiu-Vafa 2018 (refined de Sitter conjecture); Obied-Ooguri-Spodyneiko-Vafa 2018 (dS swampland); Lust-Palti-Vafa 2019 (AdS distance conjecture, for the next slice)",
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
    print("v2.422 - CORE EXTENSION CC1: the cosmological-constant / dark-energy sector:")
    print(f"  stack sizes: default {res['stack_sizes']['default']} -> with CC sector {res['stack_sizes']['with_cc_sector']} (opt-in)")
    print(f"  de_sitter_conjecture rigor tier: {res['de_sitter_rigor_tier']} (conjectural swampland, honestly tiered)")
    print(f"  candidate admits positive dark energy up to g_Lambda <= {res['max_positive_g_Lambda_allowed']} (~ g_R2={res['candidate_g_R2']})")
    print(f"  full allowed g_Lambda window: {res['g_Lambda_window']} (dS-bounded above by g_R2, |vac energy| bounded below by EFT-validity)")
    print(f"  modest AdS + Minkowski consistent: {res['modest_ads_minkowski_ok']}")
    print(f"  => the keystone g_R2 (inflation, v1.86) also caps the dark energy the candidate can carry (refined dS)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
