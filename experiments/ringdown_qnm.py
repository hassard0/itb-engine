"""Black-hole ringdown QNM splitting from Chern-Simons parity (v1.54).

In dynamical Chern-Simons gravity the parity term g_R2_parity splits the
otherwise-degenerate parity-even/odd (and +/-m) gravitational quasi-normal
modes of a ringing black hole. The leading dCS correction to the QNM spectrum
scales as the dimensionless coupling
        zeta = (l_CS / r_g)^4 ,   r_g = G M / c^2,
where l_CS is the Chern-Simons length scale and M the BH mass; the fractional
QNM frequency/damping split is then  df/f ~ g_R2_parity * zeta * O(1).

The crucial question for the engine's UNIFIED picture: in the dark-energy-cutoff
scenario (v1.44) l_CS ~ hbar c / (2.4 meV) ~ 85 um. How does the ringdown split
compare to LIGO/LISA sensitivity, and what l_CS WOULD be needed to see it?

This sharpens the probe hierarchy: propagation probes (birefringence, chiral HD)
accumulate over Gpc; the strong-field ringdown effect is local and (l_CS/r_g)^4
suppressed. Honest, order-of-magnitude (the exact dCS QNM coefficients are
spin-dependent; we use the standard zeta scaling).
"""

import json
import sys

import numpy as np

from itb.frameworks.discovered import DiscoveredParityViolating

sys.path.insert(0, ".")

G_PV = abs(DiscoveredParityViolating().encode().coefficients["g_R2_parity"])  # 0.092
HBARC_eV_m = 1.973e-7
L_CS_DE = HBARC_eV_m / 2.4e-3            # dark-energy CS length ~ 85 um (m)
GMsun_over_c2 = 1476.6                   # r_g for 1 Msun, in metres


def r_g(M_solar):
    return GMsun_over_c2 * M_solar


def df_over_f(l_CS, M_solar):
    zeta = (l_CS / r_g(M_solar))**4
    return G_PV * zeta                    # fractional QNM split (O(1) coeff ~1)


def l_CS_needed(M_solar, target_df):
    # df = g_pv * (l/rg)^4  ->  l = rg * (target/g_pv)^(1/4)
    return r_g(M_solar) * (target_df / G_PV)**0.25


def main():
    sources = {
        "LIGO stellar BH (M=60)": (60.0, 1e-3),     # ~0.1% stacked ringdown precision
        "LISA massive BH (M=1e6)": (1e6, 1e-4),      # ~1e-4 LISA QNM precision
    }
    out = {"l_CS_darkenergy_m": L_CS_DE, "g_R2_parity": G_PV, "sources": {}}
    print("=== BH ringdown QNM parity splitting (dynamical Chern-Simons) ===\n")
    print(f"  dark-energy CS length l_CS = {L_CS_DE*1e6:.0f} um; g_R2_parity = {G_PV:.3f}\n")
    print(f"  {'source':<26}{'r_g':>12}{'df/f (DE scale)':>18}{'l_CS needed':>16}")
    for name, (M, prec) in sources.items():
        df_de = df_over_f(L_CS_DE, M)
        l_need = l_CS_needed(M, prec)
        out["sources"][name] = {"M_solar": M, "r_g_m": r_g(M),
                                "df_over_f_darkenergy": df_de,
                                "detect_precision": prec, "l_CS_needed_m": l_need,
                                "l_CS_needed_over_rg": l_need / r_g(M)}
        rgs = f"{r_g(M)/1e3:.0f} km" if r_g(M) < 1e9 else f"{r_g(M)/1e9:.1f} Gm"
        print(f"  {name:<26}{rgs:>12}{df_de:>18.1e}{l_need/1e3:>13.1f} km")

    print(f"\n=== Verdict ===")
    df_ligo = out["sources"]["LIGO stellar BH (M=60)"]["df_over_f_darkenergy"]
    print(f"  At the dark-energy CS scale, the ringdown split is df/f ~ {df_ligo:.0e}")
    print(f"  — about {np.log10(1e-3/df_ligo):.0f} orders below LIGO ringdown sensitivity.")
    print(f"  To be observable, l_CS would need to be ~tens of km (comparable to the BH),")
    print(f"  i.e. ASTROPHYSICAL-scale new physics, NOT the dark-energy scale.")
    print(f"\n  => The dark-energy-cutoff hypothesis PREDICTS NULL ringdown parity splitting.")
    print(f"     Strong-field tests can't probe a meV-scale parity coupling: the effect is")
    print(f"     local and (l_CS/r_g)^4-suppressed, while the propagation probes")
    print(f"     (LIGO birefringence, chiral Hellings-Downs, CMB EB) WIN because they")
    print(f"     accumulate the tiny per-wavelength effect over Gpc baselines.")
    print(f"  Falsification value: a ringdown parity splitting DETECTION would mean")
    print(f"     l_CS ~ km (astrophysical), DISFAVORING the unified dark-energy-cutoff")
    print(f"     picture — so ringdown discriminates the parity SCALE.")

    # lever-arm comparison: propagation phase ~ (l_CS/lambda_GW) * (D/lambda_GW)?
    # birefringence accumulates ~ g_pv over a Gpc path in units of the coupling;
    # ringdown ~ g_pv*(l_CS/r_g)^4 locally. Ratio is astronomical.
    print(f"\n  (Probe-hierarchy note: birefringence/chiral-HD are O(g_R2_parity) effects")
    print(f"   accumulated over cosmological distance; ringdown is O(g_R2_parity x 1e-37).")
    print(f"   This is WHY the engine's parity coupling is a propagation-sector observable.)")

    with open("experiments/results/out_ringdown_qnm.json", "w") as f:
        json.dump(out, f, indent=2)

    # plot df/f vs l_CS
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        ls = np.logspace(-5, 5, 200)   # l_CS from 10 um to 100 km
        fig, ax = plt.subplots(figsize=(7, 4.3))
        for name, (M, prec) in sources.items():
            ax.loglog(ls, [df_over_f(l, M) for l in ls], label=name)
            ax.axhline(prec, ls=":", lw=1)
        ax.axvline(L_CS_DE, color="C3", lw=2, label="dark-energy l_CS (85 um)")
        ax.set_xlabel("Chern-Simons length l_CS [m]")
        ax.set_ylabel("fractional QNM split df/f")
        ax.set_title("BH ringdown parity split vs CS scale (g_R2_parity=0.09)")
        ax.legend(fontsize=8); ax.grid(alpha=0.3, which="both")
        plt.tight_layout(); plt.savefig("experiments/results/ringdown_qnm.png", dpi=110)
        print("  wrote experiments/results/ringdown_qnm.png")
    except Exception as e:
        print(f"  (plot skipped: {e})")
    print("\nwrote experiments/results/out_ringdown_qnm.json")


if __name__ == "__main__":
    main()
