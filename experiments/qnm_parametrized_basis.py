"""v2.214 - Operator->QNM sensitivity via the published parametrized-ringdown basis.

v2.212/v2.213 showed the in-house WKB-peak shortcut and a few-% direct re-solve cannot
produce claim-grade operator->QNM sensitivities, which need ~1e-3 frequency precision. The
right move is NOT to recompute the sensitivities in-house, but to USE the published,
peer-reviewed ones: McManus, Berti, Macedo, Kimura, Maselli, Cardoso (PRD 99 (2019)
104077) tabulate the linear QNM-shift coefficients e_j for the basis

    delta_V = (1/r_H^2) sum_j alpha_j (r_H/r)^j,    omega = omega_0 + sum_j alpha_j e_j,

with r_H = 2M. So the engine's job is: (1) take a modified Regge-Wheeler potential delta_V(r),
(2) DECOMPOSE it into the (r_H/r)^j basis -> the alpha_j (a power expansion in u = r_H/r),
(3) CONTRACT with the published e_j -> the QNM shift. The e_j are the claim-grade transfer
function; the engine supplies the (source-backed) delta_V and the linear algebra.

This module builds and validates that machinery. The physical R4 quartic delta_V (and the
extended e_j table needed for its convergence) is the next input (v2.215); the parity-odd
axis g_R4_c3 stays dark (v2.209).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

import numpy as np

VERSION = "v2.214"
DEFAULT_OUT = Path("experiments/results/v2.214/qnm_parametrized_basis.json")
R_H = 2.0
# McManus et al. Table 1, odd-parity gravitational l=2 n=0, in M=1 units (= tabulated
# r_H*e_j / 2). Source-backed transfer coefficients; extend the table for a real delta_V.
E_J = {
    0: complex(0.12362, 0.04632),
    1: complex(0.07992, 0.00910),
    2: complex(0.04832, -0.00121),
}


def decompose_delta_V(delta_V: Callable[[float], float], jmax: int,
                      u_fit: float = 0.85, npts: int = 400) -> list[complex]:
    """Power-series coefficients alpha_j of delta_V in the (r_H/r)^j basis.

    delta_V(r) = (1/r_H^2) sum_j alpha_j (r_H/r)^j  ->  with u = r_H/r,
    h(u) = r_H^2 * delta_V(r_H/u) = sum_j alpha_j u^j. So alpha_j are the Taylor
    coefficients of h(u) at u=0, recovered by a polynomial fit on u in (0, u_fit]."""
    us = np.linspace(1e-3, u_fit, npts)
    h = np.array([R_H**2 * delta_V(R_H / u) for u in us])
    # fit h(u) = sum_{j=0}^{jmax} alpha_j u^j  (power basis)
    coeffs = np.polynomial.polynomial.polyfit(us, h, jmax)
    return [complex(c) for c in coeffs]


def qnm_shift(alphas: list[complex]) -> complex:
    """delta_omega = sum_j alpha_j e_j over the available published e_j."""
    return sum(alphas[j] * E_J[j] for j in range(len(alphas)) if j in E_J)


def basis_delta_V(k: int) -> Callable[[float], float]:
    return lambda r: (1.0 / R_H**2) * (R_H / r) ** k


def validate() -> dict:
    jmax = max(E_J)
    rows = []
    # (1) each basis function delta_V_k must decompose to alpha_k=1 and shift by e_k
    for k in E_J:
        a = decompose_delta_V(basis_delta_V(k), jmax)
        dw = qnm_shift(a)
        rows.append({
            "test": f"basis_j{k}",
            "alpha_recovered": [round(abs(x), 4) for x in a],
            "alpha_k_err": abs(a[k] - 1.0),
            "delta_omega_re": dw.real, "delta_omega_im": dw.imag,
            "e_k_re": E_J[k].real, "e_k_im": E_J[k].imag,
            "shift_matches_e_k": abs(dw - E_J[k]) / abs(E_J[k]),
        })
    # (2) linearity: a combination delta_V = 1*dV0 + 2*dV1 - 0.5*dV2 -> 1 e0 + 2 e1 - 0.5 e2
    combo = lambda r: (basis_delta_V(0)(r) + 2 * basis_delta_V(1)(r)
                       - 0.5 * basis_delta_V(2)(r))
    a_combo = decompose_delta_V(combo, jmax)
    dw_combo = qnm_shift(a_combo)
    expected = E_J[0] + 2 * E_J[1] - 0.5 * E_J[2]
    combo_err = abs(dw_combo - expected) / abs(expected)

    basis_ok = all(r["alpha_k_err"] < 1e-6 and r["shift_matches_e_k"] < 1e-9 for r in rows)
    return {
        "version": VERSION,
        "method": "decompose delta_V in the McManus (r_H/r)^j basis; contract with published e_j",
        "e_j_source": "McManus et al. PRD 99 (2019) 104077, Table 1 (odd-parity grav. l=2 n=0)",
        "basis_function_tests": rows,
        "basis_functions_recover_e_j": bool(basis_ok),
        "linearity_test": {"alpha": [round(abs(x), 4) for x in a_combo],
                           "delta_omega": [dw_combo.real, dw_combo.imag],
                           "expected": [expected.real, expected.imag],
                           "rel_error": combo_err},
        "linearity_ok": bool(combo_err < 1e-6),
        "machinery_validated": bool(basis_ok and combo_err < 1e-6),
        "finding": (
            "The operator->QNM route is REFRAMED: instead of an in-house machine-precision QNM "
            "solver (the v2.212/v2.213 impasse), decompose any modified potential delta_V into "
            "the published McManus (r_H/r)^j basis and contract with their peer-reviewed e_j. The "
            "decomposition + contraction machinery is exact and validated here (basis functions "
            "recover e_k; linear combinations sum correctly). The e_j are the claim-grade transfer "
            "function; the engine supplies the source-backed delta_V."
        ),
        "claim_gate": (
            "closed: machinery validated, but a framework claim still needs (a) the PHYSICAL "
            "source-backed R4 quartic delta_V (v2.215, parity-even only; g_R4_c3 dark per v2.209), "
            "(b) the EXTENDED e_j table for convergence at the photon sphere, (c) systematics + "
            "external review."
        ),
        "references": ["McManus, Berti, Macedo, Kimura, Maselli, Cardoso, PRD 99 (2019) 104077"],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = validate()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    for r in res["basis_function_tests"]:
        print(f"{r['test']}: alpha_k_err {r['alpha_k_err']:.1e}  shift_matches_e_k {r['shift_matches_e_k']:.1e}")
    print(f"linearity rel.err {res['linearity_test']['rel_error']:.1e}  "
          f"machinery_validated={res['machinery_validated']}  wrote {out}")


if __name__ == "__main__":
    main()
