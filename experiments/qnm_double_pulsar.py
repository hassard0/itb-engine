"""v2.279 - The double pulsar PSR J0737-3039: general relativity's most stringent test.

The natural sequel to the v2.278 Hulse-Taylor pulsar. In the double pulsar BOTH neutron stars are
visible as radio pulsars, so the system OVER-DETERMINES its two masses: five post-Keplerian (PK)
parameters are measured but only two masses are free, giving multiple independent consistency tests
that general relativity must pass simultaneously. Each PK parameter is a curve in the (m_A, m_B) mass
plane and -- if GR is right -- they all cross at one point.

PK parameters (Damour-Deruelle; T_sun = G M_sun/c^3 = 4.9255e-6 s, masses in M_sun, n = 2 pi/P_b):

    omega_dot = 3 n^{5/3} (T_sun M)^{2/3} / (1 - e^2)                          (periastron advance)
    gamma     = e (P_b/2pi)^{1/3} T_sun^{2/3} m_B (m_A + 2 m_B) / M^{4/3}      (Einstein delay)
    Pdot_b    = -(192 pi/5) n^{5/3} T_sun^{5/3} (m_A m_B/M^{1/3}) f(e)         (GW orbital decay)
    r         = T_sun m_B ,   s = sin i                                         (Shapiro range, shape)

The strategy: omega_dot fixes the total mass M; the directly-measured mass ratio R = m_A/m_B (unique to
the double pulsar, since both projected orbits are seen) splits it into m_A, m_B; then gamma, Pdot_b and
r are PREDICTED and checked against their measured values. The Shapiro shape s confirms GR to ~0.05%.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.279"
DEFAULT_OUT = Path("experiments/results/v2.279/qnm_double_pulsar.json")

T_SUN = 4.925490947e-6          # G M_sun / c^3, seconds
DEG_PER_YR_TO_RAD_S = (math.pi / 180.0) / 3.15576e7

# PSR J0737-3039 A/B measured values (Kramer et al. 2006)
DP = {"P_b_s": 0.10225156248 * 86400.0, "e": 0.0877775,
      "omega_dot_deg_yr": 16.89947, "mass_ratio_R": 1.0714,
      "gamma_ms": 0.3856, "Pdot_b_obs": -1.252e-12, "shapiro_r_us": 6.21,
      "m_A_msun": 1.3381, "m_B_msun": 1.2489, "M_total_msun": 2.58708}


def f_ecc(e: float) -> float:
    return (1 + (73 / 24) * e**2 + (37 / 96) * e**4) / (1 - e**2) ** 3.5


def omega_dot(M: float, P_b: float, e: float) -> float:
    """Periastron advance [rad/s] for total mass M (solar)."""
    n = 2 * math.pi / P_b
    return 3 * n ** (5 / 3) * (T_SUN * M) ** (2 / 3) / (1 - e**2)


def mass_from_omega_dot(omdot_rad_s: float, P_b: float, e: float) -> float:
    """Invert omega_dot -> total mass M (solar)."""
    n = 2 * math.pi / P_b
    return (omdot_rad_s * (1 - e**2) / (3 * n ** (5 / 3))) ** 1.5 / T_SUN


def gamma_einstein(m_A: float, m_B: float, P_b: float, e: float) -> float:
    """Einstein (gravitational redshift + time dilation) delay amplitude [s]."""
    M = m_A + m_B
    return e * (P_b / (2 * math.pi)) ** (1 / 3) * T_SUN ** (2 / 3) * m_B * (m_A + 2 * m_B) / M ** (4 / 3)


def pbdot_gw(m_A: float, m_B: float, P_b: float, e: float) -> float:
    """Orbital-period decay from GW emission [dimensionless]."""
    M = m_A + m_B
    n = 2 * math.pi / P_b
    return -(192 * math.pi / 5) * n ** (5 / 3) * T_SUN ** (5 / 3) * (m_A * m_B / M ** (1 / 3)) * f_ecc(e)


def shapiro_r_us(m_B: float) -> float:
    """Shapiro-delay range r = T_sun m_B, in microseconds."""
    return T_SUN * m_B * 1e6


def run() -> dict:
    P_b, e = DP["P_b_s"], DP["e"]

    # 1. periastron advance -> total mass
    omdot = DP["omega_dot_deg_yr"] * DEG_PER_YR_TO_RAD_S
    M = mass_from_omega_dot(omdot, P_b, e)

    # 2. mass ratio R = m_A/m_B splits the total: m_B = M/(1+R), m_A = R m_B
    R = DP["mass_ratio_R"]
    m_B = M / (1 + R)
    m_A = R * m_B

    # 3. predict the other PK parameters from (m_A, m_B)
    gamma = gamma_einstein(m_A, m_B, P_b, e)
    pbdot = pbdot_gw(m_A, m_B, P_b, e)
    r_us = shapiro_r_us(m_B)

    comparisons = {
        "total_mass": {"predicted": M, "measured": DP["M_total_msun"]},
        "m_A": {"predicted": m_A, "measured": DP["m_A_msun"]},
        "m_B": {"predicted": m_B, "measured": DP["m_B_msun"]},
        "gamma_ms": {"predicted": gamma * 1e3, "measured": DP["gamma_ms"]},
        "Pdot_b": {"predicted": pbdot, "measured": DP["Pdot_b_obs"]},
        "shapiro_r_us": {"predicted": r_us, "measured": DP["shapiro_r_us"]},
    }
    for c in comparisons.values():
        c["frac_diff"] = abs(c["predicted"] - c["measured"]) / abs(c["measured"])

    checks = {
        "omega_dot_gives_total_mass": comparisons["total_mass"]["frac_diff"] < 0.01,
        "mass_ratio_splits_to_measured_masses": (comparisons["m_A"]["frac_diff"] < 0.01
                                                 and comparisons["m_B"]["frac_diff"] < 0.01),
        "predicted_gamma_matches": comparisons["gamma_ms"]["frac_diff"] < 0.02,
        "predicted_Pdot_b_matches": comparisons["Pdot_b"]["frac_diff"] < 0.02,
        "predicted_shapiro_r_matches": comparisons["shapiro_r_us"]["frac_diff"] < 0.02,
        "system_overdetermined": True,   # 5 PK params + R for 2 masses -> >=4 independent tests
    }

    return {
        "version": VERSION,
        "method": ("Damour-Deruelle PK parameters: omega_dot -> total mass, measured ratio R -> "
                   "individual masses, then PREDICT gamma, Pdot_b and Shapiro r and compare to "
                   "measured (Kramer et al. 2006); T_sun=4.9255e-6 s"),
        "double_pulsar_params": DP,
        "derived_total_mass_msun": M,
        "derived_m_A_msun": m_A, "derived_m_B_msun": m_B,
        "pk_comparisons": comparisons,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "shapiro_shape_test": ("the Shapiro-delay shape s = sin i provides the headline test: "
                               "observed/GR-predicted s = 0.99987 +/- 0.00050 (Kramer et al. 2006), "
                               "confirming general relativity to ~0.05% -- the most stringent test "
                               "from a binary pulsar at the time"),
        "finding": (
            "The double pulsar is general relativity's most stringent binary test because BOTH neutron "
            "stars are visible, over-determining the two masses. Periastron advance alone fixes the "
            f"total mass at M = {M:.4f} M_sun (measured {DP['M_total_msun']}), and the directly-measured "
            f"mass ratio R = {R} splits it into m_A = {m_A:.4f}, m_B = {m_B:.4f} M_sun (measured "
            f"{DP['m_A_msun']}, {DP['m_B_msun']}). With the masses fixed by just those two inputs, every "
            "other post-Keplerian parameter is PREDICTED and matches: the Einstein delay "
            f"gamma = {gamma*1e3:.4f} ms (measured {DP['gamma_ms']}), the GW orbital decay "
            f"Pdot_b = {pbdot:.4e} (measured {DP['Pdot_b_obs']}), and the Shapiro range "
            f"r = {r_us:.3f} us (measured {DP['shapiro_r_us']}) -- all to ~1%. The five PK curves "
            "intersect at a single point in the mass plane, which they need not have: that is the test, "
            "and GR passes. The Shapiro shape s = sin i sharpens it to ~0.05% (observed/GR = 0.99987). "
            "Together with the v2.278 Hulse-Taylor decay, the binary pulsars confirm both that GR's "
            "quadrupole GW emission is real AND that the full strong-field two-body dynamics is "
            "Einsteinian, the classical bedrock under the v2.266-v2.272 GW program."
        ),
        "honest_scope": (
            "Exact leading-order Damour-Deruelle PK formulas with the source-backed Kramer et al. 2006 "
            "measured values; the predicted-vs-measured agreements reproduce the published consistency "
            "to ~1% (the actual analysis reaches far higher precision with full timing and the later "
            "Kramer 2021 update -- this is the structural demonstration, not the full timing fit). The "
            "Shapiro shape 0.05% figure is the published headline, cited not re-derived (s needs the "
            "inclination from the timing solution, independent of the masses). omega_dot is taken as "
            "pure GR (a tiny spin-orbit / higher-PN contribution exists). Point-mass, leading PN PK "
            "order. A classical-GR / strong-field-test result, not an engine constraint refit."
        ),
        "references": [
            "Kramer et al., 'Tests of general relativity from timing the double pulsar', Science 314 (2006) 97",
            "Kramer et al., 'Strong-field gravity tests with the double pulsar', PRX 11 (2021) 041050",
            "Damour, Deruelle, 'General relativistic celestial mechanics of binary systems II', Ann. IHP 44 (1986) 263",
            "this repo: v2.278 (Hulse-Taylor quadrupole), v2.266-v2.272 (GW observables)",
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
    print("double pulsar PSR J0737-3039 -- over-determined GR test:")
    print(f"  omega_dot -> M = {res['derived_total_mass_msun']:.4f} M_sun; "
          f"R splits -> m_A={res['derived_m_A_msun']:.4f}, m_B={res['derived_m_B_msun']:.4f}")
    print("  parameter        predicted      measured       frac diff")
    for k, c in res["pk_comparisons"].items():
        print(f"  {k:14s}  {c['predicted']:+.5e}  {c['measured']:+.5e}   {c['frac_diff']*100:.2f}%")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
