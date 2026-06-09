"""Tests for the alternative-birefringence EFTs (v2.08)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import alt_birefringence as ab


def test_g_R2_parity_is_beta_over_kappa():
    assert ab.KAPPA_BETA == 3.4
    assert 0.34 / ab.KAPPA_BETA == __import__("pytest").approx(0.1, abs=0.001)


def test_null_scenario_ties_parity_even():
    """At beta=0 the data-driven EFT ties the parity-even survivor (0.5) -> parsimony."""
    post, even = ab.posterior_data_driven(0.0, 0.09)
    assert post["discovered_data_driven"] == __import__("pytest").approx(0.5)
    assert post[even] == __import__("pytest").approx(0.5)


def test_canonical_scenario_favors_data_driven():
    """At beta=0.34 the data-driven EFT is decisively favored over the parity-even survivor."""
    post, _ = ab.posterior_data_driven(0.34, 0.09)
    assert post["discovered_data_driven"] > 0.99


def test_higher_beta_more_favored_than_lower():
    p_low = ab.posterior_data_driven(0.1, 0.09)[0]["discovered_data_driven"]
    p_high = ab.posterior_data_driven(0.34, 0.09)[0]["discovered_data_driven"]
    assert p_high > p_low
