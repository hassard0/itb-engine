"""Tests for axial<->polar QNM isospectrality and the R4 parity-splitting discriminator (v2.218)."""

import math

from experiments.qnm_isospectrality import (
    polar_qnm,
    run,
    schwarzschild_qnm,
    zerilli_potential,
)


def test_zerilli_l2_lambda():
    # lam = (L-1)(L+2)/2 = 2 for L=2; potential is positive and finite outside the horizon
    v = zerilli_potential(3.0, L=2)
    assert v > 0 and math.isfinite(v)


def test_isospectrality_holds_to_wkb_precision():
    # axial (Regge-Wheeler) and polar (Zerilli) share the SAME QNM spectrum in GR
    for L, n in [(2, 0), (3, 0)]:
        ax = schwarzschild_qnm(n=n, L=L, s=2)
        po = polar_qnm(n=n, L=L)
        assert abs(ax - po) < 5e-3
    # l=3 is far below the l=2 WKB systematic
    assert abs(schwarzschild_qnm(0, 3, 2) - polar_qnm(0, 3)) < 1e-4


def test_run_validates_and_reports_noise_floor():
    res = run()
    assert res["isospectrality_validated"] is True
    assert res["parity_splitting_noise_floor"] < 5e-3
    # all four modes present
    assert len(res["isospectrality"]) == 4


def test_r4_discriminator_source_backed_and_above_floor():
    res = run()
    d = res["r4_discriminator"]
    # axial shift magnitude is the v2.215/v2.216 number (|-3.184 - 5.637i| ~ 6.47)
    assert abs(d["axial_shift_magnitude"] - 6.47) < 0.1
    # the shift sits far above the parity-splitting noise floor
    assert d["headroom_over_noise_floor"] > 1e3


def test_full_splitting_negative_preserved():
    res = run()
    d = res["r4_discriminator"]
    assert "un-sourceable" in d["honest_negative"].lower()
    assert "even-parity" in d["honest_negative"].lower() or "zerilli" in d["honest_negative"].lower()
    assert "g_R4_c3" in res["claim_gate"]
