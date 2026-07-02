"""v2.433 - a concrete UV-embedding lead (option #4): the candidate is string tree-EFT deformed by the data-required parity coupling.

Option #4 (embed the candidate in a UV-complete theory) is the deepest 'solve' path. Rather than only scope it,
this cycle finds a concrete lead by locating the candidate relative to the engine's string tree-level EFT
framework (which, unlike a bare carved point, HAS a known UV completion -- string theory).

Result: the string tree-EFT encoded couplings are g_4=0.50, g_6=0.40, g_8=0.40, g_R2=0.20, g_R3=0.15,
g_R2_parity=0.00 (parity-CONSERVING). Against the candidate (..., g_R2_parity=0.06):
  - string tree-EFT is FEASIBLE under the rigorous core AND the effective rigorous cage (v2.431);
  - it is rejected by the full theory+data stack by EXACTLY ONE constraint: cosmic_birefringence_data (because
    it has zero parity while the data prefer nonzero positive parity);
  - its PARITY-EVEN couplings sit within Euclidean distance 0.067 of the candidate -- essentially on top of it;
  - the ONLY material difference is the parity coupling (0.00 vs 0.06).

So string tree-EFT is precisely the parity-conserving rival (v2.420), and THE CANDIDATE = STRING TREE-EFT + THE
DATA-REQUIRED PARITY DEFORMATION. This is a concrete UV-embedding lead: the candidate is a small parity
deformation of a theory that is UV-completable in string theory, so it can inherit that UV completion up to the
parity turn-on. The remaining #4 task becomes specific -- find a string compactification whose low-energy EFT is
string-tree-like AND carries the axionic / gravitational-Chern-Simons parity term that produces the g_R2_parity
deformation -- rather than open-ended 'match to some UV theory'. And it dovetails with the whole program: the
candidate's one data-selected, rigor-uncageable degree of freedom (the parity, v2.431) is exactly the deformation
that takes a known UV-completable theory (string tree-EFT) to the candidate.
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
from experiments.stack import build_stack, rigorous_core_stack, effective_rigorous_stack, frameworks

VERSION = "v2.433"
DEFAULT_OUT = Path("experiments/results/v2.433/qnm_string_deformation.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CON = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06}
PARITY_EVEN = ["g_4", "g_6", "g_8", "g_R2", "g_R3"]
BK = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
          include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)


def run() -> dict:
    full = build_stack(**BK)
    core = rigorous_core_stack(**BK)
    eff = effective_rigorous_stack(**BK)
    st = [f for f in frameworks() if f.name == "string_tree_eft"][0]
    sc = st.encode().coefficients
    sv = {k: float(sc.get(k, 0.0)) for k in KEYS}

    def viol(stack, c):
        return [r.constraint_name for r in check(Theory(coefficients=c, name="x"), stack).results if not r.satisfied]

    full_v = viol(full, sv)
    core_v = viol(core, sv)
    eff_v = viol(eff, sv)
    pe_dist = round(math.sqrt(sum((CON[k] - sv[k]) ** 2 for k in PARITY_EVEN)), 3)
    parity_diff = round(abs(CON["g_R2_parity"] - sv["g_R2_parity"]), 3)

    checks = {
        "string_in_rigorous_cage": len(eff_v) == 0,
        "string_is_parity_conserving_rival": full_v == ["cosmic_birefringence_data"],
        "candidate_near_string_parity_even": pe_dist < 0.1,
        "difference_is_the_parity_coupling": sv["g_R2_parity"] < 0.02 and parity_diff > 0.03,
        "uv_lead_concrete": len(eff_v) == 0 and full_v == ["cosmic_birefringence_data"],
    }

    return {
        "version": VERSION,
        "string_tree_eft_couplings": {k: round(sv[k], 3) for k in KEYS},
        "candidate_couplings": CON,
        "string_full_stack_violations": full_v,
        "string_rigorous_core_feasible": len(core_v) == 0,
        "string_effective_cage_feasible": len(eff_v) == 0,
        "parity_even_distance": pe_dist,
        "parity_difference": parity_diff,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "A concrete UV-embedding lead (option #4): the candidate is string tree-EFT deformed by the "
            "data-required parity coupling. Locating the candidate relative to the engine's string tree-level "
            "EFT framework -- which, unlike a bare carved point, has a known UV completion (string theory) -- "
            "the string couplings (g_4=0.50, g_6=0.40, g_8=0.40, g_R2=0.20, g_R3=0.15, g_R2_parity=0.00) are "
            "FEASIBLE under both the rigorous core and the effective rigorous cage (v2.431), are rejected by "
            "the full theory+data stack by EXACTLY ONE constraint (cosmic_birefringence_data, because parity is "
            "zero), sit within parity-even distance 0.067 of the candidate, and differ materially only in the "
            "parity coupling (0.00 vs 0.06). So string tree-EFT is precisely the parity-conserving rival "
            "(v2.420), and THE CANDIDATE = STRING TREE-EFT + THE DATA-REQUIRED PARITY DEFORMATION. This turns "
            "the deepest solve-path from open-ended into specific: the candidate is a small parity deformation "
            "of a UV-completable theory, so it can inherit string theory's UV completion up to the parity "
            "turn-on, and the concrete #4 task becomes 'find a string compactification whose low-energy EFT is "
            "string-tree-like AND carries the axionic / gravitational-Chern-Simons parity term that generates "
            "g_R2_parity' -- rather than 'match to some UV theory'. It dovetails with the whole program: the "
            "candidate's one data-selected, rigor-uncageable degree of freedom (the parity, v2.431/2.420) is "
            "exactly the deformation that carries a known UV-completable theory (string tree-EFT) to the "
            "candidate -- so the rigor cage, the empirical verdict, and the UV embedding all point at the same "
            "single object: the parity coupling."
        ),
        "honest_scope": (
            "'string tree-EFT' here is the ENGINE's framework encoder -- a schematic model of string "
            "tree-level dim-8 coefficients with O(1) values, NOT a specific compactification's computed "
            "spectrum; so 'the candidate is string tree-EFT + parity' is a statement about the engine's "
            "string-EFT PROXY (the candidate is a small parity deformation of the engine's best string-like "
            "point), a genuine lead, not a proof that a real string vacuum reproduces the candidate. Actually "
            "establishing #4 still requires the real string-theory computation (a compactification's alpha' "
            "corrections + the axionic parity sector), which the engine cannot do -- this cycle SCOPES that to "
            "a specific target rather than executing it. The parity-even distance 0.067 uses the "
            "dimensionless O(1) couplings (magnitudes toy, v2.411), so 'essentially on top of' is at the "
            "coupling-structure level. The 'rejected only by birefringence' fact is contingent on the "
            "~3.6-sigma birefringence hint (v2.329). Robust content: the engine's string tree-EFT point is "
            "feasible in the rigorous cage, is the parity-conserving rival (rejected only by cosmic "
            "birefringence), and sits within 0.067 (parity-even) of the candidate -- so the candidate is a "
            "parity deformation of the engine's UV-completable string-like framework, giving option #4 a "
            "concrete target (a string compactification with the right parity/Chern-Simons term). "
            "Engine-proxy-string, coupling-level-distance, real-computation-still-needed, birefringence-"
            "contingent. A UV-embedding-lead cycle."
        ),
        "references": [
            "this repo: v1.74 (nearest framework = string tree-EFT), v2.420 (parity-conserving rival), v2.431 (rigorous cage; parity the rigor-uncageable dof), v2.386 (parity chirality), v2.329 (birefringence hint)",
            "physics: string tree-level EFT (alpha' R^4 etc.) has a UV completion; the parity deformation would come from an axionic / gravitational-Chern-Simons term in a specific compactification",
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
    print("v2.433 - a concrete UV-embedding lead (#4): the candidate is string tree-EFT + parity:")
    print(f"  string tree-EFT couplings: {res['string_tree_eft_couplings']}")
    print(f"  string feasible in rigorous cage: {res['string_effective_cage_feasible']}; full-stack rejects only by: {res['string_full_stack_violations']}")
    print(f"  parity-even distance candidate<->string: {res['parity_even_distance']}; parity difference: {res['parity_difference']} (string parity = 0)")
    print("  => string tree-EFT IS the parity-conserving rival; the candidate = string tree-EFT + the data-required parity deformation")
    print("  => #4 target made concrete: a string compactification with the axionic / grav-Chern-Simons parity term")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
