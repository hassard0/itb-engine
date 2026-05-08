"""Generalized 4D gravitational anomaly inflow + 't Hooft anomaly matching.

The v0.8 AnomalyCancellation constraint was a single algebraic equality.
The genuinely tight version (Alvarez-Gaumé–Witten 1984, Bardeen–Zumino,
't Hooft 1980 anomaly matching) is *multiple* coupled conditions:

(a) **Anomaly inflow** (class C universality): the total parity-violating
    content of the EFT — combining the leading and cubic Pontryagin
    couplings — must equal the inflow from the matter-graviton mixing
    sector. In our toy basis:

        g_R2_parity^2 + 2·g_R3_parity^2 ≤ ρ_inflow * g_4 * g_R2

    Combined parity content bounded by matter × graviton coupling.

(b) **'t Hooft anomaly matching** (class C): the ratio of cubic to
    leading parity-violating coefficients is fixed by the IR matter
    content the UV theory matches onto:

        |g_R3_parity / g_R2_parity| ≈ ρ_match * (g_4 + g_6)

    (with tolerance — exact ratios depend on which fermion content the
    UV theory ultimately includes). When g_R2_parity = 0 the constraint
    is trivially satisfied (both sides zero).

For parity-conserving frameworks (Pure GR, String tree-level, AS) all
parity coefficients are zero and both constraints are trivially
satisfied. For parity-violating frameworks (LQG-induced) these become
the tightest constraints in the engine, locking the parity sector to
the matter sector through anomaly considerations.

References:
  Alvarez-Gaumé, Witten. "Gravitational Anomalies." Nucl. Phys. B 234 (1984) 269.
  't Hooft. "Naturalness, chiral symmetry, and spontaneous chiral symmetry
    breaking." NATO ASI series 59 (1980), 135.
  Harlow et al. "TASI Lectures on the Cosmological Constant" (2022) — for
    the explicit gravitational anomaly inflow form."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class GeneralizedAnomalyInflow(Constraint):
    """g_R2_parity^2 + 2 * g_R3_parity^2 <= rho * g_4 * g_R2"""

    name = "generalized_anomaly_inflow"
    citation = "Alvarez-Gaumé–Witten 1984; gravitational anomaly inflow"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, rho: float = 0.06):
        self.rho = float(rho)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        lhs = gR2p * gR2p + 2.0 * gR3p * gR3p
        rhs = self.rho * g4 * gR2
        margin = rhs - lhs
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2_parity^2 + 2*g_R3_parity^2 <= {self.rho} * g_4 * g_R2",
                "inflow_lhs": lhs, "inflow_rhs": rhs, "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_R2", "g_R2_parity", "g_R3_parity"):
            out.setdefault(k, 0.0)
        out["g_4"] = self.rho * gR2
        out["g_R2"] = self.rho * g4
        out["g_R2_parity"] = -2.0 * gR2p
        out["g_R3_parity"] = -4.0 * gR3p
        return out


class tHooftAnomalyMatching(Constraint):
    """|g_R3_parity| <= ρ_match * |g_R2_parity| * (g_4 + g_6)

    't Hooft anomaly matching: the ratio of cubic to leading parity-violating
    couplings is bounded by IR matter content (g_4 + g_6 acts as a proxy for
    the matter sector strength).

    Trivially satisfied when g_R2_parity = 0 (parity-conserving frameworks),
    because then g_R3_parity must also be zero by the same anomaly argument.
    """

    name = "t_hooft_anomaly_matching"
    citation = "'t Hooft 1980, anomaly matching"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, rho_match: float = 0.5, slack: float = 0.02):
        self.rho_match = float(rho_match)
        self.slack = float(slack)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        # Trivial case: parity-conserving theory passes automatically.
        if abs(gR2p) < 1e-9 and abs(gR3p) < 1e-9:
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=True,
                margin=self.slack,
                signed_distance_margin=self._signed_distance(self.slack, grad),
                details={"bound": "trivially satisfied (parity-conserving)"},
            )
        # If g_R2_parity = 0 but g_R3_parity ≠ 0, anomaly matching is violated.
        if abs(gR2p) < 1e-9:
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=False,
                margin=-abs(gR3p),
                signed_distance_margin=self._signed_distance(-abs(gR3p), grad),
                details={
                    "bound": "g_R3_parity must vanish when g_R2_parity = 0",
                    "g_R2_parity": gR2p, "g_R3_parity": gR3p,
                },
            )
        rhs = self.rho_match * abs(gR2p) * (g4 + g6)
        margin = (rhs + self.slack) - abs(gR3p)
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"|g_R3_parity| <= {self.rho_match}*|g_R2_parity|*(g_4+g_6) + {self.slack}",
                "predicted_max_g_R3_parity": rhs + self.slack,
                "actual_g_R3_parity": gR3p,
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        gR2p = theory.coefficients.get("g_R2_parity", 0.0)
        gR3p = theory.coefficients.get("g_R3_parity", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2_parity", "g_R3_parity"):
            out.setdefault(k, 0.0)
        if abs(gR2p) > 1e-9:
            sign_r2 = 1.0 if gR2p >= 0 else -1.0
            sign_r3 = 1.0 if gR3p >= 0 else -1.0
            out["g_4"] = self.rho_match * abs(gR2p)
            out["g_6"] = self.rho_match * abs(gR2p)
            out["g_R2_parity"] = self.rho_match * sign_r2 * (
                theory.coefficients.get("g_4", 0.0)
                + theory.coefficients.get("g_6", 0.0)
            )
            out["g_R3_parity"] = -sign_r3
        return out
