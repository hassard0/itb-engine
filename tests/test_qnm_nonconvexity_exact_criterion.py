"""Tests for the exact non-convexity criterion / boundary-layer characterization (v2.305)."""

from experiments.qnm_nonconvexity_exact_criterion import (
    run, engine_margin, predicted_midpoint_margin,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_closed_form_matches_engine_to_machine_precision():
    res = run()
    assert res["max_abs_error_vs_engine"] < 1e-9


def test_closed_form_identity_on_known_counterexample():
    # the v2.304 pair: closed form must equal the engine midpoint margin exactly
    A = (1.0, 0.3, 0.22)
    B = (0.2, 0.06, 0.01)
    mid = tuple(0.5 * (a + b) for a, b in zip(A, B))
    assert abs(predicted_midpoint_margin(A, B) - engine_margin(*mid)) < 1e-12


def test_dent_is_a_boundary_layer():
    res = run()
    layer = res["boundary_layer"]
    rates = [l["dent_rate"] for l in layer]
    # monotone rising as depth eps shrinks (depths listed large -> small)
    assert all(rates[i] <= rates[i + 1] + 1e-12 for i in range(len(rates) - 1))
    # deep interior layers essentially never dent; the shallowest does
    assert rates[0] < 0.01
    assert rates[-1] > 0.05


def test_interior_uniform_box_essentially_never_dents():
    res = run()
    assert res["interior_dent_rate_uniform_box"] < 1e-9


def test_finding_states_boundary_layer_and_covariation():
    res = run()
    f = res["finding"].lower()
    assert "boundary" in f
    assert "co-vary" in f or "co-varying" in f
    assert "exact" in f


def test_honest_scope_flags():
    res = run()
    sc = res["honest_scope"].lower()
    assert "no taylor remainder" in sc or "identity, not a fit" in sc
    assert "sampler-dependent" in sc
    assert "toy basis" in sc
