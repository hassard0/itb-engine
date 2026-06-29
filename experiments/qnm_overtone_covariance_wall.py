"""v2.222 - The overtone covariance wall: does ringdown spectroscopy self-limit?

v2.221 showed the 2-mode (220+221) joint fit inflates each mode's resolvability ~4-5.5x vs the
isolated single-mode case, yet the overtone R4 advantage survived. The obvious next question:
ringdown SPECTROSCOPY proposes to fit MANY overtones (220+221+222+...) to test the Kerr
spectrum. Does the covariance penalty COMPOUND as overtones stack -- and if so, how fast? This
cycle adds the n=2 second overtone to the joint Fisher (self-contained, first principles) and
measures the compounding.

The heavily-damped high overtones (Q_2 ~ 0.31) are broad and nearly degenerate in
resolvability space, so the Fisher matrix becomes increasingly ill-conditioned. This is the
first-principles mechanism behind the published overtone-overfitting concerns (Baibhav, Berti,
Cardoso et al.). Result: R_tau for the first overtone collapses from 13.97 (2-mode) to ~494
(3-mode) -- a further ~35x -- and the Fisher condition number jumps from ~1e6 to ~3e9. Overtone
spectroscopy hits a covariance wall, so the OPTIMAL R4 strategy is a low-order (2-mode) model:
enough to exploit the overtone's huge R4 sensitivity, few enough to stay off the wall.
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

VERSION = "v2.222"
DEFAULT_OUT = Path("experiments/results/v2.222/qnm_overtone_covariance_wall.json")

# l=2 Schwarzschild QNMs n=0,1,2 (Berti-Cardoso-Will, M=1)
W = {0: 0.373672, 1: 0.346711, 2: 0.301053}
GAMMA = {0: 0.088962, 1: 0.273915, 2: 0.478277}     # |omega_I| = 1/tau
TAU = {n: 1.0 / GAMMA[n] for n in W}
R_TAU_ISOLATED = {0: 2.0007, 1: 2.5290}             # v2.219 single-mode (for total inflation)
N_SIGMA = 5.0


def _parts(t, A, n):
    e = np.exp(-t / TAU[n])
    c, s = np.cos(W[n] * t), np.sin(W[n] * t)
    return {("A", n): e * c, ("phi", n): -A * e * s,
            ("w", n): -A * t * e * s, ("tau", n): A * (t / TAU[n] ** 2) * e * c}


def joint(modes, amps=None, T: float = 300.0, npts: int = 400001) -> dict:
    amps = amps or {n: 1.0 for n in modes}
    t = np.linspace(0.0, T, npts)
    P = {}
    for n in modes:
        P.update(_parts(t, amps[n], n))
    keys = [(p, n) for n in modes for p in ("A", "phi", "w", "tau")]
    G = np.array([[np.trapezoid(P[a] * P[b], t) for b in keys] for a in keys])
    C = np.linalg.inv(G)
    idx = {k: i for i, k in enumerate(keys)}
    out = {"cond": float(np.linalg.cond(G))}
    for n in modes:
        hn = amps[n] * np.exp(-t / TAU[n]) * np.cos(W[n] * t)
        rho = float(np.sqrt(np.trapezoid(hn * hn, t)))
        out[(n, "Rt")] = rho * float(np.sqrt(C[idx[("tau", n)], idx[("tau", n)]])) / TAU[n]
        out[(n, "Rf")] = rho * float(np.sqrt(C[idx[("w", n)], idx[("w", n)]])) / W[n]
    return out


def run() -> dict:
    two = joint([0, 1])
    three = joint([0, 1, 2])
    dtq1 = abs(QC["nmax_1"]["delta_tau_qeft_1"])
    dwq0 = abs(QC["nmax_0"]["delta_omega_qeft_0"])

    # n=1 R4 damping-channel reach (gamma_reach * rho), 2-mode vs 3-mode
    reach1_2 = N_SIGMA * two[(1, "Rt")] / dtq1
    reach1_3 = N_SIGMA * three[(1, "Rt")] / dtq1
    # fundamental best reach (frequency channel) for the advantage ratio
    reach0_2 = N_SIGMA * two[(0, "Rf")] / dwq0
    reach0_3 = N_SIGMA * three[(0, "Rf")] / dwq0

    return {
        "version": VERSION,
        "method": ("joint white-noise ringdown Fisher (v2.221 machinery) extended to the n=2 "
                   "second overtone; per-mode resolvability from the joint covariance; M=1"),
        "resolvability_R_tau": {
            "isolated_1mode": R_TAU_ISOLATED,
            "two_mode_220_221": {"n0": two[(0, "Rt")], "n1": two[(1, "Rt")]},
            "three_mode_220_221_222": {"n0": three[(0, "Rt")], "n1": three[(1, "Rt")],
                                       "n2": three[(2, "Rt")]},
        },
        "fisher_condition_number": {"two_mode": two["cond"], "three_mode": three["cond"]},
        "compounding": {
            "R_tau1_isolated_to_2mode": two[(1, "Rt")] / R_TAU_ISOLATED[1],
            "R_tau1_2mode_to_3mode": three[(1, "Rt")] / two[(1, "Rt")],
            "R_tau1_isolated_to_3mode": three[(1, "Rt")] / R_TAU_ISOLATED[1],
            "cond_number_growth_2mode_to_3mode": three["cond"] / two["cond"],
        },
        "r4_overtone_reach_x_rho": {
            "n1_damping_2mode": reach1_2, "n1_damping_3mode": reach1_3,
            "overtone_advantage_2mode": reach0_2 / reach1_2,
            "overtone_advantage_3mode": reach0_3 / reach1_3,
        },
        "finding": (
            f"Covariance COMPOUNDS super-linearly. Adding the n=2 overtone inflates the first "
            f"overtone resolvability R_tau1 from {two[(1,'Rt')]:.1f} (2-mode) to "
            f"{three[(1,'Rt')]:.0f} (3-mode) -- a further ~{three[(1,'Rt')]/two[(1,'Rt')]:.0f}x, "
            f"~{three[(1,'Rt')]/R_TAU_ISOLATED[1]:.0f}x vs the isolated mode -- while the Fisher "
            f"condition number jumps from {two['cond']:.1e} to {three['cond']:.1e}. The heavily-"
            f"damped overtones (Q_2 ~ {W[2]/(2*GAMMA[2]):.2f}) are broad and near-degenerate in "
            "parameter space, so stacking them collapses resolvability. This is the first-"
            "principles mechanism behind the published overtone-overfitting concerns (Baibhav-"
            "Berti). Consequence: the v2.220/v2.221 overtone R4 advantage holds in a 2-mode model "
            f"but erodes from ~{reach0_2/reach1_2:.0f}x to ~{reach0_3/reach1_3:.0f}x if the fit is "
            "pushed to 3 modes -- so the OPTIMAL R4 strategy is the low-order (2-mode) model: "
            "enough to exploit the overtone sensitivity, few enough to stay off the covariance wall."
        ),
        "honest_scope": (
            "Equal mode self-SNR; white-noise / t=0-start Fisher (v2.219 idealizations); the n=2 "
            "qEFT deformation coefficient is NOT published (only n=0,1 are), so this measures the "
            "n=2 mode's EFFECT on the n=0/n=1 resolvability, not the n=2 R4 reach itself. The "
            "3-mode condition number ~3e9 is still safely invertible in double precision; a 4th "
            "mode would push toward the precision limit (itself the point -- the wall). REFINES "
            "v2.220/v2.221: the overtone advantage is contingent on a low-order ringdown model. "
            "Parity-odd g_R4_c3 dark (v2.209); full splitting needs the un-sourceable polar "
            "correction (v2.218); dtq_1 perturbative-delicacy caveat (v2.217)."
        ),
        "references": [
            "Baibhav, Berti, Cardoso et al. -- overtone content / overfitting of ringdown",
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 -- QNM values + multi-mode Fisher",
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 -- qEFT coefficients",
            "this repo: v2.219 (isolated), v2.220 (per-mode reach), v2.221 (2-mode covariance)",
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
    rt = res["resolvability_R_tau"]
    print(f"R_tau1: isolated {rt['isolated_1mode'][1]:.2f} -> 2-mode "
          f"{rt['two_mode_220_221']['n1']:.2f} -> 3-mode {rt['three_mode_220_221_222']['n1']:.0f}")
    c = res["fisher_condition_number"]
    print(f"Fisher cond: 2-mode {c['two_mode']:.2e} -> 3-mode {c['three_mode']:.2e}")
    a = res["r4_overtone_reach_x_rho"]
    print(f"overtone advantage: 2-mode {a['overtone_advantage_2mode']:.0f}x -> "
          f"3-mode {a['overtone_advantage_3mode']:.1f}x")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
