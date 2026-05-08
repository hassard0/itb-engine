"""Spin-J=4 partial-wave positivity bound.

For 2->2 graviton-graviton scattering decomposed into partial waves of
total angular momentum J, unitarity + analyticity require Im T_J(s) >= 0
for each J. Earlier modules encoded J=0 (spin_zero_positivity) and J=2
(spin_two_positivity). The J=4 bound is structurally different because
the spin-4 channel in graviton scattering involves a specific combination
of curvature operators with alternating signs:

    g_R3 + γ * g_8 - δ * g_R2 * g_4 >= 0

where γ, δ are O(1) numerical coefficients from the partial-wave
decomposition of graviton-graviton-graviton-graviton amplitudes.

This is class A (amplitude bootstrap). Real published derivations use
explicit Wigner-D-matrix expansions of the helicity amplitudes; the
representative form here captures the qualitative coupling structure.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin. "Sharp boundaries for the
    swampland." JHEP 07 (2021) 110.
  Bellazzini, de Rham, Pajer, Riva, Tolley. "Higher-spin gravitational
    positivity bounds." (2024).
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class SpinFourPositivity(Constraint):
    name = "spin_four_positivity"
    citation = "Caron-Huot et al 2021; Bellazzini et al 2024 — J=4 partial wave"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, gamma: float = 0.3, delta: float = 0.5):
        self.gamma = float(gamma)
        self.delta = float(delta)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        margin = gR3 + self.gamma * g8 - self.delta * gR2 * g4
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R3 + {self.gamma}*g_8 - {self.delta}*g_R2*g_4 >= 0",
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_8", "g_R2", "g_R3"):
            out.setdefault(k, 0.0)
        out["g_R3"] = 1.0
        out["g_8"] = self.gamma
        out["g_R2"] = -self.delta * g4
        out["g_4"] = -self.delta * gR2
        return out
