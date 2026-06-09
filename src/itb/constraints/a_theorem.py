"""The a-theorem as a Wilson-coefficient sign bound (v1.70).

Komargodski-Schwimmer (2011): in a 4d RG flow the Euler-density (a-)coefficient
of the Weyl anomaly is monotone, a_UV >= a_IR, so the flowed quantity
Delta_a = a_UV - a_IR >= 0.

Dr. M.'s integrate-out derivation (Pluto consult, 2026-06-08): when a heavy field
of mass M is integrated out, the coefficient of the Euler density (Gauss-Bonnet,
the R^2-type invariant in our toy basis = g_R2) acquires a contribution

        g_R2  ~  Delta_a / M^4 ,

so a-theorem monotonicity Delta_a >= 0 implies the SIGN bound

        g_R2 >= 0 .

This is a constraint of *independent physical origin* (RG monotonicity, not
2->2 forward dispersion). Whether it carries *independent information* in this
toy basis is a separate, empirical question — see the v1.70 results note: in the
current 7-coefficient basis the Euler (a) and Weyl^2 (c) anomalies collapse onto
the single coefficient g_R2, and the existing forward-positivity + cubic-positivity
bounds already imply g_R2 >= 0 on the physical (g_R3 >= 0) region. The constraint
is therefore retained as an explicit, separately-citable wall that becomes
load-bearing only once the basis resolves c - a (a Weyl^2 invariant distinct from
the Euler term).

Reference:
  Komargodski, Schwimmer. "On Renormalization Group Flows in Four Dimensions."
  JHEP 12 (2011) 099.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ATheoremMonotonicity(Constraint):
    """g_R2 >= 0 from a-theorem monotonicity (Euler-anomaly coefficient as the
    integrated-out Delta_a >= 0)."""

    name = "a_theorem_monotonicity"
    citation = "Komargodski-Schwimmer 2011 (a-theorem); integrate-out Delta_a >= 0"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=gR2 >= 0,
            margin=gR2,
            signed_distance_margin=self._signed_distance(gR2, grad),
            details={"bound": "g_R2 >= 0 (a-theorem, Delta_a >= 0)", "value": gR2},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2", 0.0)
        out["g_R2"] = 1.0
        return out
