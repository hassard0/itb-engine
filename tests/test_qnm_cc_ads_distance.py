"""Tests for the AdS distance conjecture / dS selection (v2.423, CC2)."""

from experiments.qnm_cc_ads_distance import run
from experiments.stack import rigor_of

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cc2_tagged_sourced_proxy():
    assert rigor_of("ads_distance_conjecture") == "sourced_proxy"


def test_no_ads_vacuum_de_sitter_selected():
    assert _RES["allowed_windows"]["ads_branch"] is None            # AdS empty
    ds = _RES["allowed_windows"]["ds_minkowski_branch"]
    assert ds is not None and ds[0] == 0.0 and ds[1] > 0.05          # dS/Mink survives
    assert _RES["ads_floor_cAdS1"] > _RES["eft_validity_ceiling_on_abs_gLambda"]  # floor > ceiling


def test_dS_selection_is_O1_robust():
    # AdS opens only for c_AdS below threshold ~0.94 -> dS-selection holds for O(1) c_AdS
    assert _RES["c_AdS_threshold_for_ads_to_open"] < 1.0
    assert _RES["c_AdS_threshold_for_ads_to_open"] > 0.5


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "selects de sitter" in f
    assert "not anti-de sitter" in f or "cannot be anti-de sitter" in f
    sc = _RES["honest_scope"].lower()
    assert "conjectural" in sc
    assert "o(1)-robust" in sc or "not a theorem" in sc
    assert "magnitude problem" in sc or "not the cc magnitude" in sc
