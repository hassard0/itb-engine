"""Chiral Hellings-Downs: the parity sector's signature in pulsar timing (v1.53).

Dr. M.'s proposed new signature. The gravitational Chern-Simons term g_R2_parity
gives the stochastic GW background a net circular polarization (Stokes V); in a
pulsar-timing array this appears as a PARITY-ODD component of the inter-pulsar
correlation, on top of the standard (parity-even) Hellings-Downs curve. It is a
pure tensor-sector probe of gravitational handedness, decoupled from the
photon-axion coupling behind CMB/cosmic birefringence.

Computes: (1) the standard HD overlap-reduction curve Gamma_I(zeta); (2) the
predicted circular-polarization degree Pi_V ~ g_R2_parity * A; (3) the SKA-era
detectability — with the honest caveat (Kato-Soda 2016) that the ISOTROPIC
monopole circular polarization cancels in an isotropic PTA, so the signal lives
in the ANISOTROPIC (dipole+) correlations.

References: Hellings-Downs 1983; Kato-Soda 2016; Belgacem-Kamionkowski 2020.
"""

import json
import sys

import numpy as np

from itb.frameworks.discovered import DiscoveredParityViolating
from itb.frameworks.lqg_induced import LQGInduced

sys.path.insert(0, ".")


def hellings_downs(zeta):
    """Standard (parity-even) overlap reduction function, normalized to 1/2 at 0."""
    x = (1 - np.cos(zeta)) / 2.0
    g = np.empty_like(x)
    for i, xi in enumerate(x):
        if xi <= 1e-12:
            g[i] = 0.5
        else:
            g[i] = 0.5 - 0.25 * xi + 1.5 * xi * np.log(xi)
    return g


def main():
    g_pv = abs(DiscoveredParityViolating().encode().coefficients["g_R2_parity"])
    g_lqg = abs(LQGInduced().encode().coefficients["g_R2_parity"])

    # circular-polarization degree Pi_V ~ g_R2_parity * A, A ~ O(1) (axion evolution)
    A_lo, A_hi = 0.3, 1.0
    PiV_lo, PiV_hi = g_pv * A_lo, g_pv * A_hi

    zeta = np.linspace(0, np.pi, 19)
    hd = hellings_downs(zeta)

    out = {
        "g_R2_parity_pv": g_pv, "g_R2_parity_lqg": g_lqg,
        "PiV_range": [PiV_lo, PiV_hi],
        "hd_curve": [{"deg": float(np.degrees(z)), "Gamma_I": float(g)}
                     for z, g in zip(zeta, hd)],
        "ska_shape_precision": 0.01,
    }
    with open("experiments/results/out_chiral_hd.json", "w") as f:
        json.dump(out, f, indent=2)

    print("=== Chiral Hellings-Downs: parity sector in pulsar timing (Dr. M.) ===\n")
    print(f"  parity coupling: |g_R2_parity| = {g_pv:.3f} (discovered branch), "
          f"{g_lqg:.3f} (LQG)")
    print(f"  predicted SGWB circular polarization Pi_V ~ g_R2_parity*A(O(1)) "
          f"= {PiV_lo*100:.1f}-{PiV_hi*100:.1f}%\n")
    print(f"  standard Hellings-Downs curve (parity-even Gamma_I):")
    print(f"  {'zeta(deg)':>10}{'Gamma_I':>10}")
    for z, g in zip(zeta, hd):
        if int(np.degrees(z)) % 20 == 0:
            print(f"  {np.degrees(z):>10.0f}{g:>10.4f}")
    print(f"\n  => the parity term adds a PARITY-ODD correlation component of relative")
    print(f"     size ~Pi_V ({PiV_lo*100:.0f}-{PiV_hi*100:.0f}%) on top of this curve.")
    print(f"  Experiment: SKA-era PTAs (~1% precision on the correlation SHAPE).")
    print(f"  HONEST CAVEAT (Kato-Soda 2016): the isotropic monopole circular")
    print(f"  polarization CANCELS in an isotropic PTA; the chiral signal is carried")
    print(f"  by the ANISOTROPIC (dipole and higher) cross-correlations, which the SKA")
    print(f"  can access via the kinematic dipole / GWB anisotropy. NANOGrav/EPTA have")
    print(f"  just resolved the symmetric HD curve (2023); the chiral component is the")
    print(f"  next frontier. This is a 4th, fully tensor-sector probe of g_R2_parity,")
    print(f"  complementary to LIGO GW birefringence (high-f) and CMB EB (EM sector).")

    # plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        zz = np.linspace(0.01, np.pi, 200)
        g0 = hellings_downs(zz)
        fig, ax = plt.subplots(figsize=(7, 4.3))
        ax.plot(np.degrees(zz), g0, "C0", lw=2, label="Hellings-Downs (GR, parity-even)")
        ax.fill_between(np.degrees(zz), g0 - PiV_hi * np.abs(g0), g0 + PiV_hi * np.abs(g0),
                        color="C3", alpha=0.25,
                        label=f"+/- chiral band (Pi_V up to {PiV_hi*100:.0f}%)")
        ax.axhline(0, color="k", lw=0.5)
        ax.set_xlabel("pulsar angular separation zeta [deg]")
        ax.set_ylabel("overlap reduction Gamma(zeta)")
        ax.set_title("Chiral Hellings-Downs: parity-sector signature in PTAs")
        ax.legend()
        plt.tight_layout()
        plt.savefig("experiments/results/chiral_hd.png", dpi=110)
        print("\n  wrote experiments/results/chiral_hd.png")
    except Exception as e:
        print(f"\n  (plot skipped: {e})")

    print("\nwrote experiments/results/out_chiral_hd.json")


if __name__ == "__main__":
    main()
