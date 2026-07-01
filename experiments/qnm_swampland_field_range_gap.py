"""v2.410 - SWING (honest negative / engine limitation): the candidate's Starobinsky inflation faces the field-range swampland tension the engine's SDC cannot see.

A self-critical big swing: stress-test the candidate for an INTERNAL inconsistency between two things it claims
at once. (1) It satisfies the engine's Swampland Distance Conjecture (v2.383, in Wilson-coefficient form). (2)
Its keystone curvature coupling g_R2 is the Starobinsky R^2 inflaton (early v1.86). But Starobinsky inflation
requires a SUPER-PLANCKIAN field excursion, and the REAL (field-space) swampland distance conjecture disfavors
that -- so does the candidate thread the needle, or does it inherit the well-known large-field-inflation-vs-
swampland tension?

Result: it inherits the tension, and the engine cannot see it. Starobinsky inflation over N~55 e-folds needs
Delta_phi ~ 5.3 M_Pl. The physical SDC then predicts a tower of states at m ~ M_Pl exp(-c*Delta_phi) ~ 0.005
M_Pl (c~1) DURING inflation -- far below the candidate's own species-scale cutoff (0.72 M_Pl, v2.394) -- so the
EFT description would break down mid-inflation. Yet the candidate PASSES the engine's SDC. The resolution is an
honest ENGINE LIMITATION: the engine's SDC is a toy aspect-ratio proxy (max|g|/min|g| <= 20) that bounds
coupling HIERARCHIES, not field-space DISTANCES -- so it encodes the swampland's amplitude/hierarchy shadow but
NOT its field-space geometry, which is the SDC's actual content. The candidate therefore passes a version of
the SDC that the physical, field-range SDC would flag. This is a genuine gap in the 'swampland-complete' claim
(v2.373): the carving intersects the swampland's coupling-space projections, not its moduli-space distances.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.410"
DEFAULT_OUT = Path("experiments/results/v2.410/qnm_swampland_field_range_gap.json")

SPECIES_CUTOFF = 0.716   # v2.394, in M_Pl
SDC_C = 1.0              # O(1) swampland distance-conjecture coefficient


def _starobinsky_field_range(N):
    # Einstein-frame total inflaton excursion for R^2 inflation, ~ sqrt(3/2) ln(4N/3) M_Pl
    return math.sqrt(1.5) * math.log(4.0 * N / 3.0)


def run() -> dict:
    ranges = {str(N): round(_starobinsky_field_range(N), 2) for N in (50, 55, 60)}
    dphi = _starobinsky_field_range(55)
    tower_mass = math.exp(-SDC_C * dphi)   # M_Pl units

    checks = {
        "starobinsky_field_range_super_planckian": dphi > 1.0,
        "sdc_tower_light_during_inflation": tower_mass < 0.1,
        "sdc_tower_below_species_cutoff": tower_mass < SPECIES_CUTOFF,
        "engine_sdc_is_hierarchy_not_field_range": True,   # v2.383: max|g|/min|g| <= 20, no field variable
        "swampland_complete_has_a_field_space_gap": (dphi > 1.0) and (tower_mass < SPECIES_CUTOFF),
    }

    return {
        "version": VERSION,
        "starobinsky_field_range_Mpl": ranges,
        "field_range_at_N55_Mpl": round(dphi, 2),
        "sdc_tower_mass_Mpl": round(tower_mass, 4),
        "species_cutoff_Mpl": SPECIES_CUTOFF,
        "engine_sdc_form": "max|g|/min|g_nonzero| <= 20 (aspect-ratio / coupling-hierarchy proxy, v2.383)",
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's Starobinsky inflation faces the field-range swampland tension, and the engine's "
            "SDC cannot see it -- an honest internal-consistency negative that also exposes an engine "
            "limitation. The candidate claims two things at once: it satisfies the engine's Swampland Distance "
            "Conjecture (v2.383) and its keystone g_R2 is the Starobinsky R^2 inflaton (v1.86). But Starobinsky "
            "inflation over N~55 e-folds needs a super-Planckian field excursion Delta_phi ~ 5.3 M_Pl, and the "
            "PHYSICAL (field-space) SDC then puts a tower of states at m ~ M_Pl exp(-c Delta_phi) ~ 0.005 M_Pl "
            "during inflation -- far below the candidate's own species-scale cutoff (0.72 M_Pl, v2.394) -- so "
            "the EFT would break down mid-inflation: the well-known large-field-inflation-vs-swampland tension. "
            "Yet the candidate PASSES the engine's SDC, because that SDC is a toy aspect-ratio proxy "
            "(max|g|/min|g| <= 20) that bounds coupling HIERARCHIES, not field-space DISTANCES. So the engine "
            "encodes the swampland's amplitude/hierarchy SHADOW but not its field-space GEOMETRY, which is the "
            "SDC's actual content -- and the candidate therefore passes a version of the conjecture that the "
            "real, field-range SDC would flag. This is a genuine, previously-unstated GAP in the "
            "'swampland-complete' headline (v2.373): the carving intersects the swampland conjectures' "
            "coupling-space projections, not their moduli-space distances, so results that depend on field "
            "ranges (large-field inflation, the distance/AdS-distance conjectures proper) are outside its "
            "reach. It is the honest counterweight to the recent stability run (v2.405-407): the carving is "
            "robust and converged WITHIN what it encodes, but what it encodes of the swampland is the "
            "coupling-hierarchy face, not the geometry -- so 'swampland-complete' should read "
            "'swampland-coupling-complete'. The constructive read: adding a genuine field-range / moduli-space "
            "constraint (a Delta_phi bound tied to the species scale) is a well-posed next core extension that "
            "would let the engine actually adjudicate the Starobinsky-vs-swampland question its current basis "
            "can only pose."
        ),
        "honest_scope": (
            "The Starobinsky field range Delta_phi ~ 5.3 M_Pl is the standard R^2-inflation result (imported, "
            "not engine-computed), and the SDC tower mass uses the conjecture's O(1) coefficient c ~ 1; whether "
            "Starobinsky ACTUALLY violates the SDC is genuinely DEBATED in the literature (refined-SDC forms, "
            "the value of c, and whether the tower must be below the inflationary scale are all contested), so "
            "'tension' is the known, unsettled large-field-vs-swampland issue, NOT a definitive violation -- "
            "the point is that the candidate INHERITS this open problem, and the engine is blind to it. The "
            "ROBUST, engine-grounded content is the LIMITATION: the engine's SDC is literally an aspect-ratio "
            "of Wilson coefficients (v2.383) with no field variable, so it cannot encode a field-space distance "
            "-- this is a fact about the encoding, not a modelling choice. The g_R2 = Starobinsky-inflaton "
            "identification is the v1.86 toy map (g_R2 as the R^2 coefficient at a high cutoff). The species "
            "cutoff 0.72 M_Pl is toy (v2.394). So this is an honest-negative / gap-identification swing: it "
            "adds no new prediction and does not claim the candidate is ruled out -- it shows the "
            "'swampland-complete' claim covers the coupling-hierarchy projection but not the field-space "
            "geometry, using the candidate's own Starobinsky inflation as the concrete probe. Robust content: "
            "the engine's SDC bounds coupling hierarchies not field ranges, so the swampland-complete carving "
            "has a field-space gap; the candidate's Starobinsky inflation (super-Planckian excursion) sits in "
            "exactly that blind spot -- a real, debated tension the engine cannot currently adjudicate. Imported "
            "field range, debated tension, robust engine-limitation. A swampland-gap swing."
        ),
        "references": [
            "this repo: v2.383 (engine SDC = aspect-ratio proxy), v1.86 (g_R2 = Starobinsky inflaton), v2.394 (species-scale cutoff), v2.373 (swampland-complete predictivity claim), v2.405-407 (stability -- the counterweight)",
            "physics: Ooguri-Vafa swampland distance conjecture; Starobinsky R^2 inflation (super-Planckian field range); the large-field-inflation-vs-swampland debate (Obied-Ooguri-Spodyneiko-Vafa; refined SDC)",
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
    print("SWING (honest negative / engine limitation): Starobinsky-vs-swampland tension the engine's SDC cannot see:")
    print(f"  g_R2 = Starobinsky inflaton (v1.86) -> field range {res['starobinsky_field_range_Mpl']} M_Pl (super-Planckian)")
    print(f"  physical SDC tower at Delta_phi~5.3: m ~ {res['sdc_tower_mass_Mpl']} M_Pl (<< species cutoff {res['species_cutoff_Mpl']}) -> EFT breaks mid-inflation")
    print(f"  BUT candidate passes the engine SDC ({res['engine_sdc_form']}) -- it bounds coupling HIERARCHIES not field DISTANCES")
    print(f"  => honest gap: 'swampland-complete' = swampland-COUPLING-complete; field-space geometry not encoded")
    print(f"  => constructive next step: a field-range / moduli-distance constraint tied to the species scale")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
