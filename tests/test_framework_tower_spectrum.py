"""Tests for the optional framework tower-spectrum contract."""

from itb.frameworks.base import Framework
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory
import pytest

from itb.tower import TowerSpectrum, kk_radius_tower_spectrum, sdc_tower_spectrum


class SyntheticTowerFramework(Framework):
    name = "synthetic_tower"
    citation = "unit-test fixture"

    def encode(self) -> Theory:
        return Theory(coefficients={"g_4": 0.0}, name=self.name, source=self.citation)

    def tower_spectrum(self) -> TowerSpectrum:
        return TowerSpectrum(
            tower_family="synthetic_fixture",
            phi_tower_mean=0.25,
            phi_tower_sigma=0.02,
            normalization="unit-test normalization",
            source="unit-test fixture",
            tower_mass_gap=0.8,
        )


def test_framework_tower_spectrum_defaults_to_none():
    assert PureGR().tower_spectrum() is None


def test_framework_tower_spectrum_contract_serializes():
    spectrum = SyntheticTowerFramework().tower_spectrum()

    assert spectrum.to_dict()["tower_family"] == "synthetic_fixture"
    assert spectrum.to_dict()["phi_tower_mean"] == 0.25
    assert spectrum.to_dict()["tower_mass_gap"] == 0.8


def test_sdc_tower_spectrum_converts_distance_to_phi_and_mass_gap():
    spectrum = sdc_tower_spectrum(
        tower_family="sdc_fixture",
        delta_moduli_mean=1.2,
        delta_moduli_sigma=0.1,
        lambda_sdc=0.5,
        normalization="unit-test normalization",
        source="unit-test source",
    )

    assert spectrum.phi_tower_mean == 0.6
    assert spectrum.phi_tower_sigma == 0.05
    assert spectrum.tower_mass_gap == pytest.approx(0.5488116361)
    assert spectrum.metadata["delta_moduli_mean"] == 1.2
    assert spectrum.metadata["lambda_sdc"] == 0.5


def test_sdc_tower_spectrum_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="lambda_sdc"):
        sdc_tower_spectrum(
            tower_family="bad",
            delta_moduli_mean=1.0,
            delta_moduli_sigma=0.1,
            lambda_sdc=0.0,
            normalization="unit-test normalization",
            source="unit-test source",
        )


def test_kk_radius_tower_spectrum_converts_radius_ratio_to_phi_and_mass_gap():
    spectrum = kk_radius_tower_spectrum(
        tower_family="kk_fixture",
        radius_ratio_mean=2.0,
        log_radius_sigma=0.05,
        normalization="unit-test radius normalization",
        source="unit-test source",
    )

    assert spectrum.phi_tower_mean == pytest.approx(0.69314718056)
    assert spectrum.phi_tower_sigma == 0.05
    assert spectrum.tower_mass_gap == 0.5
    assert spectrum.metadata["radius_ratio_mean"] == 2.0


def test_kk_radius_tower_spectrum_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="radius_ratio_mean"):
        kk_radius_tower_spectrum(
            tower_family="bad",
            radius_ratio_mean=0.0,
            log_radius_sigma=0.0,
            normalization="unit-test radius normalization",
            source="unit-test source",
        )
