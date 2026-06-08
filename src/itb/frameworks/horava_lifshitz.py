"""Hořava–Lifshitz gravity framework encoder.

Hořava–Lifshitz gravity achieves UV completion by abandoning Lorentz invariance
at high energy: it imposes an anisotropic (Lifshitz) scaling t -> b^z t, x -> b x
with dynamical critical exponent z = 3, which makes the theory power-counting
renormalizable. The defining feature is the presence of LARGE higher-spatial-
derivative terms in the action (up to six spatial derivatives of the metric) —
i.e. large curvature-squared and cubic-curvature couplings. The non-projectable /
detailed-balance versions can include parity-odd terms built from the
gravitational Cotton tensor.

Representative signature (toy, O(1) normalized, like the other frameworks):
large g_R2 and g_R3 (the higher-derivative terms are the whole point), comparable
large matter higher-derivative couplings, and non-zero parity from the Cotton
sector. Expected to FAIL the same constraints LQG does (forward positivity / cubic
graviton bound), since g_R3 ~ g_R2, plus extra tension from the large couplings.

IMPORTANT CAVEAT (Dr. M.): Hořava–Lifshitz *explicitly breaks Lorentz invariance*,
which is one of the assumptions used to DERIVE the amplitude-positivity bounds the
engine encodes. So the engine's exclusion of HL is unreliable — the constraints
may simply not apply in their standard form. The engine validly tests only
Lorentz-invariant, local frameworks; HL is outside that scope (see v1.58 note).
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class HoravaLifshitz(Framework):
    name = "horava_lifshitz"
    lorentz_invariant = False   # anisotropic z=3 scaling breaks Lorentz invariance
    citation = "Hořava 2009 (anisotropic Lifshitz scaling z=3); toy representative values"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.50, "g_6": 0.45, "g_8": 0.45,   # large higher-derivative matter
                "g_R2": 0.45, "g_R3": 0.40,               # large curvature terms (z=3 defining)
                "g_R2_parity": 0.10, "g_R3_parity": 0.06,  # Cotton-tensor parity-odd sector
            },
            name=self.name, source=self.citation,
        )
