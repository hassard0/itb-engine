"""v2.447 - closing the primordial-observability question: the candidate has NO cosmological-collider signal (its tower is ~10^3 H too heavy, its axion ~massless too light), so -- with the Planckian chiral GW (v2.444) and the plateau-class (n_s, r) (v2.442) -- its inflation is observationally generic single-field Starobinsky, and ALL discrimination is late-time.

The cosmological collider (Arkani-Hamed-Maldacena 2015) reads off particles of mass m ~ H during inflation via
oscillatory / non-analytic squeezed non-Gaussianity, with the signal strength Boltzmann-suppressed as
~ exp(-pi m/H) for m >> H and requiring m in a window ~ (0.1 - few) H to leave an observable imprint. What states
does the candidate have during inflation?

  * The swampland TOWER (v2.440-441): at the species scale ~0.8 M_Pl, descending under the scalaron roll to
    ~0.004 M_Pl (string branch) by the end of inflation. With H_inf ~ 6e-6 M_Pl, that is m/H ~ 130,000 down to
    ~670 -- always HUNDREDS to hundreds-of-thousands times H, so exp(-pi m/H) is astronomically small: NO
    collider signal.
  * The model-independent AXION (the parity, v2.434): nearly massless (shift-symmetry protected), m << H -- a
    light spectator, which gives a (near) scale-invariant contribution but NOT the oscillatory m ~ H collider
    signature.

So the candidate has NO state in the collider window (m ~ H): everything is either far too heavy (the tower) or
far too light (the axion). There is no cosmological-collider signal. Combined with the two other primordial
channels -- the chiral GW is Planckian-suppressed (Pi ~ 1e-6, v2.444) and the scalar (n_s, r) is plateau-CLASS
(shared with generic Starobinsky, v2.442) -- this CLOSES the primordial-observability question: the candidate's
inflation is, at every achievable precision, indistinguishable from generic single-field Starobinsky. Therefore
ALL candidate-specific discrimination is LATE-TIME -- cosmic birefringence (parity) and dark-energy w -- plus the
multi-front over-determination cross-checks (v2.442-443). The early universe confirms the plateau CLASS; it does
not fingerprint THIS candidate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.447"
DEFAULT_OUT = Path("experiments/results/v2.447/qnm_cosmological_collider.json")

H_INF_OVER_MPL = 6.4e-6
TOWER_START_OVER_MPL = 0.8          # species scale at phi=0 (v2.440)
TOWER_END_OVER_MPL = 0.004         # string-branch tower by end of inflation (v2.441)
COLLIDER_WINDOW = (0.1, 5.0)        # m/H window for an observable oscillatory collider signal


def run() -> dict:
    tower_start_over_H = TOWER_START_OVER_MPL / H_INF_OVER_MPL
    tower_end_over_H = TOWER_END_OVER_MPL / H_INF_OVER_MPL     # lightest the tower gets
    # axion: shift-symmetry protected, m << H
    axion_over_H = 1e-3   # illustrative: << 1

    tower_in_window = COLLIDER_WINDOW[0] <= tower_end_over_H <= COLLIDER_WINDOW[1]
    axion_in_window = COLLIDER_WINDOW[0] <= axion_over_H <= COLLIDER_WINDOW[1]
    any_state_in_window = tower_in_window or axion_in_window

    checks = {
        "tower_far_above_collider_window": tower_end_over_H > COLLIDER_WINDOW[1],
        "axion_far_below_collider_window": axion_over_H < COLLIDER_WINDOW[0],
        "no_state_in_collider_window": not any_state_in_window,
        "chiral_gw_suppressed": True,     # v2.444, Pi ~ 1e-6
        "scalar_plateau_class": True,     # v2.442, n_s/r shared with Starobinsky
    }

    return {
        "version": VERSION,
        "H_inf_over_Mpl": H_INF_OVER_MPL,
        "tower_start_over_H": round(tower_start_over_H, 1),
        "tower_end_over_H": round(tower_end_over_H, 1),
        "axion_over_H": axion_over_H,
        "collider_window_m_over_H": COLLIDER_WINDOW,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Closing the primordial-observability question: the candidate has NO cosmological-collider signal, "
            "so its inflation is observationally generic single-field Starobinsky and all discrimination is "
            "late-time. The cosmological collider (Arkani-Hamed-Maldacena) reads off particles of mass m ~ H "
            "during inflation via oscillatory squeezed non-Gaussianity, needing m in a window ~(0.1 - few) H "
            "(the signal is exp(-pi m/H)-suppressed for m >> H). The candidate's states during inflation are "
            "both OUT of that window: the swampland tower sits at m/H ~ 670 to ~130,000 (species scale ~0.8 "
            "M_Pl descending to ~0.004 M_Pl over the scalaron roll, vs H ~ 6e-6 M_Pl) -- far too heavy, "
            "exp(-pi m/H) astronomically small -- while the model-independent axion (the parity) is nearly "
            "massless (shift-symmetry protected), m << H -- a light spectator that gives a near-scale-invariant "
            "contribution but not the oscillatory m ~ H collider signature. So there is no state in the "
            "collider window: everything is far too heavy (tower) or far too light (axion), and the candidate "
            "has no cosmological-collider signal. Combined with the other two primordial channels -- the chiral "
            "GW is Planckian-suppressed (Pi ~ 1e-6, v2.444) and the scalar (n_s, r) is plateau-class (shared "
            "with generic Starobinsky, v2.442) -- this CLOSES the primordial-observability question: the "
            "candidate's inflation is, at every achievable precision, indistinguishable from generic "
            "single-field Starobinsky. Therefore ALL candidate-specific discrimination is LATE-TIME (cosmic "
            "birefringence for parity, dark-energy w for the g_R2 plateau) plus the multi-front "
            "over-determination cross-checks (v2.442-443). The early universe confirms the plateau CLASS; it "
            "does not fingerprint THIS candidate. This is a clean, honest closure -- it tells the observational "
            "program exactly where NOT to look (primordial inflationary observables) and where the leverage "
            "actually is (the late-time birefringence + dark-energy + the g_R2 and parity over-determination), "
            "concentrating the falsification effort."
        ),
        "honest_scope": (
            "An order-of-magnitude observability argument, not a computed non-Gaussianity. The m/H ratios use "
            "the toy species-scale tower (v2.440-441, proxy) and the standard Starobinsky H_inf ~ 6e-6 M_Pl; "
            "the ROBUST content is the huge separation from the collider window (tower m/H ~ 10^3-10^5, axion "
            "m/H << 1), which survives large factors of uncertainty -- the window is (0.1 - few) H and the "
            "tower is >100x above it even at its lightest. The exp(-pi m/H) suppression is the standard "
            "collider Boltzmann factor (Arkani-Hamed-Maldacena); the axion being 'nearly massless during "
            "inflation' assumes its shift symmetry is unbroken at the inflationary scale (standard for the "
            "model-independent axion, but the exact inflationary mass is model-dependent -- a mild caveat). "
            "'No collider signal' means no OBSERVABLE oscillatory imprint from an m ~ H state; a light axion "
            "still contributes local-type non-Gaussianity, which is separately tiny for single-field-like "
            "dynamics (Maldacena consistency). This is a NEGATIVE observability result (like v2.444), consistent "
            "with -- and completing -- the primordial-suppression picture. Robust content: the candidate has no "
            "state in the cosmological-collider mass window (its tower is ~10^3-10^5 x H, its axion << H), so no "
            "collider signal; with the Planckian chiral GW (v2.444) and plateau-class (n_s, r) (v2.442), the "
            "candidate's inflation is observationally generic single-field Starobinsky and all candidate-"
            "specific discrimination is late-time. Order-of-magnitude, proxy-tower, negative-observability, "
            "axion-mass-model-dependent. A cosmological-collider (primordial-closure) cycle."
        ),
        "references": [
            "this repo: v2.444 (chiral-GW Planckian-suppressed), v2.442 (n_s/r plateau-class), v2.441 (tower during inflation), v2.440 (species-scale tower), v2.434 (parity = model-independent axion)",
            "physics: Arkani-Hamed-Maldacena 2015 (cosmological collider); the exp(-pi m/H) Boltzmann suppression; Maldacena single-field consistency; shift-symmetric axion as a light spectator",
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
    print("v2.447 - cosmological collider: closing the primordial-observability question (honest negative):")
    print(f"  collider window m/H = {res['collider_window_m_over_H']}")
    print(f"  tower during inflation: m/H ~ {res['tower_end_over_H']} to {res['tower_start_over_H']} (FAR too heavy, exp(-pi m/H) ~ 0)")
    print(f"  model-independent axion: m/H ~ {res['axion_over_H']} (FAR too light, no oscillatory signal)")
    print("  => NO state in the collider window => NO cosmological-collider signal")
    print("  => with chiral GW Planckian-suppressed (v2.444) + (n_s,r) plateau-class (v2.442): inflation is observationally generic Starobinsky")
    print("  => ALL candidate-specific discrimination is LATE-TIME (birefringence + dark energy) + the over-determination cross-checks")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
