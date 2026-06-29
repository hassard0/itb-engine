"""Source-backed determination of the achievable qNM-to-Bresciani sensitivity rank.

v2.200 defined the gate: a claim-grade qNM-to-Bresciani bridge needs a source-backed
3x4 sensitivity matrix of rank 3 over the engine axes (g_R4_c1, g_R4_c2, g_R4_c3).
v2.205/v2.207 recorded that the public sources do not currently supply that operator
edge, and left open *which rank is achievable from public sources*.

This artifact answers that open question by reading what each public source actually
provides (fetched 2026-06-29), and determines the honest maximum sourceable rank. It does
NOT manufacture sensitivity numbers; it records an observability/rank determination with
citations, and the claim gate stays closed.

Determination (source-backed):

- The Bresciani operator basis (arXiv:2504.12855) is a pure amplitude/positivity paper.
  It defines exactly three real quartic operators via c_plus = c1 + c2 (real, parity-even)
  and c_minus = c1 - c2 + i*c3 (complex), with operators (Q2)^2, (Q2tilde)^2, Q2.Q2tilde.
  It contains NO black-hole / QNM / ringdown apparatus and NO map to QNM deformations.
  => operator-basis rank 3 is source-backed, but the qNM->operator edge is absent here.

- The only public ringdown ANALYSIS with real GW150914/GW200129 likelihoods over EFT
  operators (the qEFT route, arXiv:2411.17893) reduces each higher-derivative theory to a
  single combined length scale ell ("we can always set lambda = +/- 1"), i.e. rank 1 per
  theory family, and analyses PARITY-EVEN operators only. It explicitly defers the
  parity-violating sector: "Our analysis can readily be extended to EFTs with
  parity-violating terms. We leave such extension to future study."
  => the engine's third axis g_R4_c3 = Im(K_minus) (the parity-odd Q2.Q2tilde operator)
     is NOT constrained by any public ringdown analysis: it is a DARK axis.

- The QNM-shift computation source (Cano-Fransen-Hertog-Maenaut, arXiv:2307.07431, and the
  earlier quartic-QNM paper arXiv:2110.11378) computes parity-even and parity-odd shifts;
  the parity-odd / CP-violating shift enters the QNM spectrum only through rotation-induced
  parity mixing (birefringence) and has no attached public likelihood. So even in
  principle it is computable-but-unmeasured, not source-backed-observable.

Conclusion: a source-backed rank-3 qNM-to-Bresciani map does NOT exist. The maximum
source-backed observable rank over the engine axes is at most 2 (the two parity-even
quartic directions, separately bounded as single-ell theories => realized public rank 1
per theory), and the parity-odd third axis is dark. This preserves the negative result
the roadmap requires rather than manufacturing a projection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, ".")
from experiments.bresciani_r4_axis_dictionary import BRESCIANI_SOURCE_URL
from experiments.explicit_tower_basis import _json_default
from experiments.gw_alpha_prior_reweight_sweep import canonicalize_json_floats
from experiments.r4_parspec_qnm_bresciani_source_route_graph import (
    CANO_QUARTIC_QNM_URL,
    PYRING_EFT_RINGDOWN_ANALYSIS_URL,
)
from experiments.r4_parspec_pyring_source_probe import ROTATING_QNM_SOURCE_URL
from experiments.r4_parspec_qnm_to_bresciani_gate import (
    ENGINE_AXES,
    QNM_AXES,
    matrix_rank,
)

VERSION = "v2.209"
DEFAULT_OUT = Path(
    "experiments/results/v2.209/r4_parspec_qnm_sourceable_rank_determination.json"
)
DETERMINATION_ID = "qnm_to_bresciani_sourceable_rank_determination_v1"

# Per-engine-axis source-backed observability in public ringdown analyses.
# parity follows the Bresciani basis: c1,c2 enter c_plus (real, parity-even);
# c3 enters Im(c_minus) (parity-odd / CP-violating, the Q2.Q2tilde operator).
ENGINE_AXIS_OBSERVABILITY: dict[str, dict[str, Any]] = {
    "g_R4_c1": {
        "parity": "even",
        "bresciani_operator": "real part of c_plus / c_minus (parity-even quartic)",
        "public_qnm_observable": True,
        "citing_source": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
        "note": (
            "Parity-even quartic direction; constrained by the public qEFT ringdown "
            "analysis as a single-ell theory (rank 1)."
        ),
    },
    "g_R4_c2": {
        "parity": "even",
        "bresciani_operator": "Re(c_minus) (parity-even quartic)",
        "public_qnm_observable": True,
        "citing_source": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
        "note": (
            "Second parity-even quartic direction; the qEFT analysis bounds distinct "
            "parity-even quartic theories separately (each rank 1), so two parity-even "
            "directions are sourceable in principle but are not jointly covariance-fit "
            "in the public analysis."
        ),
    },
    "g_R4_c3": {
        "parity": "odd",
        "bresciani_operator": "Im(c_minus) = Q2.Q2tilde (parity-odd / CP-violating)",
        "public_qnm_observable": False,
        "citing_source": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
        "note": (
            "Parity-odd / CP-violating quartic operator. Explicitly deferred by the "
            "public qEFT ringdown analysis ('we leave such extension to future study'). "
            "Enters QNMs only via rotation-induced parity mixing (Cano et al.) with no "
            "attached public likelihood. DARK axis: not source-backed-observable."
        ),
    },
}

LITERATURE_PROVISIONS: dict[str, dict[str, Any]] = {
    "bresciani_operator_basis": {
        "url": BRESCIANI_SOURCE_URL,
        "role": "operator_basis_only",
        "provides": [
            "three real quartic operators (Q2)^2, (Q2tilde)^2, Q2.Q2tilde",
            "c_plus = c1 + c2 in R (parity-even); c_minus = c1 - c2 + i*c3 in C",
            "partial-wave unitarity / positivity constraints on the Wilson coefficients",
        ],
        "does_not_provide": [
            "any black-hole / QNM / ringdown apparatus",
            "any map from QNM deformation axes to c1/c2/c3",
        ],
        "evidence": (
            "Fetched 2026-06-29: pure scattering-amplitude/positivity paper; the s=2 "
            "sector has exactly three real coefficients c1,c2,c3; zero QNM content."
        ),
    },
    "qeft_public_ringdown_analysis": {
        "url": PYRING_EFT_RINGDOWN_ANALYSIS_URL,
        "role": "public_ringdown_likelihood_analysis",
        "provides": [
            "real GW150914/GW200129 ringdown likelihoods over EFT operators",
            "single combined length scale ell per theory family (rank 1)",
            "parity-even cubic and two parity-even quartic theories",
            "the ell <~ 35 km combined bound",
        ],
        "does_not_provide": [
            "a joint multi-operator covariance over the parity-even quartic axes",
            "any constraint on the parity-odd / CP-violating quartic operator",
        ],
        "evidence": (
            "Fetched 2026-06-29: 'we can always set lambda = +/- 1' (rank 1 per theory); "
            "'we leave such [parity-violating] extension to future study'."
        ),
    },
    "cano_qnm_shift_computation": {
        "url": ROTATING_QNM_SOURCE_URL,
        "secondary_url": CANO_QUARTIC_QNM_URL,
        "role": "qnm_shift_theory_no_public_likelihood",
        "provides": [
            "computed QNM frequency/damping shifts for higher-derivative operators",
            "odd- and even-parity master equations; parity-violating coupling under spin",
        ],
        "does_not_provide": [
            "a public likelihood/posterior over the operator coefficients",
            "a source-backed field-redefinition map into the Bresciani c-basis",
        ],
        "evidence": (
            "Fetched 2026-06-29: parity-violating corrections couple even at linear order "
            "for rotating black holes; rotation enhances shifts ~order of magnitude vs "
            "static; computable in principle, unmeasured (no public likelihood)."
        ),
    },
}


def source_backed_observability_incidence() -> dict[str, Any]:
    """Identity incidence over the source-backed-observable engine axes only.

    This is an observability/rank statement (which axes have a source-backed public QNM
    constraint), NOT a fabricated sensitivity matrix. The parity-odd axis has no row.
    """
    observable_axes = [
        axis for axis in ENGINE_AXES if ENGINE_AXIS_OBSERVABILITY[axis]["public_qnm_observable"]
    ]
    incidence = []
    for axis in observable_axes:
        incidence.append([1.0 if other == axis else 0.0 for other in ENGINE_AXES])
    return {
        "observable_engine_axes": observable_axes,
        "incidence_rows_are_observable_axes": True,
        "incidence_columns": list(ENGINE_AXES),
        "incidence": incidence,
        "incidence_rank": matrix_rank(incidence),
    }


def determine_sourceable_rank() -> dict[str, Any]:
    incidence = source_backed_observability_incidence()
    dark_axes = [
        axis for axis in ENGINE_AXES
        if not ENGINE_AXIS_OBSERVABILITY[axis]["public_qnm_observable"]
    ]
    max_parity_even_sourceable_rank = sum(
        1 for axis in ENGINE_AXES
        if ENGINE_AXIS_OBSERVABILITY[axis]["parity"] == "even"
        and ENGINE_AXIS_OBSERVABILITY[axis]["public_qnm_observable"]
    )
    required_rank = len(ENGINE_AXES)
    return canonicalize_json_floats({
        "determination_id": DETERMINATION_ID,
        "required_rank_for_claim_grade_map": required_rank,
        "operator_basis_rank_source_backed": 3,
        "operator_basis_has_qnm_map": False,
        "public_analysis_realized_rank_per_theory": 1,
        "max_parity_even_sourceable_rank": max_parity_even_sourceable_rank,
        "source_backed_observable_rank": incidence["incidence_rank"],
        "dark_axes": dark_axes,
        "full_rank_3_qnm_to_bresciani_source_backed": (
            incidence["incidence_rank"] >= required_rank
        ),
        "observability_incidence": incidence,
        "engine_axis_observability": ENGINE_AXIS_OBSERVABILITY,
        "verdict": (
            "A source-backed rank-3 qNM-to-Bresciani map does NOT exist. The Bresciani "
            "operator basis is rank 3 but carries no QNM map; the only public ringdown "
            "analysis is rank 1 per parity-even theory (max parity-even sourceable rank 2 "
            "across the two separately-bounded quartic theories); and the parity-odd third "
            "axis g_R4_c3 = Im(K_minus) is explicitly deferred, hence dark. The negative "
            "result is preserved; no projection is manufactured."
        ),
    })


def diagnose_qnm_sourceable_rank(*_: Any) -> dict[str, Any]:
    determination = determine_sourceable_rank()
    return canonicalize_json_floats({
        "version": VERSION,
        "basis": [
            "v2.175_bresciani_r4_axis_dictionary",
            "v2.200_qnm_to_bresciani_gate",
            "v2.205_pyring_to_bresciani_orientation_no_map",
            "v2.207_qnm_bresciani_source_route_graph",
        ],
        "engine_axes": list(ENGINE_AXES),
        "qnm_axes": list(QNM_AXES),
        "literature_provisions": LITERATURE_PROVISIONS,
        "determination": determination,
        "resolves": [
            "sourceable_rank_determined_from_public_sources",
            "parity_odd_third_axis_identified_as_dark",
        ],
        "does_not_resolve": [
            "qnm_deformation_to_bresciani_engine_r4_map_missing",
            "public_parspec_qeft_likelihood_or_posterior_samples_missing",
            "claim_grade_systematics_export_missing",
            "external_adversarial_review_missing",
        ],
        "framework_claims_ready_now": False,
        "route_status": (
            "qnm_to_bresciani_full_rank_unsourceable_parity_odd_axis_dark"
        ),
        "correct_claim": (
            "Public sources cap the qNM-to-Bresciani sensitivity at the parity-even "
            "quartic subspace (rank 1 per theory in the published analysis). The "
            "parity-odd engine axis g_R4_c3 is unconstrained by current ringdown "
            "observables, so a full-rank R4 ringdown discriminator is not source-backed."
        ),
        "incorrect_claim": (
            "The repo can invert ringdown data into all three Bresciani R4 axes, or "
            "constrains the CP-violating quartic operator from current ringdown."
        ),
        "selected_next_build_action": (
            "either execute the v2.208 pyRing rank-1 parity-even runtime likelihood as a "
            "nonclaiming null test, or seek a polarization/rotation-resolved source that "
            "constrains the parity-odd axis; do not manufacture the dark direction"
        ),
    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    result = diagnose_qnm_sourceable_rank()
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
