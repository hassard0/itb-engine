"""Bekenstein-tight bound (class B — information-theoretic).

The Bekenstein bound asserts that a localized state with energy E and radius R
satisfies S <= 2π R E. Translated to an EFT, this puts an upper bound on the
coefficient of higher-curvature gravitational operators relative to the lower
operators of the matter sector. For our toy with (g_4, g_6, g_R2):

    g_R2^2 <= (1/2) * g_4 * g_6

This is structurally similar to the amplitude-bootstrap mixed positivity
bound (`g_R2^2 <= g_4 * g_6`) but tighter by a factor of two — coming from a
*different* physical principle (entropy bounds vs. dispersion relations).

This is the engine's first class-B constraint. Together with the existing
class-A bounds and the new class-C EFT-validity box, it lights up the
binding-class diagnostic with three physically distinct origins."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class BekensteinTight(Constraint):
    name = "bekenstein_tight"
    citation = "Bekenstein bound applied to gravitational EFT (info-theoretic origin)"
    constraint_class = ConstraintClass.B_INFORMATION

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = 0.5 * g4 * g6 - gR2 * gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": "g_R2^2 <= (1/2) * g_4 * g_6",
                "g_4": g4, "g_6": g6, "g_R2": gR2, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_4", 0.0)
        out.setdefault("g_6", 0.0)
        out.setdefault("g_R2", 0.0)
        out["g_4"] = 0.5 * g6
        out["g_6"] = 0.5 * g4
        out["g_R2"] = -2.0 * gR2
        return out
