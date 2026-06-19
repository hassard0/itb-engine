"""Tests for Callister variable-evolution posterior parser guards."""

import numpy as np

from itb.gw_parity import (
    CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS,
    GW_PARITY_PROJECTION_BLOCKERS,
    parse_callister_variable_evolution_hdf_datasets,
)


def _variable_evolution_fixture():
    frequencies = np.array([20.0, 25.0, 30.0, 35.0])
    samples = 5
    return {
        "frequencies": frequencies,
        "Omg_I_model": np.ones((frequencies.size, samples)) * 1.0e-9,
        "Omg_V_model": np.linspace(
            -1.0e-10,
            1.0e-10,
            frequencies.size * samples,
        ).reshape(frequencies.size, samples),
        "kappa_Dc": np.linspace(-0.2, 0.2, samples),
        "kappa_z": np.linspace(-0.4, 0.4, samples),
        "R0": np.linspace(10.0, 20.0, samples),
        "alpha": np.linspace(-1.0, 3.0, samples),
        "beta": np.linspace(2.0, 6.0, samples),
        "zp": np.linspace(1.0, 2.0, samples),
        "zMax": np.linspace(10.0, 15.0, samples),
    }


def test_variable_evolution_parser_summarizes_grouped_release_schema():
    result = parse_callister_variable_evolution_hdf_datasets(
        {"result": _variable_evolution_fixture()},
        source_file="birefringence_variable_evolution.hdf",
    )

    assert result["schema"] == "callister_variable_evolution_hdf_v1"
    assert result["required_keys"] == list(CALLISTER_VARIABLE_EVOLUTION_HDF_KEYS)
    assert result["parser_ready"] is True
    assert result["parser_blockers"] == []
    assert result["sample_count"] == 5
    assert result["spectra_summary"]["frequencies"]["count"] == 4
    assert result["spectra_summary"]["Omg_I_model"]["shape"] == [4, 5]
    assert result["parameter_summaries"]["kappa_Dc"]["min"] == -0.2
    assert result["projection_blockers"] == list(GW_PARITY_PROJECTION_BLOCKERS)
    assert result["engine_projection_ready"] is False
    assert result["claimable_discriminator_now"] is False


def test_variable_evolution_parser_blocks_missing_keys():
    result = parse_callister_variable_evolution_hdf_datasets(
        {"result": {"frequencies": np.array([20.0, 30.0])}}
    )

    assert result["parser_ready"] is False
    assert result["parser_blockers"] == [
        "missing_callister_variable_evolution_hdf_keys"
    ]
    assert "kappa_Dc" in result["missing_keys"]


def test_variable_evolution_parser_blocks_spectrum_shape_mismatch():
    fixture = _variable_evolution_fixture()
    fixture["Omg_I_model"] = np.ones((3, 5))

    result = parse_callister_variable_evolution_hdf_datasets({"result": fixture})

    assert result["parser_ready"] is False
    assert "Omg_I_model_shape_mismatch" in result["parser_blockers"]


def test_variable_evolution_parser_blocks_nonmonotonic_frequency_grid():
    fixture = _variable_evolution_fixture()
    fixture["frequencies"] = np.array([20.0, 25.0, 25.0, 30.0])

    result = parse_callister_variable_evolution_hdf_datasets({"result": fixture})

    assert result["parser_ready"] is False
    assert "frequencies_not_strictly_increasing" in result["parser_blockers"]
