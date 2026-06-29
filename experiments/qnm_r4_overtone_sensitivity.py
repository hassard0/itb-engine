"""v2.217 - The overtone-sensitivity hierarchy of the R4 ringdown shift.

The full odd-parity R4 modified potential (needed to complete the v2.216 McManus<->qEFT
cross-check) is NOT sourceable this cycle: the 2205.05132 appendix is not cached and does
not render in fetch, and the repo's only cached source paper (2407.08929) is the CUBIC
inspiral EFT, which cites Cano 2021 for the QNM corrections rather than tabulating the
quartic delta_V. Negative preserved.

So this cycle extracts a source-backed result from data the repo ALREADY holds: the qEFT/
ParSpec QNM deformation coefficients for BOTH overtones (n=0 fundamental and n=1 first
overtone), from Silva-Ghosh-Buonanno (2205.05132). Reconstructing the complex shift per
unit dimensionless coupling gamma (ParSpec: omega_R = omega_R^0 (1+gamma dwq), tau = tau^0
(1+gamma dtq), tau ~ -1/omega_I):

    d(omega_R)/d(gamma) = omega_R^0 * dwq ,   d(omega_I)/d(gamma) = -omega_I^0 * dtq .

Finding: the FIRST OVERTONE is dramatically more sensitive to the R4 correction than the
fundamental, driven by a very large damping-time coefficient (dtq_1 = 171.35). This is
physically expected -- overtones decay fast and probe the near-horizon region, where the
higher-curvature (R4) correction concentrates -- and it identifies overtone ringdown
spectroscopy as the dominant (if perturbatively delicate) lever for higher-curvature gravity.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.r4_parspec_qeft_source_asset_audit import (
    QEFT_QNM_DEFORMATION_COEFFICIENTS as QC,
)

VERSION = "v2.217"
DEFAULT_OUT = Path("experiments/results/v2.217/qnm_r4_overtone_sensitivity.json")

# GR QNM frequencies, l=2, gravitational, M=1 (Berti-Cardoso-Will)
OMEGA0 = {0: complex(0.373672, -0.088962), 1: complex(0.346711, -0.273915)}


def qeft_shift_per_gamma(n: int) -> complex:
    d = QC[f"nmax_{n}"]
    dwq = d[f"delta_omega_qeft_{n}"]
    dtq = d[f"delta_tau_qeft_{n}"]
    return complex(OMEGA0[n].real * dwq, -OMEGA0[n].imag * dtq)


def run() -> dict:
    s0 = qeft_shift_per_gamma(0)
    s1 = qeft_shift_per_gamma(1)
    d0, d1 = QC["nmax_0"], QC["nmax_1"]
    return {
        "version": VERSION,
        "source": "Silva-Ghosh-Buonanno (2205.05132) qEFT deformation coefficients (repo extraction)",
        "qeft_coefficients": {
            "n0": {"delta_omega": d0["delta_omega_qeft_0"], "delta_tau": d0["delta_tau_qeft_0"]},
            "n1": {"delta_omega": d1["delta_omega_qeft_1"], "delta_tau": d1["delta_tau_qeft_1"]},
        },
        "complex_shift_per_gamma": {
            "n0": [s0.real, s0.imag], "n1": [s1.real, s1.imag],
            "magnitude_n0": abs(s0), "magnitude_n1": abs(s1),
        },
        "overtone_enhancement": {
            "freq_shift_ratio_n1_over_n0": abs(d1["delta_omega_qeft_1"]) / abs(d0["delta_omega_qeft_0"]),
            "damping_shift_ratio_n1_over_n0": abs(d1["delta_tau_qeft_1"]) / abs(d0["delta_tau_qeft_0"]),
            "complex_shift_magnitude_ratio_n1_over_n0": abs(s1) / abs(s0),
            "damping_response_sign_n0": "faster (Delta omega_I < 0)" if s0.imag < 0 else "slower",
            "damping_response_sign_n1": "faster (Delta omega_I < 0)" if s1.imag < 0 else "slower (Delta omega_I > 0)",
            "damping_signs_opposite": bool((s0.imag < 0) != (s1.imag < 0)),
        },
        "finding": (
            f"The n=1 first overtone is ~{abs(s1)/abs(s0):.0f}x more sensitive to the R4 "
            f"correction than the n=0 fundamental (driven by dtq_1 = {d1['delta_tau_qeft_1']}, "
            f"~{abs(d1['delta_tau_qeft_1'])/abs(d0['delta_tau_qeft_0']):.0f}x the fundamental's "
            "damping coefficient), and the two overtones respond with OPPOSITE sign in the "
            "damping: the fundamental decays faster under R4 while the first overtone decays "
            "much slower. Overtones probe the near-horizon region where R4 curvature corrections "
            "concentrate, so overtone-resolved ringdown is the dominant lever for higher-curvature "
            "gravity (cf the active overtone-ringdown literature, e.g. arXiv:2512.22728)."
        ),
        "perturbative_caveat": (
            f"dtq_1 = {d1['delta_tau_qeft_1']} is very large (O(170)); the ParSpec linear-in-gamma "
            "expansion is therefore only valid for gamma << 1/170 ~ 6e-3, so the overtone bound is "
            "perturbatively DELICATE even as it dominates the constraint. The precise n=1 value "
            "should be treated cautiously; the QUALITATIVE result (overtones vastly more sensitive) "
            "is robust."
        ),
        "claim_gate": (
            "closed on the full R4 ringdown sensitivity: the complete odd-parity delta_V (all "
            "radial terms) for a McManus cross-check is NOT sourceable this cycle (2205.05132 "
            "appendix not cached/renderable; cached 2407.08929 is the cubic inspiral paper). The "
            "overtone hierarchy here is SOURCE-BACKED (reads the published qEFT coefficients) and "
            "claim-grade as a relative statement; an independent McManus n=1 e_j cross-check is the "
            "next step. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132)",
            "active overtone-ringdown probes of higher-curvature gravity, e.g. arXiv:2512.22728",
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
    e = res["overtone_enhancement"]
    print(f"complex shift |n1|/|n0| = {e['complex_shift_magnitude_ratio_n1_over_n0']:.0f}x")
    print(f"damping coeff ratio n1/n0 = {e['damping_shift_ratio_n1_over_n0']:.0f}x")
    print(f"damping signs opposite = {e['damping_signs_opposite']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
