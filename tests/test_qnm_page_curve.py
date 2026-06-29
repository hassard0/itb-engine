"""Tests for the Page curve / information paradox (v2.275)."""

import math

from experiments.qnm_page_curve import (
    page_time_over_tau,
    run,
    s_bh,
    s_fine_page,
    s_rad_thermal,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_hawking_monotonic_to_S0():
    # coarse-grained radiation entropy rises monotonically to S_0 as M -> 0
    prev = -1.0
    for x in (1.0, 0.8, 0.5, 0.2, 0.01):
        s = s_rad_thermal(x)
        assert s >= prev
        prev = s
    assert abs(s_rad_thermal(1e-4) - 1.0) < 1e-3


def test_page_point_at_half_entropy():
    # fine-grained entropy peaks at S_0/2 when M = M_0/sqrt2
    xp = 1.0 / math.sqrt(2.0)
    assert abs(s_fine_page(xp) - 0.5) < 1e-9
    # it is the crossing of the two saddles
    assert abs(s_rad_thermal(xp) - s_bh(xp)) < 1e-9


def test_page_curve_turns_over_and_returns_information():
    # rises before the Page point, falls after -> pure final state
    assert s_fine_page(0.9) < s_fine_page(1 / math.sqrt(2))      # rising
    assert s_fine_page(0.3) < s_fine_page(1 / math.sqrt(2))      # falling
    assert s_fine_page(0.01) < 1e-2                              # information returns
    assert s_rad_thermal(0.01) > 0.99                            # Hawking would lose it


def test_island_min_prescription():
    for x in (0.95, 1 / math.sqrt(2), 0.5, 0.1):
        assert abs(s_fine_page(x) - min(s_rad_thermal(x), s_bh(x))) < 1e-15


def test_page_time_from_m_cubed_law():
    assert abs(page_time_over_tau() - (1 - 2 ** -1.5)) < 1e-12
    assert 0.6 < page_time_over_tau() < 0.7


def test_honest_scope_flags_phenomenological_model():
    res = run()
    sc = res["honest_scope"].lower()
    assert "phenomenological" in sc
    assert "page/greybody factor" in sc or "more entropic" in sc
    assert "illustrated, not proven" in sc
    assert "not an engine constraint refit" in sc
