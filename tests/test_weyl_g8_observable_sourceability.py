"""Regression tests for v2.51 Weyl/g8 observable sourceability audit."""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from weyl_g8_observable_sourceability import (  # noqa: E402
    diagnose_weyl_g8_observable_sourceability,
)


def test_sourceability_finds_no_claim_ready_route():
    result = diagnose_weyl_g8_observable_sourceability()

    assert result["candidate_count"] == 6
    assert result["claim_ready_routes"] == []
    assert result["claimable_discriminator_now"] is False
    assert result["route_status"] == "sourceability_blocked"
    assert result["claim_blockers"] == [
        "no_external_numeric_measurement_for_g_C_or_g_8",
        "g_C_routes_are_structural_or_holographic_proxies",
        "g_8_high_moment_route_is_still_an_internal_design_probe",
        "no_framework_level_source_backed_cut_to_apply_to_v2_50_frontier",
    ]


def test_sourceability_distinguishes_g_c_theory_from_measurement():
    result = diagnose_weyl_g8_observable_sourceability()
    g_c = result["axis_summary"]["g_C"]

    assert g_c["candidate_routes"] == 3
    assert g_c["source_backed_theory_routes"] == 3
    assert g_c["external_numeric_measurement_routes"] == 0
    assert g_c["claim_ready_routes"] == 0
    assert "holographic_complexity_rate" in g_c["implemented_routes_touching_axis"]


def test_sourceability_keeps_high_moment_as_design_probe():
    result = diagnose_weyl_g8_observable_sourceability()
    rows = {row["route"]: row for row in result["rows"]}
    high_moment = rows["high_scattering_moment_design_probe"]

    assert high_moment["axis"] == "g_8"
    assert high_moment["implemented_target_coefficients"] == ["g_6", "g_8"]
    assert high_moment["source_backed_theory"] is True
    assert high_moment["source_backed_axis_mapping"] is False
    assert high_moment["external_numeric_measurement"] is False
    assert high_moment["claim_ready"] is False


def test_sourceability_flags_core_forward_amplitude_as_g8_blind():
    result = diagnose_weyl_g8_observable_sourceability()
    rows = {row["route"]: row for row in result["rows"]}
    forward = rows["core_scalar_forward_amplitude"]

    assert forward["axis"] == "g_8"
    assert forward["implemented_target_coefficients"] == ["g_4", "g_6"]
    assert forward["status"] == "implemented_core_observable_does_not_touch_axis"
    assert "g_8" not in forward["implemented_target_coefficients"]
