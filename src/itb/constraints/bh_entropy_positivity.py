"""Wald-entropy positivity: a thermodynamic restatement of the WGC (v1.82).

Cheung-Liu-Remmen (2018), "Proof of the Weak Gravity Conjecture from Black Hole
Entropy"; Reall-Santos (2018). The leading higher-derivative correction to the
(near-)extremal Reissner-Nordstrom entropy at FIXED mass and charge satisfies

        Delta S_ext > 0   <=>   WGC

(the extremality bound shifts so that q_ext/m_ext > 1 and extremal black holes can
decay). In 4d the Gauss-Bonnet / Euler term is topological (no Wald-entropy shift),
so the shift is driven by the Weyl^2 coupling g_C and the matter sector g_4:

        Delta S_ext = A * g_C + B * g_4 ,   A, B > 0 .

This is a THEORETICAL consistency axiom (not data). For any positivity-satisfying
theory (g_C >= 0 from c-anomaly unitarity / the HM wedge, g_4 >= 0 from forward
positivity) it is automatically satisfied -- so it is an *independent thermodynamic
restatement* of the engine's positivity/WGC content, not expected to newly exclude
survivors. We retain it as an explicit, separately-citable consistency condition
(cf. the a-theorem, v1.70): it would only bite in an enlarged basis where g_C or g_4
could go negative.

Reference: Cheung, Liu, Remmen, JHEP 10 (2018) 004; Reall, Santos, JHEP 04 (2018) 021.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class WaldEntropyPositivity(Constraint):
    """Delta S_ext = A*g_C + B*g_4 >= 0 (CLR/WGC thermodynamic condition)."""

    name = "wald_entropy_positivity"
    citation = "Cheung-Liu-Remmen 2018; Reall-Santos 2018 (Delta S_ext > 0 <=> WGC)"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, A: float = 1.0, B: float = 0.5):
        self.A = float(A)
        self.B = float(B)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gC = theory.coefficients.get("g_C", theory.coefficients.get("g_R2", 0.0))
        g4 = theory.coefficients.get("g_4", 0.0)
        dS = self.A * gC + self.B * g4
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=dS >= 0,
            margin=dS,
            signed_distance_margin=self._signed_distance(dS, grad),
            details={"bound": "Delta S_ext = A*g_C + B*g_4 >= 0 (CLR/WGC)",
                     "delta_S_ext": dS, "g_C": gC, "g_4": g4},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_C", "g_4"):
            out.setdefault(k, 0.0)
        out["g_C"] = self.A
        out["g_4"] = self.B
        return out
