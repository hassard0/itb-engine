"""Penrose-Diosi gravity-induced wavefunction collapse framework.

Penrose (1996) and Diosi (1989) independently proposed that gravity
*modifies* quantum mechanics itself: a quantum superposition of mass
distributions decays into one classical outcome on a timescale
τ ~ ℏ / E_grav, where E_grav is the gravitational self-energy difference
between the superposed configurations.

This is qualitatively different from string theory, asymptotic safety,
LQG, or CDT — those treat gravity as something to be quantized; Penrose-
Diosi treats gravity as something that DE-quantizes matter.

In effective Wilson-coefficient terms, the Penrose-Diosi prediction is:
- Matter coefficients (g_4, g_6, g_8) very small but non-zero (matter is
  near-free with a tiny GR-induced collapse term)
- Graviton coefficients (g_R2, g_R3) very small (gravity remains
  classical-like at the EFT level)
- Specific signature: the *time-dependence* of the EFT, but our static
  basis can't capture that directly.

For our basis, the closest representative encoding: small positive
coefficients consistent with a near-classical-gravity, near-free-matter
EFT.

References:
  Penrose. "On gravity's role in quantum state reduction." Gen. Rel.
    Grav. 28 (1996) 581.
  Diosi. "Models for universal reduction of macroscopic quantum
    fluctuations." Phys. Rev. A 40 (1989) 1165.
  Bouwmeester et al — recent macroscopic-superposition experimental
    program targeting Penrose-Diosi predictions."""

from itb.frameworks.base import Framework
from itb.theory import Theory


class PenroseDiosi(Framework):
    name = "penrose_diosi"
    citation = "Penrose 1996, Diosi 1989; Bouwmeester collapse experiments"

    def encode(self) -> Theory:
        # Very small but non-zero — captures the near-classical-gravity,
        # near-free-matter character of the Penrose-Diosi regime.
        # Parity-conserving (no Pontryagin coupling).
        return Theory(
            coefficients={
                "g_4": 0.05, "g_6": 0.03, "g_8": 0.02,
                "g_R2": 0.02, "g_R3": 0.01,
                "g_R2_parity": 0.0, "g_R3_parity": 0.0,
            },
            name=self.name,
            source=self.citation,
        )
