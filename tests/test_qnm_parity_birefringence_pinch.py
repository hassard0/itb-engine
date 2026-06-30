"""Tests for the two-birefringence parity pinch (v2.347)."""

from experiments.qnm_parity_birefringence_pinch import run, ANOMALY_UPPER, CONSTRUCTED_PARITY


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_cmb_pushes_up_gw_bounds_above():
    res = run()
    # CMB central is large (above the anomaly cap); GW real bound bites below it
    assert res["cmb_central_g_R2_parity"] > res["anomaly_upper_edge"]
    assert res["gw_bound_real_O3_estimate"] < ANOMALY_UPPER


def test_toy_admits_real_excludes_constructed():
    res = run()
    toy = next(c for c in res["cases"] if c["gw_bound_label"] == "toy_loosened")
    real = next(c for c in res["cases"] if c["gw_bound_label"] == "real_O3_estimate")
    assert toy["constructed_0p06_inside"] is True
    assert real["constructed_0p06_inside"] is False
    # the real bound narrows the window to a sliver but does not (yet) close it
    assert 0.0 < real["window_width"] < 0.01
    assert real["nonempty"] is True


def test_falsification_threshold_is_cmb_lower_edge():
    res = run()
    assert abs(res["gw_falsification_threshold"] - res["cmb_2sigma_band"][0]) < 1e-9
    # a GW bound at/below the CMB lower edge would close the window
    assert res["gw_falsification_threshold"] < CONSTRUCTED_PARITY


def test_finding_and_scope_flags():
    res = run()
    f = res["finding"].lower()
    assert "pinch" in f
    assert "cmb" in f and "gw" in f
    assert "falsif" in f
    sc = res["honest_scope"].lower()
    assert "toy" in sc
    assert "v2.329" in sc or "cmb hint being real" in sc
    assert "structure" in sc
