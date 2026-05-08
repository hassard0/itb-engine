"""LIGO graviton-mass bound — first real experimental constraint.

LIGO/Virgo observations of binary black hole mergers constrain the graviton
dispersion relation. If gravitons have nonzero mass, gravitational waves
disperse; the lack of observed dispersion in GW170817 and subsequent events
gives:

    m_graviton < 1.27 × 10^-23 eV   (LIGO/Virgo, GW170817 + O3, Will 2018)

In our EFT, a nonzero graviton mass corresponds to a specific combination of
Wilson coefficients of the form `g_R2 + (mass-dependent coupling)`. The
simplification here: a higher-curvature operator with coefficient g_R2
generates an effective graviton mass scaling as `m^2 ~ g_R2 * Λ^2`, so the
LIGO bound translates to:

    g_R2 <= (m_LIGO / Λ)^2 ~ 10^-30   (in Planck units)

For the toy with our O(1)-normalized coefficients and a notional cutoff Λ
several orders of magnitude below Planck, the bound is many orders of
magnitude looser. We encode it parameterically via a `bound` argument so
callers can pick a regime-appropriate value. Default 0.1 is a representative
"the LIGO bound is moderately constraining at this cutoff" choice.

This is the engine's first link between observable cosmological-scale
gravitational physics and Wilson coefficients in the EFT.

References:
  Will, C. M. "Solar system vs. gravitational-wave bounds on the graviton
  mass." Class. Quantum Grav. 35 (2018) 17LT01.
  LIGO/Virgo Collaboration. "Tests of General Relativity with GW170817."
  Phys. Rev. Lett. 123 (2019) 011102."""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory


class LIGOGravitonMassBound(Constraint):
    name = "ligo_graviton_mass_bound"
    citation = "LIGO/Virgo (GW170817 + O3); Will 2018"
    constraint_class = ConstraintClass.B_INFORMATION  # data → information about theory

    def __init__(self, bound: float = 0.1):
        self.bound = float(bound)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        margin = self.bound - gR2
        grad = self.gradient(theory)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, grad),
            details={
                "bound": f"g_R2 <= {self.bound}  (LIGO graviton-mass)",
                "g_R2": gR2,
                "physical_origin": "m_graviton < 1.27e-23 eV → effective coupling bound",
            },
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2", 0.0)
        out["g_R2"] = -1.0
        return out
