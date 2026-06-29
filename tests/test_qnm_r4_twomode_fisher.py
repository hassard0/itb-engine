"""Tests for the two-mode (220+221) joint Fisher covariance refinement (v2.221)."""

from experiments.qnm_r4_twomode_fisher import run, twomode_fisher


def test_modes_strongly_correlated():
    j = twomode_fisher(1.0)
    # overlapping modes -> strong positive frequency/damping correlations
    assert j["corr_w0_w1"] > 0.7
    assert j["corr_tau0_tau1"] > 0.7


def test_covariance_inflates_resolvability():
    res = run()
    inf = res["covariance_inflation"]
    # joint resolvability is degraded a few-fold vs the isolated single-mode coefficients
    assert all(v > 3.0 for v in inf.values())
    assert all(v < 7.0 for v in inf.values())


def test_inflation_amplitude_independent():
    # the dimensionless inflation does not depend on the amplitude ratio (Schur-complement geometry)
    a = twomode_fisher(1.0)
    b = twomode_fisher(0.2)
    assert abs(a[(1, "tau")] - b[(1, "tau")]) < 1e-2
    assert abs(a[(0, "f")] - b[(0, "f")]) < 1e-2
    assert run()["amplitude_independent"] is True


def test_overtone_advantage_survives_covariance():
    res = run()
    # advantage drops from 177x (isolated) but stays ~2 orders of magnitude
    adv = res["overtone_advantage_joint_equal_snr"]
    assert 100 < adv < 177
    assert res["overtone_best_channel"] == "damping"


def test_honest_scope_refines_not_overturns():
    res = run()
    sc = res["honest_scope"].lower()
    assert "refines v2.220" in sc
    assert "g_R4_c3" in res["honest_scope"]
    assert "robust" in res["finding"].lower()
