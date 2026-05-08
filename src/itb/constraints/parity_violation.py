"""Parity-violating gravitational EFT constraints.

In the gravitational EFT, the Pontryagin density ε^μνρσ R_μνρσ × R^αβγδ
couples to scalars to produce parity-violating dynamics. The Wilson
coefficient g_R2_parity controls this coupling; non-zero values produce
gravitational-wave birefringence (different speeds for left- and right-
handed circular polarizations).

Two physically distinct bound structures emerge:

(1) **Parity-violating positivity** (class A): Caron-Huot et al 2024 show
    that the parity-violating analog of the mixed positivity bound has a
    different sign pattern than the parity-conserving form. In our basis:

        |g_R2|^2 + |g_R2_parity|^2 <= κ_pv * g_4 * g_6

    The combined parity content is bounded by matter, not each separately.

(2) **Polarization-decomposed positivity**: separating the graviton into
    left-handed and right-handed polarizations gives:

        (g_R2 + g_R2_parity)^2 <= κ_L * g_4 * g_6   (left-handed)
        (g_R2 - g_R2_parity)^2 <= κ_R * g_4 * g_6   (right-handed)

    These are independent constraints; a theory satisfying one need not
    satisfy the other. Parity-violating theories can have one polarization
    forbidden while the other is allowed.

References:
  Creminelli, Tambalo, Vernizzi, Yingcharoenrat (2018) on parity-violating
    EFT of gravity.
  Caron-Huot, de Rham, Tolley, Zhou (2024) on parity-decomposed positivity.
  Conde, Yin (2025) on swampland constraints from parity violation."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class ParityViolatingPositivity(Constraint):
    """|g_R2|^2 + |g_R2_parity|^2 <= κ * g_4 * g_6"""

    name = "parity_violating_positivity"
    citation = "Caron-Huot, de Rham, Tolley, Zhou 2024 (parity-decomposed)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 1.0):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        margin = self.kappa * g4 * g6 - (gR2 * gR2 + gR2p * gR2p)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2^2 + g_R2_parity^2 <= {self.kappa} * g_4 * g_6",
                "g_R2": gR2, "g_R2_parity": gR2p, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2", "g_R2_parity"):
            out.setdefault(k, 0.0)
        out["g_4"] = self.kappa * g6
        out["g_6"] = self.kappa * g4
        out["g_R2"] = -2.0 * gR2
        out["g_R2_parity"] = -2.0 * gR2p
        return out


class LeftHandedGravitonPositivity(Constraint):
    """(g_R2 + g_R2_parity)^2 <= κ * g_4 * g_6 (left-handed mode)."""

    name = "left_handed_graviton_positivity"
    citation = "Caron-Huot et al 2024 (left-helicity graviton bound)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 1.0):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        b_left = gR2 + gR2p
        margin = self.kappa * g4 * g6 - b_left * b_left
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"(g_R2 + g_R2_parity)^2 <= {self.kappa} * g_4 * g_6",
                "b_left": b_left, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        b_left = gR2 + gR2p
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2", "g_R2_parity"):
            out.setdefault(k, 0.0)
        out["g_4"] = self.kappa * g6
        out["g_6"] = self.kappa * g4
        out["g_R2"] = -2.0 * b_left
        out["g_R2_parity"] = -2.0 * b_left
        return out


class RightHandedGravitonPositivity(Constraint):
    """(g_R2 - g_R2_parity)^2 <= κ * g_4 * g_6 (right-handed mode)."""

    name = "right_handed_graviton_positivity"
    citation = "Caron-Huot et al 2024 (right-helicity graviton bound)"
    constraint_class = ConstraintClass.A_AMPLITUDE

    def __init__(self, kappa: float = 1.0):
        self.kappa = float(kappa)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        b_right = gR2 - gR2p
        margin = self.kappa * g4 * g6 - b_right * b_right
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"(g_R2 - g_R2_parity)^2 <= {self.kappa} * g_4 * g_6",
                "b_right": b_right, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        b_right = gR2 - gR2p
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2", "g_R2_parity"):
            out.setdefault(k, 0.0)
        out["g_4"] = self.kappa * g6
        out["g_6"] = self.kappa * g4
        out["g_R2"] = -2.0 * b_right
        out["g_R2_parity"] = +2.0 * b_right   # opposite sign vs left-handed
        return out


class LIGOBirefringenceBound(Constraint):
    """LIGO/Virgo non-observation of gravitational-wave birefringence
    constrains the parity-violating coefficient directly.

    From Yamada-Tanaka 2020, Wang et al 2021, and ongoing LIGO O4
    analyses, the bound on the dimensionless parity-violation parameter
    is α_PV ≲ 10^-3 — translated to our O(1)-normalized basis with the
    appropriate cutoff scale, this gives roughly |g_R2_parity| ≲ 0.05
    for typical cosmological propagation distances. The bound is loosened
    here to 0.1 for the toy regime."""

    name = "ligo_birefringence_bound"
    citation = "LIGO/Virgo non-observation of GW birefringence (O3 bound)"
    constraint_class = ConstraintClass.B_INFORMATION

    def __init__(self, bound: float = 0.1):
        self.bound = float(bound)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        margin = self.bound - abs(gR2p)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"|g_R2_parity| <= {self.bound}",
                "g_R2_parity": gR2p,
                "physical_origin": "GW circular polarization asymmetry < O(10^-3)",
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2_parity", 0.0)
        # margin = bound - |g_R2_parity|
        out["g_R2_parity"] = -1.0 if gR2p >= 0 else +1.0
        return out
