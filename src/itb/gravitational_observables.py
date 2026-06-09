"""Gravitational observables for the decisive-experiment program (v1.42).

First-class `Observable`s (predict + jacobian) for the three experiments the
engine ties together (docs/results 2026-06-08 v1.39-41), so the Fisher-metric
and first-disagreement machinery can rank them natively against the amplitude
observables:

  - YukawaForceDeviation:   short-range gravity. Fractional deviation from Newton
        delta(r) = -(1/3) exp(-r/lambda_Y),  lambda_Y = hbar c / m0,
        m0 = E_Lambda / sqrt(6 g_R2)  (Stelle R^2 scalar). Depends on g_R2.
  - GravitationalBirefringence: parity sector. Frequency-dependent polarization
        signal ~ g_R2_parity + (omega/omega0) * g_R3_parity. Depends on the parity coeffs.
  - GIEPhaseCorrection: the fractional reduction of the gravitationally-induced
        entangling phase from the same Yukawa (Dr. M.: scalar enters with -sign).

These encode the physics of docs/results v1.39-41; toy normalization, real
structure.
"""

import numpy as np

from itb.observables import Observable
from itb.theory import Theory

HBARC_eV_m = 1.973e-7
E_LAMBDA_DARK_ENERGY = 2.4e-3   # eV; dark-energy / sub-mm scale (v1.40)
SCALAR_AMP = 1.0 / 3.0


class YukawaForceDeviation(Observable):
    """Fractional deviation from Newton vs separation, from the R^2 scalar."""

    name = "yukawa_force_deviation"

    def __init__(self, separations_m, E_Lambda_eV: float = E_LAMBDA_DARK_ENERGY):
        self.r = np.asarray(separations_m, dtype=float)
        self.E_Lambda = float(E_Lambda_eV)

    def _lambda_Y(self, g_R2):
        m0 = self.E_Lambda / np.sqrt(6.0 * max(g_R2, 1e-12))
        return HBARC_eV_m / m0

    def predict(self, theory: Theory) -> np.ndarray:
        g = theory.coefficients.get("g_R2", 0.0)
        lam = self._lambda_Y(g)
        return -SCALAR_AMP * np.exp(-self.r / lam)

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        g = theory.coefficients.get("g_R2", 0.0)
        lam = self._lambda_Y(g)
        base = -SCALAR_AMP * np.exp(-self.r / lam)
        # d(delta)/d(g_R2) = base * (r/lam^2) * d(lam)/d(g_R2); d(lam)/dg = lam/(2 g)
        dlam_dg = lam / (2.0 * max(g, 1e-12))
        ddelta_dg = base * (self.r / lam**2) * dlam_dg
        cols = []
        for p in params:
            cols.append(ddelta_dg if p == "g_R2" else np.zeros_like(self.r))
        return np.stack(cols, axis=1)


class GravitationalBirefringence(Observable):
    """Frequency-dependent GW polarization rotation from the parity sector."""

    name = "gravitational_birefringence"

    def __init__(self, omegas, omega0: float = 1.0):
        self.omega = np.asarray(omegas, dtype=float)
        self.omega0 = float(omega0)

    def predict(self, theory: Theory) -> np.ndarray:
        a = theory.coefficients.get("g_R2_parity", 0.0)
        b = theory.coefficients.get("g_R3_parity", 0.0)
        return a + (self.omega / self.omega0) * b

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        cols = []
        for p in params:
            if p == "g_R2_parity":
                cols.append(np.ones_like(self.omega))
            elif p == "g_R3_parity":
                cols.append(self.omega / self.omega0)
            else:
                cols.append(np.zeros_like(self.omega))
        return np.stack(cols, axis=1)


