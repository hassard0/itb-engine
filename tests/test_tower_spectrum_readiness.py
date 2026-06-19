"""Regression tests for v2.24 tower-spectrum readiness."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from tower_spectrum_readiness import diagnose_tower_spectrum_readiness  # noqa: E402
from itb.tower import TowerSpectrum  # noqa: E402


def test_default_frameworks_have_no_actionable_tower_spectra():
    result = diagnose_tower_spectrum_readiness()

    assert result["n_native_prediction_frameworks"] == 0
    assert result["n_actionable_prediction_frameworks"] == 0
    assert result["claimable_framework_exclusions"] == []
    assert "phi_tower_mean" in result["required_actionable_fields"]
    assert result["frameworks"]["string_tree_eft"]["framework_tower_verdict"] == (
        "missing_actionable_tower_spectrum"
    )


def test_mock_predictive_adapter_can_drive_tower_verdicts():
    result = diagnose_tower_spectrum_readiness(
        spectra={
            "string_tree_eft": TowerSpectrum(
                tower_family="synthetic_fixture",
                phi_tower_mean=0.82,
                phi_tower_sigma=0.01,
                normalization="unit-test normalization",
                source="unit-test fixture",
            ),
            "asymptotic_safety": {
                "tower_family": "synthetic_fixture",
                "phi_tower_mean": 0.25,
                "phi_tower_sigma": 0.02,
                "normalization": "unit-test normalization",
                "source": "unit-test fixture",
            },
        }
    )

    assert result["frameworks"]["string_tree_eft"]["framework_tower_verdict"] == (
        "tower_excluded_by_predictive_spectrum"
    )
    assert result["frameworks"]["string_tree_eft"]["claimable_exclusion"] is True
    assert result["frameworks"]["asymptotic_safety"]["framework_tower_verdict"] == (
        "tower_allowed_by_predictive_spectrum"
    )
    assert result["claimable_framework_exclusions"] == ["string_tree_eft"]
    assert "not a quantum-gravity solution" in result["literature_guardrail"]["claim"]
