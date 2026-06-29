"""v2.227 - Covariance-corrected no-hair detectability: the realistic 220/221 forecast.

v2.226 quantified how R4 violates the 220/221 no-hair consistency and gave a critical SNR using
ISOLATED single-mode resolvability -- which it flagged as optimistic, since the two modes are
measured jointly with strong covariance (v2.221). This cycle computes the REALISTIC critical SNR
from the full two-mode joint Fisher, for the no-hair RATIO observables ln(omega_221/omega_220)
(frequency) and ln(omega_I,221/omega_I,220) (damping).

A ratio observable has a subtlety the v2.226 isolated estimate missed: the two modes' parameter
errors are strongly CORRELATED (corr ~ 0.86, v2.221), and correlated errors partially CANCEL in a
ratio. So the covariance has two competing effects -- it inflates each mode's individual
uncertainty (v2.221, ~4-5x) but the correlation reduces the ratio variance relative to treating
the inflated uncertainties as independent. The net realistic forecast is computed here.

Result: the covariance-corrected rho_crit is ~7-9x larger than the v2.226 isolated estimate (the
isolated number was optimistic), but the mode correlation MITIGATES the ratio variance (full <
diagonal, ~38% in the damping channel). The damping no-hair channel still dominates by ~200x.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.qnm_nohair_consistency import r4_nohair_violation
from experiments.qnm_r4_twomode_fisher import KEYS, TAU, W, _partials

VERSION = "v2.227"
DEFAULT_OUT = Path("experiments/results/v2.227/qnm_nohair_covariance_forecast.json")
# v2.226 isolated-resolvability critical SNRs (for the optimism comparison)
ISO_RHO_CRIT = {"freq": 2.901, "damp": 0.0188}


def ratio_uncertainty(amp_ratio: float = 1.0, T: float = 300.0, npts: int = 400001) -> dict:
    """rho_tot * sigma(ln ratio) for the freq and damping no-hair ratios, full vs diagonal."""
    t = np.linspace(0.0, T, npts)
    P = {}
    P.update(_partials(t, 1.0, 0))
    P.update(_partials(t, amp_ratio, 1))
    G = np.array([[np.trapezoid(P[a] * P[b], t) for b in KEYS] for a in KEYS])
    C = np.linalg.inv(G)
    idx = {k: i for i, k in enumerate(KEYS)}
    h = (np.exp(-t / TAU[0]) * np.cos(W[0] * t)
         + amp_ratio * np.exp(-t / TAU[1]) * np.cos(W[1] * t))
    rho = float(np.sqrt(np.trapezoid(h * h, t)))
    out = {}
    for chan, p, ref in (("freq", "w", (W[0], W[1])),
                         ("damp", "tau", (TAU[0], TAU[1]))):
        v0 = C[idx[(p, 0)], idx[(p, 0)]]
        v1 = C[idx[(p, 1)], idx[(p, 1)]]
        cov = C[idx[(p, 0)], idx[(p, 1)]]
        full = v1 / ref[1] ** 2 + v0 / ref[0] ** 2 - 2 * cov / (ref[0] * ref[1])
        diag = v1 / ref[1] ** 2 + v0 / ref[0] ** 2
        out[chan] = {
            "rho_sigma_full": rho * float(np.sqrt(full)),
            "rho_sigma_diag": rho * float(np.sqrt(diag)),
            "mode_correlation": float(cov / np.sqrt(v0 * v1)),
        }
    return out


def run() -> dict:
    ru = ratio_uncertainty()
    viol = r4_nohair_violation()
    V = {"freq": abs(viol["r4_freq_ratio_violation_per_gamma"]),
         "damp": abs(viol["r4_damp_ratio_violation_per_gamma"])}
    forecast = {}
    for chan in ("freq", "damp"):
        rc_full = ru[chan]["rho_sigma_full"] / V[chan]
        forecast[chan] = {
            "rho_crit_1sigma_full_per_gamma": rc_full,
            "rho_crit_1sigma_diag_per_gamma": ru[chan]["rho_sigma_diag"] / V[chan],
            "rho_crit_isolated_v2226_per_gamma": ISO_RHO_CRIT[chan],
            "optimism_factor_vs_isolated": rc_full / ISO_RHO_CRIT[chan],
            "correlation_mitigation": 1.0 - ru[chan]["rho_sigma_full"] / ru[chan]["rho_sigma_diag"],
        }
    damp_over_freq = forecast["freq"]["rho_crit_1sigma_full_per_gamma"] / \
        forecast["damp"]["rho_crit_1sigma_full_per_gamma"]
    return {
        "version": VERSION,
        "method": ("two-mode (220+221) joint Fisher (v2.221) -> covariance of ln-ratio "
                   "observables; rho_crit = rho_tot sigma(ln ratio) / |R4 violation per gamma| "
                   "(v2.226); white-noise, equal amplitudes, M=1"),
        "ratio_uncertainty": ru,
        "nohair_forecast": forecast,
        "damp_over_freq_sensitivity_full": damp_over_freq,
        "finding": (
            "The covariance-corrected no-hair critical SNR is "
            f"~{forecast['freq']['optimism_factor_vs_isolated']:.0f}x (freq) and "
            f"~{forecast['damp']['optimism_factor_vs_isolated']:.0f}x (damp) LARGER than the "
            "v2.226 isolated-resolvability estimate -- the isolated number was optimistic, as "
            "v2.221 covariance inflation implies. But the strong mode correlation (~0.86) "
            "partially MITIGATES the ratio variance (correlated errors cancel in a ratio): the "
            f"full-covariance rho*sigma is {100*forecast['damp']['correlation_mitigation']:.0f}% "
            "below the diagonal (correlation-ignoring) value in the damping channel, "
            f"{100*forecast['freq']['correlation_mitigation']:.0f}% in the frequency channel. The "
            f"realistic forecast: rho_crit ~ {forecast['freq']['rho_crit_1sigma_full_per_gamma']:.0f}"
            f"/gamma (freq) vs ~{forecast['damp']['rho_crit_1sigma_full_per_gamma']:.2f}/gamma "
            f"(damp) -- the damping no-hair channel still dominates by ~{damp_over_freq:.0f}x."
        ),
        "honest_scope": (
            "Equal-amplitude, white-noise, t=0-start two-mode Fisher (v2.221 idealizations). The "
            "R4 violation magnitudes are source-backed (qEFT dwq/dtq, v2.217) and the ratio "
            "covariance is from first principles. This REFINES the v2.226 isolated estimate (which "
            "was optimistic by ~7-9x) toward realism without overturning the qualitative result "
            "(damping channel dominates). A realistic overtone excitation rho_1/rho_0 < 1 would "
            "raise rho_crit further (reach scales as 1/rho_1). The dtq_1 perturbative-delicacy "
            "caveat carries (v2.217, gamma << 6e-3). Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Isi et al., PRL 123 (2019) 111102 -- 220+221 no-hair test",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 -- qEFT coefficients (v2.217)",
            "this repo: v2.221 (two-mode covariance), v2.226 (no-hair violation, isolated estimate)",
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
    for chan in ("freq", "damp"):
        f = res["nohair_forecast"][chan]
        print(f"{chan}: rho_crit full {f['rho_crit_1sigma_full_per_gamma']:.3f}/g  "
              f"(isolated v2.226 {f['rho_crit_isolated_v2226_per_gamma']}/g, "
              f"optimism {f['optimism_factor_vs_isolated']:.1f}x; "
              f"corr mitigation {100*f['correlation_mitigation']:.0f}%)")
    print(f"damp dominates freq by {res['damp_over_freq_sensitivity_full']:.0f}x")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
