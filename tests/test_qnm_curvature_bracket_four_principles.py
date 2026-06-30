"""Tests for the four-principle curvature bracket (v2.302)."""

import math

from experiments.qnm_curvature_bracket_four_principles import binding_upper, bounds, run


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_three_regime_partition():
    # g_4 >> g_6 -> entanglement; balanced -> unitarity; g_6 >> g_4 -> null energy
    assert binding_upper(1.0, 0.1)[0] == "entanglement(monogamy)"
    assert binding_upper(1.0, 1.0)[0] == "unitarity(positivity)"
    assert binding_upper(1.0, 8.0)[0] == "null_energy(QFC)"


def test_regime_boundaries():
    # boundaries at x = g_6/g_4 ~ 0.146 (entanglement<->unitarity) and x = 4 (unitarity<->null energy)
    assert binding_upper(1.0, 0.13)[0] == "entanglement(monogamy)"
    assert binding_upper(1.0, 0.16)[0] == "unitarity(positivity)"
    assert binding_upper(1.0, 3.9)[0] == "unitarity(positivity)"
    assert binding_upper(1.0, 4.2)[0] == "null_energy(QFC)"


def test_bounds_forms():
    b = bounds(0.5, 0.4)
    assert abs(b["qfc_upper"] - 0.5 / 0.5) < 1e-9            # g_4/alpha
    assert abs(b["monogamy_upper"] - 3 * 0.5 * 0.4 / 0.9) < 1e-9   # harmonic
    assert abs(b["positivity_upper"] - math.sqrt(0.2)) < 1e-9      # geometric
    assert b["gsl_lower"] == -0.5                            # thermodynamic floor


def test_frameworks_in_unitarity_regime_and_bracketed():
    res = run()
    for r in res["framework_brackets"]:
        assert r["binding_upper_principle"] == "unitarity(positivity)"
        assert 0.146 < r["x_g6_over_g4"] < 4.0
        assert r["g_R2_inside_bracket"] is True


def test_honest_scope_flags_qualitative_robust():
    res = run()
    sc = res["honest_scope"].lower()
    assert "qualitative structure is robust" in sc
    assert "three-regime partition exists for any o(1) prefactors" in sc
    assert "leading curvature coupling" in sc
