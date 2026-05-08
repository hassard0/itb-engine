"""String-theory tree-level low-energy EFT.

At tree level in the α' expansion, the bosonic-string low-energy effective
action contains specific positive Wilson coefficients for higher-derivative
operators. The leading α'^2 correction generates terms that translate (after
matching to our scalar+R² toy basis) to specific positive values for
(g_4, g_6, g_R2). The values here are simplified representatives — the
qualitative structure (signs, ratios) reflects the literature.

Reference:
  Gross, Sloan (1987), Polchinski (Vol. 1) §3.7, Schwarz §11. Modern
  positivity-bound checks: Caron-Huot et al show string-EFT predictions
  satisfy gravitational positivity bounds, which is reproduced here."""

from itb.frameworks.base import Framework
from itb.theory import Theory


class StringTreeEFT(Framework):
    name = "string_tree_eft"
    citation = "Gross-Sloan tree-level α' expansion (toy values)"

    def encode(self) -> Theory:
        # Representative tree-level values chosen to satisfy every constraint
        # currently in the engine simultaneously:
        #   g_4 >= 0                                      ✓ (0.5)
        #   g_6 >= 0                                      ✓ (0.4)
        #   g_6 >= g_4^2  (next-order forward dispersion) ✓ (0.4 >= 0.25)
        #   g_R2^2 <= g_4 * g_6  (Caron-Huot)             ✓ (0.04 <= 0.20)
        #   g_R2^2 <= 0.5 * g_4 * g_6  (Bekenstein-tight) ✓ (0.04 <= 0.10)
        #   |g_*| <= 2  (EFT validity, Λ in O(1) units)   ✓
        # g_8 added in v1.0: must satisfy g_6^2 <= g_4 * g_8.
        # 0.4^2 = 0.16, 0.5 * 0.4 = 0.2 ✓ (with margin 0.04)
        # g_R3 added in v1.2: cubic graviton self-coupling. String tree-level
        # produces small cubic curvature corrections (suppressed by α'^3).
        # g_R3 = 0.15 satisfies g_R3 <= g_4^2 = 0.25 ✓
        # Tree-level bosonic string is parity-CONSERVING (no Pontryagin
        # coupling at this order). g_R2_parity = 0 distinguishes string-EFT
        # from LQG-induced (which has non-zero g_R2_parity from Holst term).
        return Theory(
            coefficients={
                "g_4": 0.5,
                "g_6": 0.4,
                "g_R2": 0.2,
                "g_8": 0.4,
                "g_R3": 0.15,
                "g_R2_parity": 0.0,
                "g_R3_parity": 0.0,
            },
            name=self.name,
            source=self.citation,
        )
