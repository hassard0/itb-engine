"""v2.220 - Net R4 reach per overtone: sensitivity (v2.217) x resolvability (v2.219).

The three preceding cycles supply the pieces of one question. v2.217 found the n=1 first
overtone is ~491x MORE sensitive to the R4 quartic operator than the n=0 fundamental (driven
by the qEFT damping-time coefficient dtq_1 = 171.35). v2.218 made isospectrality breaking the
parity discriminator. v2.219 derived the per-mode ringdown resolvability R_f(Q), R_tau(Q). This
cycle multiplies sensitivity x resolvability to get the NET detection reach per overtone, and
asks the decisive question: does the overtone's huge sensitivity SURVIVE its much worse
resolvability (it has far lower quality factor Q, hence a larger R_f), or does the penalty
cancel the gain?

Per mode n and channel (frequency / damping), a fractional QNM deviation from coupling gamma is
gamma * |c_n| with c_n the qEFT fractional coefficient (|dwq_n| for frequency, |dtq_n| for
damping). It is resolvable at N sigma when the per-mode SNR rho_n exceeds N R(Q_n)/(|c_n| gamma),
so the reach is

    gamma_reach,n (channel) = N * R_channel(Q_n) / (|c_n| * rho_n)   (smaller = deeper reach).

At equal SNR the comparison isolates sensitivity x resolvability. The result: the overtone's
DAMPING channel dominates the R4 reach by ~2 orders of magnitude despite its low-Q resolvability
penalty -- the dtq_1 = 171.35 sensitivity wins decisively.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_ringdown_resolvability import ringdown_fisher
from experiments.r4_parspec_qeft_source_asset_audit import (
    QEFT_QNM_DEFORMATION_COEFFICIENTS as QC,
)

VERSION = "v2.220"
DEFAULT_OUT = Path("experiments/results/v2.220/qnm_r4_overtone_reach.json")

# l=2 fundamental + first overtone (Berti-Cardoso-Will, M=1)
MODES = {0: (0.373672, 0.088962), 1: (0.346711, 0.273915)}
N_SIGMA = 5.0


def mode_reach(n: int) -> dict:
    wR, wI = MODES[n]
    fish = ringdown_fisher(wR, wI)
    d = QC[f"nmax_{n}"]
    dwq = abs(d[f"delta_omega_qeft_{n}"])     # |fractional frequency shift| / gamma
    dtq = abs(d[f"delta_tau_qeft_{n}"])       # |fractional damping-time shift| / gamma
    # gamma_reach * rho (N sigma): smaller = deeper reach at fixed SNR
    reach_freq = N_SIGMA * fish["R_f"] / dwq
    reach_damp = N_SIGMA * fish["R_tau"] / dtq
    best = min(reach_freq, reach_damp)
    return {
        "n": n, "Q": fish["Q"], "R_f": fish["R_f"], "R_tau": fish["R_tau"],
        "dwq": dwq, "dtq": dtq,
        "reach_freq_x_rho": reach_freq, "reach_damp_x_rho": reach_damp,
        "best_reach_x_rho": best,
        "best_channel": "damping" if reach_damp < reach_freq else "frequency",
    }


def run() -> dict:
    m0, m1 = mode_reach(0), mode_reach(1)
    # net advantage of the overtone (at EQUAL SNR): ratio of best reaches (fund / overtone)
    overtone_advantage = m0["best_reach_x_rho"] / m1["best_reach_x_rho"]
    # crossover: the overtone still wins while rho_1/rho_0 > best_reach_1 / best_reach_0
    crossover_snr_ratio = m1["best_reach_x_rho"] / m0["best_reach_x_rho"]
    return {
        "version": VERSION,
        "method": ("per-mode ringdown Fisher resolvability (v2.219) x source-backed qEFT "
                   "fractional deformation coefficients (v2.217); reach = N R(Q)/(|c| rho), "
                   "N=5 sigma; l=2 fundamental + first overtone, M=1"),
        "modes": {"n0": m0, "n1": m1},
        "overtone_advantage_at_equal_snr": overtone_advantage,
        "dominant_channel_overtone": m1["best_channel"],
        "crossover_snr_ratio": crossover_snr_ratio,
        "finding": (
            f"The n=1 overtone's DAMPING channel reaches gamma_reach*rho = "
            f"{m1['reach_damp_x_rho']:.4f}, ~{overtone_advantage:.0f}x DEEPER than the "
            f"fundamental's best (frequency) channel ({m0['best_reach_x_rho']:.2f}) -- at equal "
            "SNR. The overtone's enormous damping-time sensitivity (dtq_1 = 171.35) decisively "
            f"overwhelms its resolvability PENALTY (low Q={m1['Q']:.2f} balloons R_f from "
            f"{m0['R_f']:.2f} to {m1['R_f']:.2f}). So sensitivity x resolvability still favors "
            "the overtone by ~2 orders of magnitude: overtone ringdown is the dominant R4 lever "
            "not just in raw sensitivity (v2.217) but in actual detection reach."
        ),
        "crossover_statement": (
            f"The overtone keeps the deeper reach as long as its SNR exceeds ~"
            f"{100*crossover_snr_ratio:.2f}% of the fundamental's (rho_1/rho_0 > "
            f"{crossover_snr_ratio:.4f}) -- an extremely weak condition, essentially always met "
            "once the overtone is detected at all. Even a heavily SNR-suppressed overtone "
            "dominates the R4 constraint."
        ),
        "honest_scope": (
            "Idealizations carried from the inputs: EQUAL-SNR comparison (the overtone is "
            "typically excited at LOWER SNR; the reach scales as 1/rho_n, so an excitation ratio "
            "rho_1/rho_0 ~ 0.1-0.3 shrinks the advantage to ~18-53x -- still dominant); the "
            "overtone Q=0.63 < 1 is heavily damped, so its single-damped-sinusoid frequency is "
            "poorly defined (correctly reflected in the large R_f); white-noise / single-mode / "
            "t=0-start Fisher (v2.219); and the qEFT coefficients carry the v2.217 caveats "
            "(dtq_1=171.35 makes the overtone perturbatively delicate -- valid for gamma << 6e-3, "
            "consistent with the ~0.07/rho reach being deep in that regime for rho >~ 30). "
            "Parity-odd g_R4_c3 stays dark (v2.209); full isospectrality splitting still needs "
            "the un-sourceable polar correction (v2.218)."
        ),
        "references": [
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132) -- qEFT coefficients",
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- QNM values + ringdown Fisher analysis",
            "this repo: v2.217 (overtone sensitivity), v2.219 (resolvability)",
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
    for k in ("n0", "n1"):
        m = res["modes"][k]
        print(f"{k}: Q={m['Q']:.3f} R_f={m['R_f']:.3f} R_tau={m['R_tau']:.3f}  "
              f"reach*rho freq={m['reach_freq_x_rho']:.4f} damp={m['reach_damp_x_rho']:.5f} "
              f"(best={m['best_channel']})")
    print(f"overtone advantage @ equal SNR = {res['overtone_advantage_at_equal_snr']:.0f}x")
    print(f"crossover SNR ratio = {res['crossover_snr_ratio']:.4f}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
