"""Tests for the gravity-from-matter rigidity swing (v2.372)."""

from experiments.qnm_gravity_from_matter_rigidity import run

_RES = run(n_walk=12000, seed=0)   # smaller walk for suite speed; the free/tight verdict is robust


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_leading_curvature_free_at_fixed_matter():
    g = _RES["gravitational_ranges_at_fixed_matter"]
    assert g["g_R2"]["extent"] > 0.05
    assert g["g_R3"]["extent"] > 0.05
    assert g["g_R2"]["free_at_fixed_matter"] is True
    assert g["g_R3"]["free_at_fixed_matter"] is True


def test_strong_form_refuted():
    assert _RES["consistency_checks"]["strong_form_gravity_from_matter_refuted"] is True


def test_five_genuine_inputs():
    assert _RES["genuine_input_count"] == 5
    assert set(_RES["genuine_inputs"]) == {"g_4", "g_6", "g_8", "g_R2", "g_R3"}


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "refuted" in f
    assert "5 genuine inputs" in f or "5 free directions" in f or "genuine inputs" in f
    assert "parity sector is determined" in f or "parity sector" in f
    sc = _RES["honest_scope"].lower()
    assert "sampled lower bounds" in sc or "sampler" in sc
    assert "toy" in sc
