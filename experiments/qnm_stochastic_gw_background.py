"""v2.272 - The stochastic gravitational-wave background: a spectral zoo and the inflation gap.

A fresh GW-cosmology probe (opening after the graviton-observable arc v2.266-v2.271). The superposition
of all unresolved gravitational-wave sources is a stochastic background, characterized by its energy
density per logarithmic frequency

    Omega_GW(f) = (1/rho_c) d rho_GW / d ln f  =  (2 pi^2 / 3) (f^2 / H_0^2) h_c(f)^2 ,

where h_c(f) is the characteristic strain. Different origins predict different SPECTRAL SHAPES, and the
spectral index is the discriminant:

  source                 h_c(f) slope alpha    Omega_GW slope (2 alpha + 2)   timing-residual gamma (3-2 alpha)
  SMBH binaries          -2/3                  +2/3                           13/3 ~ 4.33
  inflation (scale-inv)  -1                    0 (flat)                       5
  cosmic strings         -1 (flat plateau)     0 (flat)                       5
  phase transition       peaked (not power law)

The arithmetic linking the strain slope, the energy-density slope and the pulsar-timing-array index is
exact. Two physics points fall out: (1) the NANOGrav 15yr nHz signal (amplitude A ~ 2.4e-15 at 1/yr)
sits right at the SMBH-binary prediction; (2) the PRIMORDIAL inflationary background, fixed by the
tensor-to-scalar ratio r via Omega_GW ~ (1/24) Omega_r r A_s, is ~1e-16 -- far below every detector --
so a stochastic detection is astrophysical or exotic, NOT a direct view of inflation.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_inflation_tensor_qg import A_S  # 2.1e-9

VERSION = "v2.272"
DEFAULT_OUT = Path("experiments/results/v2.272/qnm_stochastic_gw_background.json")

H0_SI = 67.4 * 1000.0 / 3.086e22   # Hubble constant in s^-1 (67.4 km/s/Mpc)
OMEGA_R0 = 9.0e-5                   # radiation density today (photons + neutrinos)
F_YR = 1.0 / (365.25 * 86400.0)    # 1/yr in Hz (PTA reference frequency)
NANOGRAV_A = 2.4e-15               # NANOGrav 15yr characteristic-strain amplitude at f = 1/yr

# detector / array peak sensitivities in Omega_GW (order of magnitude)
DETECTORS = {"PTA (nHz)": 1e-9, "LISA (mHz)": 1e-13, "LIGO design (~100 Hz)": 1e-9}


def omega_gw_from_hc(f_hz: float, h_c: float, H0: float = H0_SI) -> float:
    """Omega_GW(f) = (2 pi^2 / 3)(f^2 / H_0^2) h_c(f)^2."""
    return (2 * math.pi**2 / 3.0) * (f_hz**2 / H0**2) * h_c**2


def omega_slope(alpha: float) -> float:
    """h_c ~ f^alpha  ->  Omega_GW ~ f^(2 alpha + 2)."""
    return 2 * alpha + 2.0


def timing_residual_gamma(alpha: float) -> float:
    """h_c ~ f^alpha  ->  pulsar-timing cross-power S(f) ~ f^-gamma, gamma = 3 - 2 alpha."""
    return 3.0 - 2.0 * alpha


def inflationary_omega_gw(r: float) -> float:
    """Primordial inflationary background today: Omega_GW ~ (1/24) Omega_r r A_s."""
    return (1.0 / 24.0) * OMEGA_R0 * r * A_S


def run() -> dict:
    # the spectral zoo
    sources = [
        {"name": "SMBH binaries", "alpha": -2.0 / 3.0},
        {"name": "inflation (scale-invariant)", "alpha": -1.0},
        {"name": "cosmic strings (plateau)", "alpha": -1.0},
    ]
    for s in sources:
        s["omega_slope"] = omega_slope(s["alpha"])
        s["timing_gamma"] = timing_residual_gamma(s["alpha"])

    # NANOGrav: convert the measured amplitude to Omega_GW at the reference frequency
    nanograv_omega = omega_gw_from_hc(F_YR, NANOGRAV_A)
    smbhb_gamma = timing_residual_gamma(-2.0 / 3.0)

    # primordial inflation background for a few r, vs detector sensitivities
    infl = [{"r": r, "omega_gw": inflationary_omega_gw(r)} for r in (0.036, 0.01, 1e-3)]
    infl_best = inflationary_omega_gw(0.036)   # current upper bound on r -> max primordial Omega_GW
    below_all_detectors = all(infl_best < s for s in DETECTORS.values())

    checks = {
        "smbhb_omega_slope_two_thirds": abs(omega_slope(-2.0 / 3.0) - 2.0 / 3.0) < 1e-12,
        "scale_invariant_omega_flat": abs(omega_slope(-1.0)) < 1e-12,
        "smbhb_timing_gamma_13_over_3": abs(smbhb_gamma - 13.0 / 3.0) < 1e-12,
        "gamma_plus_omega_slope_is_five": all(
            abs(timing_residual_gamma(a) + omega_slope(a) - 5.0) < 1e-12
            for a in (-2.0 / 3.0, -1.0, -0.5, 0.0)),
        "primordial_inflation_below_all_detectors": below_all_detectors,
        "nanograv_omega_order_1e_minus_8": 1e-9 < nanograv_omega < 1e-7,
    }

    return {
        "version": VERSION,
        "method": ("Omega_GW(f) = (2 pi^2/3)(f^2/H_0^2) h_c^2; spectral-index map h_c~f^alpha -> "
                   "Omega_GW~f^(2 alpha+2), PTA gamma = 3-2 alpha; primordial Omega_GW ~ (1/24) Omega_r r A_s"),
        "H0_si": H0_SI,
        "spectral_zoo": sources,
        "nanograv": {"amplitude_at_1yr": NANOGRAV_A, "f_ref_hz": F_YR,
                     "omega_gw_at_1yr": nanograv_omega, "smbhb_gamma": smbhb_gamma,
                     "note": "measured 15yr gamma ~ 3.2 is mildly shallower than the SMBHB 13/3 ~ 4.33"},
        "primordial_inflation": infl,
        "primordial_max_omega_at_r0p036": infl_best,
        "detector_sensitivities": DETECTORS,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The stochastic GW background is diagnosed by its SPECTRAL SHAPE, and the arithmetic "
            "linking the characteristic-strain slope alpha, the energy-density slope (2 alpha + 2) and "
            "the pulsar-timing index gamma (3 - 2 alpha) is exact (verified). Supermassive-black-hole "
            "binaries give h_c ~ f^-2/3, so Omega_GW ~ f^+2/3 and gamma = 13/3 ~ 4.33; a scale-"
            "invariant inflationary or cosmic-string background is FLAT in Omega_GW (gamma = 5); a "
            "phase transition is peaked -- so the slope alone separates the candidates. The NANOGrav "
            "15yr nHz signal (A ~ 2.4e-15 at 1/yr) converts to Omega_GW ~ "
            f"{nanograv_omega:.1e} and sits at the SMBH-binary prediction (its measured gamma ~ 3.2 is "
            "mildly shallower than 13/3, a live question). The decisive QG point is the GAP: the "
            "PRIMORDIAL inflationary background, fixed by the tensor-to-scalar ratio via Omega_GW ~ "
            f"(1/24) Omega_r r A_s, is at most ~{infl_best:.0e} (at the current r < 0.036) -- below the "
            "PTA, LISA and LIGO sensitivities (~1e-9 to 1e-13) by orders of magnitude. So a stochastic "
            "detection is astrophysical (binaries) or exotic (strings, phase transitions), NOT a "
            "direct image of inflation: seeing the inflationary graviton background needs a dedicated "
            "future mission, and that gap is itself the quantitative statement of how faint the "
            "quantum-gravitational vacuum signal is."
        ),
        "honest_scope": (
            "The h_c <-> Omega_GW <-> gamma conversions are EXACT (standard definitions). The NANOGrav "
            "amplitude (A ~ 2.4e-15) and the SMBHB slope are source-backed (NANOGrav 15yr); the "
            "measured gamma ~ 3.2 is mildly shallower than the nominal 13/3, which the collaboration "
            "flags -- reported honestly, not tuned. The primordial estimate Omega_GW ~ (1/24) Omega_r "
            "r A_s is the standard ORDER-OF-MAGNITUDE result; it omits the detailed transfer function, "
            "reheating history and spectral tilt n_T (which can mildly blue-tilt the spectrum), and "
            "Omega_r, H0 are fixed to fiducial values -- so the ~1e-16 ceiling is order-of-magnitude, "
            "but the conclusion (primordial background far below current detectors) is robust across "
            "the uncertainty. Detector sensitivities are representative peak values, not full "
            "power-law-integrated curves. A GW-cosmology / spectral-classification result, not an "
            "engine constraint refit."
        ),
        "references": [
            "Maggiore, 'Gravitational Wave Experiments and Early Universe Cosmology', Phys. Rept. 331 (2000) 283",
            "NANOGrav Collaboration, 'The NANOGrav 15 yr Data Set: Evidence for a GW Background', ApJL 951 (2023) L8",
            "Caprini, Figueroa, 'Cosmological backgrounds of gravitational waves', Class. Quantum Grav. 35 (2018) 163001",
            "this repo: v2.253 (inflation tensor spectrum / r), v2.271 (graviton-observables synthesis)",
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
    print("stochastic GW background -- spectral zoo (h_c ~ f^alpha):")
    for s in res["spectral_zoo"]:
        print(f"  {s['name']:30s} alpha={s['alpha']:+.3f}  Omega_GW~f^{s['omega_slope']:+.3f}  "
              f"gamma={s['timing_gamma']:.3f}")
    print(f"  NANOGrav 15yr: A={res['nanograv']['amplitude_at_1yr']:.1e} -> "
          f"Omega_GW(1/yr) ~ {res['nanograv']['omega_gw_at_1yr']:.1e}")
    print(f"  primordial inflation (r<0.036): Omega_GW <= {res['primordial_max_omega_at_r0p036']:.1e} "
          f"-- below PTA/LISA/LIGO (1e-9..1e-13)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
