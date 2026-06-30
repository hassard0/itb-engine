"""Tests for the parity-odd-cubic reflection symmetry verification (v2.352)."""

from experiments.qnm_parity_odd_cubic_symmetry import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_full_stack_reflection_symmetric():
    # every stack margin identical at +/- delta -> no constraint breaks the g_R3_parity reflection
    assert _RES["n_asymmetric_constraints"] == 0
    assert _RES["asymmetric_constraints"] == {}


def test_window_symmetric_and_centered_at_zero():
    lo, hi = _RES["feasible_window_gR3p"]
    assert lo is not None and hi is not None
    assert abs(lo + hi) < 0.005           # symmetric about 0
    assert abs(_RES["window_center"]) < 0.005
    # the edge matches the closed-form anomaly bound
    assert abs(hi - _RES["anomaly_closed_form_edge"]) < 0.01


def test_contrast_quadratic_pinned_cubic_not():
    # the parity-odd CUBIC zero is feasible (central); the parity-odd QUADRATIC zero is not (data-pinned)
    assert _RES["gR3p_zero_feasible"] is True
    assert _RES["gR2p_zero_feasible"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "unpredicted" in f
    assert "reflection" in f
    assert "verified" in f
    sc = _RES["honest_scope"].lower()
    assert "even function" in sc
    assert "t_hooft" in sc or "equality" in sc   # the flagged place a future upgrade changes the verdict
    assert "toy basis" in sc
