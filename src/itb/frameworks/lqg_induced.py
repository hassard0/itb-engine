"""LQG-induced effective EFT framework.

Loop quantum gravity produces, in its semiclassical limit, an effective
action with specific higher-curvature corrections from spin-foam amplitudes.
The pattern that distinguishes LQG-induced corrections from string-EFT or
asymptotic-safety predictions is: g_R2 is roughly comparable to the scalar
coefficients (not parametrically small), and a sign structure derived from
holonomy-flux algebra rather than dispersion.

Reference: Rovelli, Vidotto (2014); Engle-Pereira-Rovelli (2007). Toy values."""

from itb.frameworks.base import Framework
from itb.theory import Theory


class LQGInduced(Framework):
    name = "lqg_induced"
    citation = "EPR/spin-foam semiclassical limit (toy values)"

    def encode(self) -> Theory:
        # Selected so it satisfies v0.5 constraints:
        #   g_4 = 0.6, g_6 = 0.45 (>= 0.36 ✓ for convexity)
        #   g_R2 = 0.3 (Bekenstein: 0.09 <= 0.5*0.6*0.45 = 0.135 ✓)
        # Distinctive: g_R2 / sqrt(g_4*g_6) ≈ 0.58, larger than string-EFT (0.45)
        # and asymptotic-safety (0.43). LQG-induced has comparable graviton-
        # to-matter coefficients, qualitatively distinct from the others.
        # g_8 satisfies dispersion tower: g_6^2 = 0.2025 <= 0.6 * 0.4 = 0.24 ✓
        # g_R3: spin-foam amplitudes generate larger cubic-curvature
        # corrections than string-tree-level. g_R3 = 0.30 satisfies
        # g_R3 <= g_4^2 = 0.36 ✓ (with small margin)
        return Theory(
            coefficients={"g_4": 0.6, "g_6": 0.45, "g_R2": 0.3, "g_8": 0.4, "g_R3": 0.30},
            name=self.name,
            source=self.citation,
        )
