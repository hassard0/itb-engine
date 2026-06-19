"""Regression tests for v2.15 distance-prior variant diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from distance_prior_variants import diagnose_variants  # noqa: E402


def test_parity_optional_distance_prior_reconnects_lobes():
    result = diagnose_variants(
        ROOT / "experiments/results/v2.13/phases_8d_1200.json",
        samples=31,
    )
    variants = result["variants"]

    assert variants["default"]["all_connected_by_parity_zero_detour"] is False
    assert variants["default"]["lobe_to_zero_first_failure_blockers"] == {
        "swampland_distance_conjecture": 4,
    }
    assert variants["no_distance_prior"]["all_connected_by_parity_zero_detour"] is True
    assert variants["parity_optional_distance_prior"]["all_connected_by_parity_zero_detour"] is True


def test_distance_prior_variant_records_direct_residual_failures():
    result = diagnose_variants(
        ROOT / "experiments/results/v2.13/phases_8d_1200.json",
        samples=31,
    )

    failures = result["variants"]["parity_optional_distance_prior"]["direct_pair_failures"]
    assert failures
    assert {failure["first_failure"]["constraint"] for failure in failures} == {
        "t_hooft_anomaly_matching",
    }
