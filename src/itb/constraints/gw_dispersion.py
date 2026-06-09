"""LIGO GW dispersion test -- the proper tensor-sector probe (v1.85).

GW170817's arrival-time SPEED test was blind to the engine's higher-derivative
graviton sector (v1.84): delta v_g/c ~ (E_GW/M)^2 ~ 1e-20 even at a dark-energy
cutoff. The intra-messenger DISPERSION test is different and far sharper.

For omega^2 = k^2 + k^4/M^2 (the alpha=4 case of the LVK modified-dispersion
parametrization E^2 = p^2 + A_alpha p^alpha, A_4 = 1/M^2), the wavenumber is
k ~ omega(1 - (1/2)(omega/M)^2), so the propagation phase over distance D acquires
an anomalous piece (Dr. M.-confirmed; Mirshekari-Yunes-Will 2012; Will 1998):

        delta_Psi  ~  (1/2) * kappa_d * g_curv * E_GW^3 * D / M^2 .

The lever arm vs the speed test is the accumulated phase: delta_Psi / (delta v_g/c)
~ E_GW * D ~ 1e20 (omega D in natural units, for 100 Hz over ~1 Gpc). THAT ~1e20
enhancement is what lets the dispersion test reach the MEV scale for alpha=4
(LVK GWTC-3 sensitivity to M ~ 1e-3..1e-6 eV; Abbott et al PRL 127, 161102, 2021)
where the speed test is stuck at ueV. So a dark-energy-scale (~meV) higher-
derivative graviton sector sits AT THE FRONTIER of current LIGO dispersion tests
(delta_Psi ~ 0.3 rad), and improved sensitivity (~0.1 rad, stacked events) would
EXCLUDE it -- the FIRST tensor-sector probe that reaches the low cutoff.

HONEST CAVEATS (Dr. M.):
  - GHOST: achieving alpha=4 dispersion via the Weyl^2 (g_C) term typically brings a
    massive spin-2 ghost; the A_alpha parametrization is bottom-up and does not
    guarantee a ghost-free UV completion. (The engine's positivity bounds partially
    address healthiness, but the mapping is phenomenological.)
  - DEGENERACY of delta_Psi(f) with chirp mass / spins in template matching.
  - MODE MIXING: the LVK bound assumes the standard massless mode dominates.

Reference: Abbott et al (LVK), "Tests of GR with GWTC-3", PRL 127 (2021) 161102;
Mirshekari, Yunes, Will, PRD 85 (2012) 024041; Will, PRD 57 (1998) 2061.
"""

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory

HBARC_eV_m = 1.973e-7
E_GW_LIGO_eV = 4.1e-13          # ~100 Hz
E_LAMBDA_DE_eV = 2.4e-3         # dark-energy (low) cutoff
E_HIGH_eV = 1.0e25             # high cutoff (comparison)
GPC_m = 3.086e25              # 1 Gpc
PSI_SENS_RAD = 1.0           # LVK current phase sensitivity (~1 rad; ~0.1 future)


def delta_psi(g_curv: float, M_eV: float, D_m: float = GPC_m,
              kappa_d: float = 0.5, E_GW_eV: float = E_GW_LIGO_eV) -> float:
    """Accumulated anomalous GW phase (radians) from alpha=4 dispersion:
    delta_Psi = kappa_d * g_curv * E_GW^3 * D / (M^2 * hbar c)."""
    return kappa_d * g_curv * (E_GW_eV ** 3) * D_m / (M_eV ** 2 * HBARC_eV_m)


class GWDispersionBound(Constraint):
    """|delta_Psi| <= Psi_sens (LVK GWTC-3 alpha=4 dispersion). Unlike the speed
    bound, this REACHES the dark-energy cutoff via the ~1e20 cumulative-phase
    enhancement; at the dark-energy scale it sits at the frontier."""

    name = "gw_dispersion_bound"
    citation = "Abbott et al PRL 127 (2021) 161102; Mirshekari-Yunes-Will 2012 [DATA]"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, low_cutoff: bool = True, D_m: float = GPC_m,
                 psi_sens: float = PSI_SENS_RAD):
        self.low_cutoff = bool(low_cutoff)
        self.D = float(D_m)
        self.psi_sens = float(psi_sens)
        self.M = E_LAMBDA_DE_eV if low_cutoff else E_HIGH_eV

    def _g_curv(self, theory: Theory) -> float:
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gC = theory.coefficients.get("g_C", gR2)
        return abs(gR2) + abs(gC)

    def m_min_excluded(self, g_curv: float) -> float:
        """Cutoff M below which delta_Psi exceeds the sensitivity (excluded)."""
        # delta_psi(g, M) = psi_sens  ->  M = sqrt(kappa*g*E^3*D/(psi*hbar c))
        return (0.5 * g_curv * E_GW_LIGO_eV ** 3 * self.D
                / (self.psi_sens * HBARC_eV_m)) ** 0.5

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g = self._g_curv(theory)
        dpsi = delta_psi(g, self.M, self.D)
        margin = self.psi_sens - abs(dpsi)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=margin,
            details={"bound": f"|delta_Psi| <= {self.psi_sens} rad "
                              f"({'low' if self.low_cutoff else 'high'} cutoff "
                              f"M={self.M:.2e} eV, D={self.D:.2e} m)",
                     "delta_Psi_rad": dpsi, "g_curv": g,
                     "m_min_excluded_eV": self.m_min_excluded(g)},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        out = {k: 0.0 for k in theory.coefficients}
        s = -0.5 * (E_GW_LIGO_eV ** 3) * self.D / (self.M ** 2 * HBARC_eV_m)
        for k in ("g_R2", "g_C"):
            out.setdefault(k, 0.0)
            out[k] = s
        return out
