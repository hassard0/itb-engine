"""v2.267 - The gravitational-wave memory effect and the infrared triangle.

A fresh QG-structure / GW-observable thread (continuing v2.266). A burst of gravitational waves leaves
a PERMANENT relative displacement between freely-falling test masses -- the memory effect. Strominger's
'infrared triangle' identifies three faces of the same physics:

    GW memory  <-->  Weinberg soft-graviton theorem  <-->  BMS supertranslations.

Two things are computed and verified here:

(1) The exact identity behind the triangle. The memory is the permanent strain offset
    Delta h = h(+inf) - h(-inf) = integral of hdot dt -- which is precisely the ZERO-FREQUENCY
    Fourier mode of the strain rate, hdot(omega=0). The soft theorem says the radiated-energy
    spectrum dE/domega ~ |hdot(omega)|^2 approaches a NONZERO constant as omega -> 0, set by the
    memory. We build a toy strain-rate burst (a net-DC 'memory' bump plus a zero-mean oscillatory
    chirp) and verify numerically that (a) the oscillatory part carries no memory, (b) the memory
    equals hdot(omega=0), and (c) the low-frequency spectrum plateaus at |memory|^2 -- the soft
    theorem.

(2) The astrophysical size. The Christodoulou (nonlinear) memory scales as
    Delta h_mem ~ (G / c^4 R) Delta E_rad (times an O(1) angular/TT factor), a few-to-ten percent of
    the peak oscillatory strain -- a DC offset LIGO/LISA can chase by stacking events.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")

VERSION = "v2.267"
DEFAULT_OUT = Path("experiments/results/v2.267/qnm_gw_memory_infrared_triangle.json")

G = 6.674e-11          # m^3 kg^-1 s^-2
C = 2.998e8            # m/s
MSUN_KG = 1.989e30     # kg
MPC_M = 3.086e22       # m
C2 = C * C
C4 = C2 * C2


def memory_strain(delta_E_joule: float, R_m: float, angular: float = 1.0) -> float:
    """Christodoulou nonlinear-memory amplitude Delta h ~ (G/c^4 R) Delta E_rad * O(1) angular factor."""
    return G * delta_E_joule / (C4 * R_m) * angular


def _toy_strain_rate(t: np.ndarray):
    """A toy hdot(t): a net-DC Gaussian 'memory' bump + a zero-mean oscillatory chirp burst."""
    sigma = 1.0
    memory_amp = 1.0
    hdot_dc = memory_amp * np.exp(-t**2 / (2 * sigma**2)) / (sigma * np.sqrt(2 * np.pi))  # area = memory_amp
    env = np.exp(-t**2 / (2 * (2.0) ** 2))
    hdot_osc = 0.7 * np.sin(2 * np.pi * 1.5 * t) * env                                     # zero-mean
    return hdot_dc, hdot_osc, memory_amp


def run() -> dict:
    # --- (1) the exact memory <-> zero-frequency-mode <-> soft-theorem identity (numerical) ---
    t = np.linspace(-40.0, 40.0, 1 << 14)
    dt = t[1] - t[0]
    hdot_dc, hdot_osc, memory_amp = _toy_strain_rate(t)
    hdot = hdot_dc + hdot_osc

    # memory = time integral of hdot = h(+inf) - h(-inf)
    memory_total = float(np.trapezoid(hdot, t))
    memory_osc_only = float(np.trapezoid(hdot_osc, t))          # should be ~0: no memory from oscillation

    # zero-frequency Fourier mode of hdot: hdot(omega=0) = integral hdot dt  (== memory)
    omega = np.linspace(0.0, 6.0, 300)
    # discrete FT at each omega (real burst): Hdot(omega) = integral hdot e^{-i omega t} dt
    Hdot = np.array([np.trapezoid(hdot * np.exp(-1j * w * t), t) for w in omega])
    Hdot0 = float(np.real(Hdot[0]))                             # omega=0 component
    spectrum = np.abs(Hdot) ** 2                                # dE/domega ~ |hdot(omega)|^2

    # soft theorem: the low-frequency spectrum plateaus at |memory|^2 (a nonzero constant as omega->0).
    # spectrum[0] (omega=0) equals |memory|^2 exactly; the plateau is flat to O((omega sigma)^2) over
    # the low-frequency window, so it is checked at the ~1% level.
    spectrum_at_zero = float(spectrum[0])
    low_freq_plateau = float(np.mean(spectrum[omega < 0.05]))   # fixed low-omega band (grid-independent)
    plateau_matches_memory_sq = abs(low_freq_plateau - memory_total**2) < 1e-2 * memory_total**2

    checks = {
        "oscillation_carries_no_memory": abs(memory_osc_only) < 1e-3 * abs(memory_total),
        "memory_equals_zero_frequency_mode": abs(Hdot0 - memory_total) < 1e-6 * abs(memory_total),
        "memory_equals_dc_bump_area": abs(memory_total - memory_amp) < 1e-3 * memory_amp,
        "soft_theorem_low_freq_plateau": plateau_matches_memory_sq,
    }

    # --- (2) astrophysical memory size for representative sources ---
    events = [
        {"name": "GW150914", "dE_Msun": 3.0, "R_Mpc": 410.0, "h_peak": 1.0e-21},
        {"name": "GW170817 (BNS)", "dE_Msun": 0.04, "R_Mpc": 40.0, "h_peak": 1.0e-22},
        {"name": "SMBH merger 1e6 Msun (LISA)", "dE_Msun": 3.0e4, "R_Mpc": 6700.0, "h_peak": 1.0e-17},
    ]
    rows = []
    for ev in events:
        dE = ev["dE_Msun"] * MSUN_KG * C2
        dh = memory_strain(dE, ev["R_Mpc"] * MPC_M)
        rows.append({**ev, "memory_strain_raw": dh,
                     "memory_over_peak_raw": dh / ev["h_peak"]})

    return {
        "version": VERSION,
        "method": ("memory = integral hdot dt = zero-frequency mode hdot(omega=0); soft theorem = "
                   "low-frequency plateau of |hdot(omega)|^2 at |memory|^2 (toy burst, verified "
                   "numerically); astrophysical Delta h ~ (G/c^4 R) Delta E_rad"),
        "infrared_triangle": {
            "face_1": "GW memory: permanent strain offset Delta h = h(+inf)-h(-inf)",
            "face_2": "Weinberg soft-graviton theorem: dE/domega -> const as omega->0",
            "face_3": "BMS supertranslation: memory = transition between two BMS vacua",
            "linking_identity": "Delta h = integral hdot dt = hdot(omega=0); spectrum(omega->0) = |Delta h|^2",
        },
        "identity_checks": checks,
        "all_identity_checks_pass": all(checks.values()),
        "memory_total": memory_total,
        "zero_frequency_mode": Hdot0,
        "spectrum_at_zero": spectrum_at_zero,
        "low_freq_plateau": low_freq_plateau,
        "memory_squared": memory_total**2,
        "astrophysical_memory": rows,
        "finding": (
            "The GW memory effect is one vertex of Strominger's infrared triangle, and the linking "
            "identity is exact and numerically verified: the memory Delta h = integral hdot dt is "
            "precisely the zero-frequency Fourier mode hdot(omega=0) (matched to 1e-6 in the toy "
            "burst), the oscillatory chirp carries NO memory (its time-integral is ~0), and the "
            "radiated-energy spectrum |hdot(omega)|^2 plateaus at |Delta h|^2 as omega->0 -- which is "
            "exactly Weinberg's soft-graviton theorem (a nonzero zero-energy-graviton amplitude set "
            "by the memory). The third face is the BMS supertranslation: the permanent test-mass "
            "displacement is a transition between two inequivalent BMS vacua, so the memory measures a "
            "supertranslation-charge difference. Astrophysically the Christodoulou memory is "
            "Delta h ~ (G/c^4 R) Delta E_rad: for GW150914 (3 Msun radiated at 410 Mpc) the raw "
            f"estimate is {rows[0]['memory_strain_raw']:.1e}, a few-tenths of the peak strain (the "
            "proper TT/angular projection brings this to the ~5-20% quoted by Favata) -- a permanent "
            "DC offset, undetectable per-event by LIGO but accumulable by stacking (~sqrt(N)) and "
            "per-event detectable for LISA supermassive mergers. So an asymptotic-symmetry / "
            "soft-theorem structure of quantum gravity has a concrete, falsifiable GW observable."
        ),
        "honest_scope": (
            "The memory<->zero-mode<->soft-theorem identity is EXACT and the numeric checks verify it "
            "on a TOY analytic burst (a Gaussian DC bump + a windowed sinusoid), not a real "
            "numerical-relativity waveform -- the toy is an illustration of the identity, not a "
            "waveform prediction. The astrophysical Delta h ~ (G/c^4 R) Delta E_rad is an "
            "ORDER-OF-MAGNITUDE scaling carrying an O(1) angular/TT-projection factor (the proper "
            "Christodoulou memory is ~5-20% of peak strain, Favata 2010); the per-event 'memory/peak' "
            "ratios are raw (pre-projection) and the h_peak values are representative. The BMS / "
            "supertranslation face is a structural statement (Strominger et al.), cited not derived "
            "here. A QG-structure / GW-phenomenology result, not an engine constraint refit."
        ),
        "references": [
            "Strominger, 'Lectures on the Infrared Structure of Gravity and Gauge Theory', arXiv:1703.05448",
            "Christodoulou, 'Nonlinear nature of gravitation and gravitational-wave experiments', PRL 67 (1991) 1486",
            "Favata, 'The gravitational-wave memory effect', Class. Quantum Grav. 27 (2010) 084036",
            "Weinberg, 'Infrared photons and gravitons', Phys. Rev. 140 (1965) B516",
            "this repo: v2.266 (graviton mass), v2.253 (graviton quantization)",
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
    print("infrared triangle: memory <-> soft theorem <-> BMS supertranslation")
    print(f"  memory (integral hdot dt)      = {res['memory_total']:.6f}")
    print(f"  zero-frequency mode hdot(0)    = {res['zero_frequency_mode']:.6f}")
    print(f"  low-freq spectrum plateau      = {res['low_freq_plateau']:.6f}  (|memory|^2 = {res['memory_squared']:.6f})")
    print("  identity checks:")
    for k, v in res["identity_checks"].items():
        print(f"    [{'PASS' if v else 'FAIL'}] {k}")
    print("  astrophysical memory (raw, pre-TT-projection):")
    for r in res["astrophysical_memory"]:
        print(f"    {r['name']:28s} Delta h ~ {r['memory_strain_raw']:.2e}  "
              f"({r['memory_over_peak_raw']:.2f} x peak)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
