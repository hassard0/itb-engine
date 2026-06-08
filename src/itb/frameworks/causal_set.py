"""Causal Set theory framework encoder.

Causal set theory takes spacetime to be fundamentally discrete: a locally finite
partial order (the causal structure) plus a volume measure. The continuum
effective action (Benincasa–Dowker) recovers the Einstein–Hilbert term plus
non-local corrections set by the discreteness scale; the corrections are
controlled and do NOT enhance the cubic curvature sector. Causal sets are
spatially parity-symmetric (the order is causal/temporal, not chiral), so the
parity-odd couplings vanish. The framework's most distinctive prediction is a
*fluctuating* cosmological constant, Λ ~ ±1/√V — a cosmological signature rather
than a higher-derivative Wilson coefficient.

Representative signature: near-GR matter sector, moderate g_R2, SMALL cubic
g_R3 (no spin-foam-style vertex enhancement), parity-conserving. Numerically it
lands in the engine's allowed region (high g_R2/g_R3 ratio passes forward
positivity), distinguished observationally by the fluctuating-Λ feature.

IMPORTANT CAVEAT (Dr. M.): causal sets are fundamentally NON-LOCAL, and locality
is an assumption behind the swampland/positivity program. So the engine's
"feasible" verdict for causal sets is not really meaningful — the framework
happens to land in the allowed region of constraints that may not apply to it.
The engine validly tests only local, Lorentz-invariant frameworks (see v1.58).
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class CausalSet(Framework):
    name = "causal_set"
    local = False   # fundamental discreteness => non-local continuum EFT
    citation = "Bombelli-Lee-Meyer-Sorkin 1987; Benincasa-Dowker action; toy representative values"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.45, "g_6": 0.35, "g_8": 0.30,
                "g_R2": 0.20, "g_R3": 0.08,               # small cubic: no vertex enhancement
                "g_R2_parity": 0.0, "g_R3_parity": 0.0,    # spatially parity-symmetric
            },
            name=self.name, source=self.citation,
        )
