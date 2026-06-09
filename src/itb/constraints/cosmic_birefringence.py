"""Cosmic birefringence: the engine's second DATA constraint (v1.78), on the
PARITY sector -- and the first that PREFERS a NONZERO coefficient.

The sub-mm bound (v1.77) was an exclusion in the matter/scalaron sector. This is a
POSITIVE measurement in the parity/graviton sector: the isotropic rotation of the
CMB linear-polarization plane,
        beta = 0.34 +/- 0.09 deg
(Minami & Komatsu PRL 125,221301 (2020): beta=0.35+/-0.14 deg, Planck PR3;
Eskilt & Komatsu 2022 / Eskilt 2023: ~0.34+/-0.09 deg combining Planck PR4 + WMAP)
-- a ~3.6 sigma hint of a parity-violating (Chern-Simons / Pontryagin) coupling.

A nonzero beta requires a parity-odd coupling. We map the leading toy parity
coefficient g_R2_parity (the gravitational Chern-Simons / Pontryagin coupling) to
beta linearly,
        beta_pred = kappa_beta * g_R2_parity ,
with kappa_beta = 3.4 deg per unit coefficient, chosen so a plausible O(0.1) parity
coupling gives the measured O(0.3 deg). THE NORMALIZATION IS ORDER-OF-MAGNITUDE;
the robust content is that DATA NOW PREFERS A NONZERO, definite-SIGN parity
coupling -- beta = 0 (parity-even) is excluded at ~3.6 sigma, and the measured
beta > 0 selects a HANDEDNESS (g_R2_parity > 0).

Two-sided band (the theory must reproduce the measurement within n_sigma):
        |kappa_beta * g_R2_parity - beta_meas| <= n_sigma * beta_sigma .

HONESTY: cosmic birefringence is a ~3.6 sigma HINT, not a 5 sigma discovery. The
dominant systematic is the miscalibration of detector polarization angles; the
EB-nulling / foreground-EB techniques mitigate but do not eliminate it. mode:
  - "ignore"    : vacuous (do not use the measurement)
  - "hint"      : enforce the band at n_sigma (default; honest ~3.6 sigma status)
  - "confirmed" : same mechanism, label only (a hypothetical 5 sigma future)
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory

BETA_MEAS_DEG = 0.34
BETA_SIGMA_DEG = 0.09
KAPPA_BETA = 3.4          # deg per unit g_R2_parity (O(0.1) coeff -> O(0.3 deg))


class CosmicBirefringenceData(Constraint):
    """|kappa_beta * g_R2_parity - beta_meas| <= n_sigma * beta_sigma.

    A nonzero, positive-handedness parity coupling is PREFERRED; beta=0 is excluded
    at beta_meas/beta_sigma ~ 3.8 sigma."""

    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, mode: str = "hint", n_sigma: float = 2.0,
                 kappa_beta: float = KAPPA_BETA,
                 beta_meas: float = BETA_MEAS_DEG, beta_sigma: float = BETA_SIGMA_DEG):
        self.mode = mode
        self.n_sigma = float(n_sigma)
        self.kappa_beta = float(kappa_beta)
        self.beta_meas = float(beta_meas)
        self.beta_sigma = float(beta_sigma)
        self.name = "cosmic_birefringence_data"
        self.citation = ("Minami & Komatsu PRL 125,221301 (2020); "
                         "Eskilt & Komatsu 2022 (beta=0.34+/-0.09 deg) [DATA]")

    def beta_pred(self, theory: Theory) -> float:
        return self.kappa_beta * theory.coefficients.get("g_R2_parity", 0.0)

    @property
    def excludes_zero_at_sigma(self) -> float:
        return self.beta_meas / self.beta_sigma

    @property
    def preferred_band(self) -> tuple[float, float]:
        half = self.n_sigma * self.beta_sigma
        return ((self.beta_meas - half) / self.kappa_beta,
                (self.beta_meas + half) / self.kappa_beta)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        gp = theory.coefficients.get("g_R2_parity", 0.0)
        if self.mode == "ignore":
            return ConstraintResult(self.name, True, 1.0, 1.0,
                                    {"bound": "ignored (measurement not used)"})
        bpred = self.kappa_beta * gp
        half = self.n_sigma * self.beta_sigma
        margin = half - abs(bpred - self.beta_meas)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=self._signed_distance(margin, self.gradient(theory)),
            details={"bound": f"|{self.kappa_beta}*g_R2_parity - {self.beta_meas}| "
                              f"<= {self.n_sigma}*{self.beta_sigma} deg ({self.mode})",
                     "beta_pred_deg": bpred, "beta_meas_deg": self.beta_meas,
                     "preferred_g_R2_parity_band": self.preferred_band,
                     "margin": margin},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        out.setdefault("g_R2_parity", 0.0)
        if self.mode == "ignore":
            return out
        bpred = self.kappa_beta * theory.coefficients.get("g_R2_parity", 0.0)
        # d(margin)/d g_R2_parity = -sign(bpred - beta_meas) * kappa_beta
        sign = 1.0 if bpred >= self.beta_meas else -1.0
        out["g_R2_parity"] = -sign * self.kappa_beta
        return out
