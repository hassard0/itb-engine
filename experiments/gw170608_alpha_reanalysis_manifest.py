"""Public GW170608 alpha-bar reanalysis manifest for v2.104."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.explicit_tower_basis import _json_default


VERSION = "v2.104"
REQUIRED_MANIFEST_FIELDS = (
    "label",
    "event",
    "route",
    "public_inputs",
    "waveform_model",
    "likelihood_engine",
    "sampler_config",
    "systematics_plan",
    "output_contract",
    "adapter_target",
    "validation_plan",
    "synthetic_fixture",
)
ROUTE = "gw170608_source_native_alpha_bar_reanalysis"
VALID_READY_STATUSES = {"ready", "defined_ready", "closed", "bounded"}
REQUIRED_PUBLIC_INPUTS = (
    "gwosc_gwtc1_strain",
    "o2_bbh_pe_gr_validation_posterior",
    "liu_yunes_source_paper",
)
REQUIRED_OUTPUTS = (
    "alpha_bar_samples_or_likelihood",
    "alpha_bar_covariance",
    "alpha_bar_marginal_intervals",
    "systematics_budget",
    "v2_102_source_native_adapter_packet",
)
REQUIRED_SYSTEMATICS = (
    "waveform_systematics",
    "detector_calibration",
    "prior_sensitivity",
    "eft_truncation",
    "sampler_convergence",
    "public_data_reproducibility",
)


def _missing(value: Any) -> bool:
    return value in (None, "", [], {})


def _status_value(value: Any) -> str:
    if isinstance(value, dict):
        status = value.get("status")
        return str(status) if status is not None else ""
    return str(value) if value is not None else ""


def _ready(value: Any) -> bool:
    return _status_value(value) in VALID_READY_STATUSES


def _input_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    inputs = manifest.get("public_inputs")
    if not isinstance(inputs, dict):
        return {
            "present": [],
            "missing": list(REQUIRED_PUBLIC_INPUTS),
            "ready": False,
        }
    present = []
    missing = []
    not_ready = []
    for key in REQUIRED_PUBLIC_INPUTS:
        row = inputs.get(key)
        if not isinstance(row, dict):
            missing.append(key)
            continue
        present.append(key)
        if not _ready(row):
            not_ready.append(key)
    return {
        "present": present,
        "missing": missing,
        "not_ready": not_ready,
        "ready": not missing and not not_ready,
    }


def _systematics_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    plan = manifest.get("systematics_plan")
    if not isinstance(plan, dict):
        return {
            "missing": list(REQUIRED_SYSTEMATICS),
            "not_closed": list(REQUIRED_SYSTEMATICS),
            "closed": False,
        }
    components = plan.get("components")
    if not isinstance(components, dict):
        components = {}
    missing = [
        component
        for component in REQUIRED_SYSTEMATICS
        if component not in components
    ]
    not_closed = [
        component
        for component in REQUIRED_SYSTEMATICS
        if component in components and not _ready(components[component])
    ]
    return {
        "status": _status_value(plan),
        "missing": missing,
        "not_closed": not_closed,
        "closed": not missing and not not_closed and _ready(plan),
    }


def _output_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    contract = manifest.get("output_contract")
    if not isinstance(contract, dict):
        return {
            "present": [],
            "missing": list(REQUIRED_OUTPUTS),
            "ready": False,
        }
    outputs = contract.get("outputs")
    if not isinstance(outputs, dict):
        outputs = {}
    present = []
    missing = []
    not_ready = []
    for key in REQUIRED_OUTPUTS:
        row = outputs.get(key)
        if not isinstance(row, dict):
            missing.append(key)
            continue
        present.append(key)
        if not _ready(row):
            not_ready.append(key)
    return {
        "status": _status_value(contract),
        "present": present,
        "missing": missing,
        "not_ready": not_ready,
        "ready": not missing and not not_ready and _ready(contract),
    }


def evaluate_gw170608_alpha_reanalysis_manifest(
    manifest: dict[str, Any],
) -> dict[str, Any]:
    missing_fields = [
        field for field in REQUIRED_MANIFEST_FIELDS if _missing(manifest.get(field))
    ]
    blockers: set[str] = set()
    if missing_fields:
        blockers.add("missing_required_fields")
    if manifest.get("event") != "GW170608":
        blockers.add("event_not_gw170608")
    if manifest.get("route") != ROUTE:
        blockers.add("route_not_alpha_bar_reanalysis")

    inputs = _input_summary(manifest)
    if not inputs["ready"]:
        blockers.add("public_inputs_not_ready")

    waveform = manifest.get("waveform_model")
    if not isinstance(waveform, dict) or not _ready(waveform):
        blockers.add("waveform_model_not_ready")
    elif "alpha_bar_1" not in waveform.get("parameters", []):
        blockers.add("waveform_missing_alpha_bar_parameters")
    elif "alpha_bar_2" not in waveform.get("parameters", []):
        blockers.add("waveform_missing_alpha_bar_parameters")

    likelihood = manifest.get("likelihood_engine")
    if not isinstance(likelihood, dict) or not _ready(likelihood):
        blockers.add("likelihood_engine_not_ready")

    sampler = manifest.get("sampler_config")
    if not isinstance(sampler, dict) or not _ready(sampler):
        blockers.add("sampler_config_not_ready")

    systematics = _systematics_summary(manifest)
    if not systematics["closed"]:
        blockers.add("systematics_plan_not_closed")

    outputs = _output_summary(manifest)
    if not outputs["ready"]:
        blockers.add("output_contract_not_ready")

    adapter_target = manifest.get("adapter_target")
    if adapter_target != "v2.102_gw_cubic_source_native_adapter":
        blockers.add("adapter_target_not_v2_102")

    validation = manifest.get("validation_plan")
    if not isinstance(validation, dict) or not _ready(validation):
        blockers.add("validation_plan_not_ready")

    synthetic_fixture = bool(manifest.get("synthetic_fixture"))
    claim_blockers = set(blockers)
    if synthetic_fixture:
        claim_blockers.add("synthetic_fixture_not_real_reanalysis")
    claim_blockers.add("g8_joint_component_missing")

    ready = not blockers
    return {
        "label": manifest.get("label", "unnamed_alpha_reanalysis_manifest"),
        "event": manifest.get("event"),
        "route": manifest.get("route"),
        "synthetic_fixture": synthetic_fixture,
        "missing_fields": missing_fields,
        "input_summary": inputs,
        "systematics_summary": systematics,
        "output_summary": outputs,
        "manifest_ready": ready,
        "claim_ready": ready and not synthetic_fixture,
        "manifest_blockers": sorted(blockers),
        "claim_blockers": sorted(claim_blockers),
        "status": (
            "gw170608_alpha_reanalysis_claim_ready"
            if ready and not synthetic_fixture
            else "gw170608_alpha_reanalysis_rejected_or_nonpromoting"
        ),
    }


def synthetic_ready_reanalysis_manifest() -> dict[str, Any]:
    return {
        "label": "synthetic_ready_alpha_reanalysis_manifest",
        "event": "GW170608",
        "route": ROUTE,
        "public_inputs": {
            "gwosc_gwtc1_strain": {
                "status": "ready",
                "source_url": "https://gwosc.org/GWTC-1/",
            },
            "o2_bbh_pe_gr_validation_posterior": {
                "status": "ready",
                "source_url": "https://github.com/gwastro/o2-bbh-pe",
            },
            "liu_yunes_source_paper": {
                "status": "ready",
                "source_url": "https://arxiv.org/abs/2407.08929",
            },
        },
        "waveform_model": {
            "status": "ready",
            "family": "cubic_parity_preserving_higher_curvature_eft",
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
            "amplitude_corrections": True,
            "phase_corrections": True,
        },
        "likelihood_engine": {
            "status": "ready",
            "kind": "source_native_alpha_bar_likelihood",
        },
        "sampler_config": {
            "status": "ready",
            "kind": "nested_or_mcmc",
            "outputs": ["samples", "evidence", "covariance"],
        },
        "systematics_plan": {
            "status": "closed",
            "components": {
                component: "closed" for component in REQUIRED_SYSTEMATICS
            },
        },
        "output_contract": {
            "status": "ready",
            "outputs": {
                key: {"status": "ready"} for key in REQUIRED_OUTPUTS
            },
        },
        "adapter_target": "v2.102_gw_cubic_source_native_adapter",
        "validation_plan": {
            "status": "ready",
            "checks": [
                "recover_gr_o2_posteriors",
                "reproduce_paper_alpha_intervals",
                "export_v2_102_packet",
            ],
        },
        "synthetic_fixture": True,
    }


def current_public_reanalysis_manifest() -> dict[str, Any]:
    return {
        "label": "current_public_alpha_reanalysis_manifest",
        "event": "GW170608",
        "route": ROUTE,
        "public_inputs": {
            "gwosc_gwtc1_strain": {
                "status": "ready",
                "source_url": "https://gwosc.org/GWTC-1/",
                "role": "strain_and_event_metadata",
            },
            "o2_bbh_pe_gr_validation_posterior": {
                "status": "ready",
                "source_url": "https://github.com/gwastro/o2-bbh-pe",
                "path": "posteriors/GW170608/gw170608_posteriors_thinned.hdf",
                "role": "GR posterior validation target",
            },
            "liu_yunes_source_paper": {
                "status": "ready",
                "source_url": "https://arxiv.org/abs/2407.08929",
                "role": "target alpha intervals and waveform description",
            },
        },
        "waveform_model": {
            "status": "missing_implementation",
            "family": "cubic_parity_preserving_higher_curvature_eft",
            "parameters": ["alpha_bar_1", "alpha_bar_2"],
            "amplitude_corrections": "required",
            "phase_corrections": "required",
            "work_item": "implement_minimal_alpha_waveform_likelihood_stub",
        },
        "likelihood_engine": {
            "status": "missing",
            "kind": "source_native_alpha_bar_likelihood",
            "work_item": "connect_public_strain_to_alpha_waveform_likelihood",
        },
        "sampler_config": {
            "status": "missing",
            "kind": "nested_or_mcmc",
            "work_item": "define_priors_sampler_and_convergence_export",
        },
        "systematics_plan": {
            "status": "not_closed",
            "components": {
                "waveform_systematics": "missing",
                "detector_calibration": "bounded_by_public_release_needed",
                "prior_sensitivity": "missing",
                "eft_truncation": "missing",
                "sampler_convergence": "missing",
                "public_data_reproducibility": "defined_not_run",
            },
        },
        "output_contract": {
            "status": "defined_not_ready",
            "outputs": {
                "alpha_bar_samples_or_likelihood": {"status": "missing"},
                "alpha_bar_covariance": {"status": "missing"},
                "alpha_bar_marginal_intervals": {"status": "missing"},
                "systematics_budget": {"status": "missing"},
                "v2_102_source_native_adapter_packet": {"status": "missing"},
            },
        },
        "adapter_target": "v2.102_gw_cubic_source_native_adapter",
        "validation_plan": {
            "status": "defined_not_run",
            "checks": [
                "recover_public_o2_gr_posterior_scale",
                "compare_alpha_intervals_to_arxiv_2407_08929",
                "run_v2_102_adapter_gate",
            ],
        },
        "synthetic_fixture": False,
    }


def _action_queue(evaluation: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    actions = []
    if "waveform_model_not_ready" in evaluation["manifest_blockers"]:
        actions.append(manifest["waveform_model"]["work_item"])
    if "likelihood_engine_not_ready" in evaluation["manifest_blockers"]:
        actions.append(manifest["likelihood_engine"]["work_item"])
    if "sampler_config_not_ready" in evaluation["manifest_blockers"]:
        actions.append(manifest["sampler_config"]["work_item"])
    if "systematics_plan_not_closed" in evaluation["manifest_blockers"]:
        actions.append("close_alpha_reanalysis_systematics_plan")
    if "output_contract_not_ready" in evaluation["manifest_blockers"]:
        actions.append("produce_v2_102_source_native_adapter_packet")
    return actions


def diagnose_gw170608_alpha_reanalysis_manifest() -> dict[str, Any]:
    manifests = [
        synthetic_ready_reanalysis_manifest(),
        current_public_reanalysis_manifest(),
    ]
    evaluations = [
        evaluate_gw170608_alpha_reanalysis_manifest(manifest)
        for manifest in manifests
    ]
    ready = [row["label"] for row in evaluations if row["manifest_ready"]]
    claim_ready = [row["label"] for row in evaluations if row["claim_ready"]]
    current_evaluation = evaluations[1]
    current_manifest = manifests[1]

    return {
        "version": VERSION,
        "basis": [
            "v2.103_gw_alpha_interval_surrogate",
            "GWOSC_GWTC_1_public_strain",
            "gwastro_o2_bbh_pe_public_gr_validation_posteriors",
            "arXiv_2407.08929_alpha_bar_target",
        ],
        "route": ROUTE,
        "required_manifest_fields": list(REQUIRED_MANIFEST_FIELDS),
        "sample_manifest_count": len(evaluations),
        "manifest_ready_sample_manifests": ready,
        "claim_ready_sample_manifests": claim_ready,
        "claimable_discriminator_now": bool(claim_ready),
        "evaluations": evaluations,
        "current_public_manifest_action_queue": _action_queue(
            current_evaluation,
            current_manifest,
        ),
        "route_status": (
            "public_alpha_reanalysis_manifest_defined_"
            "waveform_likelihood_missing"
        ),
        "selected_next_build_action": (
            "implement_minimal_alpha_waveform_likelihood_stub"
        ),
        "best_next_artifact": (
            "A minimal alpha_bar likelihood stub with the correct parameter "
            "surface and output contract, wired to public-input placeholders "
            "before attempting an expensive full GW170608 run."
        ),
        "interpretation": (
            "The route is now an implementation manifest. Public inputs are "
            "identified, but the cubic waveform likelihood, sampler, "
            "systematics closure, and output packet still need to be built "
            "before the v2.102 source-native gate can accept a real packet."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default=(
            "experiments/results/v2.104/"
            "gw170608_alpha_reanalysis_manifest.json"
        ),
    )
    args = parser.parse_args()

    result = diagnose_gw170608_alpha_reanalysis_manifest()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, indent=2, default=_json_default),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(result, indent=2, default=_json_default))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
