"""Tests for GW polarization content (v2.268)."""

import numpy as np

from experiments.qnm_gw_polarizations import (
    GR_MODES,
    detector_tensor,
    polarization_basis,
    response,
    run,
)


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_six_modes_are_complete_basis():
    e = polarization_basis()
    assert len(e) == 6
    flat = np.array([m.flatten() for m in e.values()])
    assert int(np.linalg.matrix_rank(flat)) == 6   # span the symmetric 3x3 strain


def test_gr_modes_are_the_transverse_traceless_ones():
    res = run()
    for n in GR_MODES:
        assert res["mode_properties"][n]["traceless"] is True
        assert res["mode_properties"][n]["transverse"] is True
    # every non-GR mode breaks transverse-traceless
    for n, p in res["mode_properties"].items():
        if n not in GR_MODES:
            assert not (p["traceless"] and p["transverse"])


def test_detector_response_is_traceless():
    D = detector_tensor(np.array([1, 0, 0.]), np.array([0, 1, 0.]))
    assert abs(np.trace(D)) < 1e-12
    res = run()
    assert res["consistency_checks"]["detector_response_is_traceless"] is True


def test_single_detector_overhead_responds_only_to_plus():
    e = polarization_basis()
    D = detector_tensor(np.array([1, 0, 0.]), np.array([0, 1, 0.]))
    assert abs(response(D, e["plus"]) - 1.0) < 1e-12
    for n in ("cross", "breathing", "longitudinal", "vector_x", "vector_y"):
        assert abs(response(D, e[n])) < 1e-12


def test_scalar_modes_degenerate_and_network_rank_five():
    # the breathing and longitudinal traceless parts are antiparallel -> interferometers see rank 5
    res = run()
    assert res["consistency_checks"]["scalar_modes_degenerate_for_interferometers"] is True
    assert res["network_response_rank"] == 5
    assert res["max_separable_polarizations"] == 5
    assert res["gr_submatrix_rank"] == 2


def test_honest_scope_flags_idealization_and_ptas():
    res = run()
    sc = res["honest_scope"].lower()
    assert "idealized" in sc or "ideal detectors" in sc
    assert "pulsar-timing" in sc or "interferometers" in sc
    assert "not an engine constraint refit" in sc
