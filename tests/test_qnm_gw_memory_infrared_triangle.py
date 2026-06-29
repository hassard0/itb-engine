"""Tests for the GW memory effect / infrared triangle (v2.267)."""

from experiments.qnm_gw_memory_infrared_triangle import memory_strain, run


def test_all_identity_checks_pass():
    res = run()
    assert res["all_identity_checks_pass"] is True
    for k, v in res["identity_checks"].items():
        assert v is True, k


def test_memory_equals_zero_frequency_mode():
    res = run()
    # the linking identity: Delta h = integral hdot dt = hdot(omega=0)
    assert abs(res["memory_total"] - res["zero_frequency_mode"]) < 1e-6 * abs(res["memory_total"])


def test_spectrum_at_zero_equals_memory_squared():
    # soft theorem: dE/domega at omega=0 is the nonzero constant |memory|^2
    res = run()
    assert abs(res["spectrum_at_zero"] - res["memory_squared"]) < 1e-6 * res["memory_squared"]
    # and the low-frequency band plateaus there to ~1%
    assert abs(res["low_freq_plateau"] - res["memory_squared"]) < 1e-2 * res["memory_squared"]


def test_oscillation_carries_no_memory():
    res = run()
    assert res["identity_checks"]["oscillation_carries_no_memory"] is True


def test_astrophysical_memory_scaling():
    # Delta h ~ (G/c^4 R) Delta E: linear in radiated energy, inverse in distance
    h1 = memory_strain(1e47, 1e25)
    h2 = memory_strain(2e47, 1e25)
    h3 = memory_strain(1e47, 2e25)
    assert abs(h2 - 2 * h1) < 1e-9 * h2
    assert abs(h3 - 0.5 * h1) < 1e-9 * h1
    # GW150914 raw memory is a sizeable fraction of the peak strain
    res = run()
    gw = next(r for r in res["astrophysical_memory"] if r["name"] == "GW150914")
    assert 0.05 < gw["memory_over_peak_raw"] < 1.0


def test_infrared_triangle_has_three_faces():
    res = run()
    tri = res["infrared_triangle"]
    assert "memory" in tri["face_1"].lower()
    assert "soft" in tri["face_2"].lower()
    assert "bms" in tri["face_3"].lower() or "supertranslation" in tri["face_3"].lower()


def test_honest_scope_flags_toy_and_order_of_magnitude():
    res = run()
    sc = res["honest_scope"].lower()
    assert "toy" in sc
    assert "order-of-magnitude" in sc or "order of magnitude" in sc
    assert "favata" in sc
