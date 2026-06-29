"""v2.266 - Graviton mass bounds from gravitational-wave dispersion (the low-energy mirror of LIV).

A fresh QG-phenomenology sector opening after the swampland arc (v2.254-v2.265). General relativity's
graviton is exactly massless; a graviton rest mass m_g would make gravitational waves DISPERSIVE,

    v_g / c = sqrt(1 - (m_g c^2 / E)^2)  ~  1 - (1/2)(m_g c^2 / E)^2 ,

so the high- and low-frequency parts of an inspiral signal arrive at slightly different times. Over a
cosmological distance D the spread between two frequencies f1 < f2 is

    Delta t = (D / 2c) (m_g c^2)^2 ( 1/E1^2 - 1/E2^2 ) ,   E = h f ,

and requiring it not to smear the observed waveform bounds m_g. LIGO/Virgo's GW catalog gives
m_g < 1.2e-22 eV/c^2, i.e. a Compton wavelength lambda_g = h c / (m_g c^2) > 1e13 km.

This is the LOW-energy mirror of the v2.251 Lorentz-violation probe: a graviton MASS makes the speed
deficit grow as 1/E^2 (matters most at LOW energy / long wavelength), whereas Planck-scale LIV makes
it grow as E^n (matters most at HIGH energy). Opposite energy dependence -- so the two probes are
complementary, not redundant, and the sign of the energy dependence is the discriminant.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.266"
DEFAULT_OUT = Path("experiments/results/v2.266/qnm_graviton_mass_dispersion.json")

HC_eVm = 1.2398e-6      # h*c in eV*m  (full Compton wavelength lambda = h c /(m c^2))
H_eVs = 4.1357e-15      # Planck constant in eV*s  (E = h f)
C_M_S = 2.998e8         # speed of light, m/s
MPC_M = 3.086e22        # 1 Mpc in metres

MG_BOUND_eV = 1.2e-22   # LVC graviton-mass bound (GW150914 / GWTC)


def compton_wavelength_m(m_eV: float) -> float:
    """Full graviton Compton wavelength lambda_g = h c / (m_g c^2)."""
    return HC_eVm / m_eV


def mass_from_wavelength_eV(lambda_m: float) -> float:
    """Inverse: graviton mass from a Compton wavelength."""
    return HC_eVm / lambda_m


def graviton_velocity_over_c(E_eV: float, m_eV: float) -> float:
    """Group velocity v_g/c = sqrt(1 - (m c^2 / E)^2)."""
    return math.sqrt(max(0.0, 1.0 - (m_eV / E_eV) ** 2))


def speed_deficit(E_eV: float, m_eV: float) -> float:
    """1 - v_g/c computed directly from the series 0.5 (m/E)^2 (avoids float cancellation:
    for m/E ~ 1e-11 the (m/E)^2 ~ 1e-22 term underflows inside sqrt(1 - ...) -> exactly 1.0)."""
    return 0.5 * (m_eV / E_eV) ** 2


def dispersion_delay_s(m_eV: float, f1_hz: float, f2_hz: float, D_m: float) -> float:
    """Arrival-time spread between f1 and f2 over distance D for a graviton of mass m."""
    e1, e2 = H_eVs * f1_hz, H_eVs * f2_hz
    return (D_m / (2.0 * C_M_S)) * m_eV**2 * (1.0 / e1**2 - 1.0 / e2**2)


def run() -> dict:
    # 1. mass <-> Compton wavelength at the LVC bound (reproduce lambda_g > 1e13 km)
    lam_m = compton_wavelength_m(MG_BOUND_eV)
    lam_km = lam_m / 1e3

    # 2. dispersion delay at the bound for representative GW events (band 35-250 Hz)
    events = [
        {"name": "GW150914", "D_Mpc": 410.0, "signal_duration_s": 0.2},
        {"name": "GW170817 (BNS)", "D_Mpc": 40.0, "signal_duration_s": 100.0},
        {"name": "a z~1 LISA/3G source", "D_Mpc": 6700.0, "signal_duration_s": 1.0},
    ]
    rows = []
    for ev in events:
        d_m = ev["D_Mpc"] * MPC_M
        dt = dispersion_delay_s(MG_BOUND_eV, 35.0, 250.0, d_m)
        rows.append({**ev, "dispersion_delay_s": dt,
                     "delay_over_signal": dt / ev["signal_duration_s"]})

    # 3. fractional speed deficit at a reference GW energy (4e-12 eV ~ 1 kHz, the v2.251 value)
    e_ref = 4e-12
    deficit = speed_deficit(e_ref, MG_BOUND_eV)   # 1 - v/c via the series (float-cancellation-safe)

    # 4. consistency with the GW170817 speed bound |Delta v/c| < 1e-15
    consistent_with_gw170817 = deficit < 1e-15

    return {
        "version": VERSION,
        "method": ("massive-graviton GW dispersion v_g/c = sqrt(1-(m c^2/E)^2); arrival spread "
                   "Delta t = (D/2c)(m c^2)^2(1/E1^2-1/E2^2); Compton lambda_g = h c/(m c^2); "
                   "LVC bound m_g < 1.2e-22 eV"),
        "graviton_mass_bound_eV": MG_BOUND_eV,
        "compton_wavelength_m": lam_m,
        "compton_wavelength_km": lam_km,
        "reproduces_lvc_1e13_km": 0.5e13 < lam_km < 5e13,
        "event_dispersion": rows,
        "reference_energy_eV": e_ref,
        "speed_deficit_at_ref": deficit,
        "consistent_with_gw170817_speed_bound": consistent_with_gw170817,
        "contrast_with_liv_v2251": {
            "graviton_mass": "speed deficit ~ (m c^2/E)^2 grows as 1/E^2 -- LOW-energy / long-wavelength",
            "planck_liv": "speed deficit ~ (E/E_QG)^n grows as E^n -- HIGH-energy / short-wavelength",
            "discriminant": "the SIGN of the energy dependence (n<0 mass vs n>0 LIV)",
        },
        "finding": (
            "A graviton rest mass makes gravitational waves dispersive, v_g/c = sqrt(1-(m c^2/E)^2). "
            f"At the LVC bound m_g < 1.2e-22 eV the Compton wavelength is lambda_g = {lam_km:.2e} km "
            "-- reproducing the published lambda_g > 1e13 km. The mechanism that sets the bound: over "
            f"GW150914's ~410 Mpc the 35-250 Hz band would spread by {rows[0]['dispersion_delay_s']*1e3:.1f} "
            "ms, comparable to the ~0.2 s signal, so a heavier graviton would visibly smear the chirp "
            "-- which is why the bound lands near 1e-22 eV. The speed deficit at a reference kHz "
            f"graviton is only 1-v/c ~ {deficit:.1e}, far inside the GW170817 multimessenger "
            "speed bound |Delta v/c| < 1e-15 (so that constant-offset bound does NOT constrain a mass "
            "this small -- the dispersive in-band test is the sensitive one). This is the LOW-energy "
            "mirror of the v2.251 Lorentz-violation probe: a graviton mass makes the deficit grow as "
            "1/E^2 (worst at low energy), Planck-scale LIV makes it grow as E^n (worst at high "
            "energy) -- opposite energy dependence, so the two probes are complementary and the sign "
            "of the energy dependence is the discriminant. Massless graviton = exact GR; any nonzero "
            "m_g is a falsifiable departure."
        ),
        "honest_scope": (
            "The LVC bound m_g < 1.2e-22 eV is the source-backed value; here the dispersion-delay "
            "estimate reproduces its ORDER OF MAGNITUDE via the simple two-frequency time-spread "
            "heuristic, not the full matched-filter waveform-phase analysis LIGO actually uses (which "
            "folds the (m_g/E)^2 term into the inspiral phase). The Compton-wavelength inversion is "
            "exact. Static Yukawa-potential bounds (solar-system planetary precession, galaxy-cluster "
            "dynamics) are complementary and in places tighter (m_g <~ 1e-29 eV) but more "
            "model-dependent, so the clean dynamical GW bound is quoted as primary. A consistent "
            "nonlinear massive-gravity theory (the vDVZ discontinuity, requiring the dRGT ghost-free "
            "construction) is a separate theoretical issue not modelled here. A QG-phenomenology "
            "probe, not an engine constraint refit."
        ),
        "references": [
            "Abbott et al. (LIGO/Virgo), 'Tests of general relativity with GW150914', PRL 116 (2016) 221101",
            "Abbott et al. (LIGO/Virgo), GWTC test-of-GR papers (graviton-mass bound m_g < 1.2e-22 eV)",
            "Will, 'Bounding the mass of the graviton using gravitational-wave observations', PRD 57 (1998) 2061",
            "this repo: v2.251 (Lorentz-violation dispersion), v2.253 (graviton quantization)",
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
    print(f"graviton mass bound m_g < {res['graviton_mass_bound_eV']:.1e} eV")
    print(f"  -> Compton wavelength lambda_g = {res['compton_wavelength_km']:.2e} km "
          f"(reproduces >1e13 km: {res['reproduces_lvc_1e13_km']})")
    print("  event           D(Mpc)   dispersion delay   delay/signal")
    for r in res["event_dispersion"]:
        print(f"  {r['name']:22s} {r['D_Mpc']:7.0f}   {r['dispersion_delay_s']*1e3:8.2f} ms     "
              f"{r['delay_over_signal']:.3e}")
    print(f"  speed deficit at {res['reference_energy_eV']:.0e} eV: 1-v/c = {res['speed_deficit_at_ref']:.2e} "
          f"(within GW170817 bound: {res['consistent_with_gw170817_speed_bound']})")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
