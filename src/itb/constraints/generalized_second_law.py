"""Generalized Second Law (GSL) — Bekenstein 1973.

The total entropy S_total = A/(4G) + S_outside must be non-decreasing in
any physical process. For semiclassical black holes with higher-curvature
corrections, the Wald-entropy formula adds curvature-coefficient terms to
the area law:

    S_Wald = A/(4G) + (g_R2 / 4G) * ∮_horizon (curvature) + ...

GSL applied to evaporating or accreting black holes requires that this
correction be non-negative across all horizon areas. In the EFT, this
translates to a lower bound on g_R2:

    g_R2 >= -c_GSL

with c_GSL an O(1) prefactor (we use 0.5 as a representative value).
This is the engine's first *lower-bound* class-B constraint — most existing
class-B bounds are upper bounds (Bekenstein-tight, BNOSSW MMI). Structurally
distinct: it constrains where g_R2 *cannot go negative*, not where its
positive value is bounded above.

References:
  Bekenstein. "Black holes and entropy." Phys. Rev. D 7 (1973) 2333.
  Wald. "Black hole entropy is the Noether charge." Phys. Rev. D 48 (1993).
  Sarkar, Wall. "Generalized second law at linear order for actions that
    are functions of Lovelock densities." (2015)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class GeneralizedSecondLaw(Constraint):
    name = "generalized_second_law"
    citation = "Bekenstein 1973; Wald 1993; Sarkar-Wall 2015"
    constraint_class = ConstraintClass.B_INFORMATION

    def __init__(self, c_GSL: float = 0.5):
        self.c_GSL = float(c_GSL)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = gR2 + self.c_GSL
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2 >= -{self.c_GSL}  (lower bound from GSL)",
                "g_R2": gR2, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2", 0.0)
        out["g_R2"] = 1.0
        return out
