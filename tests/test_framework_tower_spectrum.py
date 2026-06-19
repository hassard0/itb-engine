"""Tests for the optional framework tower-spectrum contract."""

from itb.frameworks.base import Framework
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory
from itb.tower import TowerSpectrum


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
