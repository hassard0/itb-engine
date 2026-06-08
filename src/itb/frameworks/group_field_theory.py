"""Group Field Theory framework encoder.

Group field theory (GFT) is a second-quantized formulation of loop quantum
gravity / spin foams: quantum fields on a group manifold whose Feynman expansion
generates spin-foam amplitudes, and whose condensate states yield effective
cosmologies. Being built from the same spin-foam vertex structure as LQG, it
inherits LQG's qualitative signature — comparable-to-large cubic curvature
coupling (vertex amplification) and parity violation from the Immirzi parameter —
but the condensate/mean-field dynamics can shift the values somewhat from the
canonical-LQG point.

Representative signature: LQG-like — sizeable g_R2 and g_R3 (cubic ~ leading),
parity-violating. Expected to FAIL the same forward-positivity / cubic-graviton
constraints as LQG (g_R3 ~ g_R2), i.e. to be robustly disfavoured, testing
whether the engine's anti-LQG verdict extends to the broader spin-foam family.
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class GroupFieldTheory(Framework):
    name = "group_field_theory"
    citation = "Oriti et al GFT / spin-foam condensates; toy representative values"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.58, "g_6": 0.43, "g_8": 0.40,
                "g_R2": 0.28, "g_R3": 0.28,                # cubic ~ leading (spin-foam vertex)
                "g_R2_parity": 0.07, "g_R3_parity": 0.04,   # Immirzi parity
            },
            name=self.name, source=self.citation,
        )
