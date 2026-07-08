"""Tests for the axion-DE joint-test / sharp implication (v2.459)."""

from experiments.qnm_axion_de_joint_test import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_implication_and_status():
    pr = _RES["prediction"]
    assert "w0 > -1" in pr["implication"]
    assert pr["current_status"]["co_occurrence"] == "SUPPORTED"
    assert len(pr["falsifiers"]) == 2


def test_no_submm_consequence():
    assert "sub-mm" in _RES["prediction"]["consequence_no_submm"].lower()
    assert "retires" in _RES["prediction"]["consequence_no_submm"].lower()


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "requires dynamical dark energy" in f
    assert "falsif" in f
    assert "no sub-mm fifth force" in f
    sc = _RES["honest_scope"].lower()
    assert "hints, not detections" in sc or "hints not detections" in sc or "hints -- not detections" in sc
    assert "phantom past" in sc or "phantom-past" in sc
    assert "retires the scalaron-de sub-mm" in sc or "retires the dark-energy sub-mm" in sc or "retires the old scalaron-de" in sc or "retires the scalaron-de" in sc
