"""Tests for the v2.104 GW170608 alpha reanalysis manifest."""

from experiments.gw170608_alpha_reanalysis_manifest import (
    current_public_reanalysis_manifest,
    diagnose_gw170608_alpha_reanalysis_manifest,
    evaluate_gw170608_alpha_reanalysis_manifest,
    synthetic_ready_reanalysis_manifest,
)


def test_synthetic_manifest_is_ready_but_nonclaiming():
    result = evaluate_gw170608_alpha_reanalysis_manifest(
        synthetic_ready_reanalysis_manifest()
    )

    assert result["manifest_ready"] is True
    assert result["claim_ready"] is False
    assert result["manifest_blockers"] == []
    assert "synthetic_fixture_not_real_reanalysis" in result["claim_blockers"]
    assert "g8_joint_component_missing" in result["claim_blockers"]


def test_current_public_manifest_has_ready_inputs_but_missing_implementation():
    result = evaluate_gw170608_alpha_reanalysis_manifest(
        current_public_reanalysis_manifest()
    )

    assert result["manifest_ready"] is False
    assert result["input_summary"]["ready"] is True
    assert "waveform_model_not_ready" in result["manifest_blockers"]
    assert "likelihood_engine_not_ready" in result["manifest_blockers"]
    assert "sampler_config_not_ready" in result["manifest_blockers"]


def test_current_public_manifest_requires_systematics_and_outputs():
    result = evaluate_gw170608_alpha_reanalysis_manifest(
        current_public_reanalysis_manifest()
    )

    assert "systematics_plan_not_closed" in result["manifest_blockers"]
    assert "output_contract_not_ready" in result["manifest_blockers"]
    assert "waveform_systematics" in result["systematics_summary"]["not_closed"]
    assert "alpha_bar_covariance" in result["output_summary"]["not_ready"]


def test_diagnosis_selects_minimal_alpha_waveform_stub_next():
    result = diagnose_gw170608_alpha_reanalysis_manifest()

    assert result["version"] == "v2.104"
    assert result["route_status"] == (
        "public_alpha_reanalysis_manifest_defined_waveform_likelihood_missing"
    )
    assert result["selected_next_build_action"] == (
        "implement_minimal_alpha_waveform_likelihood_stub"
    )
    assert result["claimable_discriminator_now"] is False


def test_action_queue_is_concrete_and_ordered():
    result = diagnose_gw170608_alpha_reanalysis_manifest()

    assert result["current_public_manifest_action_queue"][:3] == [
        "implement_minimal_alpha_waveform_likelihood_stub",
        "connect_public_strain_to_alpha_waveform_likelihood",
        "define_priors_sampler_and_convergence_export",
    ]
    assert "produce_v2_102_source_native_adapter_packet" in result[
        "current_public_manifest_action_queue"
    ]


def test_manifest_declares_v2_102_adapter_target_and_public_sources():
    manifest = current_public_reanalysis_manifest()

    assert manifest["adapter_target"] == "v2.102_gw_cubic_source_native_adapter"
    assert manifest["public_inputs"]["gwosc_gwtc1_strain"][
        "source_url"
    ] == "https://gwosc.org/GWTC-1/"
    assert manifest["public_inputs"]["o2_bbh_pe_gr_validation_posterior"][
        "path"
    ] == "posteriors/GW170608/gw170608_posteriors_thinned.hdf"
