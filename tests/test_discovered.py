"""Tests for engine-discovered candidate theories (v1.27 / v1.31)."""

import pytest

from itb.constraints.graviton_forward_positivity import GravitonForwardPositivity
from itb.constraints.matter_s3_positivity import MatterS3Positivity
from itb.frameworks.discovered import DiscoveredNovel, DiscoveredParityViolating


def test_novel_signature():
    """The novel branch is weakly-coupled with suppressed g_8 and near-zero cubic."""
    c = DiscoveredNovel().encode().coefficients
    assert c["g_8"] < 0.10          # anomalously small dim-8 matter coupling
    assert c["g_R3"] < 0.05         # near-vanishing cubic curvature
    # passes the forward-positivity bound (leading dominates cubic)
    assert GravitonForwardPositivity(c=1.2).evaluate(DiscoveredNovel().encode()).satisfied


def test_parity_violating_is_actually_parity_violating():
    c = DiscoveredParityViolating().encode().coefficients
    assert abs(c["g_R2_parity"]) + abs(c["g_R3_parity"]) > 0.05   # genuinely parity-violating


def test_parity_branch_requires_suppressed_cubic():
    """The consistent parity-violating theory threads the needle LQG fails:
    it suppresses the cubic curvature (g_R2/g_R3 >> 1), so it still passes
    forward positivity despite violating parity."""
    t = DiscoveredParityViolating().encode()
    c = t.coefficients
    assert c["g_R2"] / c["g_R3"] > 5.0       # strongly cubic-suppressed (LQG is ~1.0)
    assert GravitonForwardPositivity(c=1.2).evaluate(t).satisfied
    assert MatterS3Positivity(c_m=1.0).evaluate(t).satisfied


def test_distinct_from_each_other():
    a = DiscoveredNovel().encode().coefficients
    b = DiscoveredParityViolating().encode().coefficients
    assert a != b
    assert DiscoveredNovel().name != DiscoveredParityViolating().name
