"""GW170817 graviton-speed bound -- and why it is BLIND to higher-derivative
gravity (the engine's third data constraint, v1.84).

GW170817 + GRB170817A bounded the gravitational-wave propagation speed,
|c_GW - c|/c < ~5e-16 (Abbott et al 2017), famously excluding quartic/quintic
Galileons and much of Horndeski dark energy.

CRUCIAL PHYSICS (Dr. M.-confirmed). The Horndeski/Galileon modification GW170817
killed was O(1) and FREQUENCY-INDEPENDENT (a background modification of the tensor
kinetic term, c_T^2 = 1 + O(1)). The engine's HIGHER-DERIVATIVE curvature couplings
(R^2, Weyl^2, R^3) instead modify the graviton DISPERSION,
        omega^2 = c^2 k^2 (1 + a (k/M)^2 + ...),
so the speed deviation is FREQUENCY-SUPPRESSED:
        delta c_GW / c  ~  kappa_c * g_curv * (E_GW / E_cutoff)^2 .
Because LIGO GWs are very low energy (E_GW ~ 4e-13 eV at 100 Hz), even a dark-energy
cutoff (E_cutoff ~ 2.4 meV) gives (E_GW/E_cutoff)^2 ~ 1e-19, so delta c_GW ~ 1e-20 --
orders of magnitude BELOW the 5e-16 bound. GW170817 is a "speed test", blind to the
(k/M)^2 dispersion of an EFT at LIGO frequencies (Dr. M.; the relevant probe is
instead LIGO's intra-messenger DISPERSION test of the waveform phase Psi(f)).

So this constraint is SATISFIED for higher-derivative gravity at any cutoff above
~8 ueV -- in particular at the dark-energy scale. It would bite only for an
ultra-low cutoff E_cutoff < E_GW*sqrt(kappa_c*g/5e-16) ~ a few ueV. We retain it as
an honest data constraint that documents which sector each experiment actually
probes: sub-mm gravity squeezes the dark-energy cutoff (light long-range scalaron),
GW170817 does NOT (high-derivative tensor dispersion).

Reference: Abbott et al (LVC+Fermi/INTEGRAL) ApJL 848 (2017) L13; Baker, Bellini,
Ferreira, Lagos, Noller, Sawicki, PRL 119 (2017) 251301.
"""

import numpy as np

from itb.constraints.base import Constraint, ConstraintClass, ConstraintResult
from itb.theory import Theory

E_GW_LIGO_eV = 4.1e-13          # ~100 Hz graviton energy
E_LAMBDA_DE_eV = 2.4e-3         # dark-energy (low) cutoff
E_HIGH_eV = 1.0e25             # high cutoff (~GUT-ish), for comparison
CGW_BOUND = 5.0e-16            # |delta c_GW|/c, GW170817


def delta_cGW(g_curv: float, E_cutoff_eV: float, kappa_c: float = 1.0,
              E_GW_eV: float = E_GW_LIGO_eV) -> float:
    """Fractional GW-speed deviation from a higher-derivative curvature coupling:
    delta c_GW/c = kappa_c * g_curv * (E_GW/E_cutoff)^2."""
    return kappa_c * g_curv * (E_GW_eV / E_cutoff_eV) ** 2


class GWSpeedBound(Constraint):
    """|delta c_GW|/c <= 5e-16 (GW170817). For higher-derivative gravity this is a
    frequency-suppressed dispersion effect; satisfied at the dark-energy cutoff and
    above (the constraint is effectively blind to this sector at LIGO frequencies)."""

    name = "gw_speed_bound"
    citation = "Abbott et al ApJL 848 (2017) L13; Baker et al PRL 119 (2017) 251301 [DATA]"
    constraint_class = ConstraintClass.C_UNIVERSALITY

    def __init__(self, low_cutoff: bool = True, kappa_c: float = 1.0):
        self.low_cutoff = bool(low_cutoff)
        self.kappa_c = float(kappa_c)
        self.E_cutoff = E_LAMBDA_DE_eV if low_cutoff else E_HIGH_eV

    def _g_curv(self, theory: Theory) -> float:
        # R^2-type dispersion-modifying couplings: g_R2 + g_C (Weyl^2)
        gR2 = theory.coefficients.get("g_R2", 0.0)
        gC = theory.coefficients.get("g_C", gR2)
        return abs(gR2) + abs(gC)

    def evaluate(self, theory: Theory) -> ConstraintResult:
        g = self._g_curv(theory)
        dc = delta_cGW(g, self.E_cutoff, self.kappa_c)
        margin = CGW_BOUND - abs(dc)
        return ConstraintResult(
            constraint_name=self.name,
            satisfied=margin >= 0,
            margin=margin,
            signed_distance_margin=margin,     # already dimensionless
            details={"bound": f"|delta c_GW| <= {CGW_BOUND:.0e} "
                              f"({'low' if self.low_cutoff else 'high'} cutoff "
                              f"E={self.E_cutoff:.2e} eV)",
                     "delta_cGW": dc, "g_curv": g,
                     "ratio_to_bound": abs(dc) / CGW_BOUND},
        )

    def gradient(self, theory: Theory) -> dict[str, float]:
        # tiny but nonzero; the constraint is effectively flat (far from binding)
        out = {k: 0.0 for k in theory.coefficients}
        s = (E_GW_LIGO_eV / self.E_cutoff) ** 2 * self.kappa_c
        for k in ("g_R2", "g_C"):
            out.setdefault(k, 0.0)
            out[k] = -np.sign(theory.coefficients.get(k, 0.0) or 1.0) * s
        return out
