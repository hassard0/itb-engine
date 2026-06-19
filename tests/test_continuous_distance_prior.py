"""Regression tests for v2.16 continuous distance-prior diagnostics."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from continuous_distance_prior import diagnose_continuous_priors  # noqa: E402


PHASES = ROOT / "experiments/results/v2.13/phases_8d_1200.json"


def _row_by_value(rows: list[dict], value: float) -> dict:
    return next(row for row in rows if row["value"] == value)


def test_continuous_prior_sweeps_reconnect_when_small_parity_coefficients_are_smoothed():
    result = diagnose_continuous_priors(
        PHASES,
        samples=31,
        thresholds=[1e-6, 0.02, 0.03, 0.05],
        floors=[0.005, 0.02, 0.03, 0.05],
    )
    variants = result["variants"]

    assert variants["default"]["all_connected_by_parity_zero_detour"] is False
    assert variants["default"]["lobe_to_zero_first_failure_blockers"] == {
        "swampland_distance_conjecture": 4,
    }
    assert variants["no_distance_prior"]["all_connected_by_parity_zero_detour"] is True

    hard_rows = variants["hard_threshold_sweep"]["rows"]
    smooth_rows = variants["smooth_floor_sweep"]["rows"]
    sector_rows = variants["sector_norm_threshold_sweep"]["rows"]

    assert _row_by_value(hard_rows, 1e-6)["all_connected_by_parity_zero_detour"] is False
    assert _row_by_value(hard_rows, 0.05)["all_connected_by_parity_zero_detour"] is True
    assert _row_by_value(smooth_rows, 0.005)["all_connected_by_parity_zero_detour"] is False
    assert _row_by_value(smooth_rows, 0.05)["all_connected_by_parity_zero_detour"] is True
    assert _row_by_value(sector_rows, 1e-6)["all_connected_by_parity_zero_detour"] is False
    assert _row_by_value(sector_rows, 0.05)["all_connected_by_parity_zero_detour"] is True


def test_continuous_prior_result_is_labeled_as_diagnostic_not_canonical_sdc():
    result = diagnose_continuous_priors(
        PHASES,
        samples=11,
        thresholds=[1e-6, 0.05],
        floors=[0.005, 0.05],
    )

    assert result["basis"] == [
        "g_4",
        "g_6",
        "g_8",
        "g_R2",
        "g_R3",
        "g_C",
        "g_R2_parity",
        "g_R3_parity",
    ]
    assert "diagnostics" in result["literature_guardrail"]["claim"]
    assert "moduli/tower model" in result["literature_guardrail"]["claim"]
    assert result["variants"]["soft_active_log_sweep"]["first_connecting_value"] is not None
