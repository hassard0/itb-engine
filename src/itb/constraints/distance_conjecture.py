"""Swampland Distance Conjecture (Ooguri-Vafa 2007).

In any consistent quantum gravity theory, infinite-distance limits in the
moduli space are accompanied by an exponentially light tower of states.
Operationally, this means the EFT cannot have arbitrarily large *aspect
ratios* between its Wilson coefficients — the largest coefficient cannot
exceed the smallest non-zero one by more than an exponential factor in
some scale.

For our static toy basis, we encode a representative form: the ratio of
the largest non-zero Wilson coefficient to the smallest non-zero one must
be bounded by a fixed factor R_max:

    max(|g_*|) / min(|g_*|, nonzero) <= R_max

with R_max = 20 representing a 'reasonable hierarchy' (one decade plus).
This is much looser than the literal exponential of moduli distance, but
captures the qualitative content: pathologically anisotropic theories
(some coefficients large, others tiny) violate the conjecture.

For our toy frameworks, the largest aspect ratios are:
  - String tree EFT: max=0.5, min(nonzero)=0.15  → ratio ≈ 3.3 ✓
  - LQG-induced:     max=0.6, min(nonzero)=0.04  → ratio ≈ 15  ✓ (close)
  - CDT:             max=0.55, min(nonzero)=0.15 → ratio ≈ 3.7 ✓

Pure GR has all zeros → constraint vacuous, trivially satisfied.

References:
  Ooguri, Vafa. "On the geometry of the string landscape and the swampland."
    Nucl. Phys. B 766 (2007) 21.
  Palti. "The Swampland: Introduction and Review." Fortsch. Phys. 67 (2019).
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class DistanceConjecture(Constraint):
    name = "swampland_distance_conjecture"
    citation = "Ooguri-Vafa 2007 swampland distance conjecture; Palti 2019 review"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, R_max: float = 20.0, min_threshold: float = 1e-6):
        self.R_max = float(R_max)
        self.min_threshold = float(min_threshold)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        coefficients = theory.coefficients
        nonzero_abs = [abs(v) for v in coefficients.values()
                       if abs(v) > self.min_threshold]
        if len(nonzero_abs) <= 1:
            # Trivially satisfied — no aspect ratio defined.
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=True,
                margin=self.R_max,
                signed_distance_margin=self.R_max,
                details={"trivially_satisfied": "≤1 nonzero coefficient"},
            )
        max_abs = max(nonzero_abs)
        min_abs = min(nonzero_abs)
        ratio = max_abs / min_abs
        margin = self.R_max - ratio
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"max(|g_*|)/min(|g_*|, nonzero) <= {self.R_max}",
                "ratio": ratio,
                "max_coef": max_abs,
                "min_coef": min_abs,
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        # Gradient of margin w.r.t. coefficients depends on which is max/min;
        # treat as small perturbation around current point.
        out = {k: 0.0 for k in theory.coefficients}
        return out
