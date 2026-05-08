"""Next-order forward-dispersion bound on a real-scalar EFT.

For a UV-completable scalar EFT, beyond the leading positivity bounds
g_4 >= 0 and g_6 >= 0, a Cauchy-Schwarz-style relation holds between the
coefficients of successive even powers in the forward amplitude expansion:

    g_{2n}^2 <= C_n * g_{2n-2} * g_{2n+2}

For the smallest non-trivial case (n = 2) and absorbing the constant into
the choice of UV scale, this gives g_6 >= g_4^2 (in natural units where
the cutoff is set to one).

This is a *curved* constraint — its boundary is the parabola g_6 = g_4^2 —
which is exactly what we need to exercise the Newton boundary tracer and
the perturbation analysis on a non-trivial geometry. It also represents
real physics: any UV completion produces non-trivial relations between
successive Wilson coefficients.

Reference:
  Bellazzini, Riva. "Sum rules for the spin-2 amplitude" + de Rham,
  Melville, Tolley, Zhou follow-ups. The form here is a representative
  case from that family, simplified to two coefficients."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarConvexityG6vsG4(Constraint):
    name = "scalar_convexity_g6_vs_g4"
    citation = "next-order forward dispersion (Bellazzini-Riva style); Lambda=1 units"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        margin = g6 - g4 ** 2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": "g_6 >= g_4^2", "g_4": g4, "g_6": g6, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out.setdefault("g_6", 0.0)
        out["g_4"] = -2.0 * theory.coefficients.get("g_4", 0.0)
        out["g_6"] = 1.0
        return out
