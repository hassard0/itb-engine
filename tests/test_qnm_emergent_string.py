"""Tests for the Emergent String Conjecture UV dichotomy (v2.440)."""

from experiments.qnm_emergent_string import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_kk_branch_planckian_and_submm_invisible():
    assert _RES["KK_branch_extra_dimension_size_m"] < 1e-30
    assert _RES["KK_branch_extra_dimension_size_m"] < _RES["submm_reach_m"]


def test_candidate_satisfies_submm():
    assert _RES["consistency_checks"]["candidate_satisfies_submm"] is True


def test_dichotomy_is_string_xor_kk():
    d = _RES["dichotomy"].lower()
    assert "string" in d and "kk" in d and "xor" in d


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "emergent string conjecture" in f
    assert "dichotomy" in f
    assert "planckian" in f and "submm-invisible" in f
    sc = _RES["honest_scope"].lower()
    assert "conjecture" in sc
    assert "presupposes the string landscape" in sc
    assert "does not engine-exclude" in sc or "does not" in sc
