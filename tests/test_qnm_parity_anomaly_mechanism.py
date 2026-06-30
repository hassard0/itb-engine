"""Tests for the parity-anomaly mechanism (v2.318)."""

from experiments.qnm_parity_anomaly_mechanism import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_binding_wall_is_anomaly_matching():
    res = run()
    assert res["parity_free_worst_case"]["constraint"] == "t_hooft_anomaly_matching"


def test_anomaly_matching_relieved_by_parity():
    res = run()
    assert res["t_hooft_anomaly_matching_gradient"] > 1e-3


def test_relieved_constraints_are_chirality_family():
    res = run()
    for r in res["relieved_by_parity"][:2]:
        n = r["constraint"]
        assert "anomaly" in n or "handed" in n


def test_forbidden_zone_and_parity_optimum():
    res = run()
    fz = res["forbidden_zone_at_parity_0p012"]
    assert fz["signed_distance"] < 0
    assert "distance" in fz["constraint"]
    po = res["parity_optimum"]
    assert po["signed_distance"] > po["vs_parity_free"] + 1e-3


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "anomaly matching" in f
    assert "chirality" in f or "chiral" in f
    assert "forbidden zone" in f
    sc = res["honest_scope"].lower()
    assert "convex_hull" in sc
    assert "toy basis" in sc
