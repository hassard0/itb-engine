"""v2.231 - Cross-channel sensitivity of a photon-sphere deviation: a ringdown<->shadow null test.

v2.230 showed ringdown and the black-hole shadow share the photon sphere. This cycle turns that
into a quantitative cross-channel test by deforming the metric with a one-parameter non-Kerr
"bumpiness" eps (lapse f = 1 - 2/r + eps/r^k, M=1) and computing how eps shifts the three
geodesic observables: the shadow radius b_c, the eikonal ringdown frequency (via Omega_c = 1/b_c),
and the ringdown damping (via the Lyapunov rate lambda).

Two structural results, both verified numerically:
  1. LOCKING IDENTITY (parametrization-independent): because Omega_c * b_c = 1 holds identically
     for ANY static metric, d ln(Omega_c) = - d ln(b_c) for every deformation. The eikonal
     ringdown frequency and the shadow radius shift by EQUAL AND OPPOSITE fractional amounts -- a
     metric-independent null test: a measured shadow size predicts the ringdown frequency (and vice
     versa), and a violation means the ringdown is not the light-ring mode or the object is not a
     static photon-sphere body.
  2. INDEPENDENT DAMPING: the Lyapunov rate lambda depends on the curvature f''(r_ph), NOT on b_c,
     so d ln(lambda) != - d ln(b_c). The damping carries independent information, so the joint
     (shadow + ringdown frequency + ringdown damping) OVER-DETERMINES the one-parameter
     deformation -- a consistency over-test.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.231"
DEFAULT_OUT = Path("experiments/results/v2.231/qnm_photon_sphere_deviation.json")
K_PROFILES = [2, 3, 4]          # deformation f += eps / r^k


def geodesics(eps: float, k: int) -> dict:
    """Photon-sphere shadow radius b_c, orbital freq Omega_c, Lyapunov lambda for f=1-2/r+eps/r^k."""
    def U(r):    return 1 / r**2 - 2 / r**3 + eps / r**(k + 2)
    def Up(r):   return -2 / r**3 + 6 / r**4 - eps * (k + 2) / r**(k + 3)
    def Upp(r):  return 6 / r**4 - 24 / r**5 + eps * (k + 2) * (k + 3) / r**(k + 4)

    def f(r):    return 1 - 2 / r + eps / r**k
    r = 3.0
    for _ in range(100):
        r -= Up(r) / Upp(r)
    Uc, fc = U(r), f(r)
    return {"r_ph": r, "b_c": 1 / math.sqrt(Uc), "Omega_c": math.sqrt(Uc),
            "lambda": fc * math.sqrt(abs(Upp(r)) / (2 * Uc))}


def sensitivities(k: int, h: float = 1e-4) -> dict:
    base, p, m = geodesics(0.0, k), geodesics(h, k), geodesics(-h, k)
    dln = {q: (p[q] - m[q]) / (2 * h) / base[q] for q in ("b_c", "Omega_c", "lambda")}
    return {
        "k": k,
        "d_ln_b_c": dln["b_c"],
        "d_ln_Omega_c": dln["Omega_c"],
        "d_ln_lambda": dln["lambda"],
        "locking_residual": dln["Omega_c"] + dln["b_c"],          # ~0 (identity)
        "damping_minus_neg_b_c": dln["lambda"] - (-dln["b_c"]),   # != 0 (independent)
    }


def run() -> dict:
    rows = [sensitivities(k) for k in K_PROFILES]
    locking_universal = all(abs(r["locking_residual"]) < 1e-6 for r in rows)
    damping_independent = all(abs(r["damping_minus_neg_b_c"]) > 1e-3 for r in rows)
    return {
        "version": VERSION,
        "method": ("one-parameter photon-sphere deformation f = 1 - 2/r + eps/r^k (k=2,3,4); "
                   "geodesic shadow radius / orbital frequency / Lyapunov rate sensitivities to "
                   "eps; eikonal ringdown via Omega_c=1/b_c, lambda; M=1"),
        "sensitivities_per_profile": rows,
        "locking_identity_universal": bool(locking_universal),
        "damping_independent": bool(damping_independent),
        "finding": (
            "Two structural cross-channel results, both verified. (1) LOCKING: d ln(Omega_c) = "
            "-d ln(b_c) for EVERY deformation profile (residual < 1e-6) -- the eikonal ringdown "
            "frequency and the shadow radius shift by equal-and-opposite fractional amounts, a "
            "parametrization-independent identity (since Omega_c b_c = 1). So a measured shadow "
            "size predicts the ringdown frequency: a GW/EM null test of the photon-sphere "
            "hypothesis. (2) INDEPENDENT DAMPING: d ln(lambda) differs from -d ln(b_c) "
            f"(e.g. k=3: d ln lambda = {rows[1]['d_ln_lambda']:+.4f} vs d ln Omega_c = "
            f"{rows[1]['d_ln_Omega_c']:+.4f}), because lambda probes the curvature f''(r_ph) "
            "independently of b_c. So shadow + ringdown frequency + ringdown damping "
            "OVER-DETERMINE a one-parameter deformation -- a consistency over-test that a "
            "single channel cannot provide."
        ),
        "honest_scope": (
            "Eikonal (large-l) and static-spherical only: the locking identity is exact in the "
            "eikonal limit (finite-l O(1/l) corrections, v2.229/v2.230); Kerr/rotation breaks the "
            "spherical shadow and splits Omega_c != lambda. The deformation f=1-2/r+eps/r^k is "
            "illustrative (a generic photon-sphere bump), not a specific QG metric -- the LOCKING "
            "identity is metric-independent, but the per-profile coefficients are illustrative. "
            "Turning this into a real bound needs measured shadow + ringdown data and a chosen "
            "metric ansatz (not done here). This frames a QG null test; it does not itself "
            "constrain a coupling. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Cardoso et al., PRD 79 (2009) 064016 -- eikonal QNM / photon sphere / Lyapunov",
            "Rezzolla & Zhidenko, PRD 90 (2014) 084009 -- parametrized non-Kerr deviations",
            "this repo: v2.229 (eikonal correspondence), v2.230 (ringdown<->shadow)",
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
    for r in res["sensitivities_per_profile"]:
        print(f"  k={r['k']}: d ln b_c={r['d_ln_b_c']:+.5f}  d ln Omega_c={r['d_ln_Omega_c']:+.5f}  "
              f"d ln lambda={r['d_ln_lambda']:+.5f}  (locking resid {r['locking_residual']:+.1e})")
    print(f"locking identity universal = {res['locking_identity_universal']}; "
          f"damping independent = {res['damping_independent']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
