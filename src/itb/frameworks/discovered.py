"""Engine-discovered candidate theories (not from the prior literature).

These are NOT phenomenological frameworks proposed by a research program; they
are points in Wilson-coefficient space that the engine's generative search
(docs/results 2026-06-08 v1.27 / v1.31) found to be (a) consistent with the full
corrected constraint stack and (b) maximally unlike any catalogued framework.
They are promoted to first-class Framework encoders so the comparison machinery
(fingerprint, first-disagreement, survival) can treat them on equal footing.

Both are honest toy-precision objects: their coordinates will move once
constraints are encoded at literature precision. What is robust is their
qualitative signature.
"""

from itb.frameworks.base import Framework
from itb.theory import Theory


class DiscoveredNovel(Framework):
    """Robust novel branch (v1.27): weakly-coupled, with an anomalously small
    dimension-8 matter coupling and near-vanishing cubic curvature. Sits ~0.33
    from any catalogued framework and is feasible in ~76% of the prefactor box —
    as robust as the known frameworks. Distinguishing observable: g_8."""

    name = "discovered_novel"
    citation = "ITB generative search 2026-06-08 (v1.27); engine-discovered, not from literature"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.340, "g_6": 0.117, "g_8": 0.045,
                "g_R2": 0.136, "g_R3": 0.017,
                "g_R2_parity": 0.021, "g_R3_parity": 0.017,
            },
            name=self.name, source=self.citation,
        )


class DiscoveredParityViolating(Framework):
    """Maximally parity-violating consistent branch (v1.31). Demonstrates that a
    parity-violating quantum gravity CAN satisfy every constraint — unlike
    LQG-induced (excluded) — provided it SUPPRESSES its cubic curvature
    (g_R2/g_R3 ≈ 8 here, vs LQG's 1.0). It is fragile (feasible in ~10% of the
    prefactor box). Distinguishing observable: the parity amplitude
    (g_R2_parity, g_R3_parity)."""

    name = "discovered_parity_violating"
    citation = "ITB generative search 2026-06-08 (v1.31); engine-discovered, not from literature"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.647, "g_6": 0.490, "g_8": 0.376,
                "g_R2": 0.395, "g_R3": 0.050,
                "g_R2_parity": -0.092, "g_R3_parity": 0.044,
            },
            name=self.name, source=self.citation,
        )


class DiscoveredHighG8(Framework):
    """The second robust novel branch (v1.32 catalog #1): a STRONG dimension-8
    matter coupling (g_8 ≈ 0.55, far above any catalogued framework's ~0.3-0.4),
    cubic-suppressed and mildly parity-violating, feasible in ~63% of the
    prefactor box. Together with DiscoveredNovel (g_8 ≈ 0.045) it brackets the
    dimension-8 coupling from both ends — the loosest direction of the allowed
    region (v1.33). Distinguishing observable: g_8 (matter forward amplitude)."""

    name = "discovered_high_g8"
    citation = "ITB generative search 2026-06-08 (v1.32 catalog); engine-discovered, not from literature"

    def encode(self) -> Theory:
        return Theory(
            coefficients={
                "g_4": 0.453, "g_6": 0.208, "g_8": 0.552,
                "g_R2": 0.210, "g_R3": 0.036,
                "g_R2_parity": 0.033, "g_R3_parity": -0.028,
            },
            name=self.name, source=self.citation,
        )
