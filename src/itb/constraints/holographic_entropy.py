"""Holographic entropy cone constraints (Bao-Nezami-Ooguri-Stoica-Sully-Walter
2015 and predecessors).

The HEC is a polytope in entropy-vector space describing which entanglement-
entropy patterns are achievable by holographic states. The defining
inequalities split into two classes:

(a) GENERAL quantum inequalities — hold for any state in any quantum theory:
    - Subadditivity (SA):           S_A + S_B >= S_AB
    - Strong subadditivity (SSA):   S_AB + S_BC >= S_B + S_ABC
    - Weak monotonicity (WM):       S_AB + S_BC >= S_A + S_C

(b) HOLOGRAPHIC-SPECIFIC inequalities — hold for states with classical
    Ryu-Takayanagi geometric duals:
    - Monogamy of mutual information (MMI):
          S_AB + S_BC + S_AC >= S_A + S_B + S_C + S_ABC

A theory that satisfies (a) is consistent with quantum mechanics. A theory
that ALSO satisfies (b) is consistent with classical holography. The
distinction is informative: a candidate UV completion that fails MMI but
passes SA could still be a valid quantum theory of gravity — it just
isn't a holographic one.

Translating these inequalities to a Wilson-coefficient EFT requires a state
and a region geometry. For the toy basis (g_4, g_6, g_R2, g_8), we use
representative forms that capture the *structure* of each inequality:
positive linear combinations for SA/SSA, and an asymmetric harmonic-mean-
style bound for MMI.

These are not the literal published entropy-cone inequalities — they are
representatives that share the relevant inequality geometry. Encoding the
literal forms requires committing to a specific holographic state, which
is a research-grade modeling choice beyond v1.1's scope.

References:
  Bao, Nezami, Ooguri, Stoica, Sully, Walter. "The Holographic Entropy
  Cone." JHEP 09 (2015) 130.
  Hayden, Headrick, Maloney. "Holographic Mutual Information is Monogamous."
  Phys. Rev. D 87 (2013) 046003."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class HolographicSubadditivity(Constraint):
    """Class B: holds for ALL quantum states (general SA).

    Translation: S_A + S_B - S_AB >= 0. In our toy basis we use the proxy
    'matter contribution dominates graviton-mediated mixing':

        g_4 + g_6 - g_R2 >= 0

    Captures the structural feature of subadditivity: the sum of separate
    contributions exceeds the joint one. Linear and class-B."""

    name = "holographic_subadditivity"
    citation = "general SA inequality (BNOSSW 2015 §2.1, Hayden-Headrick-Maloney 2013)"
    constraint_class = ConstraintClass.B_INFORMATION

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = g4 + g6 - gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={"bound": "g_4 + g_6 - g_R2 >= 0 (SA)", "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        out["g_4"] = 1.0
        out["g_6"] = 1.0
        out["g_R2"] = -1.0
        return out


class BNOSSWMonogamy(Constraint):
    """Class B: holds ONLY for holographic states (MMI).

    Translation: a holographic state cannot have arbitrary tripartite
    correlations. In our toy basis we use the harmonic-mean-style form:

        g_4 * g_6 / (g_4 + g_6) - g_R2 >= 0   when g_4 + g_6 > 0
        margin = -1                            when g_4 + g_6 <= 0

    This is tighter than Bekenstein-tight when g_4 and g_6 are asymmetric,
    capturing the MMI structure (correlations restricted by holographic
    geometry). Non-holographic UV completions can violate this without
    violating SA — that's the whole point of MMI."""

    name = "bnossw_monogamy"
    citation = "Bao-Nezami-Ooguri-Stoica-Sully-Walter 2015 (MMI of holographic states)"
    constraint_class = ConstraintClass.B_INFORMATION

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        denom = g4 + g6
        # Trivially satisfied at the no-correlation point (Pure GR limit).
        if g4 == 0.0 and g6 == 0.0 and gR2 == 0.0:
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=True,
                margin=0.0,
                signed_distance_margin=0.0,
                details={"bound": "MMI: trivially satisfied at origin", "denom": denom},
            )
        # When matter coefficients are zero or negative but g_R2 > 0, MMI is
        # genuinely violated (no holographic state has graviton-mediated
        # correlations without matter).
        if denom <= 0:
            margin = -abs(gR2) if gR2 != 0.0 else 0.0
            grad = self.gradient(theory)
            return ConstraintResult(
                constraint_name=self.name,
                satisfied=margin >= 0,
                margin=margin,
                signed_distance_margin=self._signed_distance(margin, grad),
                details={
                    "bound": "MMI: requires g_4 + g_6 > 0 when g_R2 > 0",
                    "denom": denom, "g_R2": gR2,
                },
            )
        harmonic = (g4 * g6) / denom
        margin = harmonic - gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": "g_4*g_6/(g_4+g_6) - g_R2 >= 0 (MMI proxy)",
                "harmonic": harmonic,
                "g_R2": gR2,
                "margin": margin,
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        out = {k: 0.0 for k in theory.coefficients}
        for k in ("g_4", "g_6", "g_R2"):
            out.setdefault(k, 0.0)
        denom = g4 + g6
        if denom > 0:
            denom_sq = denom * denom
            # d(g4 g6/(g4+g6))/dg4 = g6 (g4+g6) - g4 g6 ) / (g4+g6)^2
            #                     = g6 * g6 / (g4+g6)^2
            out["g_4"] = (g6 * g6) / denom_sq
            out["g_6"] = (g4 * g4) / denom_sq
            out["g_R2"] = -1.0
        return out
