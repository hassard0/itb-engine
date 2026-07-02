"""Tests for the asymptotic-safety discriminator / honest negative (v2.437)."""

from experiments.qnm_uv_discriminator import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_all_R2_completions_have_towers():
    t = _RES["species_table"]
    for n in ("string_tree_eft", "asymptotic_safety", "cdt"):
        assert t[n]["has_tower"] is True
        assert t[n]["N"] > 1.05


def test_species_scale_does_not_discriminate():
    assert _RES["R2_bearing_N_spread"] < 0.5   # viable completions clustered


def test_only_no_R2_has_N1():
    assert _RES["species_table"]["pure_gr"]["N"] == 1.0
    assert _RES["species_table"]["pure_gr"]["has_R2"] is False


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "fails at low energy" in f or "does not discriminate" in f
    assert "tower spectrum" in f
    assert "robust" in f
    sc = _RES["honest_scope"].lower()
    assert "negative result" in sc or "honest negative" in sc or "the species-scale discriminator fails" in sc
    assert "spectrum" in sc
