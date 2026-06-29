"""v2.269 - GW amplitude birefringence: parity-violating gravity splits the graviton helicities.

A fresh GW-propagation probe (continuing the v2.266-v2.268 GW thread) and the graviton analog of the
v2.252 cosmic birefringence (which rotated PHOTON polarization via an electromagnetic Chern-Simons
term). Parity-violating gravity -- the gravitational Chern-Simons / Pontryagin term R R-dual, the
engine's g_R2_parity sector -- treats the two circular GW polarizations differently as they propagate:

    h_R(D, f) = h_R^GR exp(+zeta) ,   h_L(D, f) = h_L^GR exp(-zeta) ,   zeta ~ kappa * k * D

(AMPLITUDE birefringence: one helicity is amplified, the other damped, with zeta growing linearly
with the wavenumber k = 2 pi f / c and the propagation distance D). The right/left circular
polarizations are the helicity +/-2 eigenstates built from the v2.268 plus/cross tensors,
e_{R,L} = (e_plus +/- i e_cross)/sqrt(2). The clean, falsifiable signature: a source that emits EQUAL
right and left amplitudes (an edge-on / linearly polarized binary, Stokes V = 0 in GR) acquires a
propagation-induced net circular polarization V = tanh(2 zeta) -- nonzero only if gravity violates
parity, and CHROMATIC (growing with frequency), which distinguishes it from any achromatic source
effect.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.qnm_gw_polarizations import polarization_basis

VERSION = "v2.269"
DEFAULT_OUT = Path("experiments/results/v2.269/qnm_gw_birefringence.json")

C_M_S = 2.998e8
MPC_M = 3.086e22


def circular_basis():
    """Right/left circular polarization tensors e_{R,L} = (e_plus +/- i e_cross)/sqrt(2)."""
    e = polarization_basis()
    eR = (e["plus"] + 1j * e["cross"]) / math.sqrt(2)
    eL = (e["plus"] - 1j * e["cross"]) / math.sqrt(2)
    return eR, eL


def _rot_z(psi: float) -> np.ndarray:
    c, s = math.cos(psi), math.sin(psi)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def birefringence_exponent(kappa: float, f_hz: float, D_m: float) -> float:
    """Leading Chern-Simons amplitude-birefringence exponent zeta ~ kappa * k * D, k = 2 pi f / c."""
    k = 2 * math.pi * f_hz / C_M_S
    return kappa * k * D_m


def induced_circular_polarization(zeta: float) -> float:
    """Stokes V/I induced on an intrinsically LINEAR (equal R/L) source: (|A_R|^2-|A_L|^2)/(sum) = tanh(2 zeta)."""
    return math.tanh(2 * zeta)


def run() -> dict:
    eR, eL = circular_basis()

    # 1. helicity check: under a rotation by psi about the propagation axis, e_{R,L} are eigenstates
    #    with eigenvalue exp(-/+ 2 i psi) (helicity +/- 2).
    psi = 0.37
    R = _rot_z(psi)
    eR_rot = R @ eR @ R.T
    eL_rot = R @ eL @ R.T
    # eigenvalue = <e, e_rot>/<e,e> using Frobenius inner product with conjugate
    lam_R = np.sum(np.conj(eR) * eR_rot) / np.sum(np.conj(eR) * eR)
    lam_L = np.sum(np.conj(eL) * eL_rot) / np.sum(np.conj(eL) * eL)
    helicity_R_ok = bool(abs(lam_R - np.exp(-2j * psi)) < 1e-12)
    helicity_L_ok = bool(abs(lam_L - np.exp(+2j * psi)) < 1e-12)

    # 2. orthonormal and unit-helicity: <e_R,e_L> = 0, <e_R,e_R> = <e_L,e_L> = 2 (||e_plus||^2)
    orth = bool(abs(np.sum(np.conj(eR) * eL)) < 1e-12)
    norm_ok = bool(abs(np.sum(np.conj(eR) * eR) - 2.0) < 1e-12)

    # 3. amplitude birefringence: a linear source acquires a chromatic induced circular polarization
    kappa = 1.0e-27          # representative parity coupling (illustrative units, see honest scope)
    D = 400.0 * MPC_M
    bands = [35.0, 100.0, 250.0]
    rows = []
    for f in bands:
        z = birefringence_exponent(kappa, f, D)
        rows.append({"f_hz": f, "zeta": z, "induced_V": induced_circular_polarization(z),
                     "amp_ratio_R_over_L": math.exp(2 * z)})
    # chromaticity: zeta scales linearly with frequency
    chromatic = bool(abs(rows[2]["zeta"] / rows[0]["zeta"] - bands[2] / bands[0]) < 1e-9)
    gr_limit_V = induced_circular_polarization(0.0)   # parity-conserving: no induced polarization

    # 4. representative bound: requiring |induced V| < 0.1 at 100 Hz over 400 Mpc bounds kappa
    z_for_V01 = 0.5 * math.atanh(0.1)
    k100 = 2 * math.pi * 100.0 / C_M_S
    kappa_bound = z_for_V01 / (k100 * D)

    checks = {
        "circular_modes_are_helicity_pm2": helicity_R_ok and helicity_L_ok,
        "circular_modes_orthonormal": orth and norm_ok,
        "gr_limit_has_no_induced_polarization": abs(gr_limit_V) < 1e-15,
        "birefringence_is_chromatic": chromatic,
        "induced_V_is_tanh_2zeta": abs(rows[1]["induced_V"] - math.tanh(2 * rows[1]["zeta"])) < 1e-15,
    }

    return {
        "version": VERSION,
        "method": ("circular polarizations e_{R,L}=(e_plus +/- i e_cross)/sqrt2 as helicity +/-2 "
                   "eigenstates; Chern-Simons amplitude birefringence h_{R,L}=h^GR exp(+/-zeta), "
                   "zeta~kappa k D; induced Stokes V=tanh(2 zeta) on a linear source"),
        "helicity_eigenvalues": {"R": [float(lam_R.real), float(lam_R.imag)],
                                 "L": [float(lam_L.real), float(lam_L.imag)],
                                 "expected_R": [float(np.cos(2*psi)), float(-np.sin(2*psi))]},
        "birefringence_bands": rows,
        "gr_limit_induced_V": gr_limit_V,
        "representative_kappa_bound_for_V_below_0p1": kappa_bound,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "engine_link": ("the parity coupling kappa is the engine's gravitational-Chern-Simons / "
                        "Pontryagin sector g_R2_parity (the same parity axis whose dim-4 photon "
                        "analog gives the v2.252 cosmic-birefringence hint); GW amplitude "
                        "birefringence is its graviton-helicity face"),
        "finding": (
            "Parity-violating (Chern-Simons) gravity splits the two graviton helicities as they "
            "propagate: the right/left circular polarizations -- exact helicity +/-2 eigenstates "
            "built from the plus/cross tensors (verified: a rotation by psi about the line of sight "
            "multiplies them by exp(-/+2 i psi)) -- are amplified and damped by h_{R,L}=h^GR "
            "exp(+/-zeta) with zeta ~ kappa k D growing linearly with frequency and distance. The "
            "clean signature is a propagation-induced net circular polarization on an intrinsically "
            "LINEAR (edge-on, Stokes V=0 in GR) source: V = tanh(2 zeta), nonzero ONLY if gravity "
            "violates parity, and CHROMATIC (zeta ~ f, verified) -- which distinguishes it from any "
            "achromatic source effect or an inclination-driven intrinsic circular polarization. In "
            "the parity-conserving (GR) limit zeta=0 the induced V vanishes exactly. This is the "
            "graviton analog of the v2.252 cosmic birefringence (an electromagnetic Chern-Simons term "
            "rotating photon polarization), the same parity axis the engine carries as g_R2_parity, "
            "and a concrete falsifiable test: a measured frequency-dependent circular-polarization "
            "excess in a GW signal would be smoking-gun parity violation in gravity."
        ),
        "honest_scope": (
            "The helicity-eigenstate result and the induced-V = tanh(2 zeta) formula are EXACT for "
            "the model. The amplitude-birefringence form zeta ~ kappa k D is the standard LEADING "
            "Chern-Simons parametrization (Alexander-Yunes); the actual zeta is an integral of the "
            "CS scalar's evolution (proportional to the time-derivative of the coupling) along the "
            "line of sight, so kappa here is a representative effective coupling in illustrative "
            "units, NOT a calibrated physical value -- the representative_kappa_bound is therefore "
            "an illustration of how a V<0.1 measurement maps to a coupling bound, not a re-derivation "
            "of the published LVC limit. Real sources have an intrinsic inclination-dependent circular "
            "polarization that must be modelled to extract the propagation part (the chromaticity is "
            "the discriminant). A GW-propagation / parity-test result, not an engine constraint refit."
        ),
        "references": [
            "Alexander, Yunes, 'Chern-Simons Modified General Relativity', Phys. Rept. 480 (2009) 1",
            "Yunes, Mirshekari, ... amplitude/velocity birefringence of GWs in parity-violating gravity",
            "Okounkova et al.; Ng et al. -- LIGO/Virgo birefringence constraints",
            "this repo: v2.252 (cosmic birefringence, photon CS), v2.268 (GW polarizations)",
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
    print("GW amplitude birefringence (parity-violating / Chern-Simons gravity)")
    he = res["helicity_eigenvalues"]
    print(f"  helicity eigenvalue R = {he['R'][0]:+.4f}{he['R'][1]:+.4f}i "
          f"(expected {he['expected_R'][0]:+.4f}{he['expected_R'][1]:+.4f}i)")
    print("  induced circular polarization on a linear source (zeta ~ kappa k D):")
    for r in res["birefringence_bands"]:
        print(f"    f={r['f_hz']:6.1f} Hz   zeta={r['zeta']:.3e}   induced V={r['induced_V']:.3e}")
    print(f"  GR limit induced V = {res['gr_limit_induced_V']:.1e}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
