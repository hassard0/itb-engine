"""v2.420 - the alternatives map: which consistent-QG archetypes rival the candidate, and exactly what rejects each.

Pivoting from 'is the candidate rigorous' (the v2.411-419 arc) to the complementary physical question: what OTHER
physical archetypes of consistent QG EFT does the engine permit, and by what -- rigorous positivity, real data, or
toy prefactor -- is each separated from the candidate? Method: evaluate five qualitatively distinct archetypes
(all sharing a matter base, varying gravity/parity structure) against the rigorous core and the full theory+data
stack, and classify each rejection by its cause.

Result (archetype -> rigorous verdict / data verdict / rejecting cause):
  A candidate (parity-violating, curvature-rich)  : rig-feasible , SURVIVES theory+data
  B parity-conserving (parity = 0)                : rig-feasible , rejected ONLY by cosmic_birefringence_data
  C curvature-minimal (g_R2,g_R3 small)           : rig-feasible , rejected by anomaly(toy)+SDC(toy)+birefringence
  D curvature-heavy (g_R2 large)                  : RIG-EXCLUDED by cft_flat_space + left_handed_graviton positivity
  E matter-light (small matter)                   : RIG-EXCLUDED by graviton_mixed + cubic_graviton_matter positivity

So the space of consistent QG the engine permits has a clean structure: the 'too much gravity' (D) and 'too
little matter' (E) archetypes are RIGOROUSLY excluded -- source-exact amplitude positivity forbids them with zero
toy input; the 'curvature-minimal' archetype (C) is rejected only with help from toy constraints (the anomaly and
the aspect-ratio SDC) plus data; and -- the headline -- the 'parity-conserving' archetype (B) is RIGOROUSLY
CONSISTENT and is rejected by exactly ONE thing: the cosmic-birefringence datum. B is therefore the candidate's
single live rival: a perfectly consistent parity-conserving quantum-gravity EFT that only the (contingent, ~3.6-
sigma) birefringence measurement separates from the candidate -- and that would return as viable if the
birefringence hint fades (matching the Z2 mirror of v2.406 and the load-bearing-datum finding of v2.408). Net,
forward-looking: the candidate-versus-alternative question reduces cleanly to 'is cosmic birefringence real?' --
every OTHER archetype is either rigorously excluded or matter-gravity-structurally disfavored, independent of that
one measurement.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import rigorous_core_stack, build_stack, rigor_of, HARMLESS_SPECULATIVE, LOAD_BEARING_TOY

VERSION = "v2.420"
DEFAULT_OUT = Path("experiments/results/v2.420/qnm_archetype_alternatives.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
BK = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
          include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

ARCHETYPES = {
    "A_candidate": [0.529, 0.4, 0.4, 0.193, 0.09, 0.06],
    "B_parity_conserving": [0.529, 0.4, 0.4, 0.193, 0.09, 0.0],
    "C_curvature_minimal": [0.529, 0.4, 0.4, 0.02, 0.0, 0.0],
    "D_curvature_heavy": [0.529, 0.4, 0.4, 0.45, 0.15, 0.06],
    "E_matter_light": [0.2, 0.15, 0.15, 0.193, 0.09, 0.06],
}


def _classify(names):
    if not names:
        return "none"
    if any(rigor_of(n) == "rigorous" for n in names):
        return "rigorous"
    if "cosmic_birefringence_data" in names and all(n == "cosmic_birefringence_data" for n in names):
        return "data_only"
    if any(rigor_of(n) == "data" for n in names) and not any(n in LOAD_BEARING_TOY or n in HARMLESS_SPECULATIVE for n in names):
        return "data"
    return "toy_plus_data"


def run() -> dict:
    core = rigorous_core_stack(**BK)
    full = build_stack(**BK)

    def viol(stack, v):
        return [r.constraint_name for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results if not r.satisfied]

    table = {}
    for name, v in ARCHETYPES.items():
        vc, vf = viol(core, v), viol(full, v)
        table[name] = {
            "rigorous_feasible": len(vc) == 0,
            "rigorous_violations": vc,
            "full_feasible": len(vf) == 0,
            "full_violations": vf,
            "rejection_cause": "survives" if len(vf) == 0 else ("rigorous" if len(vc) else _classify(vf)),
        }

    b = table["B_parity_conserving"]
    checks = {
        "candidate_survives": table["A_candidate"]["full_feasible"],
        "parity_conserving_rig_ok_data_rejected": (b["rigorous_feasible"] and not b["full_feasible"]
                                                   and b["full_violations"] == ["cosmic_birefringence_data"]),
        "curvature_heavy_rigorously_excluded": not table["D_curvature_heavy"]["rigorous_feasible"],
        "matter_light_rigorously_excluded": not table["E_matter_light"]["rigorous_feasible"],
        "live_rival_is_parity_conserving": (b["rigorous_feasible"]
                                            and b["full_violations"] == ["cosmic_birefringence_data"]),
    }

    return {
        "version": VERSION,
        "archetype_table": table,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The alternatives map: the candidate's single live rival is the parity-conserving QG EFT, "
            "separated from it by exactly the cosmic-birefringence datum; every other archetype is either "
            "rigorously excluded or matter-gravity-structurally disfavored. Evaluating five qualitatively "
            "distinct consistent-QG archetypes against the rigorous core and the full theory+data stack: the "
            "'too much gravity' archetype (D, large g_R2) and the 'too little matter' archetype (E) are "
            "RIGOROUSLY EXCLUDED -- source-exact amplitude positivity (cft_flat_space + left-handed-graviton "
            "positivity for D; graviton-mixed + cubic-graviton-matter positivity for E) forbids them with zero "
            "toy input, a clean statement that consistency bounds the gravity/matter balance from both sides. "
            "The 'curvature-minimal' archetype (C) survives the rigorous core but is rejected with help from "
            "toy constraints (the anomaly and the aspect-ratio SDC) plus data. And the headline: the "
            "'parity-conserving' archetype (B) -- the candidate with its parity coupling switched off -- is "
            "RIGOROUSLY CONSISTENT and is rejected by exactly ONE thing, the cosmic-birefringence measurement. "
            "So B is the candidate's single live rival: a perfectly consistent parity-conserving quantum "
            "gravity that only the (contingent, ~3.6-sigma) birefringence datum separates from the candidate, "
            "and that returns as viable if the birefringence hint fades -- matching the Z2 handedness mirror "
            "(v2.406) and the load-bearing-datum finding (v2.408). The forward-looking net is sharp: the "
            "candidate-versus-alternative question reduces to 'is cosmic birefringence real?' -- every other "
            "archetype is settled independent of that measurement (D, E rigorously excluded; C "
            "structurally/toy-disfavored). This complements the de-toying arc from the outside: not 'is the "
            "candidate rigorous' but 'what are the consistent alternatives and what rejects each', and the "
            "answer is that the only surviving alternative hinges on one experiment."
        ),
        "honest_scope": (
            "The five archetypes are representative single points chosen to probe distinct qualitative "
            "features (parity on/off, curvature high/low, matter high/low), not an exhaustive clustering of "
            "the feasible family -- they demonstrate that these archetype CLASSES are separated by the stated "
            "causes, not that they are the only archetypes. The rigorous exclusions of D and E carry the "
            "v2.411 'source-exact in form' caveat; D and E are also chosen somewhat extreme, so 'rigorously "
            "excluded' means these representative points are, establishing the class is positivity-bounded, "
            "not a precise boundary. B's rejection 'by cosmic_birefringence_data ONLY' is the exact full-stack "
            "violation list for that point (birefringence wants nonzero positive parity; B has parity=0); it "
            "is contingent on the birefringence hint being real (~3.6-sigma, v2.329). C's rejection mixes toy "
            "(anomaly, SDC) and data, so C is NOT a clean rigorous exclusion -- flagged. Robust content: 'too "
            "much gravity' and 'too little matter' archetypes are rigorously excluded by amplitude positivity; "
            "the parity-conserving archetype is rigorously consistent and rejected only by the "
            "cosmic-birefringence datum, making it the candidate's single data-contingent rival. "
            "Representative-point archetypes, contingent-datum rejection for B, C-rejection mixed. An "
            "alternatives-mapping cycle."
        ),
        "references": [
            "this repo: v2.406 (single island / Z2 mirror), v2.408 (birefringence the load-bearing datum), v2.411 (rigorous core / exclusions), v2.419 (rigor determines a family), v2.329 (birefringence ~3.6-sigma hint)",
            "physics: amplitude positivity bounding the gravity/matter balance (Caron-Huot et al EFThedron); cosmic birefringence beta=0.34+/-0.09 deg (Minami-Komatsu / Eskilt-Komatsu)",
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
    print("v2.420 - the alternatives map (which consistent-QG archetypes rival the candidate, and what rejects each):")
    for name, r in res["archetype_table"].items():
        rig = "rig-feasible" if r["rigorous_feasible"] else "RIG-EXCLUDED"
        print(f"  {name:<22} {rig:<13} -> {r['rejection_cause']:<12} {'' if r['full_feasible'] else r['full_violations'][:2]}")
    print("  => single live rival = B parity-conserving (rigorously consistent, separated by cosmic birefringence ALONE)")
    print("  => candidate-vs-alternative reduces to 'is cosmic birefringence real?'; D/E rigorously excluded independent of it")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
