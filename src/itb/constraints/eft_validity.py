"""EFT validity bound (class C — gravitational universality / EFT consistency).

A consistent effective field theory has a finite cutoff Λ. Wilson coefficients
of dimension-d operators are at most O(1) when expressed in cutoff units.
For the toy with (g_4, g_6, g_R2) we treat all three as bounded by the same
dimensionless O(1) constant `box`. This is the constraint that closes the
allowed region — without it, the region runs off to infinity (as the
completeness check correctly diagnosed in v0.4).

Conceptually, this is a *universality* constraint: any consistent UV completion
imposes a finite cutoff on the EFT, regardless of whether that completion is
string theory, asymptotic safety, or LQG. So we file it under class C.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class EFTValidityBox(Constraint):
    name = "eft_validity_box"
    citation = "EFT cutoff Λ; Wilson coefficients O(1) in cutoff units"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, box: float = 2.0):
        self.box = float(box)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        # Margin is the *minimum* slack across all box faces.
        margins = []
        for k in ("g_4", "g_6", "g_R2"):
            v = theory.coefficients.get(k, 0.0)
            margins.append(self.box - v)        # upper-face slack
            margins.append(v + self.box)        # lower-face slack
        margin = min(margins) if margins else 0.0
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": f"|g_*| <= {self.box}", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        # The binding face has gradient (-sign(coefficient)) for that direction.
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        binding_key = None
        binding_margin = float("inf")
        binding_sign = 0.0
        for k in ("g_4", "g_6", "g_R2"):
            v = theory.coefficients.get(k, 0.0)
            up = self.box - v
            down = v + self.box
            if up < binding_margin:
                binding_margin = up
                binding_key = k
                binding_sign = -1.0
            if down < binding_margin:
                binding_margin = down
                binding_key = k
                binding_sign = +1.0
        if binding_key is not None:
            out[binding_key] = binding_sign
        return out
