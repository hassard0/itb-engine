"""Tests for the neutron-star tidal deformability (v2.291)."""

from experiments.qnm_ns_tidal_deformability import lambda_tidal, love_k2, run, tov_love


def test_all_checks_pass():
    res = run()
    assert res["all_checks_pass"] is True
    for k, v in res["consistency_checks"].items():
        assert v is True, k


def test_love_number_in_neutron_star_range():
    res = run()
    for s in res["sequence"]:
        assert 0.02 < s["k2"] < 0.20


def test_lambda_falls_steeply_with_mass():
    res = run()
    lambdas = [s["Lambda"] for s in res["sequence"]]
    for i in range(len(lambdas) - 1):
        assert lambdas[i + 1] < lambdas[i] + 1e-6      # heavier/more compact -> less deformable


def test_stiff_polytrope_disfavored_by_gw170817():
    # the v2.290 stiff EOS makes the 1.4 Msun star too large -> Lambda above the 800 bound
    res = run()
    assert res["reference_1p4_msun"]["Lambda"] > 800
    assert res["reference_1p4_msun"]["R_km"] > 13.5    # larger than GW170817 allows


def test_lambda_definition():
    # Lambda = (2/3) k2 C^-5
    assert abs(lambda_tidal(0.1, 0.15) - (2 / 3) * 0.1 / 0.15**5) < 1e-9


def test_tov_love_central_value():
    # y starts at 2 and the star has a finite surface
    M, R, yR = tov_love(0.8e-3)
    assert R > 0 and M > 0
    assert 0.0 < yR < 2.0      # y decreases from 2 toward the surface for a normal star


def test_honest_scope_flags_tension_and_toy():
    res = run()
    sc = res["honest_scope"].lower()
    assert "toy" in sc
    assert "representative" in sc
    fnd = res["finding"].lower()
    assert "tension" in fnd and "disfavored" in fnd
