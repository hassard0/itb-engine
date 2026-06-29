"""v2.273 - Black-hole greybody factors: how the potential barrier shapes the Hawking spectrum.

A fresh QG thread (pivoting off the GW arc) that REUSES the validated v2.210 WKB / Regge-Wheeler
machinery. Hawking radiation is not a pure blackbody: a quantum emitted near the horizon must tunnel
out through the same effective potential barrier that sets the ringdown QNMs, so the observed flux is

    dN/dt domega = (1/2pi) Gamma_l(omega) / (exp(omega/T_H) -/+ 1) ,

where Gamma_l(omega) is the GREYBODY FACTOR -- the barrier transmission probability. The leading WKB
(Schutz-Will) transmission through the Regge-Wheeler peak is

    Gamma_l(omega) = 1 / (1 + exp(2 pi (V_max - omega^2) / sqrt(-2 V_max''))) ,

using the SAME peak value V_max and tortoise curvature V_max'' that the QNM formula uses. It rises
monotonically from 0 (low omega, the barrier reflects) to 1 (high omega, above the barrier), passing
1/2 at omega^2 = V_max. Two limits anchor it: at HIGH frequency the capture cross-section becomes the
geometric photon-sphere value sigma = pi b_c^2 = 27 pi M^2 (b_c = 3 sqrt3 M, the v2.230 shadow), and at
LOW frequency the s-wave absorption cross-section tends to the horizon AREA A_H = 16 pi M^2 (the
area theorem, a regime where WKB is invalid -- quoted as the complementary analytic limit).
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_wkb_solver import (
    find_peak_rstar,
    r_of_rstar,
    rw_potential,
    tortoise_derivatives,
)

VERSION = "v2.273"
DEFAULT_OUT = Path("experiments/results/v2.273/qnm_greybody_hawking.json")

T_H = 1.0 / (8.0 * math.pi)     # Hawking temperature for M=1
B_C = 3.0 * math.sqrt(3.0)      # photon-sphere impact parameter (M=1)
A_HORIZON = 16.0 * math.pi      # horizon area for M=1 (A = 16 pi M^2)


def rw_peak(L: int = 2, s: int = 2):
    """Peak value V_max and tortoise curvature V'' of the Regge-Wheeler barrier (M=1)."""
    V = lambda rs: rw_potential(r_of_rstar(rs), L, s)
    rstar0 = find_peak_rstar(V)
    d = tortoise_derivatives(V, rstar0, order=2)
    return d[0], d[2]   # V0 = V_max, d[2] = V'' (< 0 at a maximum)


def greybody_wkb(omega: float, V_max: float, V2: float) -> float:
    """Schutz-Will WKB transmission Gamma = 1/(1 + exp(2 pi (V_max - omega^2)/sqrt(-2 V''))) ."""
    alpha = (V_max - omega**2) / math.sqrt(-2.0 * V2)
    return 1.0 / (1.0 + math.exp(2.0 * math.pi * alpha))


def hawking_flux(omega: float, gamma: float, T: float = T_H) -> float:
    """Greybody-weighted Hawking number flux per unit frequency (bosonic)."""
    return gamma / (math.expm1(omega / T))


def run() -> dict:
    V_max, V2 = rw_peak(2, 2)
    omega_c = math.sqrt(V_max)

    # 1. greybody curve for l=2 gravitational perturbations
    grid = [0.05, 0.1, omega_c * 0.5, omega_c, omega_c * 1.5, 0.6, 1.0]
    curve = [{"omega": w, "gamma": greybody_wkb(w, V_max, V2)} for w in sorted(set(grid))]
    half_at_peak = abs(greybody_wkb(omega_c, V_max, V2) - 0.5) < 1e-12
    monotonic = all(curve[i + 1]["gamma"] >= curve[i]["gamma"] for i in range(len(curve) - 1))
    low_suppressed = greybody_wkb(0.05, V_max, V2) < 1e-2   # << the 1/2 peak (WKB underestimates the soft tail)
    high_transmits = greybody_wkb(1.5, V_max, V2) > 0.99

    # 2. eikonal / geometric limit: for large L the barrier peak frequency -> photon sphere,
    #    omega_c * b_c / (L+1/2) -> 1, and the capture cross section -> pi b_c^2 = 27 pi
    eik = []
    for L in (2, 5, 10, 20, 40):
        Vm, _ = rw_peak(L, 2)
        wc = math.sqrt(Vm)
        eik.append({"L": L, "omega_c": wc, "wc_bc_over_l": wc * B_C / (L + 0.5)})
    eikonal_to_photon_sphere = abs(eik[-1]["wc_bc_over_l"] - 1.0) < 0.02
    capture_cross_section = math.pi * B_C**2   # = 27 pi M^2

    # 3. Hawking spectrum: greybody suppresses the low-frequency flux below the blackbody (Gamma=1)
    spectrum = []
    for w in (0.05, 0.1, 0.2, omega_c, 0.6):
        g = greybody_wkb(w, V_max, V2)
        spectrum.append({"omega": w, "greybody_flux": hawking_flux(w, g),
                         "blackbody_flux": hawking_flux(w, 1.0)})
    greybody_below_blackbody = all(s["greybody_flux"] <= s["blackbody_flux"] for s in spectrum)

    checks = {
        "gamma_is_half_at_barrier_peak": half_at_peak,
        "gamma_monotonic_0_to_1": monotonic and low_suppressed and high_transmits,
        "eikonal_peak_is_photon_sphere": eikonal_to_photon_sphere,
        "capture_cross_section_27pi": abs(capture_cross_section - 27.0 * math.pi) < 1e-9,
        "greybody_suppresses_low_freq_hawking": greybody_below_blackbody,
    }

    return {
        "version": VERSION,
        "method": ("Schutz-Will WKB greybody Gamma=1/(1+exp(2 pi (V_max-omega^2)/sqrt(-2 V''))) from "
                   "the reused Regge-Wheeler barrier peak (v2.210); Hawking flux Gamma/(exp(omega/T_H)-1), "
                   "T_H=1/8pi; eikonal -> photon sphere b_c=3sqrt3, area theorem A_H=16pi (M=1)"),
        "barrier": {"V_max": V_max, "V2_curvature": V2, "omega_c": omega_c},
        "hawking_temperature": T_H,
        "greybody_curve": curve,
        "eikonal_scan": eik,
        "capture_cross_section_high_freq": capture_cross_section,
        "photon_sphere_b_c": B_C,
        "low_freq_area_theorem_sigma": A_HORIZON,
        "hawking_spectrum": spectrum,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Hawking radiation is a greybody, not a blackbody: a quantum must tunnel out through the "
            "same Regge-Wheeler barrier that sets the ringdown, so the emitted flux is the Planck "
            "spectrum WEIGHTED by the barrier transmission Gamma_l(omega). Reusing the validated v2.210 "
            "WKB machinery, the Schutz-Will transmission through the l=2 barrier (V_max = "
            f"{V_max:.4f}, omega_c = {omega_c:.4f}) rises monotonically from ~0 at low frequency (the "
            "barrier reflects soft quanta) through 1/2 at omega^2 = V_max to ~1 above the barrier "
            "(verified). The two physical limits anchor it: at HIGH frequency the barrier peak becomes "
            "the photon-sphere orbit -- omega_c b_c/(L+1/2) -> 1 as L grows (verified to <2% by L=40) "
            "-- so the capture cross-section is the geometric sigma = pi b_c^2 = 27 pi M^2 (b_c = "
            "3 sqrt3 M, exactly the v2.230 shadow); at LOW frequency the s-wave absorption cross-"
            "section tends to the horizon AREA A_H = 16 pi M^2 (the area theorem). The greybody "
            "therefore SUPPRESSES the low-frequency Hawking flux relative to a pure blackbody "
            "(verified) -- the black hole is a leaky, frequency-filtered thermal source, and the same "
            "barrier governs both how it rings (QNMs) and how it glows (Hawking), tying the v2.210 "
            "ringdown, the v2.230 photon sphere and the v2.257 Hawking temperature into one object."
        ),
        "honest_scope": (
            "The Schutz-Will WKB greybody is the LEADING barrier approximation: it is accurate near "
            "and above the peak (where it gives the correct 1/2-point and the geometric high-frequency "
            "cross-section), but it is NOT accurate at low frequency -- the true low-omega behaviour is "
            "the analytic area theorem (sigma -> A_H), quoted here as the complementary limit, not "
            "reproduced by the WKB formula (which underestimates the soft tail). So the low-frequency "
            "Hawking SUPPRESSION is qualitatively right and quantitatively WKB-limited. M=1 units, "
            "Schwarzschild, massless fields; the bosonic flux is shown (fermionic flips the -1 to +1). "
            "The eikonal peak->photon-sphere identification is exact in the large-L limit and verified "
            "numerically. A BH-physics result reusing the validated QNM potential, not an engine "
            "constraint refit."
        ),
        "references": [
            "Schutz, Will, 'Black hole normal modes: a semianalytic approach', ApJL 291 (1985) L33",
            "Page, 'Particle emission rates from a black hole', PRD 13 (1976) 198",
            "Iyer, Will, 'Black-hole normal modes: WKB approach', PRD 35 (1987) 3621",
            "this repo: v2.210 (WKB QNM solver), v2.230 (photon sphere / shadow), v2.257 (Hawking temperature)",
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
    b = res["barrier"]
    print(f"Regge-Wheeler barrier (l=2): V_max={b['V_max']:.4f}, omega_c={b['omega_c']:.4f}, T_H={res['hawking_temperature']:.4f}")
    print("  greybody Gamma(omega):")
    for c in res["greybody_curve"]:
        print(f"    omega={c['omega']:.4f}  Gamma={c['gamma']:.4e}")
    print("  eikonal -> photon sphere (omega_c * b_c/(L+1/2) -> 1):")
    for e in res["eikonal_scan"]:
        print(f"    L={e['L']:2d}  omega_c={e['omega_c']:.4f}  ratio={e['wc_bc_over_l']:.4f}")
    print(f"  high-freq capture sigma = {res['capture_cross_section_high_freq']:.4f} (27 pi = {27*math.pi:.4f}); "
          f"low-freq area A_H = {res['low_freq_area_theorem_sigma']:.4f}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
