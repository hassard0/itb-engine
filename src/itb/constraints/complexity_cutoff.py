"""Complexity-as-cutoff constraint (v0.4 theorize-doc Idea #3).

The conjecture: the universe doesn't have unlimited computational capacity.
Susskind's "complexity = action" duality, Lloyd's bound on physical
computation, and Bekenstein-Brillouin-Margolus-Levitin information bounds
all suggest that the *aggregate* computational content of an EFT — not each
Wilson coefficient individually — is what's constrained.

In our toy basis, we encode this as a weighted L2 norm:

    sum_i (w_i * g_i^2) <= C_max

where w_i is proportional to the dimension of the operator. Higher-dimension
operators (which require more derivative calculations / more loop orders to
evaluate) carry more "complexity" per unit coefficient. EFT-validity bounds
each coefficient individually; complexity-cutoff bounds the aggregate.

This is class C (universality): a complexity bound, if real, applies to any
consistent quantum theory of gravity regardless of UV completion.

Genuinely new feature relative to EFT-validity: a theory with many small
nonzero coefficients can violate the complexity cutoff even when each
coefficient passes EFT validity. UV completions that produce *broad
support* across many higher-curvature operators get penalized.

References (speculative — this constraint family is research-grade conjecture):
  Susskind. "Computational Complexity and Black Hole Horizons." (2014).
  Lloyd. "Ultimate physical limits to computation." Nature 406 (2000).
  Bekenstein. "Universal upper bound on the entropy-to-energy ratio."
    Phys. Rev. D 23 (1981) 287."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


# Operator-dimension weights for the toy basis. Larger weight = higher-dim
# operator = more complexity per unit coefficient.
_DEFAULT_WEIGHTS: dict[str, float] = {
    "g_4": 1.0,        # leading EFT, dimension-4 (effectively)
    "g_6": 2.0,        # next-order, dimension-6
    "g_8": 3.0,        # next-next-order, dimension-8
    "g_R2": 1.0,       # leading curvature, treated dim-4
    "g_R3": 2.0,       # cubic curvature, dim-6
    "g_R2_parity": 1.0,
    "g_R3_parity": 2.0,
}


class ComplexityCutoff(Constraint):
    """Aggregate weighted-L2 norm of Wilson coefficients bounded by C_max."""

    name = "complexity_cutoff"
    citation = "Susskind 2014 / Lloyd 2000 / Bekenstein 1981 (aggregate-computational bound)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(
        self,
        c_max: float = 1.5,
        weights: dict[str, float] | None = None,
    ):
        self.c_max = float(c_max)
        self.weights = dict(weights or _DEFAULT_WEIGHTS)

    def _complexity(self, theory: Theory) -> float:
        c = 0.0
        for k, v in theory.coefficients.items():
            w = self.weights.get(k, 1.0)
            c += w * v * v
        return c

    def evaluate(self, theory: Theory) -> ConstraintResult:
        complexity = self._complexity(theory)
        margin = self.c_max - complexity
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"weighted-L2 complexity <= {self.c_max}",
                "complexity": complexity,
                "weights": dict(self.weights),
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k, v in theory.coefficients.items():
            w = self.weights.get(k, 1.0)
            # margin = c_max - sum w_i v_i^2; d/dv_i = -2 w_i v_i
            out[k] = -2.0 * w * v
        return out
