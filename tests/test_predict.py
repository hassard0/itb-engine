"""Tests for the unified predictions module + CLI (v1.63)."""

import pytest

from itb.cli import main
from itb.predict import FRAMEWORKS, predict, render


def test_all_frameworks_predictable():
    assert len(FRAMEWORKS) == 12
    for name in FRAMEWORKS:
        p = predict(name)
        assert p["framework"] == name
        assert "observables" in p and "scope" in p


def test_parity_branch_fingerprint():
    p = predict("discovered_parity_violating")
    assert p["parity_violating"] is True
    assert p["observables"]["gw_birefringence_g_R2_parity"] > 0.05
    assert p["observables"]["chiral_HD_circular_polarization_pct"][1] > 0


def test_out_of_scope_flagged():
    assert predict("horava_lifshitz")["scope"]["in_scope"] is False
    assert predict("causal_set")["scope"]["in_scope"] is False
    assert predict("string_tree_eft")["scope"]["in_scope"] is True


def test_yukawa_range_for_string():
    # string g_R2=0.2 -> lambda_Y = sqrt(6*0.2)*1.973e-7/2.4e-3*1e6 ~ 90 um
    assert predict("string_tree_eft")["observables"]["submm_yukawa_range_um_at_DE_scale"] == pytest.approx(90, abs=2)


def test_unknown_framework_raises():
    with pytest.raises(KeyError):
        predict("does_not_exist")


def test_render_is_string():
    assert "fingerprint" in render("asymptotic_safety")


def test_cli_predict_runs():
    assert main(["predict", "discovered_parity_violating"]) == 0
    assert main(["predict", "list"]) == 0
    assert main(["predict", "bogus"]) == 2
