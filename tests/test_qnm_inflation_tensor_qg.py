"""Tests for the inflation tensor-sector QG probe (v2.253)."""

from experiments.qnm_inflation_tensor_qg import H_inflation_gev, V_quarter_gev, run


def test_current_bound_near_gut_scale():
    # r < 0.036 -> V^{1/4} ~ 1.4e16 GeV, near the GUT scale
    v = V_quarter_gev(0.036)
    assert 1e16 < v < 2e16


def test_energy_scale_scales_as_r_quarter():
    # V^{1/4} ~ r^{1/4}
    assert abs(V_quarter_gev(0.16) / V_quarter_gev(0.01) - 2.0) < 1e-6


def test_hubble_scales_as_sqrt_r():
    assert abs(H_inflation_gev(0.04) / H_inflation_gev(0.01) - 2.0) < 1e-6


def test_future_targets_lower_energy():
    res = run()
    rows = res["tensor_targets"]
    by_r = sorted(rows, key=lambda x: x["r"])
    vs = [x["V_quarter_GeV"] for x in by_r]
    assert all(vs[i] < vs[i + 1] for i in range(len(vs) - 1))


def test_honest_scope_prospective_quantization():
    res = run()
    sc = res["honest_scope"].lower()
    assert "prospective" in sc and "not detected" in sc
    assert "slow-roll" in sc
    assert "g_R4_c3" in res["honest_scope"]
