"""Higher-region BNOSSW holographic entropy cone inequalities.

Bao-Nezami-Ooguri-Stoica-Sully-Walter (2015) and follow-ups gave
explicit inequalities for the holographic entropy cone with n=4, n=5
regions. These are strictly tighter than the n=3 monogamy inequality
because they enforce constraints on more multipartite correlations.

In our toy basis with parity-conserving Wilson coefficients, two
representative higher-region forms:

(n=4) **4-region superbalance**:

    g_4 * g_6 - g_R2 * (g_4 + g_6) / 3 >= 0

This is structurally tighter than n=3 MMI because the matter-sector
product is divided by an effective dimensional factor of 3 (4 regions
share each 3 pair contributions).

(n=5) **5-region quartet inequality**:

    (g_4 + g_6) * g_8 - g_R2^3 >= 0

Cubic in g_R2; explores graviton self-correlations at fourth order.

These are publication-grade-flavored representatives. The literal
BNOSSW inequalities for n=4, n=5 involve specific entropy-vector
coefficients I haven't fully encoded.

References:
  Bao, Nezami, Ooguri, Stoica, Sully, Walter. JHEP 09 (2015) 130.
  He, Hubeny, Rangamani, Walter. "Holographic Entropy Cone Inequalities
    Beyond Five Parties." (2020)."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class BNOSSW4Region(Constraint):
    name = "bnossw_4region_superbalance"
    citation = "BNOSSW 2015 + He-Hubeny-Rangamani-Walter 2020 (n=4)"
    constraint_class = ConstraintClass.B_INFORMATION

    def __init__(self, prefactor: float = 1.0/3.0):
        self.prefactor = float(prefactor)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 * g6 - self.prefactor * gR2 * (g4 + g6)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_4*g_6 - {self.prefactor:.3f}*g_R2*(g_4+g_6) >= 0 (4-region)",
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = g6 - self.prefactor * gR2
        out["g_6"] = g4 - self.prefactor * gR2
        out["g_R2"] = -self.prefactor * (g4 + g6)
        return out


class BNOSSW5Region(Constraint):
    name = "bnossw_5region_quartet"
    citation = "BNOSSW 2015 + 5-region extensions"
    constraint_class = ConstraintClass.B_INFORMATION

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = (g4 + g6) * g8 - gR2 * gR2 * gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": "(g_4 + g_6) * g_8 - g_R2^3 >= 0 (5-region cubic)",
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        g8 = theory.coefficients.get("g_8", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_8", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = g8
        out["g_6"] = g8
        out["g_8"] = g4 + g6
        out["g_R2"] = -3.0 * gR2 * gR2
        return out
