"""Tests for the new-theory program ledger / capstone synthesis (v2.323)."""

from experiments.qnm_program_ledger import run

_RES = run()


def test_all_checks_pass():
    assert _RES["all_checks_pass"] is True
    for k, v in _RES["consistency_checks"].items():
        assert v is True, k


def test_robust_tier_reconfirmed():
    c = _RES["consistency_checks"]
    assert c["constructed_satisfies_theory_and_data"] is True
    assert c["no_named_framework_satisfies_both"] is True
    assert c["parity_even_frameworks_data_excluded"] is True
    assert c["lqg_theory_excluded_under_convex_hull"] is True


def test_ledger_has_all_tiers():
    led = _RES["ledger"]
    keys = " ".join(led).lower()
    assert "robust" in keys
    assert "schematic" in keys
    assert "honest negative" in keys or "correction" in keys


def test_correction_is_carried_forward():
    led = _RES["ledger"]
    text = " ".join(item for items in led.values() for item in items).lower()
    assert "v2.316" in text and "artifact" in text
    assert "degenerate" in text          # the v2.308 honest negative
    assert "fragile" in text             # the v2.320 fragility


def test_headline_and_scope():
    assert "both" in _RES["headline"].lower() or "theory and current data" in _RES["headline"].lower()
    sc = _RES["honest_scope"].lower()
    assert "toy basis" in sc
    assert "right streets" in sc
