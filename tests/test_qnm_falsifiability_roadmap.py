"""Tests for the falsifiability roadmap (v2.328)."""

from experiments.qnm_falsifiability_roadmap import run, beta_pred, chirality


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_roadmap_has_three_parity_probes_plus_matter():
    res = run()
    tests = [r["test"] for r in res["roadmap"]]
    assert "cosmic_birefringence" in tests
    assert any("chiral" in t for t in tests)
    assert any("leptogenesis" in t for t in tests)
    assert any("matter" in t for t in tests)


def test_parity_even_predicts_zero_on_parity_probes():
    res = run()
    for r in res["roadmap"][:3]:
        assert "0" in r["parity_even_prediction"]


def test_constructed_predictions_right_handed():
    assert beta_pred(0.06) > 0
    assert chirality(0.06) > 0


def test_beta_within_measurement_at_low_edge():
    res = run()
    # constructed beta is below the central measured value (low edge) but within ~3 sigma
    assert res["beta_tension_sigma"] > 0
    assert abs(res["beta_tension_sigma"]) < 3.0


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "falsifiable" in f or "refutable" in f
    assert "chiral" in f and "discriminator" in f
    sc = res["honest_scope"].lower()
    assert "order-of-magnitude" in sc
    assert "symmetry statement" in sc
    assert "toy basis" in sc
