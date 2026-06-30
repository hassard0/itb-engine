"""Tests for the screening-mandate robustness refinement (v2.355)."""

from experiments.qnm_screening_mandate_robustness import run, CONSTRUCTED, CP_EVEN_EXPECTED

_RES = run(n_search=4000, seed=0)


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_sector_mandates_screening_data_independent():
    # at the constructed sector, parity 0, birefringence OFF, every small g_R2 is infeasible
    for gR2, viol in _RES["constructed_sector_violations_nobire"].items():
        assert len(viol) > 0, gR2
        # and the cause is exactly the CP-even, data-independent set
        assert set(viol) == CP_EVEN_EXPECTED, (gR2, viol)


def test_unscreened_branch_exists_without_birefringence():
    pt = _RES["unscreened_nobire_feasible_point"]
    assert pt is not None
    # the alternative lives at smaller couplings and below the cap
    assert pt["g_4"] < CONSTRUCTED["g_4"]
    assert pt["g_R2"] <= _RES["g_R2_max_unscreened"]


def test_with_birefringence_unscreened_still_empty():
    assert _RES["unscreened_withbire_empty"] is True


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "partly robust" in f or "partial" in f.replace("partial robustness", "partly robust") or "data-independent" in f
    assert "cp-even" in f
    assert "selects" in f
    sc = _RES["honest_scope"].lower()
    assert "empirical" in sc
    assert "witness" in sc or "exhibiting one feasible point" in sc
    assert "toy basis" in sc
