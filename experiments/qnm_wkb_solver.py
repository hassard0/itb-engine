"""First-principles quasinormal-mode (QNM) solver via the 3rd-order Iyer-Will WKB method.

This is the engine's in-house black-hole-spectroscopy capability: given an effective
perturbation potential V(r) it computes the ringdown QNM frequencies omega = omega_R +
i omega_I (omega_I < 0) directly from the potential and its tortoise-coordinate
derivatives at the peak -- no external QNM library. Validated against the canonical
Schwarzschild gravitational modes:
    omega_220 = 0.373672 - 0.088962 i
    omega_221 = 0.346711 - 0.273915 i
(Berti-Cardoso-Will tabulated values, M=1, G=c=1; reproduced here to ~0.2%).

Method (Schutz-Will 1985; Iyer-Will 1987, 3rd order):
  omega^2 = [V0 + sqrt(-2 V2) Lam] - i nu sqrt(-2 V2) (1 + Om),   nu = n + 1/2,
with V_k = d^k V / dr*^k at the potential peak (r* = tortoise coordinate) and Lam, Om
the standard 2nd/3rd-order correction polynomials in the V_k and nu. Derivatives are
taken numerically via Fornberg finite-difference weights, so the solver works for ANY
potential -- including higher-derivative / EFT-modified Regge-Wheeler potentials, which is
the capability the R4 ringdown route (v2.208/v2.209) needs to compute operator->QNM
sensitivities in-house.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np

VERSION = "v2.210"
DEFAULT_OUT = Path("experiments/results/v2.210/qnm_wkb_solver.json")
REFERENCE = {0: complex(0.373672, -0.088962), 1: complex(0.346711, -0.273915)}


def f_metric(r: float) -> float:
    return 1.0 - 2.0 / r          # Schwarzschild, M = 1


def rw_potential(r: float, L: int = 2, s: int = 2) -> float:
    """Regge-Wheeler potential (M=1): V = f [ L(L+1)/r^2 + (1-s^2) 2/r^3 ]; s=2 -> -6/r^3."""
    return f_metric(r) * (L * (L + 1) / r**2 + (1 - s * s) * 2.0 / r**3)


def r_of_rstar(rstar: float, r_guess: float | None = None) -> float:
    """Invert r* = r + 2 ln(r/2 - 1) (Newton)."""
    r = r_guess if (r_guess is not None and r_guess > 2.0) else max(rstar, 2.01)
    for _ in range(80):
        val = r + 2.0 * math.log(r / 2.0 - 1.0) - rstar
        d = 1.0 + 2.0 / (r - 2.0)
        step = val / d
        r -= step
        if r <= 2.0:
            r = 2.0 + 1e-13
        if abs(step) < 1e-14:
            break
    return r


def fornberg_weights(z: float, x: np.ndarray, m: int) -> np.ndarray:
    """Finite-difference weights c[k, n] for derivatives 0..m at point z on grid x."""
    n = len(x)
    c = np.zeros((m + 1, n))
    c1, c4 = 1.0, x[0] - z
    c[0, 0] = 1.0
    for i in range(1, n):
        mn = min(i, m)
        c2 = 1.0
        c5, c4 = c4, x[i] - z
        for j in range(i):
            c3 = x[i] - x[j]
            c2 *= c3
            if j == i - 1:
                for k in range(mn, 0, -1):
                    c[k, i] = c1 * (k * c[k - 1, i - 1] - c5 * c[k, i - 1]) / c2
                c[0, i] = -c1 * c5 * c[0, i - 1] / c2
            for k in range(mn, 0, -1):
                c[k, j] = (c4 * c[k, j] - k * c[k - 1, j]) / c3
            c[0, j] = c4 * c[0, j] / c3
        c1 = c2
    return c


def tortoise_derivatives(V_of_rstar: Callable[[float], float], rstar0: float,
                         order: int = 6, h: float = 0.08, half_points: int = 5) -> list[float]:
    """d^k V/dr*^k at rstar0 for k=0..order, via central Fornberg finite differences."""
    offsets = np.arange(-half_points, half_points + 1) * h
    samples = np.array([V_of_rstar(rstar0 + o) for o in offsets])
    weights = fornberg_weights(0.0, offsets, order)
    return [float(weights[k] @ samples) for k in range(order + 1)]


def find_peak_rstar(V_of_rstar: Callable[[float], float], lo: float = -2.0,
                    hi: float = 8.0) -> float:
    """Locate the potential peak in r* (coarse scan + golden-section refine)."""
    grid = np.linspace(lo, hi, 4000)
    rs0 = grid[int(np.argmax([V_of_rstar(g) for g in grid]))]
    a, b = rs0 - 0.01, rs0 + 0.01
    gr = (math.sqrt(5) - 1) / 2
    c, d = b - gr * (b - a), a + gr * (b - a)
    for _ in range(80):
        if V_of_rstar(c) < V_of_rstar(d):
            a = c
        else:
            b = d
        c, d = b - gr * (b - a), a + gr * (b - a)
    return 0.5 * (a + b)


def wkb3_from_derivs(V0: float, V2: float, V3: float, V4: float, V5: float, V6: float,
                     n: int) -> complex:
    """3rd-order Iyer-Will WKB QNM from the potential-peak tortoise derivatives."""
    nu = n + 0.5
    s = (-2.0 * V2) ** 0.5
    lam = (1.0 / s) * ((1.0 / 8) * (V4 / V2) * (0.25 + nu**2)
                       - (1.0 / 288) * (V3 / V2) ** 2 * (7 + 60 * nu**2))
    om = (1.0 / (-2.0 * V2)) * (
        (5.0 / 6912) * (V3 / V2) ** 4 * (77 + 188 * nu**2)
        - (1.0 / 384) * (V3**2 * V4 / V2**3) * (51 + 100 * nu**2)
        + (1.0 / 2304) * (V4 / V2) ** 2 * (67 + 68 * nu**2)
        + (1.0 / 288) * (V3 * V5 / V2**2) * (19 + 28 * nu**2)
        - (1.0 / 288) * (V6 / V2) * (5 + 4 * nu**2))
    w2 = (V0 + s * lam) - 1j * nu * s * (1.0 + om)
    return complex(w2 ** 0.5)


def qnm(V_of_rstar: Callable[[float], float], n: int = 0, **kw) -> complex:
    rstar0 = find_peak_rstar(V_of_rstar)
    d = tortoise_derivatives(V_of_rstar, rstar0, order=6, **kw)
    return wkb3_from_derivs(d[0], d[2], d[3], d[4], d[5], d[6], n)


def schwarzschild_qnm(n: int = 0, L: int = 2, s: int = 2, **kw) -> complex:
    V = lambda rs: rw_potential(r_of_rstar(rs), L, s)
    return qnm(V, n=n, **kw)


def qnm_potential_sensitivity(delta_V_of_r: Callable[[float], float], n: int = 0,
                              L: int = 2, s: int = 2, t: float = 1e-3, **kw) -> dict:
    """Linear QNM sensitivity d(omega)/d(eps) to a deformation V -> V + eps * delta_V.

    Computed analytically through the WKB formula: V -> V + eps delta_V shifts each
    peak tortoise-derivative V_k -> V_k + eps * (delta_V)_k, so d(omega)/d(eps) is the
    directional derivative of the smooth WKB function wkb3_from_derivs(...) along the
    deformation's derivative vector. This avoids re-solving the QNM for a tiny potential
    change (which would fight the solver's ~1e-3 floor); the finite difference is over the
    SMOOTH WKB formula with exact derivative inputs, holding the peak at linear order.

    This is the operator->QNM machinery: a higher-derivative (e.g. R4 quartic) modification
    of the Regge-Wheeler potential maps to a definite ringdown (omega_R, omega_I) shift."""
    base = lambda rs: rw_potential(r_of_rstar(rs), L, s)
    rstar0 = find_peak_rstar(base)
    Vk = tortoise_derivatives(base, rstar0, order=6, **kw)
    dVk = tortoise_derivatives(lambda rs: delta_V_of_r(r_of_rstar(rs)), rstar0,
                               order=6, **kw)

    def w_of_t(tt: float) -> complex:
        v = [Vk[k] + tt * dVk[k] for k in range(7)]
        return wkb3_from_derivs(v[0], v[2], v[3], v[4], v[5], v[6], n)

    w0 = w_of_t(0.0)
    dwde = (w_of_t(t) - w_of_t(-t)) / (2.0 * t)
    return {"omega0": w0, "d_omega_d_eps": dwde,
            "d_omega_R_d_eps": dwde.real, "d_omega_I_d_eps": dwde.imag}


def validate() -> dict:
    rows = []
    for n in (0, 1):
        w = schwarzschild_qnm(n)
        ref = REFERENCE[n]
        rel = abs(w - ref) / abs(ref)
        rows.append({"mode": f"22{n}", "omega_re": w.real, "omega_im": w.imag,
                     "ref_re": ref.real, "ref_im": ref.imag, "rel_error": rel})
    # sensitivity demonstration: a representative short-range (higher-derivative-like)
    # potential deformation delta_V ~ f(r) * M^4 / r^6 (the shape a dimension-8 / quartic
    # curvature correction contributes near the photon sphere). Shows operator->QNM works.
    demo_deltaV = lambda r: f_metric(r) * 1.0 / r**6
    sens = qnm_potential_sensitivity(demo_deltaV, n=0)

    return {
        "version": VERSION,
        "method": "3rd-order Iyer-Will WKB; exact RW potential; Fornberg tortoise derivatives",
        "units": "M=1, G=c=1",
        "validation": rows,
        "max_rel_error": max(r["rel_error"] for r in rows),
        "validated": max(r["rel_error"] for r in rows) < 5e-3,
        "sensitivity_demo": {
            "delta_V": "f(r) / r^6  (representative short-range / dim-8 deformation shape)",
            "d_omegaR_d_eps": sens["d_omega_R_d_eps"],
            "d_omegaI_d_eps": sens["d_omega_I_d_eps"],
            "note": ("operator->QNM machinery: a potential deformation maps to a finite "
                     "ringdown (omega_R, omega_I) shift. Plugging the physical R4 quartic "
                     "delta_V here yields the engine's own operator->QNM sensitivity."),
        },
        "capability": (
            "first-principles QNM frequencies from any perturbation potential; the in-house "
            "black-hole-spectroscopy tool the R4 ringdown route needs to compute "
            "operator->QNM sensitivities without a published map (cf v2.209)."
        ),
        "references": [
            "Schutz & Will, ApJ 291 (1985) L33", "Iyer & Will, PRD 35 (1987) 3621",
            "Berti, Cardoso, Will, PRD 73 (2006) 064030 (tabulated omega values)",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    result = validate()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
    for r in result["validation"]:
        print(f"omega_{r['mode']} = {r['omega_re']:.6f} {r['omega_im']:+.6f}i  "
              f"ref {r['ref_re']:.6f} {r['ref_im']:+.6f}i  rel.err={r['rel_error']:.2e}")
    print(f"validated={result['validated']}  wrote {out}")


if __name__ == "__main__":
    main()
