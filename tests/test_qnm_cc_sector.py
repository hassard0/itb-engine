"""Tests for the cosmological-constant / dark-energy sector (v2.422, CC1)."""

from experiments.qnm_cc_sector import run
from experiments.stack import build_stack, rigor_of


_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_cc_sector_is_opt_in():
    default = build_stack(rfc_form="convex_hull", include_data=True)
    cc = build_stack(rfc_form="convex_hull", include_data=True, include_cc_sector=True)
    names_default = {c.name for c in default}
    names_cc = {c.name for c in cc}
    assert "de_sitter_conjecture" not in names_default   # untouched by default
    assert "de_sitter_conjecture" in names_cc
    assert len(cc) >= len(default) + 1


def test_cc_constraint_tagged_sourced_proxy():
    assert rigor_of("de_sitter_conjecture") == "sourced_proxy"


def test_candidate_admits_bounded_dark_energy():
    assert _RES["max_positive_g_Lambda_allowed"] > 0.05
    assert abs(_RES["max_positive_g_Lambda_allowed"] - _RES["candidate_g_R2"]) < 0.02
    win = _RES["g_Lambda_window"]
    assert win[0] < 0 < win[1]   # window spans AdS to dS


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "dark energy" in f
    assert "refined de sitter" in f or "refined-ds" in f
    sc = _RES["honest_scope"].lower()
    assert "conjectural" in sc
    assert "does not address the cc magnitude" in sc or "no absolute scale" in sc
