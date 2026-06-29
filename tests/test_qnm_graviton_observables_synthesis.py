"""Tests for the graviton-observables synthesis capstone (v2.271)."""

import math

import numpy as np

from experiments.qnm_graviton_observables_synthesis import run
from experiments.qnm_gw_polarizations import GR_MODES, polarization_basis
from experiments.qnm_gw_birefringence import circular_basis


def test_all_checks_pass():
    res = run()
    assert res["all_pass"] is True
    assert res["checks_passed"] == res["checks_total"] == 5
    for c in res["consistency_checks"]:
        assert c["pass"] is True, c["name"]


def test_circular_modes_built_from_gr_tensor_modes():
    # v2.269 circular basis == helicity-2 combination of v2.268 GR tensor modes
    e = polarization_basis()
    eR_expected = (e[GR_MODES[0]] + 1j * e[GR_MODES[1]]) / math.sqrt(2)
    eR, _ = circular_basis()
    assert np.max(np.abs(eR - eR_expected)) < 1e-12


def test_five_observables_map_to_five_properties():
    res = run()
    props = {t["property"] for t in res["graviton_observables"]}
    assert len(res["graviton_observables"]) == 5
    assert len(props) == 5   # all distinct
    for key in ("MASS", "SPIN / helicity", "PARITY"):
        assert key in props


def test_propagation_channel_map_three_filled_one_empty():
    res = run()
    m = res["propagation_channel_map"]
    assert "mass dispersion" in m["chromatic_parity_even"]
    assert "birefringence" in m["chromatic_parity_odd"]
    assert "distance ratio" in m["achromatic_parity_even"]
    assert "none" in m["achromatic_parity_odd"].lower()


def test_all_gr_null_limits_hold():
    res = run()
    for k, v in res["gr_null_limits"].items():
        assert v is True, k


def test_honest_scope_is_synthesis_not_new_bound():
    res = run()
    sc = res["honest_scope"].lower()
    assert "no new bound" in sc
    assert "synthesis" in sc or "cross-verification" in sc
    assert "not an engine constraint refit" in sc
