"""v2.215 - The engine's source-backed R4 (quartic-curvature) odd-parity ringdown sensitivity.

Combining two independent published results via the v2.214 contraction machinery:

  - Modified potential (Silva-Ghosh-Buonanno, arXiv:2205.05132, the repo's existing qEFT
    source): the leading odd-parity (axial / Regge-Wheeler) correction from the quartic
    (dimension-8 = R4) curvature operator is a SINGLE high power,
        delta_V_l^- = -18 eta_2 (l+2)(l+1) l (l-1) (r_g/r)^10 ,
    which for l=2 is delta_V_2^- = -432 eta_2 (r_g/r)^10  (eta_2 = parity-even quartic
    coupling; the perturbation is odd-parity but the OPERATOR is parity-even, so this is
    the parity-even R4 slice -- the parity-odd operator axis g_R4_c3 stays dark, v2.209).

  - Transfer coefficient (McManus et al., PRD 99 (2019) 104077, Table 1): the linear
    QNM-shift coefficient for the odd-parity gravitational l=2 n=0 basis function (r_H/r)^10
    is  r_H * e_10^- = 0.0036853 + 0.0065244 i  ->  e_10^- (M=1) = that / r_H.

Because delta_V is a SINGLE basis function at j=10, the McManus contraction is exact and
needs only e_10 (no convergence series): with r_g = 2M = r_H (standard gravitational radius),
    alpha_10 = r_H^2 * (-432 eta_2)  and  d(omega)/d(eta_2) = alpha_10/eta_2 * e_10
             = -432 * r_H^2 * e_10 = -1728 * e_10  (M=1).

HONEST: the r_g = 2M normalization and the completeness of the single-(r_g/r)^10 form are
taken from the search-surfaced expression; the exact convention and whether other terms
contribute live in the 2205.05132 appendix (not machine-readable here). The claim gate stays
closed on the final NUMBER pending that appendix check and the eta_2<->gamma map needed to
cross-validate against the repo's qEFT deformation coefficients (delta_omega_qeft_0 = -0.2114).
What is solid: e_10 is sourced, the R4 quartic odd-parity operator lives at j=10 in the
McManus basis, and the contraction machinery (v2.214) is exact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.qnm_parametrized_basis import R_H, decompose_delta_V

VERSION = "v2.215"
DEFAULT_OUT = Path("experiments/results/v2.215/qnm_r4_sensitivity.json")

# McManus et al. Table 1, odd-parity gravitational l=2 n=0: r_H * e_j^-  (sourced; this
# cycle adds j=3,4,10 to the j=0,1,2 of v2.214). e_j (M=1) = these / r_H.
RH_E_J = {
    0: complex(0.24725, 0.092643),
    1: complex(0.15985, 0.018208),
    2: complex(0.096632, -0.0024155),
    3: complex(0.058491, -0.0037179),
    4: complex(0.036679, -0.00043870),
    10: complex(0.0036853, 0.0065244),
}
E_J = {j: v / R_H for j, v in RH_E_J.items()}            # M=1 units

# R4 quartic odd-parity correction, l=2: delta_V_2^- = -18*eta_2*(l+2)(l+1)l(l-1)*(r_g/r)^10
L = 2
R4_ODD_PREFACTOR = -18 * (L + 2) * (L + 1) * L * (L - 1)  # = -432 for l=2
R_G = 2.0                                                  # r_g = 2M = horizon (M=1)


def r4_delta_V(eta2: float = 1.0):
    """Odd-parity Regge-Wheeler correction from the quartic (R4) operator (per eta_2)."""
    return lambda r: R4_ODD_PREFACTOR * eta2 * (R_G / r) ** 10


def r4_sensitivity() -> dict:
    # alpha_10 analytically: delta_V = c*(r_g/r)^10 = (1/r_H^2) alpha_10 (r_H/r)^10
    #   with r_g = r_H -> alpha_10 = c * r_H^2 = R4_ODD_PREFACTOR * r_H^2 (per eta_2)
    c = R4_ODD_PREFACTOR                                   # per eta_2
    alpha10_analytic = c * R_H**2
    # cross-check via the v2.214 decomposition machinery (numerical polyfit)
    alphas = decompose_delta_V(r4_delta_V(1.0), jmax=10)
    alpha10_numeric = alphas[10]
    decomp_ok = abs(alpha10_numeric - alpha10_analytic) / abs(alpha10_analytic) < 1e-6
    # contraction: only j=10 is nonzero
    dwde = alpha10_analytic * E_J[10]                     # d(omega)/d(eta_2), M=1
    return {
        "r4_odd_parity_delta_V": "delta_V_2^- = -432 eta_2 (r_g/r)^10  (Silva-Ghosh-Buonanno)",
        "r_g_convention": "r_g = 2M = r_H = 2 (standard gravitational radius; M=1)",
        "alpha_10_per_eta2_analytic": alpha10_analytic,
        "alpha_10_per_eta2_numeric": [alpha10_numeric.real, alpha10_numeric.imag],
        "decomposition_cross_check_ok": bool(decomp_ok),
        "e_10_M1": [E_J[10].real, E_J[10].imag],
        "d_omega_d_eta2_re": dwde.real,
        "d_omega_d_eta2_im": dwde.imag,
        "interpretation": (
            "The engine computes the R4 (quartic, parity-even operator) odd-parity l=2 "
            "ringdown sensitivity d(omega)/d(eta_2) = -1728 * e_10 ~ "
            f"{dwde.real:.3f} {dwde.imag:+.3f} i (M=1) by combining a source-backed modified "
            "potential (2205.05132) with a source-backed transfer coefficient (McManus e_10). "
            "eta_2 > 0 lowers the ringdown frequency. This is the parity-even R4 slice; the "
            "parity-odd operator axis g_R4_c3 stays dark (v2.209)."
        ),
    }


def run() -> dict:
    sens = r4_sensitivity()
    return {
        "version": VERSION,
        "method": "source-backed delta_V (2205.05132) decomposed in the McManus basis, "
                  "contracted with source-backed e_10 (1901.01265) via v2.214 machinery",
        "e_j_sourced": {str(j): [v.real, v.imag] for j, v in RH_E_J.items()},
        "r4_odd_parity_sensitivity": sens,
        "milestone": (
            "First source-backed beyond-GR (R4 quartic) ringdown sensitivity computed in-house: "
            "two independent published results combined via the validated contraction machinery."
        ),
        "claim_gate": (
            "closed on the NUMBER: the r_g=2M normalization and the completeness of the "
            "single-(r_g/r)^10 odd-parity form are taken from the search-surfaced expression "
            "and need verification against the 2205.05132 appendix; cross-validation against "
            "the repo's qEFT coefficient (delta_omega_qeft_0=-0.2114) needs the eta_2<->gamma "
            "map. SOLID: e_10 sourced, R4 quartic odd-parity -> j=10 basis structure, exact "
            "contraction machinery. Parity-odd g_R4_c3 dark (v2.209); even-parity (Zerilli) "
            "sector and systematics + review still required before a framework claim."
        ),
        "references": [
            "Silva, Ghosh, Buonanno, PRD 107 (2023) 044030 (arXiv:2205.05132) -- modified RW potential",
            "McManus, Berti, Macedo, Kimura, Maselli, Cardoso, PRD 99 (2019) 104077 -- e_j",
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
    s = res["r4_odd_parity_sensitivity"]
    print(f"alpha_10/eta2 = {s['alpha_10_per_eta2_analytic']:.1f}  decomp_ok={s['decomposition_cross_check_ok']}")
    print(f"d(omega)/d(eta_2) = {s['d_omega_d_eta2_re']:.4f} {s['d_omega_d_eta2_im']:+.4f} i  (M=1)")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
