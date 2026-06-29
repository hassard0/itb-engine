"""v2.251 - Lorentz-violation / modified dispersion: testing Planck-scale spacetime structure.

A fresh thread, pivoting off black holes to the flagship quantum-gravity-PHENOMENOLOGY probe: is
spacetime smooth at the Planck length, or does a discrete/quantum structure show up as an
energy-dependent propagation speed? A generic Lorentz-violating (LIV) modified dispersion

    E^2 = p^2 c^2 [ 1 - s (E / E_QG)^n ]   =>   v(E)/c ~ 1 - s (n+1)/2 (E / E_QG)^n ,

makes quanta of different energy travel at slightly different speeds, so two messengers emitted
together from a source at light-travel distance D arrive separated by

    Delta t ~ (D/c) [ (E_hi/E_QG)^n - (E_lo/E_QG)^n ]   (linear n=1: (D/c)(E_hi-E_lo)/E_QG),

bounding the quantum-gravity scale E_QG > (D/c) Delta E / Delta t_obs (n=1). The decisive feature:
the bound scales with the MESSENGER ENERGY, so high-energy gamma-ray-burst photons (GeV) reach
E_QG ~ E_Planck, while low-energy gravitons (~1e-12 eV) give dispersion bounds ~22 orders of
magnitude weaker -- but the multi-messenger GW170817 GW-vs-photon SPEED comparison is instead the
strongest bound on the constant-offset (n=0 / graviton-mass) sector. Photon and graviton channels
are complementary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VERSION = "v2.251"
DEFAULT_OUT = Path("experiments/results/v2.251/qnm_lorentz_violation_dispersion.json")
E_PLANCK_eV = 1.22e28        # 1.22e19 GeV
GYR_S = 3.156e16             # 1 Gyr in seconds


def e_qg_bound_linear(D_over_c_s: float, dE_eV: float, dt_s: float) -> float:
    """Linear (n=1) LIV lower bound: E_QG > (D/c) Delta E / Delta t_obs."""
    return D_over_c_s * dE_eV / dt_s


def run() -> dict:
    messengers = [
        {"name": "Fermi GRB 090510 photons", "E_eV": 30e9, "light_travel_Gyr": 7.0, "dt_s": 1.0,
         "comment": "GeV gamma-rays, z~0.9 -- the strongest single-messenger time-of-flight bound"},
        {"name": "LIGO/Virgo GW dispersion", "E_eV": 4e-12, "light_travel_Gyr": 1.3, "dt_s": 0.1,
         "comment": "kHz gravitons (~1e-12 eV), z~0.1 -- weak because the graviton energy is tiny"},
    ]
    rows = []
    for m in messengers:
        Dc = m["light_travel_Gyr"] * GYR_S
        b = e_qg_bound_linear(Dc, m["E_eV"], m["dt_s"])
        rows.append({**m, "E_QG_lower_bound_eV": b, "in_units_of_E_Planck": b / E_PLANCK_eV})
    # pure energy scaling at FIXED D, dt (isolates the linear E-dependence of the bound)
    energy_ratio = messengers[0]["E_eV"] / messengers[1]["E_eV"]
    Dc_ref, dt_ref = 1.0 * GYR_S, 1.0
    bound_ratio = (e_qg_bound_linear(Dc_ref, messengers[0]["E_eV"], dt_ref)
                   / e_qg_bound_linear(Dc_ref, messengers[1]["E_eV"], dt_ref))
    return {
        "version": VERSION,
        "method": ("linear (n=1) LIV time-of-flight bound E_QG > (D/c) Delta E / Delta t_obs; D = "
                   "light-travel distance; messenger energies from GRB photons vs LIGO gravitons; "
                   "plus the GW170817 GW-EM speed bound for the constant-offset sector"),
        "E_Planck_eV": E_PLANCK_eV,
        "messenger_bounds": rows,
        "gw170817_speed_bound": {"observable": "|Delta v / c| < 1e-15 (GW vs gamma, 40 Mpc, 1.7 s)",
                                 "sector": "n=0 constant offset / graviton mass -- the strongest there"},
        "energy_scaling": {"messenger_energy_ratio_grb_over_gw": energy_ratio,
                           "bound_ratio_at_fixed_D_dt": bound_ratio,
                           "scales_linearly": abs(bound_ratio / energy_ratio - 1) < 1e-9},
        "finding": (
            f"The linear-LIV time-of-flight bound reaches E_QG > {rows[0]['E_QG_lower_bound_eV']:.1e} "
            f"eV ~ {rows[0]['in_units_of_E_Planck']:.2f} E_Planck from a single 30 GeV GRB photon -- "
            "right at the Planck scale, the headline quantum-gravity-phenomenology result. The same "
            f"analysis on LIGO gravitons gives only E_QG > {rows[1]['E_QG_lower_bound_eV']:.1e} eV "
            f"(~{rows[1]['in_units_of_E_Planck']:.0e} E_Planck), ~22 orders of magnitude weaker, "
            "because the bound scales with the MESSENGER ENERGY and gravitons (~1e-12 eV) are ~1e40 "
            "times lower-energy than GeV gamma-rays. So gravitational waves are a POOR probe of "
            "energy-dependent (n>=1) LIV dispersion -- but the multi-messenger GW170817 GW-vs-photon "
            "SPEED comparison (|Delta v/c| < 1e-15) is instead the STRONGEST bound on the "
            "constant-offset (n=0 / graviton-mass) sector. The two channels are complementary: "
            "high-energy photons probe Planck-suppressed dispersion, GW170817 probes the constant "
            "speed offset -- together testing whether spacetime is smooth at the Planck length."
        ),
        "honest_scope": (
            "Order-of-magnitude time-of-flight reconstruction (linear n=1 leading; n=2 quadratic LIV "
            "is far weaker). The precise bounds use the cosmological distance integral with the "
            "(1+z) energy factors, the source-intrinsic emission-time systematics (the dominant "
            "uncertainty in GRB LIV bounds), and the detailed Fermi / LVC analyses -- not done here; "
            "the light-travel-distance approximation and representative (E, z, Delta t) give the "
            "right scale and the messenger-energy scaling, which is the point. The sign s (subluminal "
            "vs superluminal) is not fixed. Self-contained reconstruction of a real QG-phenomenology "
            "probe, not a published bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Amelino-Camelia et al., Nature 393 (1998) 763 -- quantum-gravity time-of-flight",
            "Abdo et al. (Fermi), Nature 462 (2009) 331 -- GRB 090510 LIV bound ~E_Planck",
            "Abbott et al. (LVC), ApJL 848 (2017) L13 -- GW170817 GW-EM speed; LVC TGR dispersion papers",
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
    print("messenger                     E_QG lower bound (eV)   / E_Planck")
    for r in res["messenger_bounds"]:
        print(f"  {r['name']:28s} {r['E_QG_lower_bound_eV']:.2e}            {r['in_units_of_E_Planck']:.2e}")
    print(f"\nGW170817 speed bound: {res['gw170817_speed_bound']['observable']}")
    print(f"energy scaling (fixed D,dt): bound ratio {res['energy_scaling']['bound_ratio_at_fixed_D_dt']:.2e} "
          f"== energy ratio {res['energy_scaling']['messenger_energy_ratio_grb_over_gw']:.2e} "
          f"(linear: {res['energy_scaling']['scales_linearly']})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
