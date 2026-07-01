"""Tests for the program ledger v2 consolidation (v2.363)."""

from experiments.qnm_program_ledger_v2 import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_constructed_unique_no_named_framework():
    assert _RES["constructed_theory_and_data_ok"] == [True, True]
    assert not any(_RES["named_framework_both_ok"].values())


def test_three_channels_live_verified():
    fal = _RES["channel_falsifiers_live"]
    assert set(fal) == {"parity", "ringdown", "screening"}
    assert all(fal.values())


def test_tiers_present():
    tiers = _RES["robustness_tiers"]
    assert len(tiers) == 4
    # each tier has content
    for name, items in tiers.items():
        assert len(items) >= 3, name


def test_finding_and_scope_flags():
    f = _RES["finding"].lower()
    assert "three" in f and "channel" in f
    assert "parity-deformed" in f and "string-like" in f
    assert "birefringence" in f
    sc = _RES["honest_scope"].lower()
    assert "re-verified by check()" in sc or "re-verified" in sc
    assert "toy basis" in sc
    assert "updates the v2.323 ledger" in sc
