"""Tests for the Trans-Planckian Censorship Conjecture tensor bound (v2.263)."""

import math

from experiments.qnm_trans_planckian_censorship import (
    run,
    tcc_H_max_gev,
    tcc_r_max,
)
from experiments.qnm_inflation_tensor_qg import A_S, M_PL_GEV, H_inflation_gev


def test_tcc_hubble_cap_is_exponential():
    # H_max = M_Pl e^{-N}
    assert abs(tcc_H_max_gev(60.0) - M_PL_GEV * math.exp(-60.0)) < 1e-12 * M_PL_GEV
    assert tcc_H_max_gev(70.0) < tcc_H_max_gev(60.0) < tcc_H_max_gev(44.0)


def test_r_max_matches_closed_form():
    for n in (44.0, 50.0, 60.0):
        assert abs(tcc_r_max(n) - 2.0 * math.exp(-2 * n) / (math.pi**2 * A_S)) < 1e-300 + 1e-12 * tcc_r_max(n)


def test_roundtrip_H_self_consistent():
    # H(r_max) via the v2.253 slow-roll relation must reproduce the direct TCC H_max
    res = run()
    for row in res["tcc_bounds"]:
        assert row["roundtrip_H_consistent"] is True
        assert abs(H_inflation_gev(row["r_max"]) - row["H_max_gev"]) / row["H_max_gev"] < 1e-9


def test_reproduces_bedroya_vafa_order_of_magnitude():
    res = run()
    a = res["bedroya_vafa_anchor"]
    assert a["reproduces_bedroya_vafa_order"] is True
    assert 1e8 < a["V_quarter_max_gev"] < 1e10   # ~ 6e8 GeV
    assert 1e-32 < a["r_max"] < 1e-29            # ~ 1e-30


def test_tcc_ceiling_far_below_every_detector():
    res = run()
    # even the most generous N and the most speculative floor leave a huge gap
    for f in res["detection_floor_gaps"]:
        assert f["orders_above_tcc_N44"] > 20    # >20 orders of magnitude unreachable
    # qualitative falsifiable claim recorded
    assert "falsif" in res["finding"].lower()


def test_honest_scope_flags_conjecture_and_N_sensitivity():
    res = run()
    sc = res["honest_scope"].lower()
    assert "conjecture" in sc
    assert "sensitive to n" in sc or "e^{-2n}" in sc
    assert "qualitative" in sc
