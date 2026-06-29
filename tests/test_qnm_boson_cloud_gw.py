"""Tests for the boson-cloud continuous-GW signature (v2.245)."""

from experiments.qnm_boson_cloud_gw import detector_band, f_gw_hz, run


def test_annihilation_frequency():
    # f = mu c^2/(pi hbar): a 1e-12 eV boson radiates at a few hundred Hz (LIGO band)
    f = f_gw_hz(1e-12)
    assert 100 < f < 1000


def test_band_assignment():
    assert "LIGO" in detector_band(300.0)
    assert "LISA" in detector_band(1e-2)
    assert "PTA" in detector_band(1e-6)


def test_window_maps_to_detector_bands():
    res = run()
    bands = {r["band"] for r in res["cloud_gw_bands"]}
    # stellar -> LIGO, supermassive -> LISA, largest -> PTA
    assert any("LIGO" in b for b in bands)
    assert any("LISA" in b for b in bands)
    assert any("PTA" in b for b in bands)


def test_frequency_scales_with_mass():
    # heavier black holes (lighter bosons) -> lower GW frequency
    res = run()
    stellar = next(r for r in res["cloud_gw_bands"] if "stellar" in r["system"])
    m87 = next(r for r in res["cloud_gw_bands"] if "M87" in r["system"])
    assert max(m87["f_gw_hz"]) < min(stellar["f_gw_hz"])


def test_honest_scope_frequency_not_strain():
    res = run()
    sc = res["honest_scope"].lower()
    assert "strain" in sc and "not computed here" in sc
    assert "monochromatic" in sc
    assert "g_R4_c3" in res["honest_scope"]
