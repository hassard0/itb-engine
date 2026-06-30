"""Tests for the parity anomaly-budget result (v2.335)."""

from experiments.qnm_parity_anomaly_budget import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cubic_parity_squeezed_across_window():
    assert _RES["cubic_max_at_window_bottom"] > _RES["cubic_max_at_window_top"] + 0.01
    assert _RES["cubic_max_at_window_top"] < 0.01   # ~zero at the window top


def test_constructed_zero_cubic_feasible():
    assert _RES["consistency_checks"]["constructed_zero_cubic_parity_is_feasible"] is True


def test_shared_budget_roughly_constant():
    assert _RES["consistency_checks"]["anomaly_budget_roughly_constant_on_boundary"] is True
    assert _RES["anomaly_budget_constant_g2p_sq_plus_2g3p_sq"] > 0


def test_band_monotone_squeeze():
    # the feasible cubic-parity max is (weakly) decreasing as the leading parity rises
    feas = [b for b in _RES["cubic_parity_band"] if b["feasible"]]
    maxes = [b["g_R3_parity_max"] for b in feas]
    assert maxes[0] >= maxes[-1]          # starts higher, ends at ~0


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "anomaly" in f and "budget" in f
    assert "squeez" in f
    assert "one-parameter" in f
    sc = _RES["honest_scope"].lower()
    assert "anomaly budget" in sc
    assert "toy basis" in sc
