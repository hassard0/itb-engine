"""Stronger swampland conjectures: Scalar WGC and Repulsive Force Conjecture.

The original Weak Gravity Conjecture (Arkani-Hamed-Motl-Nicolis-Vafa 2007)
states that any U(1) gauge theory coupled to gravity must contain a state
with q/m >= extremal. The robustness map (v1.12) found this form too
loose for our basis — all frameworks pass by 60-70% margin.

Two stronger variants from the swampland literature:

(1) **Scalar WGC** (Palti 2017): when scalar fields are included, the
    gravitational force on a charged state must be weaker than the sum
    of gauge + scalar attractive forces. In our toy basis, this gives:

        g_4 - β * g_6 - g_R2 >= 0    (β > 0)

    A non-trivial bound when β is large enough that the scalar field
    contribution g_6 dominates matter g_4.

(2) **Repulsive Force Conjecture** (Heidenreich-Reece-Rudelius 2019):
    in any consistent QG theory, the long-range force between two
    extremal black holes (or two BPS states) must be non-attractive.
    In our basis, this gives a quadratic bound:

        g_4 * g_6 - g_R2 - γ * g_R2^2 >= 0

    Tighter than original WGC at large g_R2.

Both are published, both are class C universality (any consistent QG
must satisfy them), and both have different functional forms than the
original WGC — meaning their robustness profiles will differ.

References:
  Palti. "The Weak Gravity Conjecture and Scalar Fields." JHEP 08 (2017) 034.
  Heidenreich, Reece, Rudelius. "The Repulsive Force Conjecture." (2019).
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ScalarWGC(Constraint):
    """Palti 2017 scalar weak gravity conjecture.

        g_4 - β * g_6 - g_R2 >= 0
    """

    name = "scalar_wgc"
    citation = "Palti 2017 (scalar weak gravity conjecture)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, beta: float = 0.5):
        self.beta = float(beta)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 - self.beta * g6 - gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_4 - {self.beta}*g_6 - g_R2 >= 0",
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = 1.0
        out["g_6"] = -self.beta
        out["g_R2"] = -1.0
        return out


class RepulsiveForceConjecture(Constraint):
    """Heidenreich-Reece-Rudelius 2019 repulsive force conjecture.

    Two structural forms are available via `form`:

    - ``"matter_product"`` (default, the original v1.x encoding):
          g_4 * g_6 - g_R2 - γ * g_R2^2 >= 0

    - ``"convex_hull"`` (physically-corrected; recommended):
          g_4 - g_R2 - γ * g_R2^2 >= 0

    The RFC/WGC convex-hull condition pits the matter charge-to-mass coupling
    (a single matter coefficient, here g_4) against the gravitational strength
    (graviton coefficient g_R2). The original ``matter_product`` form instead
    multiplies *two* matter-sector coefficients (g_4·g_6) against g_R2. The
    2026-06 prefactor-realism study (docs/results/2026-06-08-*) found that the
    matter_product form excludes EVERY candidate framework for any γ>0 — a
    100% "universal exclusion" that is an artifact of the spurious product
    (the encoded frameworks all have g_4·g_6 ≈ g_R2 by construction). Re-cast
    as ``convex_hull`` the conjecture excludes none of them, isolating the real
    discriminating physics in the complexity-cutoff and cubic-curvature
    constraints. The default is kept as ``matter_product`` for backward
    compatibility; new analyses should pass ``form="convex_hull"``.
    """

    name = "repulsive_force_conjecture"
    citation = "Heidenreich-Reece-Rudelius 2019 (repulsive force conjecture)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, gamma: float = 1.0, form: str = "matter_product"):
        self.gamma = float(gamma)
        if form not in ("matter_product", "convex_hull"):
            raise ValueError(f"unknown RFC form: {form}")
        self.form = form

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if self.form == "convex_hull":
            margin = g4 - gR2 - self.gamma * gR2 * gR2
            bound = f"g_4 - g_R2 - {self.gamma}*g_R2^2 >= 0"
        else:
            margin = g4 * g6 - gR2 - self.gamma * gR2 * gR2
            bound = f"g_4*g_6 - g_R2 - {self.gamma}*g_R2^2 >= 0"
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": bound, "form": self.form, "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        if self.form == "convex_hull":
            out["g_4"] = 1.0
        else:
            out["g_4"] = g6
            out["g_6"] = g4
        out["g_R2"] = -1.0 - 2.0 * self.gamma * gR2
        return out
