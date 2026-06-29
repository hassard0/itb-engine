"""v2.236 - How a deformation lifts the GR-zero tidal Love number: the new-physics signal.

v2.235 verified the GR black-hole tidal Love number is exactly zero (the horizon-regular static
perturbation is a tail-free Legendre polynomial). This cycle computes the SIGNAL: how a non-Kerr /
higher-curvature / exotic-compact-object deformation induces a NONZERO Love number -- the tidal-sector
analog of the v2.231 photon-sphere-deviation null test.

A naive outward integration of the deformed static equation is ill-conditioned (the tiny induced
x^{-l-1} response tail is swamped by the x^l growing tidal field). The stable, correct route is
FIRST-ORDER perturbation theory. Writing the static even-parity operator in self-adjoint form
[(1-x^2) y']' + [l(l+1) - 4/(1-x^2)] y = 0 and deforming the potential by eps * V(x), the horizon-
regular solution acquires an induced response whose decaying-tail coefficient is

    (B/A)  =  -(eps / W0) * INTEGRAL_1^inf  V(x) * P_l^2(x)^2  dx          (k_l proportional to B/A),

with P_l^2 the unperturbed regular (polynomial) solution and W0 the (constant) Wronskian. This is a
convergent overlap integral of known functions -- no unstable integration. The Love number is zero
in GR (no deformation -> no integral) and is lifted LINEARLY by any deformation localized enough for
the overlap to converge (i.e. near-horizon / higher-curvature new physics, V falling faster than the
growing solution).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad

VERSION = "v2.236"
DEFAULT_OUT = Path("experiments/results/v2.236/qnm_love_number_deformation.json")

# unperturbed horizon-regular solutions P_l^2(x) (polynomials)
P = {2: lambda x: 3 * (x**2 - 1), 3: lambda x: 15 * x * (x**2 - 1)}
# minimum deformation falloff n for the overlap to converge (P_l^2^2 ~ x^{2l} ; need n > 2l+1)
N_MIN = {2: 6, 3: 8}


def overlap_integral(l: int, n: int) -> float:
    """I = int_1^inf P_l^2(x)^2 / x^n dx  -- the first-order tidal-response sensitivity (V = 1/x^n)."""
    Pl = P[l]
    val, _ = quad(lambda x: Pl(x) ** 2 / x**n, 1.0, np.inf)
    return val


def closed_form_l2(n: int) -> float:
    return 9 * (1 / (n - 5) - 2 / (n - 3) + 1 / (n - 1))


def induced_love_proxy(l: int, n: int, eps: float, W0: float = 24.0) -> float:
    """First-order induced (B/A) proxy for the Love number (up to the Love-number convention)."""
    return -(eps / W0) * overlap_integral(l, n)


def run() -> dict:
    # l=2 sensitivity for several deformation localizations, verified vs closed form
    l2 = []
    for n in (6, 8, 10):
        I = overlap_integral(2, n)
        l2.append({"n": n, "overlap_integral": I, "closed_form": closed_form_l2(n),
                   "match": abs(I - closed_form_l2(n)) < 1e-6})
    # GR baseline + linearity check for n=8
    gr_zero = induced_love_proxy(2, 8, 0.0)
    lin = [induced_love_proxy(2, 8, e) for e in (0.01, 0.02, 0.04)]
    linear = abs(lin[1] / lin[0] - 2) < 1e-6 and abs(lin[2] / lin[0] - 4) < 1e-6
    # l=3 (needs faster falloff)
    l3 = [{"n": n, "overlap_integral": overlap_integral(3, n)} for n in (10, 12)]
    return {
        "version": VERSION,
        "method": ("first-order perturbation theory on the self-adjoint static even-parity operator; "
                   "induced response (B/A) = -(eps/W0) int P_l^2^2 V dx for V=1/x^n; stable overlap "
                   "integral, no unstable outward integration"),
        "l2_sensitivity": l2,
        "l3_sensitivity": l3,
        "gr_baseline_zero": gr_zero,
        "linear_in_eps": bool(linear),
        "finding": (
            "Any localized (near-horizon / higher-curvature) deformation LIFTS the GR-zero tidal "
            "Love number, linearly in the deformation strength. The induced response is the "
            "convergent overlap integral I = int_1^inf P_l^2(x)^2 / x^n dx (verified against the "
            "closed form to 1e-6: n=6 -> 4.800, n=8 -> 0.686, n=10 -> 0.229 for l=2), which is "
            "exactly zero with no deformation (the GR baseline, v2.235) and scales as eps "
            "(verified: doubling/quadrupling eps doubles/quadruples the response). The sensitivity "
            "DECREASES with deformation localization (larger n -> smaller overlap with the x^l tidal "
            "field). So a measured nonzero tidal Love number is the new-physics signal, and this "
            "overlap integral is the transfer function mapping a near-horizon deformation to the "
            "observable -- the tidal-sector analog of the v2.231 photon-sphere-deviation null test."
        ),
        "honest_scope": (
            "First-order (linear response), static, electric-type (even-parity), Schwarzschild "
            "baseline. The reported quantity is the response OVERLAP INTEGRAL (and a proxy B/A with a "
            "representative Wronskian W0=24); the absolute Love-number value folds in the Love-number "
            "convention normalization (the M^{2l+1} factors and the exact Wronskian) -- the robust, "
            "verified physics is that the GR-zero is lifted LINEARLY by any convergent (localized) "
            "deformation, with the P_l^2-overlap as the transfer function. The deformation must fall "
            "faster than x^{-(2l+1)} for a convergent response (near-horizon new physics); a "
            "non-localized tidal-scale deformation needs the full matched calculation. The specific "
            "deformation profile is illustrative, not a derived QG metric. Parity-odd g_R4_c3 stays "
            "dark (v2.209)."
        ),
        "references": [
            "Binnington & Poisson, PRD 80 (2009) 084018; Damour & Nagar, PRD 80 (2009) 084035",
            "Cardoso, Franzin, Maselli, Pani, Raposo (2017) -- Love numbers of exotic compact objects",
            "this repo: v2.235 (BH Love number = 0), v2.231 (photon-sphere deviation null test)",
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
    for r in res["l2_sensitivity"]:
        print(f"  l=2 n={r['n']:2d}: overlap I = {r['overlap_integral']:.5f} "
              f"(closed form {r['closed_form']:.5f}, match {r['match']})")
    print(f"GR baseline (eps=0) = {res['gr_baseline_zero']}; linear in eps = {res['linear_in_eps']}")
    print("a localized deformation lifts the GR-zero Love number linearly -> new-physics signal")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
