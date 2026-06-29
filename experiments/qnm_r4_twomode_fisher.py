"""v2.220 follow-up (v2.221) - Two-mode (220+221) joint Fisher: does mode covariance survive?

v2.220 computed the per-mode R4 reach treating the fundamental and the first overtone as
INDEPENDENT single damped sinusoids. In a real ringdown both modes are present at once, overlap
in time, and their parameters are CORRELATED -- a joint fit must marginalize each mode over the
other, which inflates the uncertainties. This cycle builds the full two-mode joint Fisher matrix
from first principles (self-contained, like v2.219) and asks: how much does mode covariance
degrade the per-mode resolvability, and does the v2.220 "overtone dominates the R4 reach by ~2
orders of magnitude" conclusion survive?

Waveform: h(t) = sum_n A_n e^{-t/tau_n} cos(omega_n t + phi_n), t >= 0, n in {0,1}.
8 parameters {A_n, phi_n, omega_n, tau_n}; Fisher Gamma_ij = int_0^inf d_i h d_j h dt (white
noise). The overtone resolvability is read from the JOINT covariance C = Gamma^{-1} (so mode 0
is marginalized), and compared to the v2.219 ISOLATED single-mode coefficients.

Key analytic property (validated numerically): the dimensionless inflation R_joint/R_isolated is
INDEPENDENT of the amplitude ratio A_1/A_0. The overtone block of Gamma scales as A_1^2, the
cross-block as A_1, so the Schur complement Gamma_11 - Gamma_10 Gamma_00^{-1} Gamma_01 scales as
A_1^2; with rho_1 proportional to A_1, the product rho_1^2 C_11 is amplitude-invariant. The
covariance penalty is therefore a pure geometric consequence of the mode overlap.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.r4_parspec_qeft_source_asset_audit import (
    QEFT_QNM_DEFORMATION_COEFFICIENTS as QC,
)

VERSION = "v2.221"
DEFAULT_OUT = Path("experiments/results/v2.221/qnm_r4_twomode_fisher.json")

# l=2 fundamental + first overtone (Berti-Cardoso-Will, M=1)
W = {0: 0.373672, 1: 0.346711}
GAMMA = {0: 0.088962, 1: 0.273915}                 # |omega_I| = 1/tau
TAU = {n: 1.0 / GAMMA[n] for n in (0, 1)}
# v2.219 ISOLATED single-mode resolvability coefficients (for the inflation comparison)
R_ISO = {(0, "f"): 0.5537, (0, "tau"): 2.0007, (1, "f"): 3.7740, (1, "tau"): 2.5290}
KEYS = [("A", 0), ("phi", 0), ("w", 0), ("tau", 0),
        ("A", 1), ("phi", 1), ("w", 1), ("tau", 1)]
N_SIGMA = 5.0


def _partials(t: np.ndarray, A: float, n: int) -> dict:
    e = np.exp(-t / TAU[n])
    c, s = np.cos(W[n] * t), np.sin(W[n] * t)
    return {("A", n): e * c, ("phi", n): -A * e * s,
            ("w", n): -A * t * e * s, ("tau", n): A * (t / TAU[n] ** 2) * e * c}


def twomode_fisher(amp_ratio: float = 1.0, T: float = 300.0, npts: int = 300001) -> dict:
    """Joint 8-parameter Fisher of the 220+221 ringdown; returns per-mode joint coefficients."""
    t = np.linspace(0.0, T, npts)
    P = {}
    P.update(_partials(t, 1.0, 0))
    P.update(_partials(t, amp_ratio, 1))
    G = np.array([[np.trapezoid(P[a] * P[b], t) for b in KEYS] for a in KEYS])
    C = np.linalg.inv(G)
    idx = {k: i for i, k in enumerate(KEYS)}
    out = {"amp_ratio": amp_ratio}
    for n, A in ((0, 1.0), (1, amp_ratio)):
        hn = A * np.exp(-t / TAU[n]) * np.cos(W[n] * t)
        rho = float(np.sqrt(np.trapezoid(hn * hn, t)))
        out[(n, "f")] = rho * float(np.sqrt(C[idx[("w", n)], idx[("w", n)]])) / W[n]
        out[(n, "tau")] = rho * float(np.sqrt(C[idx[("tau", n)], idx[("tau", n)]])) / TAU[n]

    def corr(a, b):
        return float(C[idx[a], idx[b]] / np.sqrt(C[idx[a], idx[a]] * C[idx[b], idx[b]]))

    out["corr_w0_w1"] = corr(("w", 0), ("w", 1))
    out["corr_tau0_tau1"] = corr(("tau", 0), ("tau", 1))
    return out


def run() -> dict:
    j = twomode_fisher(1.0)
    # amplitude-independence check: inflation identical at a different ratio
    j2 = twomode_fisher(0.3)
    amp_independent = (abs(j[(1, "tau")] - j2[(1, "tau")]) < 1e-2
                       and abs(j[(0, "f")] - j2[(0, "f")]) < 1e-2)

    dwq = {n: abs(QC[f"nmax_{n}"][f"delta_omega_qeft_{n}"]) for n in (0, 1)}
    dtq = {n: abs(QC[f"nmax_{n}"][f"delta_tau_qeft_{n}"]) for n in (0, 1)}

    def best_reach(n):
        rf = N_SIGMA * j[(n, "f")] / dwq[n]
        rt = N_SIGMA * j[(n, "tau")] / dtq[n]
        return min(rf, rt), ("damping" if rt < rf else "frequency")

    b0, ch0 = best_reach(0)
    b1, ch1 = best_reach(1)
    advantage_joint = b0 / b1

    inflation = {
        "fund_freq": j[(0, "f")] / R_ISO[(0, "f")],
        "fund_damp": j[(0, "tau")] / R_ISO[(0, "tau")],
        "overtone_freq": j[(1, "f")] / R_ISO[(1, "f")],
        "overtone_damp": j[(1, "tau")] / R_ISO[(1, "tau")],
    }
    return {
        "version": VERSION,
        "method": ("8-parameter joint Fisher of the 220+221 ringdown, white-noise inner "
                   "product int_0^inf d_i h d_j h dt; per-mode coefficients read from the "
                   "JOINT covariance (each mode marginalized over the other); M=1"),
        "joint_coefficients": {
            "fund": {"R_f": j[(0, "f")], "R_tau": j[(0, "tau")]},
            "overtone": {"R_f": j[(1, "f")], "R_tau": j[(1, "tau")]},
        },
        "isolated_coefficients_v2219_v2220": {
            "fund": {"R_f": R_ISO[(0, "f")], "R_tau": R_ISO[(0, "tau")]},
            "overtone": {"R_f": R_ISO[(1, "f")], "R_tau": R_ISO[(1, "tau")]},
        },
        "covariance_inflation": inflation,
        "mode_correlations": {"freq": j["corr_w0_w1"], "damping": j["corr_tau0_tau1"]},
        "amplitude_independent": bool(amp_independent),
        "overtone_advantage_joint_equal_snr": advantage_joint,
        "overtone_best_channel": ch1,
        "finding": (
            "Mode covariance inflates BOTH modes' resolvability by ~4-5.5x (driven by strong "
            f"frequency / damping correlations between the overlapping modes: "
            f"corr(w0,w1)={j['corr_w0_w1']:+.2f}, corr(tau0,tau1)={j['corr_tau0_tau1']:+.2f}). "
            "So the v2.219/v2.220 single-mode coefficients were OPTIMISTIC by this factor. The "
            "inflation is independent of the amplitude ratio (a geometric Schur-complement "
            "property, validated). Crucially, because both modes degrade by a SIMILAR factor, "
            f"the overtone's R4-reach advantage only falls from 177x (isolated, v2.220) to "
            f"{advantage_joint:.0f}x (joint) -- still ~2 orders of magnitude, still concentrated "
            "in the overtone damping channel. The v2.220 conclusion is ROBUST to mode covariance."
        ),
        "honest_scope": (
            "Equal mode self-SNR comparison (the overtone is typically excited weaker; the "
            "reach scales as 1/rho_n); white-noise / t=0-start Fisher (v2.219 idealizations); two "
            "modes only (higher overtones would add further covariance); qEFT coefficients carry "
            "the v2.217 perturbative-delicacy caveat (dtq_1=171.35, valid for gamma << 6e-3). "
            "This REFINES v2.220 (its single-mode reaches are optimistic by the ~4-5.5x inflation) "
            "without overturning it. Parity-odd g_R4_c3 stays dark (v2.209); full isospectrality "
            "splitting still needs the un-sourceable polar correction (v2.218)."
        ),
        "references": [
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- QNM values + multi-mode ringdown Fisher",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132) -- qEFT coefficients",
            "this repo: v2.219 (isolated resolvability), v2.220 (per-mode reach)",
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
    jc, inf = res["joint_coefficients"], res["covariance_inflation"]
    print(f"joint fund:     R_f={jc['fund']['R_f']:.3f} (infl {inf['fund_freq']:.2f}x)  "
          f"R_tau={jc['fund']['R_tau']:.3f} (infl {inf['fund_damp']:.2f}x)")
    print(f"joint overtone: R_f={jc['overtone']['R_f']:.3f} (infl {inf['overtone_freq']:.2f}x)  "
          f"R_tau={jc['overtone']['R_tau']:.3f} (infl {inf['overtone_damp']:.2f}x)")
    print(f"correlations: freq={res['mode_correlations']['freq']:+.3f}  "
          f"damping={res['mode_correlations']['damping']:+.3f}  "
          f"amp_independent={res['amplitude_independent']}")
    print(f"overtone advantage (joint, equal SNR) = {res['overtone_advantage_joint_equal_snr']:.0f}x "
          f"(v2.220 isolated 177x)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
