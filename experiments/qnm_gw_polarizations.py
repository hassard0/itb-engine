"""v2.268 - Gravitational-wave polarization content: GR's two modes vs the six of a general theory.

A fresh falsifiable-gravity probe (continuing the v2.266/v2.267 GW thread). A massless spin-2 metric
theory can carry up to SIX gravitational-wave polarizations -- the Eardley-Lee-Will E(2) classification
-- but general relativity predicts exactly TWO (the transverse-traceless 'plus' and 'cross'). For a
wave propagating along z the six modes are symmetric 3x3 strain patterns:

    plus        diag( 1, -1, 0)          tensor   (GR)   -- transverse, traceless
    cross       off-diag xy              tensor   (GR)   -- transverse, traceless
    breathing   diag( 1,  1, 0)          scalar          -- transverse, isotropic (trace)
    longitudinal diag( 0,  0, 1)         scalar          -- along propagation
    vector-x    off-diag xz              vector          -- mixed transverse/longitudinal shear
    vector-y    off-diag yz              vector

These six are a COMPLETE basis for the symmetric 3x3 strain (6 independent components), so 'how many
polarizations' is literally 'how much of that basis the theory excites'. GR excites a 2-dimensional
(tensor) subspace; scalar-tensor adds a breathing mode; the most general theory fills all six.
Detecting any non-tensor mode falsifies GR's polarization content -- and a detector NETWORK can
separate at most (rank of its response matrix) polarizations, so resolving all six needs >= 6
independent detectors, while GR's two need only two.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")

VERSION = "v2.268"
DEFAULT_OUT = Path("experiments/results/v2.268/qnm_gw_polarizations.json")


def polarization_basis() -> dict:
    """The six GW polarization strain tensors for propagation along z (symmetric 3x3)."""
    e = {}
    e["plus"] = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], float)
    e["cross"] = np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], float)
    e["breathing"] = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 0]], float)
    e["longitudinal"] = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 1]], float)
    e["vector_x"] = np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], float)
    e["vector_y"] = np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], float)
    return e


GR_MODES = ("plus", "cross")
CLASSES = {"plus": "tensor", "cross": "tensor", "vector_x": "vector",
           "vector_y": "vector", "breathing": "scalar", "longitudinal": "scalar"}


def detector_tensor(arm1: np.ndarray, arm2: np.ndarray) -> np.ndarray:
    """Michelson detector response tensor D = 1/2 (a (x) a - b (x) b)."""
    a = arm1 / np.linalg.norm(arm1)
    b = arm2 / np.linalg.norm(arm2)
    return 0.5 * (np.outer(a, a) - np.outer(b, b))


def response(D: np.ndarray, e: np.ndarray) -> float:
    """Antenna response F = D : e (Frobenius contraction)."""
    return float(np.sum(D * e))


def _rot(axis: str, ang: float) -> np.ndarray:
    c, s = np.cos(ang), np.sin(ang)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def run() -> dict:
    e = polarization_basis()
    names = list(e.keys())

    # 1. the six modes are a complete, independent basis for the symmetric 3x3 strain
    flat = np.array([e[n].flatten() for n in names])
    basis_rank = int(np.linalg.matrix_rank(flat))

    # 2. classify each mode (transverse?, traceless?) and confirm GR = the 2 transverse-traceless ones
    mode_props = {}
    for n in names:
        m = e[n]
        traceless = bool(abs(np.trace(m)) < 1e-12)
        transverse = bool(abs(m[2, 0]) + abs(m[2, 1]) + abs(m[2, 2]) < 1e-12)  # no z (propagation) components
        mode_props[n] = {"class": CLASSES[n], "traceless": traceless, "transverse": transverse,
                         "is_GR": n in GR_MODES}
    gr_are_tt = bool(all(mode_props[n]["traceless"] and mode_props[n]["transverse"] for n in GR_MODES))
    nongr_break_tt = bool(all(not (mode_props[n]["traceless"] and mode_props[n]["transverse"])
                              for n in names if n not in GR_MODES))

    # 3. single-detector degeneracy: arms along x,y, source overhead (wave along z) -> only 'plus' responds
    D0 = detector_tensor(np.array([1, 0, 0.]), np.array([0, 1, 0.]))
    single = {n: response(D0, e[n]) for n in names}
    single_degenerate = bool(abs(single["plus"] - 1.0) < 1e-12
                             and all(abs(single[n]) < 1e-12 for n in names if n != "plus"))

    # 4. network rank: stack varied detector orientations; rank of the (detectors x 6) response matrix
    #    is how many polarizations are separable. Use a deterministic set of rotated detectors.
    orientations = [("z", 0.3), ("z", 0.9), ("x", 0.5), ("y", 0.7), ("x", 1.2),
                    ("y", 1.9), ("z", 2.4), ("x", 0.2)]
    rows = []
    for axis, ang in orientations:
        R = _rot(axis, ang)
        D = detector_tensor(R @ np.array([1, 0, 0.]), R @ np.array([0, 1, 0.]))
        rows.append([response(D, e[n]) for n in names])
    M = np.array(rows)                                  # (8 detectors) x (6 polarizations)
    full_rank = int(np.linalg.matrix_rank(M))
    gr_cols = M[:, [names.index("plus"), names.index("cross")]]
    gr_rank = int(np.linalg.matrix_rank(gr_cols))
    # how many detectors to first reach the maximum (5) interferometer-separable rank
    detectors_for_full = next((k for k in range(1, len(rows) + 1)
                               if np.linalg.matrix_rank(M[:k]) == 5), None)

    # the Michelson response tensor is TRACELESS, so it sees only the traceless part of each mode;
    # the two scalar modes' traceless parts are proportional -> degenerate for any interferometer.
    def traceless(m):
        return m - np.trace(m) / 3.0 * np.eye(3)
    tl_b, tl_l = traceless(e["breathing"]), traceless(e["longitudinal"])
    # antiparallel: tl_l = -tl_b  ->  the cross product (flattened) vanishes
    scalar_degenerate = bool(np.linalg.norm(tl_b / np.linalg.norm(tl_b)
                                            + tl_l / np.linalg.norm(tl_l)) < 1e-12)
    detector_traceless = bool(abs(np.trace(detector_tensor(np.array([1, 0, 0.]),
                                                           np.array([0, 1, 0.])))) < 1e-12)

    checks = {
        "six_modes_complete_basis": basis_rank == 6,
        "gr_modes_are_transverse_traceless": gr_are_tt,
        "nongr_modes_break_tt": nongr_break_tt,
        "single_detector_overhead_degenerate": single_degenerate,
        "interferometer_network_rank_five": full_rank == 5,
        "scalar_modes_degenerate_for_interferometers": scalar_degenerate,
        "detector_response_is_traceless": detector_traceless,
        "gr_needs_only_two": gr_rank == 2,
    }

    return {
        "version": VERSION,
        "method": ("six E(2) polarization strain tensors (sym 3x3) for z-propagation; antenna "
                   "response F = D:e with D = 1/2(a(x)a - b(x)b); basis rank, TT classification, "
                   "single-detector degeneracy, and network response-matrix rank"),
        "mode_properties": mode_props,
        "polarization_classes": {"tensor (GR)": ["plus", "cross"],
                                 "vector": ["vector_x", "vector_y"],
                                 "scalar": ["breathing", "longitudinal"]},
        "basis_rank": basis_rank,
        "single_detector_overhead_response": single,
        "network_response_rank": full_rank,
        "gr_submatrix_rank": gr_rank,
        "detectors_to_resolve_separable": detectors_for_full,
        "max_separable_polarizations": full_rank,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "A general massless metric theory carries six GW polarizations -- the Eardley-Lee-Will "
            "E(2) set -- and they form a COMPLETE basis for the symmetric 3x3 strain (rank 6, "
            "verified), split into two tensor, two vector and two scalar modes. General relativity "
            "excites only the two TENSOR modes (plus, cross), which are exactly the transverse and "
            "traceless ones (verified), while every non-GR mode breaks transverse-tracelessness. So "
            "detecting ANY non-tensor polarization falsifies GR's polarization content. But there is "
            "a sharp limit on what interferometers can measure: the Michelson response tensor "
            "D = 1/2(a(x)a - b(x)b) is TRACELESS (verified), so it sees only the traceless part of "
            "each mode -- and the two SCALAR modes (breathing diag(1,1,0), longitudinal diag(0,0,1)) "
            "have PROPORTIONAL traceless parts (antiparallel, verified), so no interferometer network "
            "can ever separate them. The (detectors x 6) response matrix therefore saturates at rank "
            "FIVE, not six (verified): an interferometer array can resolve at most five polarization "
            "combinations, the two scalars collapsing to one measurable scalar. (A single detector "
            "with the source overhead is even more degenerate -- it responds ONLY to plus.) GR's "
            "two-mode content is fully captured by just two detectors (gr submatrix rank 2). This is "
            "why current 3-detector events (GW170814) test tensor-vs-vector-vs-scalar HYPOTHESES -- "
            "and favour pure tensor -- rather than measuring all amplitudes; a concrete, falsifiable, "
            "near-term test of gravity beyond GR, with the scalar-mode degeneracy a fundamental "
            "interferometer limitation (Chatziioannou-Yunes-Cornish)."
        ),
        "honest_scope": (
            "The six strain tensors and their TT classification are exact (a linear-algebra fact "
            "about the symmetric 3x3 perturbation for z-propagation), and the single-detector "
            "degeneracy, the traceless-response scalar degeneracy, and the rank-5 network result are "
            "exact for the idealized Michelson response D = 1/2(a(x)a - b(x)b). The rank result uses "
            "a deterministic set of rotated ideal detectors; a REAL network's separability also "
            "depends on sky position, noise and the sources' amplitudes (the actual LIGO/Virgo "
            "polarization tests are Bayesian model comparisons, not a literal rank count). The "
            "scalar-mode degeneracy is specific to INTERFEROMETERS (pulsar-timing arrays, sensitive "
            "to the trace differently, can in principle break it). The E(2) class of a SPECIFIC "
            "alternative theory (Brans-Dicke etc.) is not computed here -- this is the "
            "model-independent polarization-content framework. A falsifiable-gravity / "
            "GW-phenomenology result, not an engine constraint refit."
        ),
        "references": [
            "Eardley, Lee, Lightman, Wagoner, Will, 'Gravitational-wave observations as a tool for testing relativistic gravity', PRL 30 (1973) 884; PRD 8 (1973) 3308",
            "Will, 'The confrontation between general relativity and experiment', Living Rev. Rel. 17 (2014) 4",
            "Abbott et al. (LIGO/Virgo), 'GW170814: A three-detector observation ... tests of polarization', PRL 119 (2017) 141101",
            "this repo: v2.266 (graviton mass), v2.267 (GW memory / infrared triangle)",
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
    print("GW polarizations (E(2) classification): GR = 2 tensor, general theory = 6")
    for n, p_ in res["mode_properties"].items():
        tag = "GR" if p_["is_GR"] else "  "
        print(f"  [{tag}] {n:13s} class={p_['class']:7s} traceless={p_['traceless']!s:5s} "
              f"transverse={p_['transverse']!s:5s}")
    print(f"  basis rank = {res['basis_rank']} (complete sym 3x3)")
    print(f"  single detector, overhead source -> only 'plus' responds: "
          f"{res['consistency_checks']['single_detector_overhead_degenerate']}")
    print(f"  interferometer network rank = {res['network_response_rank']} (scalars degenerate -> max 5, not 6); "
          f"GR needs {res['gr_submatrix_rank']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
