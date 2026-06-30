"""Tests for the cosmic-birefringence-favors-parity result (v2.321)."""

from experiments.qnm_cosmic_birefringence_favors_parity import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_parity_even_frameworks_disfavored():
    for r in _RES["frameworks_vs_data"]:
        if abs(r["g_R2_parity"]) < 1e-9:
            assert r["data_favored"] is False
            assert abs(r["beta_pred_deg"]) < 1e-9


def test_lqg_data_favored():
    lqg = next(r for r in _RES["frameworks_vs_data"] if r["framework"] == "lqg_induced")
    assert lqg["data_favored"] is True


def test_data_requires_positive_parity():
    assert _RES["data_required_parity_threshold"] > 1e-3
    assert _RES["data_central_parity"] > 0


def test_joint_window_nonempty_and_above_threshold():
    w = _RES["joint_consistency_plus_data_window"]
    assert w is not None and w[0] < w[1]
    # the joint window sits at or above the data-required threshold
    assert w[0] >= _RES["data_required_parity_threshold"] - 1e-3


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "cosmic birefringence" in f
    assert "parity-even" in f and "disfavored" in f
    assert "converg" in f
    sc = _RES["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "toy basis" in sc
