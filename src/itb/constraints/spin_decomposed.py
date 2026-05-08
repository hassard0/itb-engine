"""Spin-decomposed positivity bounds (Caron-Huot-style, separated by spin).

The full positivity bound on a 2→2 amplitude is a sum over partial waves:

    Im T_l(s) >= 0   for each spin l

For our toy with (g_4, g_6, g_R2), the spin-0 and spin-2 partial-wave
positivity bounds give *different* combinations of coefficients:

    spin-0: g_4 - α * g_R2 >= 0   (matter mode dominates with small graviton mixing)
    spin-2: g_R2 + β * g_6 >= 0   (graviton mode with sub-leading higher-derivative)

Decomposing positivity by spin reveals which physics dominates which
direction in coefficient space — the binding-class diagnostic gets even
sharper (we can see *which spin sector* is doing the work)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class SpinZeroPositivity(Constraint):
    name = "spin_zero_positivity"
    citation = "spin-decomposed Adams positivity, l=0 partial wave"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, alpha: float = 0.5):
        self.alpha = float(alpha)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 - self.alpha * gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"g_4 - {self.alpha}*g_R2 >= 0", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = 1.0
        out["g_R2"] = -self.alpha
        return out


class SpinTwoPositivity(Constraint):
    name = "spin_two_positivity"
    citation = "spin-decomposed graviton positivity, l=2 partial wave"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, beta: float = 0.3):
        self.beta = float(beta)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = gR2 + self.beta * g6
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"g_R2 + {self.beta}*g_6 >= 0", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_6", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_R2"] = 1.0
        out["g_6"] = self.beta
        return out
