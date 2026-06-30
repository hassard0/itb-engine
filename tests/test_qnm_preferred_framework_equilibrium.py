"""Tests for the preferred-framework multi-principle-equilibrium analysis (v2.314)."""

from experiments.qnm_preferred_framework_equilibrium import run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_preferred_is_interior():
    res = run()
    assert res["worst_case_constraint"]["signed_distance"] > 0.0


def test_worst_case_is_universality():
    res = run()
    assert res["worst_case_constraint"]["class"] == "C_UNIVERSALITY"


def test_tight_cluster_spans_two_families():
    res = run()
    assert "A_AMPLITUDE" in res["tight_cluster_classes"]
    assert "C_UNIVERSALITY" in res["tight_cluster_classes"]
    # the tight cluster has members of both families
    classes = [cls for _, _, cls in res["tight_cluster"]]
    assert classes.count("A_AMPLITUDE") >= 2
    assert classes.count("C_UNIVERSALITY") >= 2


def test_families_in_tension():
    res = run()
    # at least one coupling moves the two families' margins in opposite directions
    assert any(t["opposite_sign"] for t in res["tension_gradients"])
    assert res["consistency_checks"]["no_single_move_improves_worst_case"] is True


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "equilibrium" in f
    assert "tension" in f
    assert "amplitude" in f and "universality" in f
    sc = res["honest_scope"].lower()
    assert "engine's literal output" in sc
    assert "toy basis" in sc