class BlackHoleEntropyShift(Observable):
    """Leading higher-derivative correction to the (near-)extremal black-hole
    entropy at fixed mass M and charge Q, Delta S_ext, in units of the leading Wald
    correction (v1.82).

    Cheung-Liu-Remmen (2018) / Reall-Santos (2018): the sign of Delta S_ext is fixed
    by the same positivity structure as the Weak Gravity Conjecture, and

        Delta S_ext > 0  <=>  WGC  (the extremality bound shifts so q_ext/m_ext > 1,
                                    i.e. extremal black holes can decay).

    KEY (Dr. M.-confirmed): in 4d the Gauss-Bonnet / Euler invariant is TOPOLOGICAL,
    so it does NOT shift the Wald entropy. Thus g_R2 (the Euler coupling) drops out;
    the shift is driven by the Weyl^2 coupling g_C and the matter sector g_4:

        Delta S_ext = A * g_C + B * g_4 ,   A, B > 0 (positive geometric factors).

    Toy normalization A=1 (Weyl^2, dominant for the gravitational sector), B=0.5
    (matter). The robust content is the SIGN (positive for any positivity-satisfying,
    hence WGC-consistent, theory) and the ORDERING by g_C; the precise factors are
    UV-dependent (Dr. M.). g_C defaults to g_R2 (the holographic a=c portrait) when a
    framework carries no explicit Weyl^2 coupling.
    """

    name = "bh_entropy_shift"

    def __init__(self, A: float = 1.0, B: float = 0.5):
        self.A = float(A)
        self.B = float(B)

    def predict(self, theory: Theory) -> np.ndarray:
        gC = theory.coefficients.get("g_C", theory.coefficients.get("g_R2", 0.0))
        g4 = theory.coefficients.get("g_4", 0.0)
        return np.array([self.A * gC + self.B * g4])

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        cols = []
        for p in params:
            if p == "g_C":
                cols.append(np.array([self.A]))
            elif p == "g_4":
                cols.append(np.array([self.B]))
            else:                       # g_R2 (Euler) is topological in 4d -> 0
                cols.append(np.array([0.0]))
        return np.stack(cols, axis=1)


class HolographicEtaOverS(Observable):
    """Shear viscosity / entropy density of a putative AdS/CFT dual, in KSS units.

    In Gauss-Bonnet / R^2 higher-derivative gravity the AdS5/CFT4 dual plasma has
    (Brigante-Liu-Myers-Shenker-Yaida; Dr. M.-confirmed standard form)
        eta/s = (1/4pi) (1 - 8 lambda_GB),     lambda_GB = lam_map * g_R2,
    so a positive curvature coupling LOWERS eta/s below the KSS bound 1/4pi. We
    report eta/s in units of 1/4pi (= 1 - 8*lam_map*g_R2): values < 1 mean KSS is
    violated by the dual. Causality (Brigante et al lambda_GB <= 9/100) caps the
    violation at eta/s >= (1 - 0.72) = 0.28 KSS-units.

    IMPORTANT (Dr. M.): the toy g_R2 (~0.2-0.4) CANNOT be lambda_GB directly — that
    would give eta/s < 0 (unphysical) and violate causality. lam_map ~ 0.22 maps
    the toy g_R2 to lambda_GB so the largest framework g_R2 (~0.4) sits just under
    the causality bound. This mapping is order-of-magnitude; the *ordering* by g_R2
    is the robust content.
    """

    name = "holographic_eta_over_s"

    def __init__(self, lam_map: float = 0.22):
        self.lam_map = float(lam_map)

    def predict(self, theory: Theory) -> np.ndarray:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        return np.array([1.0 - 8.0 * self.lam_map * gR2])   # eta/s in units of 1/4pi

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        cols = [np.array([-8.0 * self.lam_map]) if p == "g_R2" else np.array([0.0])
                for p in params]
        return np.stack(cols, axis=1)


class GIEPhaseCorrection(Observable):
    """Fractional change of the GIE entangling phase from the R^2 Yukawa at the
    superposition scale r (single kinematic point). Negative: the scalar reduces
    the phase (Dr. M.)."""

    name = "gie_phase_correction"

    def __init__(self, r_m: float, E_Lambda_eV: float = E_LAMBDA_DARK_ENERGY):
        self.r = float(r_m)
        self._yuk = YukawaForceDeviation([r_m], E_Lambda_eV)

    def predict(self, theory: Theory) -> np.ndarray:
        return self._yuk.predict(theory)

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        return self._yuk.jacobian(theory, params)
