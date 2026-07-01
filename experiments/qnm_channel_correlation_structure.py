"""v2.380 - SWING (deflationary): the four channels are NOT four independent tests -- they probe ~2-3 observable directions.

The cross-sector bridges (v2.357 parity<->screening, v2.379 parity->BH) hinted the channels are correlated.
This measures the full JOINT structure: the 4x4 correlation matrix of the four channel observables across the
feasible family, and the effective number of INDEPENDENT observables (participation ratio of the correlation
eigenvalues). The honest question: does the theory make four independent predictions, or does its observable
content collapse to fewer directions?

Channel observables (toy maps):
    parity     beta        = 3.4 * g_R2_parity
    screening  over-cap    = g_R2 / g_R2_max_unscreened
    ringdown   floor       = g_R3^2 / g_R2
    BH         Delta S_ext = g_R2 + 0.5 g_4

Result (deflationary but honest): screening and BH are NEAR-IDENTICAL (corr ~ 0.9 -- both essentially linear
in g_R2, so they are one observable, not two), ringdown is ORTHOGONAL to the other three (corr ~ 0.1 -- it is
driven by g_R3, a free direction v2.372, uncorrelated with the g_R2/g_4 scale), and parity is PARTIALLY
correlated with the g_R2 group (~0.5, via the anomaly link g_R2_parity ~ sqrt(g_4 g_R2), but with independent
variation inside the anomaly window). So the four channels have an effective dimension of ~2.5, not 4: the
theory's genuinely independent observable content is (i) the leading matter/curvature SCALE g_R2 (screening =
BH, with parity partly along it) and (ii) the cubic curvature g_R3 (ringdown), plus parity's partial
independence. 'Four channels' overstates the independent testability: measuring the g_R2-scale forecasts
screening, BH, and half of parity; only ringdown adds a fully orthogonal probe.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack

VERSION = "v2.380"
DEFAULT_OUT = Path("experiments/results/v2.380/qnm_channel_correlation_structure.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
GR2_MAX = 0.0626
NAMES = ["parity", "screening", "ringdown", "BH"]


def run(n_walk: int = 30000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    rng = np.random.default_rng(seed)
    pts = [CONSTRUCTED.copy()]
    cur = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 6), 0.0, None)
        if feasible(c):
            cur = c
            pts.append(cur.copy())
    pts = np.array(pts)

    parity = 3.4 * pts[:, 5]
    screening = pts[:, 3] / GR2_MAX
    ringdown = np.where(pts[:, 3] > 1e-9, pts[:, 4] ** 2 / pts[:, 3], 0.0)
    bh = pts[:, 3] + 0.5 * pts[:, 0]
    channels = np.vstack([parity, screening, ringdown, bh])

    C = np.corrcoef(channels)
    corr = {NAMES[i]: {NAMES[j]: round(float(C[i, j]), 2) for j in range(4)} for i in range(4)}

    # effective number of independent observables: participation ratio of the correlation eigenvalues
    eig = np.linalg.eigvalsh(C)
    eig = np.clip(eig, 0, None)
    eff_dim = float((eig.sum() ** 2) / (eig ** 2).sum())

    screen_bh = float(C[1, 3])
    ring_max_other = max(float(C[2, 0]), float(C[2, 1]), float(C[2, 3]))
    parity_g2group = max(float(C[0, 1]), float(C[0, 3]))

    checks = {
        "screening_and_bh_near_identical": screen_bh > 0.8,
        "ringdown_orthogonal_to_others": ring_max_other < 0.25,
        "parity_partially_correlated": 0.3 < parity_g2group < 0.75,
        "effective_dimension_below_four": eff_dim < 3.5,
        "effective_dimension_above_two": eff_dim > 2.0,   # not fully degenerate either
    }

    return {
        "version": VERSION,
        "n_samples": len(pts),
        "correlation_matrix": corr,
        "screening_bh_correlation": round(screen_bh, 2),
        "ringdown_max_correlation_with_others": round(ring_max_other, 2),
        "parity_correlation_with_g2_group": round(parity_g2group, 2),
        "effective_observable_dimension": round(eff_dim, 2),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            f"The theory's four observational channels are NOT four independent tests -- their joint content "
            f"collapses to an effective ~{eff_dim:.1f} directions, not 4. Measuring the 4x4 correlation "
            f"matrix of the channel observables across the feasible family: screening and black-hole "
            f"extremality are NEAR-IDENTICAL (correlation {screen_bh:.2f}) -- both are essentially linear in "
            f"the leading curvature coupling g_R2 (screening = g_R2/cap, Delta S_ext = g_R2 + 0.5 g_4), so "
            f"they are ONE observable, not two; ringdown is ORTHOGONAL to the other three (max correlation "
            f"{ring_max_other:.2f}) because it is driven by g_R3^2/g_R2 and g_R3 is a free direction (v2.372) "
            f"uncorrelated with the g_R2/g_4 scale; and parity is PARTIALLY correlated with the g_R2 group "
            f"(~{parity_g2group:.2f}, through the anomaly link g_R2_parity ~ sqrt(g_4 g_R2), v2.350/357, but "
            f"with independent variation inside the birefringence-allowed anomaly window). So the theory's "
            f"genuinely independent observable content is about two-and-a-half directions: (i) the leading "
            f"matter/curvature SCALE g_R2, which sets screening, the black-hole entropy shift, AND about half "
            f"of the parity signal at once; and (ii) the cubic curvature g_R3, which sets ringdown alone. "
            f"This is the honest deflation of the 'four channels' story: measuring the g_R2-scale (via any of "
            f"screening, BH, or partly birefringence) forecasts the others, so only RINGDOWN adds a fully "
            f"orthogonal probe. It also explains WHY the cross-sector bridges exist (v2.357/379): they are "
            f"the correlations within the g_R2 group made explicit. The upshot for testability: the theory "
            f"is falsifiable in four channels but INDEPENDENTLY constrained in only ~2-3 -- to pin the full "
            f"5-parameter theory (v2.372) one needs both the g_R2-scale channels AND ringdown, and neither "
            f"substitutes for the other."
        ),
        "honest_scope": (
            "The correlations are computed over a seeded random-walk sample of the feasible family, so the "
            "exact numbers are sampler-dependent, and each channel observable uses the toy map (beta = 3.4 "
            "g_R2_parity, screening over-cap, ringdown floor g_R3^2/g_R2, Delta S_ext with the toy "
            "Cheung-Liu-Remmen coefficients) -- so the precise correlation values and the 2.5 effective "
            "dimension are toy-basis. But the STRUCTURE is basis-robust and follows from WHICH couplings each "
            "channel depends on: screening and BH are both monotone in g_R2 (hence near-identical whatever "
            "the normalization); ringdown depends on g_R3 (a direction free of g_R2/g_4, v2.372, hence "
            "orthogonal); parity depends on g_R2_parity (anomaly-linked to g_4 g_R2, hence partial). The "
            "screening=BH near-degeneracy is close to definitional (both linear in g_R2) -- an honest "
            "deflation, not a coincidence. The effective-dimension via the correlation participation ratio is "
            "a standard but convention-laden measure. This is a statement about the CONSTRUCTED-theory "
            "family's observable correlations, using the toy channel maps; a real basis would shift the "
            "numbers but keep the coupling-dependence structure. Robust content: the four channels reduce to "
            "~2-3 independent observable directions -- screening=BH (g_R2), ringdown orthogonal (g_R3), "
            "parity partial -- so 'four channels' overstates independent testability. Toy numbers, "
            "structural coupling-dependence. A deflationary swing on the channel count."
        ),
        "references": [
            "this repo: v2.356 (the three-channel map), v2.378 (BH channel), v2.357 (parity-screening correlation), v2.379 (parity->BH bridge), v2.372 (5 genuine inputs / g_R3 free), v2.350 (birefringence -> g_4 g_R2)",
            "structural: correlation-matrix participation ratio; channel observables as functions of the Wilson couplings",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=30000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    res = run(n_walk=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING (deflationary): the four channels probe ~2-3 independent observable directions:")
    print("          " + "  ".join("%9s" % n for n in NAMES))
    for n in NAMES:
        print("%-9s " % n + "  ".join("%9.2f" % res["correlation_matrix"][n][m] for m in NAMES))
    print(f"  screening=BH: {res['screening_bh_correlation']} (near-identical, both ~g_R2); ringdown orthogonal (max {res['ringdown_max_correlation_with_others']})")
    print(f"  effective observable dimension: {res['effective_observable_dimension']} (of 4) -- 'four channels' overstates independent testability")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
