"""Baseline: pure general relativity with no higher-curvature corrections.
All higher-order Wilson coefficients are zero (free theory limit).
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class PureGR(Framework):
    name = "pure_gr"
    citation = "Einstein 1915, free-theory limit"

    def encode(self) -> Theory:
        return Theory(
            coefficients={"g_4": 0.0, "g_6": 0.0},
            name=self.name,
            source=self.citation,
        )
