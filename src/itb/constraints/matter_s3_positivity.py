"""Matter-sector s^3 forward-dispersion positivity.

The matter-side partner of the forward-limit graviton positivity. For 2->2
matter scattering the forward amplitude has a low-energy expansion
  A(s,0) = ... + g_4 s^2 + g_6 s^3 + g_8 s^4 + ...
whose coefficients are dispersive moments of a positive spectral density. The
Hankel matrix [[g_4, g_6],[g_6, g_8]] is positive-semidefinite (giving
g_4*g_8 >= g_6^2, already encoded as the dispersion tower). The remaining,
independent statement from the s^3 moment is that the dimension-6 (next-order)
coefficient is cutoff-suppressed relative to the dimension-4 (leading) one:
the same positive integral is dominated by its leading-energy behaviour, so

    g_4  >=  c_m * g_6              (c_m an O(1) cutoff ratio, ~1)

i.e. the leading matter coupling dominates the next-order one. This is the
matter analogue of graviton_forward_positivity (g_R2 >= c*g_R3) and is
independent of the existing matter bounds, which either bound g_6 from BELOW
(scalar convexity, g_6 >= g_4^2) or relate the Hankel determinant (dispersion
tower, g_6^2 <= g_4*g_8).

Honest note: at the representative framework values all candidates satisfy this
comfortably (g_4/g_6 ratios 1.25-1.38), so it is expected to be a non-binding
("informative null") matter-sector constraint at canonical c_m -- consistent
with the v1.20 finding that Class-A matter constraints do little local pruning.
It starts to bind only for c_m above ~1.25.

References:
  Caron-Huot, Van Duong. "Extremal Effective Field Theories." JHEP 05 (2021) 280.
  Arkani-Hamed, Huang, Huang. "The EFT-Hedron." JHEP 05 (2021) 259.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class MatterS3Positivity(Constraint):
    """Forward s^3 moment: leading matter coupling dominates next-order.

        g_4 - c_m * g_6 >= 0
    """

    name = "matter_s3_positivity"
    citation = "Caron-Huot-Van Duong 2021 / Arkani-Hamed-Huang-Huang 2021 (dispersive moments)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, c_m: float = 1.0):
        self.c_m = float(c_m)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        margin = g4 - self.c_m * g6
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_4 >= {self.c_m}*g_6 (matter s^3 forward moment)",
                "g_4": g4, "g_6": g6, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6"):
            out.setdefault(k, 0.0)
        out["g_4"] = 1.0
        out["g_6"] = -self.c_m
        return out
