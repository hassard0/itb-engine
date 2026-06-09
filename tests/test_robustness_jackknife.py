"""Tests for the robustness jackknife (v2.07)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import robustness_jackknife as rj


def _synthetic_result():
    return {"V0": 30, "n": 100000, "eff_dim": 3.3,
            "gate": {"swampland_distance_conjecture": 200, "generalized_anomaly_inflow": 90,
                     "complexity_cutoff": 30, "hofman_maldacena_wedge": 12},
            "fw": {"string_tree_eft": True, "asymptotic_safety": True,
                   "lqg_induced": False, "horava_lifshitz": False}}


def test_predicates_return_bools():
    pr = rj.predicates(_synthetic_result())
    assert all(isinstance(v, bool) for v in pr.values())
    assert len(pr) >= 8


def test_known_robust_predicates_hold_on_canonical_like():
    pr = rj.predicates(_synthetic_result())
    assert pr["island_nonempty"] is True
    assert pr["lqg_induced_infeasible"] is True
    assert pr["distance_conj_top_gatekeeper"] is True
    assert pr["island_eff_dim_in_[2.5,4.5]"] is True


def test_structural_scores_are_unit():
    assert all(v == 1.0 for v in rj.STRUCTURAL.values())
    # plausible ranges define the prefactor perturbations
    assert set(rj.PLAUSIBLE_RANGES) == set(rj.CANONICAL)
