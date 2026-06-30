"""Tests for the global prefactor-sensitivity sweep (v2.345)."""

from experiments.qnm_prefactor_sensitivity_sweep import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_constructed_feasible_at_canonical():
    res = run()
    assert res["base_feasible_at_canonical"] is True
    assert res["base_violations"] == []


def test_all_eleven_swept_and_partitioned():
    res = run()
    assert res["n_prefactors"] == 11
    assert res["n_slack"] + res["n_load_bearing"] == 11
    # the load-bearing set is exactly the prefactors not feasible across the full band
    lb = {r["prefactor"] for r in res["per_prefactor"] if not r["feasible_across_full_band"]}
    assert lb == set(res["load_bearing_prefactors"])


def test_every_break_is_an_edge_effect():
    res = run()
    # the point stays feasible across the bulk (>= 70%) of every prefactor's band
    for r in res["per_prefactor"]:
        assert r["feasible_grid_fraction"] >= 0.7, r["prefactor"]
    assert res["min_feasible_grid_fraction"] >= 0.7


def test_anomaly_rho_load_bearing_consistent_with_v2344():
    res = run()
    # v2.344: constructed parity 0.06 violates the anomaly budget near the rho=0.03 floor
    assert "anomaly_rho" in res["load_bearing_prefactors"]
    row = next(r for r in res["per_prefactor"] if r["prefactor"] == "anomaly_rho")
    assert row["first_break"]["constraints"] == ["generalized_anomaly_inflow"]
    assert abs(row["first_break"]["value"] - 0.03) < 1e-6


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "marginal" in f
    assert "chebyshev" in f and "v2.333" in f
    sc = res["honest_scope"].lower()
    assert "one-at-a-time" in sc or "oat" in sc
    assert "joint" in sc
    assert "toy basis" in sc
