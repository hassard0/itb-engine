"""Tests for the v2.209 qNM-to-Bresciani sourceable-rank determination."""

import json
from pathlib import Path

from experiments.r4_parspec_qnm_to_bresciani_gate import ENGINE_AXES, QNM_AXES
from experiments.r4_parspec_qnm_sourceable_rank_determination import (
    DETERMINATION_ID,
    ENGINE_AXIS_OBSERVABILITY,
    LITERATURE_PROVISIONS,
    determine_sourceable_rank,
    diagnose_qnm_sourceable_rank,
    main,
    source_backed_observability_incidence,
)


def test_axis_invariants_and_parity_partition():
    assert ENGINE_AXES == ("g_R4_c1", "g_R4_c2", "g_R4_c3")
    assert tuple(ENGINE_AXIS_OBSERVABILITY) == ENGINE_AXES
    # exactly two parity-even and one parity-odd engine axis
    parities = [ENGINE_AXIS_OBSERVABILITY[a]["parity"] for a in ENGINE_AXES]
    assert parities.count("even") == 2
    assert parities.count("odd") == 1
    # the parity-odd axis is the (CP-violating) third engine axis
    assert ENGINE_AXIS_OBSERVABILITY["g_R4_c3"]["parity"] == "odd"


def test_parity_odd_axis_is_dark_and_others_observable():
    assert ENGINE_AXIS_OBSERVABILITY["g_R4_c1"]["public_qnm_observable"] is True
    assert ENGINE_AXIS_OBSERVABILITY["g_R4_c2"]["public_qnm_observable"] is True
    assert ENGINE_AXIS_OBSERVABILITY["g_R4_c3"]["public_qnm_observable"] is False


def test_incidence_rank_is_two_over_observable_axes():
    incidence = source_backed_observability_incidence()
    assert incidence["observable_engine_axes"] == ["g_R4_c1", "g_R4_c2"]
    assert incidence["incidence_columns"] == list(ENGINE_AXES)
    assert incidence["incidence_rank"] == 2


def test_determination_is_a_source_backed_negative():
    det = determine_sourceable_rank()
    assert det["determination_id"] == DETERMINATION_ID
    assert det["required_rank_for_claim_grade_map"] == 3
    assert det["operator_basis_rank_source_backed"] == 3
    assert det["operator_basis_has_qnm_map"] is False
    assert det["public_analysis_realized_rank_per_theory"] == 1
    assert det["max_parity_even_sourceable_rank"] == 2
    assert det["source_backed_observable_rank"] == 2
    assert det["dark_axes"] == ["g_R4_c3"]
    assert det["full_rank_3_qnm_to_bresciani_source_backed"] is False


def test_literature_provisions_cite_primary_sources():
    urls = {p["url"] for p in LITERATURE_PROVISIONS.values()}
    assert "https://arxiv.org/abs/2504.12855" in urls          # Bresciani operator basis
    assert "https://arxiv.org/abs/2411.17893" in urls          # public qEFT ringdown analysis
    # the operator-basis source is explicitly recorded as carrying no QNM map
    assert (
        "any map from QNM deformation axes to c1/c2/c3"
        in LITERATURE_PROVISIONS["bresciani_operator_basis"]["does_not_provide"]
    )


def test_claim_gate_stays_closed():
    diag = diagnose_qnm_sourceable_rank()
    assert diag["framework_claims_ready_now"] is False
    assert diag["qnm_axes"] == list(QNM_AXES)
    assert "qnm_deformation_to_bresciani_engine_r4_map_missing" in diag["does_not_resolve"]
    assert "sourceable_rank_determined_from_public_sources" in diag["resolves"]
    assert diag["route_status"] == (
        "qnm_to_bresciani_full_rank_unsourceable_parity_odd_axis_dark"
    )


def test_main_writes_json(tmp_path: Path):
    out = tmp_path / "rank.json"
    import sys
    argv = sys.argv
    sys.argv = ["prog", "--out", str(out)]
    try:
        main()
    finally:
        sys.argv = argv
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["determination"]["dark_axes"] == ["g_R4_c3"]
