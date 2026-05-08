"""CFT-to-flat-space bound (Caron-Huot 2024 program).

Modern conformal-bootstrap results in d=4 give specific upper bounds on
operator dimensions and OPE coefficients in any unitary CFT. Caron-Huot
and collaborators (2024) demonstrated that *taking the flat-space limit*
of bootstrap-allowed CFT amplitudes produces specific bounds on the
gravitational EFT Wilson coefficients.

The structural form of the bound is:

    g_R2 + g_R3 - α * (g_4 + g_6) <= 0

with α an O(1) prefactor encoding the CFT-to-flat-space mapping. This is
class A (amplitude bootstrap) but with a different shape than the
existing Caron-Huot positivity bounds — it sums graviton-sector
coefficients and bounds them by a sum of matter coefficients, rather
than a quadratic mixed-positivity.

References:
  Caron-Huot, Mazac, Rastelli, Simmons-Duffin (2021-2024) for the
  flat-space limit procedure.
  Penedones, Trevisani, Yamazaki (2018) for the original CFT-to-flat-space
  amplitude reconstruction.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class CFTFlatSpaceBound(Constraint):
    name = "cft_flat_space_bound"
    citation = "Caron-Huot et al 2024 (CFT-to-flat-space bootstrap)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, alpha: float = 0.5):
        self.alpha = float(alpha)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR3 = theory.coefficients.get("g_R3", 0.0)
        margin = self.alpha * (g4 + g6) - (gR2 + gR3)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2 + g_R3 <= {self.alpha}*(g_4 + g_6)",
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2", "g_R3"):
            out.setdefault(k, 0.0)
        out["g_4"] = self.alpha
        out["g_6"] = self.alpha
        out["g_R2"] = -1.0
        out["g_R3"] = -1.0
        return out
