"""v2.213 - Independent Riccati (log-derivative) QNM solver, and the precision requirement
for claim-grade operator->QNM sensitivities.

Two results:
  (A) An INDEPENDENT QNM method. phi = psi'/psi (d/dr*) satisfies phi' = -(phi^2 + omega^2
      - V); phi stays bounded (no amplitude blow-up), so two-sided matching phi_L(match) =
      phi_R(match) is well-conditioned. This independently lands omega_220 within ~4% of the
      exact value, confirming the WKB solver (v2.210) is in the right place with a completely
      different method. It is BC-limited (the finite-r outgoing asymptotic) and does not
      improve with domain size, so a few-% is its floor without a higher-order asymptotic
      series -- i.e. it is a ballpark cross-check, not a precision tool.

  (B) The PRECISION REQUIREMENT (extends v2.212). v2.212 showed the WKB-at-peak sensitivity
      misses the published parametrized-ringdown e_j by ~150% (peak-vs-global). Here we show
      a FULL global re-solve at ~1% precision ALSO fails: finite-differencing two ~1%-accurate
      omegas for the small e_j (~0.05-0.12) gives erratic results (rel.err 0.5-3.4, even sign
      flips), because the BC error differs between V and V+delta_V. CONCLUSION: a claim-grade
      in-house operator->QNM sensitivity requires a QNM solver accurate to << e_j * alpha ~
      1e-3 (a pseudospectral / Leaver continued-fraction solver), not a peak shortcut and not
      a ~1% direct re-solve.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, ".")
from experiments.qnm_wkb_solver import schwarzschild_qnm

VERSION = "v2.213"
DEFAULT_OUT = Path("experiments/results/v2.213/qnm_riccati_solver.json")
R_H = 2.0
REF = {(2, 0): complex(0.3736716844, -0.0889623157),
       (2, 1): complex(0.3467110, -0.2739150)}
# McManus et al. parametrized-ringdown e_j (M=1, odd-parity gravitational l=2 n=0)
E_REF = {0: complex(0.12362, 0.04632), 1: complex(0.07992, 0.00910),
         2: complex(0.04832, -0.00121)}


def r_of_rstar(rstar: float, rg: float | None = None) -> float:
    r = rg if (rg and rg > 2.0) else max(rstar, 2.01)
    for _ in range(80):
        val = r + 2.0 * math.log(r / 2.0 - 1.0) - rstar
        r -= val / (1.0 + 2.0 / (r - 2.0))
        if r <= 2.0:
            r = 2.0 + 1e-13
    return r


def rw_potential(r: float, L: int = 2, s: int = 2) -> float:
    f = 1.0 - 2.0 / r
    return f * (L * (L + 1) / r**2 + (1 - s * s) * 2.0 / r**3)


def _phi_integrate(omega: complex, Vfunc: Callable[[float], float], ra: float, rb: float,
                   phi0: complex, n: int) -> complex:
    h = (rb - ra) / n
    rs, rg, phi = ra, r_of_rstar(ra), phi0
    for _ in range(n):
        def g(rstar, ph, rgg):
            r = r_of_rstar(rstar, rgg)
            return -(ph * ph + omega * omega - Vfunc(r)), r
        k1, r1 = g(rs, phi, rg)
        k2, _ = g(rs + 0.5 * h, phi + 0.5 * h * k1, r1)
        k3, _ = g(rs + 0.5 * h, phi + 0.5 * h * k2, r1)
        k4, r4 = g(rs + h, phi + h * k3, r1)
        phi += (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        rs += h
        rg = r4
    return phi


def riccati_wronskian(omega: complex, Vfunc: Callable[[float], float], L: int = 2,
                      rmin: float = -30.0, rmax: float = 40.0, rmatch: float = 2.39,
                      n: int = 6000) -> complex:
    phiL = _phi_integrate(omega, Vfunc, rmin, rmatch, -1j * omega, n)
    rR = r_of_rstar(rmax)
    fR = 1.0 - 2.0 / rR
    phiR0 = 1j * omega - 1j * L * (L + 1) * fR / (2.0 * omega * rR * rR)
    phiR = _phi_integrate(omega, Vfunc, rmax, rmatch, phiR0, n)
    return phiL - phiR


def _muller(f, x0, x1, x2, tol=1e-12, maxit=200):
    f0, f1, f2 = f(x0), f(x1), f(x2)
    for _ in range(maxit):
        q = (x2 - x1) / (x1 - x0)
        A = q * f2 - q * (1 + q) * f1 + q * q * f0
        B = (2 * q + 1) * f2 - (1 + q) ** 2 * f1 + q * q * f0
        C = (1 + q) * f2
        dsc = cmath.sqrt(B * B - 4 * A * C)
        den = B + dsc if abs(B + dsc) > abs(B - dsc) else B - dsc
        if den == 0:
            break
        x3 = x2 - (x2 - x1) * 2 * C / den
        f3 = f(x3)
        x0, x1, x2, f0, f1, f2 = x1, x2, x3, f1, f2, f3
        if abs(x3 - x2) < tol:
            break
    return x2


def riccati_qnm(seed: complex, Vfunc: Callable[[float], float] | None = None, L: int = 2,
                **kw) -> complex:
    V = Vfunc if Vfunc is not None else (lambda r: rw_potential(r, L))
    return _muller(lambda w: riccati_wronskian(w, V, L=L, **kw), seed * 0.99, seed * 1.01, seed)


def cross_validate() -> list[dict]:
    rows = []
    for (L, n), ref in REF.items():
        w_ric = riccati_qnm(ref, L=L)
        w_wkb = schwarzschild_qnm(n=n, L=L)
        rows.append({
            "mode": f"l{L}_n{n}",
            "riccati_re": w_ric.real, "riccati_im": w_ric.imag,
            "riccati_rel_err": abs(w_ric - ref) / abs(ref),
            "wkb_rel_err": abs(w_wkb - ref) / abs(ref),
            "two_methods_agree_to": abs(w_ric - w_wkb) / abs(ref),
        })
    return rows


def sensitivity_precision_study(alpha: float = 0.15) -> dict:
    """Compute e_j via a full Riccati re-solve of V + alpha*delta_V_j; show ~1% omega
    precision is INSUFFICIENT for the small e_j (erratic)."""
    rows = []
    base = lambda r: rw_potential(r, 2)
    for j in (0, 1, 2):
        def Vp(r, j=j, sgn=+1):
            return base(r) + sgn * alpha * (1.0 / R_H**2) * (R_H / r) ** j
        wp = riccati_qnm(REF[(2, 0)], Vfunc=lambda r, j=j: Vp(r, j, +1))
        wm = riccati_qnm(REF[(2, 0)], Vfunc=lambda r, j=j: Vp(r, j, -1))
        ej = (wp - wm) / (2 * alpha)
        rows.append({"j": j, "e_resolve_re": ej.real, "e_resolve_im": ej.imag,
                     "e_ref_re": E_REF[j].real, "e_ref_im": E_REF[j].imag,
                     "rel_error": abs(ej - E_REF[j]) / abs(E_REF[j])})
    return {"alpha": alpha, "rows": rows,
            "max_rel_error": max(r["rel_error"] for r in rows),
            "resolve_at_1pct_reproduces_e_j": bool(max(r["rel_error"] for r in rows) < 0.10)}


def run() -> dict:
    cv = cross_validate()
    sp = sensitivity_precision_study()
    return {
        "version": VERSION,
        "riccati_method": "log-derivative two-sided matching; independent of WKB",
        "cross_validation": cv,
        "riccati_omega220_rel_err": cv[0]["riccati_rel_err"],
        "fundamental_two_methods_agree_few_pct": bool(cv[0]["two_methods_agree_to"] < 5e-2),
        "sensitivity_precision_study": sp,
        "two_methods_agree_to": cv[0]["two_methods_agree_to"],
        "finding": (
            "Two independent QNM methods (WKB v2.210 at ~0.15%, Riccati here at ~4%) land "
            "omega_220 in the same place (agreeing to ~4%), confirming the frequency. BUT a "
            "full few-%-precision re-solve does NOT yield claim-grade e_j: finite-differencing "
            "two few-%-accurate omegas for the small e_j (~0.05-0.12) is erratic (rel.err "
            "0.5-3.5, sign flips). Combined with v2.212 (WKB-peak shortcut off ~150%), this "
            "SCOPES the requirement: a claim-grade in-house operator->QNM sensitivity needs a "
            "QNM solver accurate to << e_j*alpha ~ 1e-3 -- a pseudospectral (Chebyshev "
            "hyperboloidal) or Leaver continued-fraction solver, NOT a peak shortcut and NOT a "
            "few-% direct re-solve."
        ),
        "claim_gate": "closed: in-house operator->QNM sensitivity is NOT yet claim-grade; "
                      "v2.214 = high-precision pseudospectral solver.",
        "references": [
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 (omega values)",
            "McManus et al., PRD 99 (2019) 104077 (e_j)",
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
    for r in res["cross_validation"]:
        print(f"{r['mode']}: riccati rel.err {r['riccati_rel_err']:.2e}  "
              f"wkb rel.err {r['wkb_rel_err']:.2e}  agree {r['two_methods_agree_to']:.2e}")
    sp = res["sensitivity_precision_study"]
    for r in sp["rows"]:
        print(f"j={r['j']}: e_resolve rel.err {r['rel_error']:.3f}")
    print(f"resolve_at_1pct_reproduces_e_j = {sp['resolve_at_1pct_reproduces_e_j']}  wrote {out}")


if __name__ == "__main__":
    main()
