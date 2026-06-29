"""Tests for the overtone covariance wall (v2.222)."""

from experiments.qnm_overtone_covariance_wall import joint, run


def test_adding_overtone_inflates_resolvability():
    two = joint([0, 1])
    three = joint([0, 1, 2])
    # the first overtone damping resolvability degrades further when n=2 is added to the fit
    assert three[(1, "Rt")] > two[(1, "Rt")] > 0
    assert three[(1, "Rt")] / two[(1, "Rt")] > 10      # a further order-of-magnitude


def test_condition_number_explodes():
    two = joint([0, 1])
    three = joint([0, 1, 2])
    # the Fisher matrix becomes far more ill-conditioned as overtones stack
    assert three["cond"] > 100 * two["cond"]


def test_compounding_is_superlinear():
    res = run()
    c = res["compounding"]
    # 2-mode inflation ~5.5x; 3-mode adds another ~35x -> ~195x vs isolated
    assert c["R_tau1_isolated_to_2mode"] > 3
    assert c["R_tau1_2mode_to_3mode"] > 10
    assert c["R_tau1_isolated_to_3mode"] > 100


def test_overtone_advantage_erodes_but_persists():
    res = run()
    a = res["r4_overtone_reach_x_rho"]
    # advantage drops from ~140x (2-mode) to ~10x (3-mode) -- eroded but still favorable
    assert a["overtone_advantage_2mode"] > a["overtone_advantage_3mode"]
    assert 3 < a["overtone_advantage_3mode"] < 30


def test_honest_scope_n2_qeft_absent():
    res = run()
    sc = res["honest_scope"].lower()
    assert "not published" in sc
    assert "low-order" in res["finding"].lower()
    assert "g_R4_c3" in res["honest_scope"]
