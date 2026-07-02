"""Tests for the string-deformation UV-embedding lead (v2.433)."""

from experiments.qnm_string_deformation import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_string_in_cage_and_is_parity_conserving_rival():
    assert _RES["string_effective_cage_feasible"] is True
    assert _RES["string_rigorous_core_feasible"] is True
    assert _RES["string_full_stack_violations"] == ["cosmic_birefringence_data"]


def test_candidate_is_string_plus_parity():
    assert _RES["parity_even_distance"] < 0.1
    assert _RES["string_tree_eft_couplings"]["g_R2_parity"] < 0.02
    assert _RES["parity_difference"] > 0.03


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "string tree-eft + the data-required parity" in f or "string tree-eft + parity" in f or "parity deformation" in f
    assert "uv" in f
    sc = _RES["honest_scope"].lower()
    assert "engine's framework encoder" in sc or "not a specific compactification" in sc
    assert "real string-theory computation" in sc or "real computation-still-needed" in sc or "still requires the real" in sc
