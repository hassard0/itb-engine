"""Emergent / entropic gravity framework encoder (Verlinde).

In Verlinde's entropic-gravity program gravity is not a fundamental interaction
but an emergent, thermodynamic phenomenon: the gravitational force arises from the
tendency of an information-theoretic system to increase entropy, and the
large-scale ("dark gravity") regime produces a MOND-like modification that
substitutes for dark matter. Its physics lives in the INFRARED / large-scale,
emergent regime — not in a UV expansion of a fundamental graviton field.

Scope (v1.65): emergent gravity is flagged `fundamental = False`. The engine's
amplitude-positivity bounds expand the *fundamental graviton* 2->2 amplitude in
higher-derivative Wilson coefficients; emergent gravity has no such fundamental
UV expansion, so a positivity feasibility verdict — pass or fail — is not
meaningful. (It is also non-local in the thermodynamic/holographic sense.)

Representative UV signature: because the modifications are infrared, the UV
higher-derivative coefficients map to near-GR / small values, parity-conserving.
Numerically this lands in the allowed region — but the scope flag makes clear the
engine declines to adjudicate it.
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class EmergentGravity(Framework):
    name = "emergent_gravity"
    fundamental = False     # gravity is not a fundamental UV field here
    local = False           # entropic/holographic origin is non-local
    citation = "Verlinde 2011/2016 (entropic / emergent gravity); toy representative values"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.30, "g_6": 0.20, "g_8": 0.15,   # near-GR UV (modifications are IR)
                "g_R2": 0.10, "g_R3": 0.05,
                "g_R2_parity": 0.0, "g_R3_parity": 0.0,
            },
            name=self.name, source=self.citation,
        )
