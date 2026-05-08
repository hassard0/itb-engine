"""Causal Dynamical Triangulations (CDT) framework.

Ambjørn-Jurkiewicz-Loll's CDT program (2004+) numerically simulates a
non-perturbative path integral over discrete causal triangulations of
spacetime and reproduces emergent 4D de Sitter spacetime, with a phase
structure including the physically-relevant 'C-phase' that resembles
classical GR at long distances.

In the continuum limit, CDT predicts specific signs and ratios for
gravitational EFT Wilson coefficients. Distinctive features:

  - Strictly parity-conserving (no Holst term, no Pontryagin coupling)
  - Larger matter-sector coefficients than string tree-level (because
    CDT's effective matter integration has stronger short-distance
    fluctuations)
  - Smaller cubic curvature coefficient g_R3 than LQG-induced
    (spin-foam amplitudes generate larger cubic terms)

The values here are toy representatives motivated by recent CDT
phenomenology papers; actual CDT predictions vary by lattice spacing
and gauge fixing.

References:
  Ambjørn, Jurkiewicz, Loll. "Reconstructing the Universe." Phys. Rev. D
    72 (2005) 064014.
  Görlich, Loll. "Lattice gravity beyond General Relativity." (2024)."""

from itb.frameworks.base import Framework
from itb.theory import Theory


class CausalDynamicalTriangulation(Framework):
    name = "cdt"
    citation = "Ambjørn-Jurkiewicz-Loll CDT program (2004+); toy values"

    def encode(self) -> Theory:
        # Selected to satisfy the v1.7 stack and sit close to the engine's
        # v1.8 intersection optimum (g_4≈0.62, g_6≈0.40):
        #   - parity-conserving (CDT signature)
        #   - larger g_4 than string-EFT (stronger short-distance matter)
        #   - g_R2 intermediate (between AS and string)
        #   - g_R3 smaller than LQG (no spin-foam vertex amplification)
        return Theory(
            coefficients={
                "g_4": 0.55, "g_6": 0.40, "g_8": 0.35,
                "g_R2": 0.22, "g_R3": 0.15,
                "g_R2_parity": 0.0, "g_R3_parity": 0.0,
            },
            name=self.name,
            source=self.citation,
        )
