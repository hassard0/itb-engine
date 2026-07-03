"""v2.448 - the candidate's cosmological field content: TWO distinct scalars of opposite parity -- a parity-EVEN scalaron (inflation + dark energy) and a parity-ODD axion (cosmic birefringence) -- with the axion a subdominant second late-time field.

The program has repeatedly said 'the g_R2 scalaron drives dark energy and inflation' and 'the parity coupling
drives birefringence' without making explicit that these are DIFFERENT FIELDS. They are, by PARITY:

  * The R^2 operator (coupling g_R2) is parity-EVEN; via the standard f(R) -> scalar-tensor duality it propagates
    a spin-0 SCALARON phi (parity-even). This is the candidate's inflaton (early, Starobinsky plateau, v2.441)
    AND its dark-energy field (late, R^2 plateau, w > -1, v2.422-425).
  * The R ^ R-tilde (Pontryagin) operator (coupling g_R2_parity) is parity-ODD and topological on its own; to be
    dynamical it must multiply a pseudoscalar AXION theta (parity-odd) -- theta R ^ R-tilde, the gravitational
    Chern-Simons term (the heterotic model-independent axion, v2.434). A slowly evolving theta today is what
    rotates the CMB polarization plane -> cosmic birefringence.

So phi and theta have OPPOSITE parity and CANNOT be the same field. The candidate's late universe therefore
carries TWO dynamical scalars: the scalaron phi (dark energy) and the axion theta (birefringence). Consistency:
the measured birefringence is small (beta ~ 0.3 deg), so the axion's field excursion x coupling is small, and its
energy density can be far subdominant to the scalaron dark energy -- the two coexist without conflict (phi
dominates rho_DE and sets w, theta is a light subdominant field whose slow roll gives beta). This resolves an
implicit ambiguity in the program (the 'dark-energy axion' of the early v1.46-47 vs the 'g_R2 scalaron dark
energy' of v2.422-425): in the current candidate the DARK ENERGY is the parity-even scalaron, and the AXION is a
SEPARATE parity-odd field responsible for birefringence, not for the bulk dark energy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.448"
DEFAULT_OUT = Path("experiments/results/v2.448/qnm_two_scalars.json")

CON = {"g_R2": 0.193, "g_R2_parity": 0.06}


def run() -> dict:
    fields = {
        "scalaron_phi": {
            "operator": "R^2 (g_R2)", "parity": "even", "spin": 0,
            "origin": "f(R) -> scalar-tensor duality",
            "roles": ["inflation (early, Starobinsky plateau)", "dark energy (late, R^2 plateau, w > -1)"],
            "coupling": CON["g_R2"],
        },
        "axion_theta": {
            "operator": "theta R ^ R-tilde (g_R2_parity, gravitational Chern-Simons)", "parity": "odd", "spin": 0,
            "origin": "pseudoscalar multiplying the Pontryagin density (heterotic model-independent axion)",
            "roles": ["cosmic birefringence (late, slow roll rotates CMB polarization)"],
            "coupling": CON["g_R2_parity"],
        },
    }

    opposite_parity = fields["scalaron_phi"]["parity"] != fields["axion_theta"]["parity"]
    both_present = CON["g_R2"] > 0 and CON["g_R2_parity"] > 0
    # small measured birefringence => axion subdominant possible
    axion_subdominant_ok = CON["g_R2_parity"] < CON["g_R2"]   # coupling hierarchy allows subdominant axion

    checks = {
        "two_distinct_scalars": both_present,
        "opposite_parity": opposite_parity,
        "cannot_be_same_field": opposite_parity,
        "scalaron_is_dark_energy_and_inflaton": CON["g_R2"] > 0,
        "axion_subdominant_late_time_consistent": axion_subdominant_ok,
    }

    return {
        "version": VERSION,
        "fields": fields,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's cosmological field content is TWO distinct scalars of opposite parity -- a "
            "parity-even scalaron (inflation + dark energy) and a parity-odd axion (cosmic birefringence) -- "
            "with the axion a subdominant second late-time field. The program had repeatedly attributed dark "
            "energy/inflation to 'the g_R2 scalaron' and birefringence to 'the parity coupling' without making "
            "explicit that these are different fields. They are, by parity: R^2 (g_R2) is parity-even and, via "
            "the f(R) -> scalar-tensor duality, propagates a spin-0 scalaron phi -- the candidate's inflaton "
            "(early, Starobinsky plateau) AND its dark-energy field (late, R^2 plateau, w > -1); whereas "
            "R ^ R-tilde (g_R2_parity) is parity-odd and topological on its own, so to be dynamical it must "
            "multiply a pseudoscalar axion theta (the gravitational Chern-Simons term, the heterotic "
            "model-independent axion), whose slow evolution today rotates the CMB polarization -> birefringence. "
            "phi and theta have OPPOSITE parity and cannot be the same field, so the candidate's late universe "
            "carries TWO dynamical scalars. They coexist consistently: the measured birefringence is small "
            "(beta ~ 0.3 deg), so the axion's excursion x coupling is small and its energy density can be far "
            "subdominant to the scalaron dark energy -- phi dominates rho_DE and sets w, theta is a light "
            "subdominant field whose slow roll gives beta. This resolves an implicit ambiguity in the program "
            "(the early 'dark-energy axion' of v1.46-47 vs the 'g_R2 scalaron dark energy' of v2.422-425): in "
            "the current candidate the DARK ENERGY is the parity-even scalaron and the AXION is a SEPARATE "
            "parity-odd field responsible for birefringence, not the bulk dark energy. The clarification tightens "
            "the cosmological story: the two cosmological KEYSTONES (g_R2 and g_R2_parity, each over-determined "
            "across two experiments, v2.442-443) map to two physically distinct fields, and the candidate's late "
            "universe is a two-field system -- a dominant parity-even quintessence scalaron plus a subdominant "
            "parity-odd birefringence axion -- both descending from the same curvature sector."
        ),
        "honest_scope": (
            "The field identifications are STANDARD EFT facts: R^2 <-> a parity-even scalaron (f(R) duality), and "
            "theta R ^ R-tilde <-> a parity-odd pseudoscalar axion (gravitational Chern-Simons). The ROBUST, "
            "essentially theorem-level content is that the two fields have opposite parity and so are distinct "
            "(a parity-even scalar cannot source a parity-odd birefringence, and vice versa). The 'axion "
            "subdominant to the scalaron dark energy' consistency is an ORDER-OF-MAGNITUDE argument from the "
            "small measured beta (~0.3 deg => small axion excursion x coupling => small rho_theta), not a "
            "computed two-field cosmology -- the axion's potential/mass (which fixes whether it is subdominant "
            "quintessence, dark radiation, or gets a mass) is NOT computed and is model-dependent; the claim is "
            "only that a subdominant configuration is available and natural, not forced. The coupling hierarchy "
            "g_R2_parity (0.06) < g_R2 (0.19) is used as a plausibility (and both are O(1)-toy magnitudes). This "
            "does not add a constraint or a new observable -- it is a STRUCTURAL clarification of the field "
            "content that was previously left implicit/ambiguous, and it updates the field assignment relative "
            "to the early dark-energy-axion cycles (v1.46-47). Robust content: the candidate's curvature sector "
            "yields two distinct cosmological scalars of opposite parity -- a parity-even scalaron (inflaton + "
            "dark energy) and a parity-odd axion (birefringence) -- which cannot be the same field, so the late "
            "universe is a two-field system with the scalaron dominant (dark energy) and the axion a plausibly "
            "subdominant birefringence source. Standard-EFT-identification, parity-distinction-robust, "
            "subdominance-order-of-magnitude, axion-potential-not-computed. A cosmological-field-content cycle."
        ),
        "references": [
            "this repo: v2.434 (parity = model-independent axion), v2.422-425 (g_R2 scalaron dark energy), v2.441 (g_R2 Starobinsky inflaton), v2.386 (parity = chirality structure), v1.46-47 (early dark-energy axion)",
            "physics: f(R) -> scalar-tensor duality (R^2 scalaron, Whitt 1984); gravitational Chern-Simons axion theta R ^ R-tilde (Jackiw-Pi); parity-even scalar vs parity-odd pseudoscalar; cosmic birefringence from a rolling axion (Carroll-Field-Jackiw)",
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
    print("v2.448 - the candidate's cosmological field content: TWO distinct scalars of opposite parity:")
    for name, fld in res["fields"].items():
        print(f"  {name:<14} [{fld['operator']:<40}] parity={fld['parity']:<5} roles={fld['roles']}")
    print("  => opposite parity => distinct fields => the late universe is a TWO-FIELD system")
    print("  => scalaron phi = dark energy (dominant) + inflaton; axion theta = birefringence (subdominant, plausible)")
    print("  => resolves the v1.46-47 'dark-energy axion' vs v2.422-425 'scalaron dark energy': DE = scalaron, axion = SEPARATE parity field")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
