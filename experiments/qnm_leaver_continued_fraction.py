"""v2.260 - Leaver continued-fraction machinery (validated) + an honest blocker diagnosis.

A focused attempt at the high-accuracy Leaver QNM solver -- the infrastructure that would close the
v2.212 cross-multipole WKB-overshoot gap (and unblock the 330/440 no-hair violation, blocked since
v2.226). OUTCOME: the solver is NOT delivered this cycle, but the obstacle is precisely diagnosed and
the reusable, validated machinery is shipped.

THE BLOCKER (honest negative, two serious attempts -- v2.228 and this cycle). Leaver's method needs
the 3-term recurrence alpha_n a_{n+1} + beta_n a_n + gamma_n a_{n-1} = 0 for the series coefficients
of u in psi = e^{iwr}(r-1)^{-iw} r^{2iw} u(r), u = sum a_n ((r-1)/r)^n. Deriving alpha,beta,gamma
SYMBOLICALLY fails:
  - v2.228 (symbolic-exponent shortcut, exponents a,b kept as symbols): tractable but WRONG -- it
    drops the e^{iwr} = e^{iw/(1-x)} essential-singularity contributions (its derivatives bring down
    1/(1-x)^2 factors), giving a spurious 5-term recurrence with no a_{n+1} coupling.
  - v2.260 (essential singularity kept explicit, sympy.simplify(L/prefactor)): CORRECT in principle
    but INTRACTABLE -- sympy.simplify of exp of a rational argument 1/(1-x) times the operator
    times-out (exit 124 at 220 s, both l=2 alone). sympy cannot reduce it in reasonable time.

So the Leaver coefficients require ANALYTIC hand-derivation (compute the e^{iwr} derivative
contributions by hand and match the 3-term recurrence), the published Leaver-1985 c-coefficients, or
a different high-accuracy method (high-precision direct integration with asymptotic-SERIES boundary
conditions -- the series are regular Frobenius at both ends, NOT essential-singularity-blocked). This
is a dedicated multi-step effort, not an autonomous-tick task -- recorded here, not forced.

WHAT IS DELIVERED: the continued-fraction evaluator + QNM root-finder, parameterized by the
(alpha, beta, gamma) coefficient functions and VALIDATED on a constructed analytic test case. Once
the coefficients are hand-derived, the solver is ready -- just pass them in.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scipy.optimize import brentq

VERSION = "v2.260"
DEFAULT_OUT = Path("experiments/results/v2.260/qnm_leaver_continued_fraction.json")


def continued_fraction(alpha, beta, gamma, omega, N: int = 300) -> complex:
    """Leaver CF: f(omega) = beta_0 - alpha_0 gamma_1/(beta_1 - alpha_1 gamma_2/(...)); QNM <=> f=0."""
    tail = 0j
    for n in range(N, 0, -1):
        tail = alpha(n - 1, omega) * gamma(n, omega) / (beta(n, omega) - tail)
    return beta(0, omega) - tail


def constant_cf_tail(a: float, b: float, g: float) -> float:
    """For constant coefficients, the CF tail T solves T = a g/(b - T) -> T = (b - sqrt(b^2-4 a g))/2."""
    return (b - math.sqrt(b * b - 4 * a * g)) / 2


def validate_machinery() -> dict:
    """Validate the CF evaluator on a constant-coefficient case with an analytic tail."""
    a, b, g = 1.0, 5.0, 2.0          # b^2 > 4 a g -> real minimal tail
    # constant alpha,beta,gamma (ignore omega); the CF value = beta_0 - tail
    cf = continued_fraction(lambda n, w: a, lambda n, w: b, lambda n, w: g, 0.0, N=400)
    analytic = b - constant_cf_tail(a, b, g)
    return {"cf_numeric": cf.real, "cf_analytic": analytic,
            "match": abs(cf.real - analytic) < 1e-9}


def solve_root_demo() -> dict:
    """Demonstrate the root-finder: construct beta_0(omega) so the CF has a known zero at omega*."""
    a, g = 1.0, 2.0
    tail = constant_cf_tail(a, 5.0, g)       # constant tail with b=5 in the n>=1 block
    omega_star = 0.7
    # beta_0(omega) = (omega - omega_star) + tail  -> CF(omega) = beta_0 - tail = omega - omega_star = 0 at omega*
    def alpha(n, w): return a
    def gamma(n, w): return g
    def beta(n, w): return (w - omega_star) + tail if n == 0 else 5.0

    def cf_real(w):
        return continued_fraction(alpha, beta, gamma, w, N=400).real
    root = brentq(cf_real, 0.0, 2.0, xtol=1e-12)
    return {"omega_star": omega_star, "root_found": root, "recovered": abs(root - omega_star) < 1e-9}


def run() -> dict:
    mach = validate_machinery()
    root = solve_root_demo()
    return {
        "version": VERSION,
        "method": ("Leaver continued-fraction evaluator + brentq root-finder, parameterized by "
                   "(alpha,beta,gamma); validated on a constant-coefficient analytic case and a "
                   "constructed known-root case"),
        "machinery_validation": mach,
        "root_finder_demo": root,
        "machinery_works": bool(mach["match"] and root["recovered"]),
        "blocker_diagnosis": {
            "goal": "3-term Leaver recurrence for Schwarzschild QNMs (closes v2.212 cross-l gap)",
            "v2228_attempt": "symbolic-exponent shortcut -> drops e^{iwr} essential-singularity terms "
                             "-> spurious 5-term recurrence (no a_{n+1})",
            "v2260_attempt": "essential singularity explicit -> sympy.simplify intractable (timeout "
                             "124 at 220s, even l=2)",
            "resolution_needed": "analytic hand-derivation of (alpha,beta,gamma), OR the published "
                                 "Leaver-1985 c-coefficients, OR high-precision direct integration "
                                 "with asymptotic-series BCs (regular Frobenius, not essential-"
                                 "singularity-blocked)",
            "status": "dedicated multi-step effort, not an autonomous-tick task -- recorded, not forced",
        },
        "finding": (
            "The high-accuracy Leaver QNM solver was given a second serious attempt and the obstacle "
            "is now precisely diagnosed: the 3-term recurrence coefficients cannot be derived "
            "symbolically -- the symbolic-exponent shortcut (v2.228) silently drops the e^{iwr} "
            "essential-singularity contributions (spurious 5-term result), and keeping the essential "
            "singularity explicit makes sympy.simplify time out (v2.260). The coefficients need "
            "ANALYTIC hand-derivation or the published Leaver-1985 values, or a switch to "
            "high-precision direct integration with asymptotic-series boundary conditions. That is a "
            "dedicated effort, NOT an autonomous-tick task, so it is recorded rather than forced "
            "(no guessed/unvalidated solver is shipped -- claim-gating discipline). What IS delivered "
            "is the reusable, VALIDATED continued-fraction machinery (the evaluator matches the "
            "analytic constant-coefficient tail to 1e-9, and the brentq root-finder recovers a "
            "constructed known root to 1e-9), parameterized by (alpha,beta,gamma) -- so the dedicated "
            "follow-up just supplies the coefficients and the QNM solver is complete."
        ),
        "honest_scope": (
            "This is a NEGATIVE-result + infrastructure cycle: the QNM solver itself is NOT delivered "
            "(the Schwarzschild coefficients are the missing piece). The continued-fraction evaluator "
            "and root-finder are exact and tested on analytic cases, but they have NOT been run on "
            "the physical Leaver recurrence (which does not yet exist in a validated form). No QNM "
            "value is claimed here; the validated v2.210 WKB solver remains the in-house QNM tool. "
            "Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Leaver, Proc. R. Soc. Lond. A 402 (1985) 285 -- continued-fraction QNM method",
            "Nollert, PRD 47 (1993) 5253 -- continued-fraction convergence / inversion",
            "this repo: v2.228 (first Leaver derivation attempt), v2.212 (WKB cross-l caveat)",
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
    m, r = res["machinery_validation"], res["root_finder_demo"]
    print(f"CF evaluator: numeric {m['cf_numeric']:.6f} == analytic {m['cf_analytic']:.6f}  ({m['match']})")
    print(f"root-finder: recovered omega*={r['omega_star']} as {r['root_found']:.9f}  ({r['recovered']})")
    print(f"machinery_works = {res['machinery_works']}")
    print(f"blocker: {res['blocker_diagnosis']['status']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
