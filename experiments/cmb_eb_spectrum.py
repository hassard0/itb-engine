"""The real CMB EB spectrum predicted by the dark-energy-axion birefringence (v1.48).

Cosmic birefringence rotates CMB polarization by beta, mixing E and B and
generating a parity-odd EB correlation that is ZERO in standard LambdaCDM:

    C_l^EB,obs = (1/2) sin(4 beta) [C_l^EE - C_l^BB]

This computes the real LambdaCDM C_l^EE, C_l^BB with CAMB (Planck cosmology) and
the predicted C_l^EB for the dark-energy-axion rotation beta = 0.34 deg (v1.46-47),
turning the prediction into a concrete, data-comparable spectrum. Reports the EB
amplitude, its acoustic-peak shape, and detectability vs Planck.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

BETA_DEG = 0.34          # dark-energy-axion birefringence (v1.46/47)
DEG = np.pi / 180.0


def main():
    import camb

    pars = camb.set_params(H0=67.4, ombh2=0.0224, omch2=0.120,
                           ns=0.965, As=2.1e-9, tau=0.054, r=0.0)
    pars.set_for_lmax(2500, lens_potential_accuracy=1)
    results = camb.get_results(pars)
    powers = results.get_cmb_power_spectra(pars, CMB_unit="muK")  # D_l = l(l+1)C_l/2pi
    tot = powers["total"]               # columns: TT, EE, BB, TE
    ell = np.arange(tot.shape[0])
    EE = tot[:, 1]
    BB = tot[:, 2]

    beta = BETA_DEG * DEG
    EB = 0.5 * np.sin(4 * beta) * (EE - BB)   # predicted EB (same D_l units)

    # characterize over the acoustic range
    lo, hi = 50, 2000
    sl = slice(lo, hi)
    peak_l = int(lo + np.argmax(np.abs(EB[sl])))
    out = {
        "beta_deg": BETA_DEG,
        "sin4beta": float(np.sin(4 * beta)),
        "EB_peak_ell": peak_l,
        "EB_peak_Dl_muK2": float(EB[peak_l]),
        "EE_peak_Dl_muK2": float(np.max(EE[sl])),
        "EB_over_EE_at_peak": float(EB[peak_l] / EE[peak_l]),
        "spectrum_sample": {str(l): {"EE": float(EE[l]), "BB": float(BB[l]),
                                     "EB": float(EB[l])}
                            for l in (100, 300, 500, 700, 1000, 1500, 2000)},
    }
    with open("experiments/out_cmb_eb.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"=== Predicted CMB EB spectrum from dark-energy-axion birefringence ===")
    print(f"  beta = {BETA_DEG} deg  =>  sin(4 beta) = {out['sin4beta']:.4f}")
    print(f"  (LambdaCDM has C_l^EB = 0 exactly; a nonzero EB is the parity-odd smoking gun)\n")
    print(f"  {'ell':>5} {'D_l^EE':>12} {'D_l^BB':>12} {'D_l^EB (pred)':>14}  [muK^2]")
    for l in (100, 300, 500, 700, 1000, 1500, 2000):
        s = out["spectrum_sample"][str(l)]
        print(f"  {l:>5} {s['EE']:>12.4f} {s['BB']:>12.5f} {s['EB']:>14.4f}")
    print(f"\n  EB peaks at ell~{peak_l}: D_l^EB = {out['EB_peak_Dl_muK2']:.3f} muK^2 "
          f"({out['EB_over_EE_at_peak']*100:.2f}% of EE there)")
    print(f"  This is the acoustic-peak-shaped EB Minami-Komatsu fit in Planck data;")
    print(f"  amplitude ~1% of EE is at Planck's sensitivity and a clean target for")
    print(f"  LiteBIRD / CMB-S4. The SAME dark-energy axion predicts (v1.46) a correlated")
    print(f"  GW birefringence at |g_R2_parity|~0.09 (LIGO O5) — the multi-messenger test.")
    print(f"\nwrote experiments/out_cmb_eb.json")


if __name__ == "__main__":
    main()
