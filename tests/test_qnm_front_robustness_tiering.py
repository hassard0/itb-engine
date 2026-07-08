"""Tests for the four-front robustness tiering (v2.460)."""

from experiments.qnm_front_robustness_tiering import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_front_is_toy_map():
    assert _RES["toy_map_fronts"] == ["matter_cmb_s4"]
    assert "TOY-MAP" in _RES["fronts"]["matter_cmb_s4"]["tier"]


def test_three_robust_scale_clean():
    assert set(_RES["robust_fronts"]) == {"parity_birefringence", "inflation_r", "dark_energy_w"}


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "toy-map" in f and "weakest" in f
    assert "which we map to g_4 in the toy basis" in f
    assert "three scale-clean" in f
    sc = _RES["honest_scope"].lower()
    assert "matter dominance is genuinely rigorous" in sc or "matter dominance (g_4" in sc
    assert "map toy" in sc or "observable map" in sc
    assert "not 'matter dominance is wrong'" in sc or "not that matter dominance" in sc or "not 'matter dominance" in sc
