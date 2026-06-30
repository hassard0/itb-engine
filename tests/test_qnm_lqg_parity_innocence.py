"""Tests for the lqg parity-innocence diagnostic (v2.310)."""

from experiments.qnm_lqg_parity_innocence import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_parity_toggle_leaves_failures_identical():
    res = run()
    assert res["full_failures"] == res["parity_off_failures"]
    assert len(res["full_failures"]) == 6
    # no constraint changes satisfaction when parity is zeroed
    assert res["parity_sensitive_constraints_at_lqg"] == []


def test_failures_are_cp_even():
    res = run()
    # the known CP-even failure set
    assert "graviton_forward_positivity" in res["full_failures"]
    assert "repulsive_force_conjecture" in res["full_failures"]
    # none of the parity-named constraints are in the failure set
    for name in res["full_failures"]:
        assert "parity" not in name and "birefringence" not in name and "anomaly_inflow" not in name


def test_lqg_parity_inside_window_with_small_headroom():
    res = run()
    # at the actual lqg parity value (mult 1.0) no new parity failures
    row0 = [r for r in res["headroom_scan"] if r["mult"] == 1.0][0]
    assert row0["new_parity_failures"] == []
    # the first parity failure appears just above (marginal, factor > 1)
    assert res["parity_headroom_first_failure_multiplier"] > 1.0
    assert res["parity_headroom_first_failure_multiplier"] <= 1.5


def test_uniform_downscaling_does_not_heal():
    res = run()
    base_nf = res["magnitude_scan"][0]["n_fail"]
    assert all(r["n_fail"] >= base_nf for r in res["magnitude_scan"])


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "not because of its parity" in f
    assert "cp-even" in f
    assert "ratios" in f
    sc = res["honest_scope"].lower()
    assert "engine's literal output" in sc
    assert "toy basis" in sc
