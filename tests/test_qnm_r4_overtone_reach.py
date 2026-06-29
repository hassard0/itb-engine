"""Tests for the net R4 overtone reach synthesis (v2.220)."""

from experiments.qnm_r4_overtone_reach import mode_reach, run


def test_overtone_has_lower_Q_and_worse_resolvability():
    m0, m1 = mode_reach(0), mode_reach(1)
    # the first overtone is more heavily damped: lower Q, larger R_f (worse freq resolvability)
    assert m1["Q"] < m0["Q"]
    assert m1["R_f"] > m0["R_f"]


def test_overtone_damping_channel_dominates_reach():
    m1 = mode_reach(1)
    # despite the resolvability penalty, the overtone's damping channel is far deeper
    assert m1["best_channel"] == "damping"
    assert m1["best_reach_x_rho"] < m1["reach_freq_x_rho"]


def test_net_overtone_advantage_is_two_orders():
    res = run()
    # sensitivity x resolvability still favors the overtone by ~2 orders of magnitude
    assert res["overtone_advantage_at_equal_snr"] > 100
    # the crossover SNR ratio is tiny -> the overtone wins under an extremely weak condition
    assert res["crossover_snr_ratio"] < 0.01
    assert res["dominant_channel_overtone"] == "damping"


def test_honest_scope_preserved():
    res = run()
    sc = res["honest_scope"].lower()
    assert "equal-snr" in sc
    assert "g_R4_c3" in res["honest_scope"]
    assert "perturbatively delicate" in sc or "gamma << 6e-3" in sc
