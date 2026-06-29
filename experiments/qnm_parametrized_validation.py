"""v2.212 - Validate the in-house operator->QNM sensitivity against the published
parametrized-ringdown coefficients of McManus, Berti, Macedo, Kimura, Maselli, Cardoso
(PRD 99, 104077 (2019), arXiv:1901.01265).

That framework writes the modified Regge-Wheeler potential as
    delta_V = (1/r_H^2) sum_j alpha_j (r_H/r)^j,   r_H = 2M = 2 (M=1),
and the QNM shift is linear: omega = omega_0 + sum_j alpha_j e_j, with e_j tabulated
(complex). So d(omega)/d(alpha_j) computed by qnm_potential_sensitivity should reproduce
e_j. We compare for the gravitational (odd-parity, Regge-Wheeler) l=2, n=0 fundamental.

Tabulated r_H * e_j (Table 1, odd-parity gravitational, l=2 n=0):
    j=0: 0.24725  + 0.092643 i
    j=1: 0.15985  + 0.018208 i
    j=2: 0.096632 - 0.0024155 i
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.qnm_wkb_solver import qnm_potential_sensitivity

VERSION = "v2.212"
DEFAULT_OUT = Path("experiments/results/v2.212/qnm_parametrized_validation.json")
R_H = 2.0                                  # horizon radius, M=1
# tabulated r_H * e_j (odd-parity gravitational, l=2, n=0); McManus et al. Table 1
RH_E = {0: complex(0.24725, 0.092643),
        1: complex(0.15985, 0.018208),
        2: complex(0.096632, -0.0024155)}


def basis_delta_V(j: int):
    """delta_V_j(r) = (1/r_H^2) (r_H/r)^j  -- the McManus parametrization basis."""
    return lambda r: (1.0 / R_H**2) * (R_H / r) ** j


def run() -> dict:
    rows = []
    for j in (0, 1, 2):
        sens = qnm_potential_sensitivity(basis_delta_V(j), n=0)
        e_wkb = sens["d_omega_d_eps"]          # d(omega)/d(alpha_j), M=1 units
        e_ref = RH_E[j] / R_H                   # tabulated e_j in M=1 units
        rel = abs(e_wkb - e_ref) / abs(e_ref)
        rows.append({
            "j": j,
            "e_wkb_re": e_wkb.real, "e_wkb_im": e_wkb.imag,
            "e_ref_re": e_ref.real, "e_ref_im": e_ref.imag,
            "rel_error": rel,
        })
    max_rel = max(r["rel_error"] for r in rows)
    return {
        "version": VERSION,
        "target": "McManus et al. PRD 99 (2019) 104077 parametrized-ringdown e_j "
                  "(odd-parity gravitational, l=2, n=0)",
        "basis": "delta_V_j = (1/r_H^2)(r_H/r)^j, r_H=2 (M=1); omega=omega_0+sum_j alpha_j e_j",
        "comparison": rows,
        "max_rel_error": max_rel,
        "wkb_peak_sensitivity_reproduces_e_j": bool(max_rel < 0.10),
        "finding": (
            "NEGATIVE: the WKB-at-peak operator->QNM sensitivity (v2.211) is numerically "
            "STABLE but NOT ACCURATE -- it misses the published parametrized-ringdown e_j by "
            "~150% (a consistent ~2.5x on the real parts, with the imaginary parts diverging, "
            "so it is not a fixable normalization). Stability != correctness."
        ),
        "diagnosis": (
            "The exact first-order QNM sensitivity is a GLOBAL mode-overlap integral, "
            "d(omega)/d(alpha_j) = integral psi_0^2 delta_V_j dr* / (2 omega_0 integral psi_0^2 "
            "dr*), over the (regularized) QNM eigenfunction -- this is what McManus et al. "
            "compute. 3rd-order WKB-at-peak only uses delta_V_j's value and derivatives at the "
            "single potential-peak point, so it captures the correct STRUCTURE (finite, complex, "
            "j-dependent, decreasing with j) but is quantitatively off by O(1) factors for these "
            "slowly-varying / horizon-weighted basis functions. The QNM frequencies themselves "
            "(v2.210/v2.211) remain validated; only the peak-shortcut SENSITIVITY is inaccurate."
        ),
        "fix_next": (
            "v2.213: implement the proper first-order overlap-integral sensitivity using the "
            "QNM eigenfunction (with the QNM norm / Leung-Maassen-van den Brink regularization), "
            "or full Leaver-grade re-solve of V + delta_V, and re-validate against e_j."
        ),
        "claim_gate": "closed: in-house operator->QNM sensitivity is NOT yet claim-grade.",
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    for r in res["comparison"]:
        print(f"j={r['j']}: e_wkb={r['e_wkb_re']:+.5f}{r['e_wkb_im']:+.5f}i  "
              f"e_ref={r['e_ref_re']:+.5f}{r['e_ref_im']:+.5f}i  rel.err={r['rel_error']:.3f}")
    print(f"max_rel_error={res['max_rel_error']:.3f}  wrote {out}")


if __name__ == "__main__":
    main()
