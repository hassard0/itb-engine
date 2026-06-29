"""v2.278 - The Hulse-Taylor binary pulsar: the quadrupole formula and the first evidence for GWs.

A fresh sector (stepping off the black-hole cycles): the cleanest classical confirmation that
gravitational waves are real. A binary loses energy to gravitational radiation at the rate given by
the quadrupole formula (Peters-Mathews 1963; Peters 1964), so its orbit shrinks and its period
decays. For PSR B1913+16 (Hulse-Taylor) the predicted decay matches the measured value to ~0.1% -- the
1993 Nobel-winning indirect detection of GWs, two decades before LIGO.

    dP/dt = -(192 pi / 5) (G^{5/3} / c^5) (m1 m2 / M^{1/3}) (2 pi / P)^{5/3} f(e) ,

    f(e) = (1 + 73/24 e^2 + 37/96 e^4) / (1 - e^2)^{7/2}     (eccentricity enhancement, f(0)=1) ,

with M = m1 + m2. The high eccentricity of B1913+16 (e=0.617) boosts the emission ~12x over a circular
orbit (the periastron whips are where most GW power is radiated), and the orbit will merge in ~300 Myr.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.278"
DEFAULT_OUT = Path("experiments/results/v2.278/qnm_hulse_taylor_quadrupole.json")

G = 6.674e-11          # m^3 kg^-1 s^-2
C = 2.998e8            # m/s
MSUN = 1.989e30        # kg
YR_S = 3.156e7

# PSR B1913+16 parameters (Weisberg & Huang 2016)
HT = {"m1_msun": 1.4398, "m2_msun": 1.3886, "P_s": 27906.98, "e": 0.6171,
      "observed_Pdot": -2.398e-12, "observed_err": 0.004e-12}


def f_eccentricity(e: float) -> float:
    """GW-emission enhancement f(e) = (1 + 73/24 e^2 + 37/96 e^4)/(1-e^2)^{7/2}, f(0)=1."""
    return (1 + (73 / 24) * e**2 + (37 / 96) * e**4) / (1 - e**2) ** 3.5


def pdot_gw(m1_kg: float, m2_kg: float, P_s: float, e: float) -> float:
    """Orbital-period decay from GW emission (Peters 1964)."""
    M = m1_kg + m2_kg
    pref = -(192 * math.pi / 5) * (G ** (5 / 3) / C**5)
    return pref * (m1_kg * m2_kg / M ** (1 / 3)) * (2 * math.pi / P_s) ** (5 / 3) * f_eccentricity(e)


def semi_major_axis(m1_kg: float, m2_kg: float, P_s: float) -> float:
    """Kepler: a^3 = G M P^2 / (4 pi^2)."""
    return (G * (m1_kg + m2_kg) * P_s**2 / (4 * math.pi**2)) ** (1 / 3)


def merger_time_circular_yr(m1_kg: float, m2_kg: float, a_m: float) -> float:
    """Circular-orbit inspiral time tau = (5/256)(c^5/G^3) a^4/(m1 m2 M)."""
    M = m1_kg + m2_kg
    return (5 / 256) * (C**5 / G**3) * a_m**4 / (m1_kg * m2_kg * M) / YR_S


def run() -> dict:
    m1, m2 = HT["m1_msun"] * MSUN, HT["m2_msun"] * MSUN
    pdot = pdot_gw(m1, m2, HT["P_s"], HT["e"])
    fe = f_eccentricity(HT["e"])
    a = semi_major_axis(m1, m2, HT["P_s"])
    tau_circ = merger_time_circular_yr(m1, m2, a)
    # eccentric inspiral is shorter; leading correction ~ (1-e^2)^{7/2} (full Peters integral is coupled)
    tau_ecc = tau_circ * (1 - HT["e"] ** 2) ** 3.5

    ratio = pdot / HT["observed_Pdot"]

    checks = {
        "circular_limit_f_is_one": abs(f_eccentricity(0.0) - 1.0) < 1e-12,
        "eccentricity_enhances_emission": fe > 11.0 and fe < 13.0,   # HT e=0.617 -> ~11.85
        "f_monotonic_in_e": f_eccentricity(0.3) < f_eccentricity(0.6) < f_eccentricity(0.9),
        "predicted_matches_observed_within_1pct": abs(ratio - 1.0) < 0.01,
        "predicted_Pdot_order_2p4e_minus_12": -2.45e-12 < pdot < -2.35e-12,
        "merges_within_a_few_hundred_Myr": 1e8 < tau_ecc < 1e9,
    }

    return {
        "version": VERSION,
        "method": ("Peters 1964 quadrupole orbital decay dP/dt = -(192 pi/5)(G^{5/3}/c^5)"
                   "(m1 m2/M^{1/3})(2 pi/P)^{5/3} f(e), f(e)=(1+73/24 e^2+37/96 e^4)/(1-e^2)^{7/2}; "
                   "PSR B1913+16 parameters (Weisberg-Huang 2016)"),
        "hulse_taylor_params": HT,
        "f_eccentricity": fe,
        "predicted_Pdot": pdot,
        "observed_Pdot": HT["observed_Pdot"],
        "predicted_over_observed": ratio,
        "semi_major_axis_m": a,
        "merger_time_circular_yr": tau_circ,
        "merger_time_eccentric_yr": tau_ecc,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The quadrupole formula reproduces the Hulse-Taylor orbital decay to ~0.1%: for "
            "PSR B1913+16 (two ~1.4 Msun neutron stars, P=7.75 hr, e=0.617) Peters' formula predicts "
            f"dP/dt = {pdot:.4e}, versus the measured {HT['observed_Pdot']:.4e} -- a ratio of "
            f"{ratio:.4f}, agreement to better than 1%. The high eccentricity boosts the GW luminosity "
            f"by f(e) = {fe:.2f} over a circular orbit (most of the radiation comes from the fast "
            "periastron passage, where the quadrupole moment changes fastest), and the orbit will "
            f"spiral in and merge in ~{tau_ecc/1e6:.0f} Myr. This is the 1993 Nobel-winning indirect "
            "detection of gravitational waves -- the orbit is demonstrably losing exactly the energy "
            "the quadrupole formula says it radiates as GWs, two decades before LIGO saw them "
            "directly. It anchors the whole GW program (v2.266-v2.272): the same quadrupole emission "
            "whose stochastic background, polarizations and propagation those cycles probed is here "
            "measured, classically and unambiguously, in a single binary."
        ),
        "honest_scope": (
            "The Peters quadrupole formula and f(e) are exact leading-order results, and the predicted "
            "dP/dt uses the source-backed PSR B1913+16 parameters (Weisberg-Huang 2016); the ~0.1% "
            "agreement is the published result (after the small kinematic / galactic-acceleration "
            "correction to the OBSERVED value, which this experiment does not re-derive -- it compares "
            "to the already-corrected intrinsic value). The merger time uses the CIRCULAR-orbit Peters "
            "formula with a leading (1-e^2)^{7/2} eccentricity factor; the exact inspiral time needs "
            "the coupled da/dt, de/dt integral (the orbit circularizes as it shrinks), so ~300 Myr is "
            "order-correct, not exact. Point-mass, leading post-Newtonian quadrupole order. A "
            "classical-GR / GW-confirmation result, not an engine constraint refit."
        ),
        "references": [
            "Peters, Mathews, 'Gravitational radiation from point masses in a Keplerian orbit', Phys. Rev. 131 (1963) 435",
            "Peters, 'Gravitational radiation and the motion of two point masses', Phys. Rev. 136 (1964) B1224",
            "Weisberg, Huang, 'Relativistic measurements from timing the binary pulsar PSR B1913+16', ApJ 829 (2016) 55",
            "this repo: v2.266-v2.272 (gravitational-wave observables)",
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
    print("Hulse-Taylor binary pulsar PSR B1913+16 -- quadrupole orbital decay:")
    print(f"  f(e={HT['e']}) = {res['f_eccentricity']:.3f}  (circular f(0)=1)")
    print(f"  predicted dP/dt = {res['predicted_Pdot']:.4e}")
    print(f"  observed  dP/dt = {res['observed_Pdot']:.4e}")
    print(f"  predicted/observed = {res['predicted_over_observed']:.4f}")
    print(f"  merger in ~{res['merger_time_eccentric_yr']/1e6:.0f} Myr")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
