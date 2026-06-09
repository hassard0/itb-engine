"""The sub-mm gravity bound: the engine's FIRST data-sourced constraint (v1.77).

Every other constraint in the stack is a theoretical axiom (positivity, causality,
holographic entropy, swampland). THIS one comes from an experiment: the Eot-Wash /
Washington torsion-balance tests of the gravitational inverse-square law.

Physics (v1.76). The R^2 operator is an f(R) theory; its scalaron mediates a Yukawa
fifth force of strength alpha = 1/3 (the unscreened metric-f(R) value, beta=1/sqrt6
=> alpha=2 beta^2 = 1/3) at Compton wavelength
        lambda(g_R2) = (hbar c / E_Lambda) * sqrt(6 g_R2)
with E_Lambda the dark-energy cutoff (2.4 meV). The 95% CL Eot-Wash exclusion
(Lee et al PRL 124,101101 2020; Kapner et al PRL 98,021101 2007) requires the
predicted alpha to sit BELOW the experimental curve at that lambda. Since alpha=1/3
is fixed, this is the single-coefficient bound

        lambda(g_R2) <= lambda_max  <=>  g_R2 <= g_R2_max,

where lambda_max is where the exclusion curve crosses |alpha|=1/3 (~50 um), giving
g_R2_max ~ 0.063.

SCREENING. The bound assumes the scalaron is UNSCREENED and couples to the Standard
Model. Chameleon (Khoury-Weltman), Vainshtein/derivative screening, or a
dark-sector-only / disformal coupling all evade torsion balances. Those scenarios
are encoded by `screened=True`, which makes the constraint vacuous. The default
`screened=False` is the minimal, most-constraining (and most-falsifiable) case.

This is a DATA constraint with the experiment's reading uncertainty (the curve
points are order-of-magnitude readings of the published figure); the qualitative
content -- a dark-energy-scale unscreened scalaron is excluded, forcing g_R2 small
-- is robust to that uncertainty (v1.76 missed the bound by ~an order of magnitude).
"""

import numpy as np

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory

HBARC_eV_m = 1.973e-7
E_LAMBDA_DE = 2.4e-3
SCALAR_AMP = 1.0 / 3.0          # unscreened f(R) scalaron coupling alpha

# Eot-Wash 95% CL exclusion: (lambda_um, |alpha| excluded above). Read from the
# published curve (Lee et al 2020; Kapner et al 2007). See docs/results v1.76.
_EXCL_L = np.array([20.0, 30.0, 38.6, 50.0, 56.0, 60.0, 70.0, 80.0, 100.0, 150.0, 200.0])
_EXCL_A = np.array([25.0, 3.0, 1.0, 0.35, 0.18, 0.15, 0.08, 0.045, 0.02, 0.006, 0.003])


def _alpha_excluded_at(lam_um: float) -> float:
    return float(np.exp(np.interp(np.log(lam_um), np.log(_EXCL_L), np.log(_EXCL_A))))


def _lambda_um(g_R2: float, E_Lambda_eV: float) -> float:
    return (HBARC_eV_m / E_Lambda_eV) * np.sqrt(6.0 * max(g_R2, 0.0)) * 1e6


def _g_R2_for_lambda(lam_um: float, E_Lambda_eV: float) -> float:
    s = lam_um / ((HBARC_eV_m / E_Lambda_eV) * 1e6)      # = sqrt(6 g_R2)
    return (s * s) / 6.0


class SubmmGravityYukawaBound(Constraint):
    """g_R2 <= g_R2_max from the Eot-Wash sub-mm fifth-force exclusion (unscreened
    f(R) scalaron). Vacuous if `screened=True`."""

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, screened: bool = False, scalar_amp: float = SCALAR_AMP,
                 E_Lambda_eV: float = E_LAMBDA_DE):
        self.screened = bool(screened)
        self.scalar_amp = float(scalar_amp)
        self.E_Lambda = float(E_Lambda_eV)
        self.name = "submm_gravity_yukawa_bound"
        self.citation = ("Eot-Wash: Lee et al PRL 124,101101 (2020); "
                         "Kapner et al PRL 98,021101 (2007) [DATA]")
        # lambda where the exclusion curve crosses the predicted alpha
        grid = np.linspace(20.0, 200.0, 6000)
        bound = np.array([_alpha_excluded_at(l) for l in grid])
        below = grid[bound >= self.scalar_amp]     # excluded region is lambda above
        self.lambda_max_um = float(below.max()) if below.size else 200.0
        self.g_R2_max = _g_R2_for_lambda(self.lambda_max_um, self.E_Lambda)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        if self.screened:
            return ConstraintResult(
                self.name, True, 1.0, 1.0,
                {"bound": "screened (chameleon/Vainshtein/dark) - vacuous",
                 "g_R2": gR2})
        margin = self.g_R2_max - gR2
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, self.gradient(theory)),
            details={"bound": f"g_R2 <= {self.g_R2_max:.4f} "
                              f"(unscreened f(R) scalaron, lambda <= {self.lambda_max_um:.1f} um)",
                     "g_R2": gR2, "lambda_um": _lambda_um(gR2, self.E_Lambda),
                     "margin": margin})

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2", 0.0)
        if not self.screened:
            out["g_R2"] = -1.0
        return out
