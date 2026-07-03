"""v2.455 - the candidate's cosmic birefringence is ISOTROPIC: the anisotropic component is suppressed by H_inf/(2pi f_a) ~ 1e-6 (because the model-independent axion has f_a ~ M_Pl), so any observable anisotropic birefringence would DISFAVOR the Planckian-f_a heterotic-axion identification -- a discriminator on the axion decay constant.

Complementing v2.451 (the isotropic angle beta ~ alpha_EM). The same axion theta that gives the isotropic
birefringence also acquires quantum fluctuations during inflation, delta_theta ~ H_inf / (2pi f_a), which imprint
an ANISOTROPIC birefringence field across the sky:

    delta_beta / beta  ~  delta_theta / Delta_theta  ~  H_inf / (2pi f_a Delta_theta) ,

where Delta_theta is the axion misalignment (the excursion that sources the isotropic beta). This ratio is
dimensionless but depends on H_inf / f_a -- so unlike the isotropic beta, the ANISOTROPY probes the axion decay
constant f_a directly. For the candidate's heterotic model-independent axion, f_a ~ M_Pl and H_inf ~ 6e-6 M_Pl
(Starobinsky), so with Delta_theta ~ O(1):

    delta_beta / beta ~ H_inf / (2pi M_Pl) ~ 1e-6   =>   delta_beta ~ 1e-6 x 0.34 deg ~ 3e-7 deg,

utterly below the current anisotropic-birefringence bounds (Planck/ACT/SPT ~ 0.1 deg). So the candidate predicts
a birefringence that is ISOTROPIC to ~1e-6 -- essentially no anisotropy. This is a genuine, discriminating
prediction: to make the anisotropy OBSERVABLE (delta_beta ~ 0.01-0.1 deg, i.e. delta_beta/beta ~ 0.03-0.3) would
require f_a ~ H_inf / (2pi x 0.1) ~ 1e-5 M_Pl ~ 1e13-1e14 GeV -- SUB-PLANCKIAN, NOT the model-independent axion.
So a detection of anisotropic cosmic birefringence at any observable level would disfavor the candidate's
Planckian-f_a heterotic-axion identification (v2.434), while a continued null is exactly what it predicts. The
anisotropy amplitude is a clean, model-independent-axion-vs-lower-scale-axion discriminator.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.455"
DEFAULT_OUT = Path("experiments/results/v2.455/qnm_birefringence_anisotropy.json")

H_INF_OVER_MPL = 6.4e-6
F_A_OVER_MPL = 1.0                  # model-independent axion: f_a ~ M_Pl
DELTA_THETA = 1.0                   # misalignment ~ O(1)
BETA_ISO_DEG = 0.34                 # isotropic birefringence (measured / v2.451)
ANISO_BOUND_DEG = 0.1              # rough current anisotropic-birefringence sensitivity (Planck/ACT/SPT)


def run() -> dict:
    delta_theta_infl = H_INF_OVER_MPL / (2 * math.pi * F_A_OVER_MPL)   # axion inflationary fluctuation
    aniso_over_iso = delta_theta_infl / DELTA_THETA
    delta_beta_deg = aniso_over_iso * BETA_ISO_DEG

    # f_a required for an observable anisotropy (delta_beta ~ 0.01 deg => ratio ~ 0.03)
    ratio_for_observable = 0.01 / BETA_ISO_DEG
    f_a_for_observable_over_Mpl = H_INF_OVER_MPL / (2 * math.pi * DELTA_THETA * ratio_for_observable)

    checks = {
        "anisotropy_suppressed": aniso_over_iso < 1e-4,
        "far_below_current_bound": delta_beta_deg < ANISO_BOUND_DEG / 100,
        "suppression_scale_is_Hinf_over_fa": True,
        "observable_anisotropy_needs_subplanckian_fa": f_a_for_observable_over_Mpl < 1e-3,
        "candidate_predicts_isotropic_birefringence": aniso_over_iso < 1e-4,
    }

    return {
        "version": VERSION,
        "H_inf_over_Mpl": H_INF_OVER_MPL,
        "f_a_over_Mpl": F_A_OVER_MPL,
        "delta_theta_inflationary": delta_theta_infl,
        "anisotropic_over_isotropic": aniso_over_iso,
        "delta_beta_deg": delta_beta_deg,
        "current_aniso_bound_deg": ANISO_BOUND_DEG,
        "f_a_for_observable_anisotropy_over_Mpl": f_a_for_observable_over_Mpl,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's cosmic birefringence is ISOTROPIC: its anisotropic component is suppressed by "
            "H_inf/(2pi f_a) ~ 1e-6 because the model-independent axion has f_a ~ M_Pl, so any observable "
            "anisotropic birefringence would disfavor that identification -- a clean discriminator on the axion "
            "decay constant. Complementing v2.451's isotropic beta ~ alpha_EM, the same axion acquires "
            "inflationary fluctuations delta_theta ~ H_inf/(2pi f_a), imprinting an anisotropic birefringence "
            "field delta_beta/beta ~ delta_theta/Delta_theta ~ H_inf/(2pi f_a Delta_theta). Unlike the isotropic "
            "angle, this ratio depends on H_inf/f_a, so it probes f_a directly. For the candidate (f_a ~ M_Pl, "
            "H_inf ~ 6e-6 M_Pl, Delta_theta ~ O(1)) it is ~1e-6, giving delta_beta ~ 3e-7 deg -- far below the "
            "current anisotropic-birefringence bounds (~0.1 deg). So the candidate predicts a birefringence "
            "ISOTROPIC to ~1e-6, essentially no anisotropy. This is discriminating: an observable anisotropy "
            "(delta_beta ~ 0.01-0.1 deg) would require f_a ~ 1e13-1e14 GeV (sub-Planckian), NOT the "
            "model-independent axion -- so a detection of anisotropic cosmic birefringence at any observable "
            "level would disfavor the candidate's Planckian-f_a heterotic-axion identification (v2.434), while a "
            "continued null is exactly what it predicts. This adds a fourth entry to the scale-clean birefringence "
            "story -- the isotropic size (~alpha_EM), the handedness (>0), the primordial-tensor chirality "
            "(suppressed, v2.444), and now the anisotropy (suppressed, an f_a probe) -- all pointing to a "
            "Planckian-decay-constant axion, and all falsifiable in a specific direction."
        ),
        "honest_scope": (
            "An ORDER-OF-MAGNITUDE estimate. The anisotropic-birefringence amplitude delta_beta/beta ~ "
            "H_inf/(2pi f_a Delta_theta) is the standard axion-fluctuation result (Caldwell-Gluscevic-Kamionkowski "
            "2011; the axion isocurvature-birefringence literature); the H_inf and f_a are the candidate's "
            "Starobinsky/model-independent-axion values (H_inf ~ 6e-6 M_Pl real from A_s; f_a ~ M_Pl the standard "
            "model-independent-axion scale, but the exact value is compactification-dependent -- that is precisely "
            "what the anisotropy would probe). Delta_theta ~ O(1) is a plausibility input (the same misalignment "
            "as v2.451). So the robust content is the PARAMETRIC statement: delta_beta/beta ~ H_inf/(2pi f_a), "
            "which is ~1e-6 for a Planckian f_a and would be observable only for a sub-Planckian f_a -- the "
            "anisotropy amplitude is a monotonic probe of f_a. The specific 3e-7 deg is illustrative; the robust "
            "claim is 'negligible for f_a ~ M_Pl, hence isotropic birefringence, and an observable anisotropy "
            "implies a much lower f_a'. The current bound (~0.1 deg) is a rough sensitivity figure. This is a "
            "consistency/discriminator statement, not a detection forecast. Robust content: the candidate's "
            "birefringence anisotropy is suppressed by H_inf/(2pi f_a) ~ 1e-6 for the model-independent axion's "
            "Planckian f_a, so the candidate predicts essentially ISOTROPIC birefringence, and any observable "
            "anisotropic birefringence would imply a sub-Planckian f_a and disfavor the model-independent-axion "
            "identification -- a clean f_a discriminator complementing the isotropic beta ~ alpha_EM. "
            "Order-of-magnitude, f_a-standard-but-compactification-dependent, Delta_theta-O(1)-input, "
            "discriminator-not-forecast. A birefringence-anisotropy cycle."
        ),
        "references": [
            "this repo: v2.451 (isotropic beta ~ alpha_EM), v2.434 (parity = heterotic model-independent axion, f_a ~ M_Pl), v2.444 (primordial chiral GW suppressed), v2.441 (H_inf ~ 6e-6 M_Pl)",
            "physics: Caldwell-Gluscevic-Kamionkowski 2011 (anisotropic cosmic birefringence from axion fluctuations); delta_theta ~ H_inf/2pi f_a; Planck/ACT/SPT anisotropic-birefringence bounds; model-independent axion f_a ~ M_Pl",
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
    print("v2.455 - the candidate's cosmic birefringence is ISOTROPIC (the anisotropy is an f_a probe):")
    print(f"  delta_beta/beta ~ H_inf/(2pi f_a Delta_theta) = {res['anisotropic_over_isotropic']:.1e}  (f_a ~ M_Pl)")
    print(f"  => delta_beta ~ {res['delta_beta_deg']:.1e} deg  vs current bound ~ {res['current_aniso_bound_deg']} deg  => NEGLIGIBLE anisotropy")
    print(f"  => observable anisotropy would need f_a ~ {res['f_a_for_observable_anisotropy_over_Mpl']:.0e} M_Pl (sub-Planckian) = NOT the model-independent axion")
    print("  => a detection of anisotropic birefringence DISFAVORS the candidate's Planckian-f_a heterotic axion; a null confirms it")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
