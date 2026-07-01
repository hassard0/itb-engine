"""Tests for the extremal-BH fourth-channel swing (v2.378)."""

from experiments.qnm_extremal_bh_channel import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_shift_positive_bh_decays():
    assert _RES["constructed_delta_S_ext"] > 0
    assert _RES["constructed_extremal_bh_decays"] is True


def test_matter_floor_guarantees_positivity():
    # the g_C-independent matter term alone is positive -> WGC from matter positivity
    assert _RES["matter_only_floor_B_g4"] > 0
    assert _RES["constructed_delta_S_ext"] >= _RES["matter_only_floor_B_g4"] - 1e-9


def test_wgc_automatic_for_positive_g4_frameworks_gr_marginal():
    rows = {r["framework"]: r for r in _RES["framework_delta_S_ext"]}
    # pure GR (g_4=0) is marginal (no shift); all matter-bearing frameworks decay
    assert rows["pure_gr"]["delta_S_ext"] == 0.0
    for name, r in rows.items():
        if r["g_4"] > 1e-9:
            assert r["extremal_bh_decays"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "fourth channel" in f
    assert "extremal" in f and "decay" in f
    assert "wgc-complete by construction" in f or "consequence of matter positivity" in f
    sc = _RES["honest_scope"].lower()
    assert "simplified encoding" in sc
    assert "non-discriminating" in sc
    assert "toy" in sc
