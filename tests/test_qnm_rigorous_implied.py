"""Tests for the de-toying-by-redundancy cycle (v2.412)."""

from experiments.qnm_rigorous_implied import run
from experiments.stack import IMPLIED_BY_RIGOROUS, effective_rigorous_stack, rigorous_core_stack

_RES = run(n_walk=12000)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_matter_dominance_and_bh_decay_are_rigorous():
    r = _RES["redundancy_given_rigorous_core"]
    assert r["weak_gravity_conjecture"] > 0.999      # matter dominance ceiling implied by rigorous core
    assert r["wald_entropy_positivity"] > 0.999       # extremal-BH decay implied by rigorous core


def test_effective_core_capability():
    core = rigorous_core_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                               include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    eff = effective_rigorous_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                                   include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    assert len(eff) == len(core) + len(IMPLIED_BY_RIGOROUS)
    assert "weak_gravity_conjecture" in IMPLIED_BY_RIGOROUS
    assert "wald_entropy_positivity" in IMPLIED_BY_RIGOROUS


def test_genuine_toy_cuts_localized():
    # the toy cuts that actually carry weight are the anomaly / SDC / complexity / birefringence
    names = {g["constraint"] for g in _RES["genuine_toy_cuts_below_rigorous"]}
    assert "anomaly_cancellation" in names
    assert "swampland_distance_conjecture" in names
    assert "cosmic_birefringence_data" in names


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "secretly rigorous" in f or "implied by the rigorous core" in f
    assert "matter dominance" in f
    sc = _RES["honest_scope"].lower()
    assert "empirical" in sc
    assert "not a proof of global implication" in sc or "feasible region" in sc
    assert "trivially satisfied" in sc or "non-binding" in sc
