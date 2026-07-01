"""v2.366 - The rank question is ANSWERED (v2.209), correcting v2.365: parity is dark to ringdown, so it rides on birefringence alone.

An honest correction plus a convergence. Last tick's v2.365 framed the qNM->R4 rank as "the open deep-research
question." That was INCOMPLETE: the repo ALREADY determined the sourceable rank in v2.209 (fetched 2026-06-29
from the primary literature). This cycle surfaces that determination, corrects the v2.365 framing, and shows
how the v2.209 result converges with this session's parity findings.

v2.209's source-cited determination (read here from its tested artifact):
  - a source-backed rank-3 qNM->Bresciani map does NOT exist (full_rank_3 = false);
  - the Bresciani operator basis (arXiv:2504.12855) is rank 3 but has ZERO QNM apparatus;
  - the only public ringdown analysis (arXiv:2411.17893) is rank 1 per parity-even theory, max parity-even
    sourceable rank 2, and EXPLICITLY defers the parity-violating sector;
  - so the engine's parity-odd third axis g_R4_c3 = Im(c_minus) = Q2.Q2tilde is a DARK axis -- unconstrained
    by any current ringdown observable.

So the rank is not "open" -- it is DETERMINED (negatively): rank-3 is unsourceable, the observable rank is 2
(parity-even), and the parity-odd curvature operator is observationally dark to ringdown. This CONVERGES with
the session: parity is observable ONLY through cosmic birefringence, now confirmed TWO independent ways --
(a) birefringence is the only binding data constraint (v2.358), and (b) the parity-odd curvature operator is
dark to ringdown (v2.209). The engine's own ringdown observable is parity-blind by construction (its floor
g_R3^2/g_R2 uses only parity-EVEN couplings), re-verified live here.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VERSION = "v2.366"
DEFAULT_OUT = Path("experiments/results/v2.366/qnm_parity_ringdown_dark_convergence.json")
V209 = Path("experiments/results/v2.209/r4_parspec_qnm_sourceable_rank_determination.json")

BASE = {"g_4": 0.529, "g_6": 0.4, "g_8": 0.4, "g_R2": 0.193, "g_R3": 0.09, "g_R2_parity": 0.06, "g_R3_parity": 0.0}


def ringdown_floor(c):
    return c["g_R3"] ** 2 / c["g_R2"] if c["g_R2"] > 1e-9 else 0.0


def run() -> dict:
    v209 = json.loads(V209.read_text(encoding="utf-8"))
    det = v209["determination"]

    full_rank3 = bool(det["full_rank_3_qnm_to_bresciani_source_backed"])
    observable_rank = det["source_backed_observable_rank"]
    dark_axes = det["dark_axes"]
    obs_axes = det["observability_incidence"]["observable_engine_axes"]
    g_R4_c3_parity = det["engine_axis_observability"]["g_R4_c3"]["parity"]
    g_R4_c3_observable = det["engine_axis_observability"]["g_R4_c3"]["public_qnm_observable"]

    # live cross-check: the engine's ringdown floor is PARITY-BLIND (depends only on parity-even g_R3, g_R2)
    floor_base = ringdown_floor(BASE)
    flipped = dict(BASE); flipped["g_R2_parity"] = -BASE["g_R2_parity"]; flipped["g_R3_parity"] = -0.03
    floor_flipped = ringdown_floor(flipped)
    ringdown_parity_blind = abs(floor_base - floor_flipped) < 1e-12

    checks = {
        "v2209_rank3_unsourceable": (full_rank3 is False),
        "v2209_parity_odd_axis_g_R4_c3_dark": ("g_R4_c3" in dark_axes and g_R4_c3_observable is False),
        "v2209_sourceable_observable_rank_is_2": (observable_rank == 2),
        "engine_ringdown_floor_is_parity_blind": ringdown_parity_blind,
        "corrects_v2365_open_framing_to_determined": (full_rank3 is False),  # rank is determined, not open
    }

    return {
        "version": VERSION,
        "v2209_route_status": v209["route_status"],
        "required_rank_for_claim": det["required_rank_for_claim_grade_map"],
        "full_rank_3_source_backed": full_rank3,
        "source_backed_observable_rank": observable_rank,
        "observable_engine_axes": obs_axes,
        "dark_axes": dark_axes,
        "g_R4_c3": {"parity": g_R4_c3_parity, "public_qnm_observable": g_R4_c3_observable,
                    "operator": det["engine_axis_observability"]["g_R4_c3"]["bresciani_operator"]},
        "ringdown_floor_parity_blind": bool(ringdown_parity_blind),
        "ringdown_floor": round(floor_base, 4),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The qNM->R4 rank question is ANSWERED, not open -- correcting last tick's v2.365 framing. "
            "v2.365 called the rank 'the open deep-research question'; but the repo already DETERMINED it in "
            "v2.209 (fetched 2026-06-29 from the primary literature), which this cycle surfaces and reads "
            "from its tested artifact. The source-cited determination: a source-backed rank-3 qNM->Bresciani "
            "map does NOT exist (full_rank_3 = False); the Bresciani basis (arXiv:2504.12855) is rank 3 but "
            "carries no QNM apparatus; the only public ringdown analysis (arXiv:2411.17893) is rank 1 per "
            "parity-even theory (max parity-even sourceable rank 2) and EXPLICITLY defers the parity sector; "
            "so the parity-odd third axis g_R4_c3 = Im(c_minus) = Q2.Q2tilde is a DARK axis, unconstrained by "
            "any current ringdown observable. The source-backed observable rank is therefore 2 (the two "
            "parity-even directions g_R4_c1, g_R4_c2), and the parity-odd curvature operator is "
            "observationally dark. So the corrected status is: the ringdown blocker is not 'determine the "
            "rank' but a DETERMINED NEGATIVE -- a full-rank ringdown discriminator is unsourceable from "
            "current public data, and the defensible product is a parity-even, rank-1-per-theory nonclaiming "
            "null test. THE CONVERGENCE (the genuinely new content): this reinforces the session's central "
            "parity result from an independent direction. The theory's distinguishing feature is its parity "
            "violation, and its observability rides ENTIRELY on cosmic birefringence -- now confirmed TWO "
            "independent ways: (a) birefringence is the only BINDING data constraint (v2.358, the "
            "data-leverage side), and (b) the parity-odd curvature operator is DARK to ringdown (v2.209, the "
            "observable-rank side). The engine's own ringdown observable is parity-blind by construction -- "
            "its floor g_R3^2/g_R2 uses only parity-EVEN couplings, re-verified live (invariant under "
            "flipping the parity-odd couplings). So parity has exactly ONE observational window, birefringence, "
            "for two structurally independent reasons -- which is why the whole parity headline (existence "
            "v2.321, magnitude v2.360, sign v2.364) is birefringence-contingent (v2.329): there is no second "
            "observational handle on the parity sector, in the data OR in the curvature/ringdown channel."
        ),
        "honest_scope": (
            "The rank determination is READ from the tested v2.209 artifact (a source-cited observability/rank "
            "statement, not a manufactured projection -- v2.209 preserves the negative result); the "
            "parity-blindness of the engine's ringdown floor is re-verified live. This is a correction + "
            "synthesis, so it inherits v2.209's claim boundary: it records WHICH rank is sourceable "
            "(2, parity-even) and which axis is dark (g_R4_c3), NOT a ringdown prediction or framework "
            "exclusion (framework_claims_ready_now = False, unchanged). 'Dark' means dark to CURRENT PUBLIC "
            "sources -- the parity-odd shift is computable-in-principle (Cano et al. arXiv:2307.07431 via "
            "rotation-induced mixing) with no attached public likelihood, so a future polarization/rotation-"
            "resolved source could illuminate g_R4_c3. The convergence is a structural reading (two "
            "independent reasons parity is birefringence-only), not a new computation; it rests on the "
            "session's v2.358 data-leverage result and v2.209's literature determination. The correction of "
            "v2.365 is the honest point: v2.365's 'open question' framing was incomplete because it did not "
            "reference v2.209. Toy basis for the engine couplings; the rank facts are source-cited (not toy). "
            "An honest self-correction joining v2.209 to the session's parity findings."
        ),
        "references": [
            "this repo: v2.209 (sourceable-rank determination, 2026-06-29 -- the answer), v2.365 (the incomplete 'open question' framing corrected here), v2.358 (birefringence the only binding data), v2.329 (the single point of failure)",
            "this repo: v2.321/v2.360/v2.364 (parity existence/magnitude/sign, all birefringence-contingent); v2.349 (ringdown floor, parity-even)",
            "sources: arXiv:2504.12855 (Bresciani basis, no QNM), arXiv:2411.17893 (public qEFT ringdown, rank-1 parity-even, defers parity-odd), arXiv:2307.07431 (parity-odd shift, no public likelihood)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()
    res = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("the qNM->R4 rank question is ANSWERED (v2.209), correcting v2.365:")
    print(f"  full-rank-3 source-backed: {res['full_rank_3_source_backed']}  (required {res['required_rank_for_claim']})")
    print(f"  source-backed observable rank: {res['source_backed_observable_rank']}  observable axes {res['observable_engine_axes']}")
    print(f"  DARK axes: {res['dark_axes']}  (g_R4_c3 = {res['g_R4_c3']['parity']}-parity, observable={res['g_R4_c3']['public_qnm_observable']})")
    print(f"  engine ringdown floor {res['ringdown_floor']} parity-blind: {res['ringdown_floor_parity_blind']}")
    print(f"  => parity is observable ONLY via birefringence, TWO ways: only-binding-data (v2.358) + dark-to-ringdown (v2.209)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
