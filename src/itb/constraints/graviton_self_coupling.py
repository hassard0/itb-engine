"""Graviton self-coupling bounds — from cubic curvature operators.

The Wilson coefficient g_R3 of the leading cube-of-Riemann operator
(Riemann_μνρσ Riemann^ρσ_αβ Riemann^αβ_μν, or the equivalent in the
Lovelock basis) controls graviton-graviton-graviton scattering at one-loop
in the gravitational EFT.

The Caron-Huot 2024 program produces two structurally distinct bounds:

1. **Positivity** (class A): g_R3 >= 0 from twice-subtracted dispersion of
   graviton-graviton 2->2 scattering with cubic vertex insertion.

2. **Cross-sector cubic bound** (class A): the coefficient of cubic
   gravitational interactions cannot exceed a specific power of matter
   couplings. In simplified form:

       g_R3 <= κ * g_4^2

   This says cubic graviton self-interaction is parametrically bounded by
   (squared) matter self-interaction. UV completions that predict large
   cubic graviton coupling without correspondingly large matter coupling
   are inconsistent.

Reference:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin. "Sharp boundaries for the
  swampland." JHEP 07 (2021) 110.
  Caron-Huot, de Rham, Tolley, Zhou. "Positivity bounds on bouncing
  cosmologies and their gauge fields." (2024).
  de Rham, Tolley. "TT bar deformations and gravitational positivity bounds."
  (2024)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CubicCurvaturePositivity(Constraint):
    """g_R3 >= 0 from graviton-graviton dispersion."""

    name = "cubic_curvature_positivity"
    citation = "Caron-Huot et al 2021, 2024"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR3 = theory.coefficients.get("g_R3", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=gR3 >= 0,
            margin=gR3,
            signed_distance_margin=self._signed_distance(gR3, grad),
            details={"bound": "g_R3 >= 0", "value": gR3},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R3", 0.0)
        out["g_R3"] = 1.0
        return out


class CubicGravitonMatterBound(Constraint):
    """Cubic graviton self-coupling bounded by squared matter coupling:

        g_R3 <= κ * g_4^2

    This is a class-A amplitude-bootstrap constraint linking graviton
    self-interactions to matter content."""

    name = "cubic_graviton_matter_bound"
    citation = "Caron-Huot, de Rham, Tolley, Zhou (2024) — gravitational positivity"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 1.0):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        margin = self.kappa * g4 * g4 - gR3
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R3 <= {self.kappa} * g_4^2",
                "g_4": g4, "g_R3": gR3, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R3"):
            out.setdefault(k, 0.0)
        out["g_4"] = 2.0 * self.kappa * g4
        out["g_R3"] = -1.0
        return out
