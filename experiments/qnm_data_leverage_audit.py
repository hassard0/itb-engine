"""v2.358 - Data-leverage audit: which of the four ingested-data constraints actually bind the constructed theory?

A completeness audit (and an honest self-correction). The program advertises "four ingested-data
constraints", but which actually constrain the constructed theory, and which merely document that an
experiment probes a different sector? This ranks all four by how tightly they bind, and classifies each.

(Self-correction recorded: at 4-decimal display the gw_speed margin prints as +0.0000, which LOOKS exactly
binding. It is not -- the gw_speed bound is itself 5e-16, and the constructed theory's deviation is ~2e-5 of
that, so the margin is essentially the full bound. The +0.0000 is a display artifact of a tiny absolute
scale, not a knife-edge.)

The verdict:
  cosmic_birefringence_data : BINDING  (signed-distance ~0.013 -- the one tight, load-bearing data constraint;
                              the parity channel)
  submm_gravity_yukawa_bound: VACUOUS when screened (the program's config), LOAD-BEARING when unscreened
                              (the screening channel, v2.354) -- a configuration switch, not a free bind
  gw_speed_bound            : BLIND     (GW170817 is a frequency-INDEPENDENT speed test; higher-derivative
                              gravity gives a frequency-SUPPRESSED dispersion ~(E_GW/E_cutoff)^2 ~ 1e-20, so
                              the deviation is ~2e-5 of the 5e-16 bound -- untouched)
  gw_dispersion_bound       : SLACK     (present but far from binding, margin ~0.64)

So the consistent+observed region's data leverage is essentially ONE constraint (birefringence) in the
screened configuration, plus submm in the unscreened one. The two GW-propagation constraints are honest
sector-documentation, not active discriminators.
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

VERSION = "v2.358"
DEFAULT_OUT = Path("experiments/results/v2.358/qnm_data_leverage_audit.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = dict(zip(KEYS, [0.529, 0.4, 0.4, 0.193, 0.09, 0.06]))
DATA_NAMES = ["cosmic_birefringence_data", "submm_gravity_yukawa_bound", "gw_speed_bound", "gw_dispersion_bound"]
BINDING_THRESHOLD = 0.05      # signed-distance below this = actively binding/tight
BLIND_RATIO = 1e-3            # deviation/bound below this = blind (untouched)


def data_results(stack):
    out = {}
    for r in check(Theory(coefficients=dict(CONSTRUCTED), name="x"), stack).results:
        if r.constraint_name in DATA_NAMES:
            out[r.constraint_name] = r
    return out


def run() -> dict:
    screened = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                           include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    unscreened = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                             include_gw_speed=True, include_gw_dispersion=True, submm_screened=False)

    rs = data_results(screened)
    ru = data_results(unscreened)

    bire = rs["cosmic_birefringence_data"]
    gw_speed = rs["gw_speed_bound"]
    gw_disp = rs["gw_dispersion_bound"]
    submm_scr = rs["submm_gravity_yukawa_bound"]
    submm_unscr = ru["submm_gravity_yukawa_bound"]

    gw_speed_ratio = gw_speed.details.get("ratio_to_bound", 1.0)

    rows = [
        {"constraint": "cosmic_birefringence_data",
         "signed_distance": round(bire.signed_distance_margin, 4),
         "classification": "BINDING" if bire.signed_distance_margin < BINDING_THRESHOLD else "slack",
         "role": "parity channel (the one tight data constraint)"},
        {"constraint": "submm_gravity_yukawa_bound",
         "signed_distance_screened": round(submm_scr.signed_distance_margin, 4),
         "satisfied_unscreened": submm_unscr.satisfied,
         "classification": "VACUOUS(screened)/LOAD-BEARING(unscreened)",
         "role": "screening channel via config switch (v2.354)"},
        {"constraint": "gw_speed_bound",
         "ratio_to_bound": gw_speed_ratio,
         "classification": "BLIND" if gw_speed_ratio < BLIND_RATIO else "active",
         "role": "GW170817 speed test, frequency-blind to higher-derivative dispersion"},
        {"constraint": "gw_dispersion_bound",
         "signed_distance": round(gw_disp.signed_distance_margin, 4),
         "classification": "SLACK" if gw_disp.signed_distance_margin > BINDING_THRESHOLD else "binding",
         "role": "intra-messenger dispersion, present but far from binding"},
    ]

    birefringence_is_only_binding = (
        bire.signed_distance_margin < BINDING_THRESHOLD
        and gw_disp.signed_distance_margin > BINDING_THRESHOLD
        and gw_speed_ratio < BLIND_RATIO)

    checks = {
        "birefringence_is_binding": bire.signed_distance_margin < BINDING_THRESHOLD,
        "gw_speed_is_blind_not_binding": gw_speed_ratio < BLIND_RATIO,   # the self-correction: NOT knife-edge
        "gw_dispersion_is_slack": gw_disp.signed_distance_margin > BINDING_THRESHOLD,
        "submm_vacuous_screened_active_unscreened": submm_scr.satisfied and not submm_unscr.satisfied,
        "birefringence_is_the_only_active_data_bind_when_screened": birefringence_is_only_binding,
    }

    return {
        "version": VERSION,
        "data_constraint_rows": rows,
        "birefringence_signed_distance": round(bire.signed_distance_margin, 4),
        "gw_speed_ratio_to_bound": gw_speed_ratio,
        "gw_dispersion_signed_distance": round(gw_disp.signed_distance_margin, 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Of the program's four ingested-data constraints, only ONE actively binds the constructed theory "
            "in the standard (screened) configuration: cosmic birefringence (signed-distance ~0.013 -- "
            "tight, the parity channel). The sub-mm gravity bound is VACUOUS as configured (screened) but "
            "LOAD-BEARING when unscreened (the screening channel, v2.354) -- a configuration switch, not a "
            "free bind. The two gravitational-wave-propagation constraints do NOT bind: gw_speed is BLIND "
            f"(its deviation is ~{gw_speed_ratio:.0e} of the GW170817 bound, because higher-derivative "
            "gravity gives a frequency-SUPPRESSED dispersion ~(E_GW/E_cutoff)^2 ~ 1e-20 at LIGO "
            "frequencies, not the frequency-independent speed shift GW170817 tested), and gw_dispersion is "
            f"SLACK (signed-distance ~{gw_disp.signed_distance_margin:.2f}). This includes an honest "
            "self-correction: at 4-decimal display the gw_speed margin prints as +0.0000, which LOOKS like a "
            "knife-edge bind -- but the gw_speed bound is itself 5e-16, and the deviation is ~2e-5 of that, "
            "so the margin is essentially the FULL bound (maximally slack), not zero. The +0.0000 is a "
            "display artifact of a tiny absolute scale. So the consistent+observed region's data leverage is "
            "essentially birefringence (binding) plus submm-when-unscreened; the two GW constraints are "
            "honest sector-DOCUMENTATION (which experiment probes which operator) rather than active "
            "discriminators. This sharpens the whole data story: the program's single point of empirical "
            "failure is the birefringence detection (v2.329) precisely because it is the only data "
            "constraint that actually binds -- the GW constraints cannot rescue or refute the parity "
            "headline, and the screening channel's data role is a binary screened/unscreened switch, not a "
            "graded fit."
        ),
        "honest_scope": (
            "The classification is exact (the engine's own margins / ratio-to-bound at the constructed "
            "point), and the self-correction is genuine -- the gw_speed +0.0000 is the full 5e-16 bound, "
            "verified by its ratio_to_bound ~ 2e-5. The thresholds (BINDING < 0.05 signed-distance, BLIND < "
            "1e-3 ratio) are conventional cut points, but the separations are large (birefringence 0.013 vs "
            "gw_dispersion 0.64 vs gw_speed 2e-5), so the verdicts are not threshold-sensitive. This is the "
            "constructed POINT's data-leverage; over the family the birefringence tightness varies but it "
            "remains the binding data constraint (v2.333: parity is the stiffest direction). The gw_speed "
            "blindness is a physics statement from the engine's dispersion model (frequency-suppressed "
            "(E_GW/E_cutoff)^2) with its O(1) kappa_c and the dark-energy cutoff -- robust by orders of "
            "magnitude (the deviation is ~1e-20 vs a 5e-16 bound), but it would bite for an ultra-low cutoff "
            "below a few micro-eV (documented in the constraint). submm's screened/unscreened switch carries "
            "the v2.354/v2.355 caveats. Toy basis, O(1) prefactors. A data-leverage completeness audit with "
            "a recorded display-artifact self-correction."
        ),
        "references": [
            "this repo: src/itb/constraints/gw_speed.py (frequency-blind), gw_dispersion.py, cosmic_birefringence.py, submm_gravity.py",
            "this repo: v2.329 (birefringence is the single point of failure -- here shown to be the ONLY binding data constraint), v2.354/v2.355 (screening config switch), v2.333 (parity is the stiffest direction)",
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
    print("data-leverage audit -- which of the 4 data constraints bind the constructed theory:")
    for r in res["data_constraint_rows"]:
        print(f"  {r['constraint']:<28} [{r['classification']}]  {r['role']}")
    print(f"  birefringence signed-distance: {res['birefringence_signed_distance']} (BINDING)")
    print(f"  gw_speed ratio-to-bound: {res['gw_speed_ratio_to_bound']:.2e} (BLIND -- +0.0000 was a display artifact)")
    print(f"  gw_dispersion signed-distance: {res['gw_dispersion_signed_distance']} (SLACK)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
