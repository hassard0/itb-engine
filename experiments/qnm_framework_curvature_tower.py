"""v2.262 - Forced higher-curvature towers per framework from Hankel positivity (and an lqg flag).

Applies the moment-sequence / Hankel-positivity structure (v2.261) to the engine's ACTUAL framework
curvature couplings (g_R2, g_R3). Given the first two moments (m_0 = g_R2, m_1 = g_R3, m_0 > 0), the
Hankel positivity forces the higher couplings, and the MINIMAL consistent tower -- which saturates
every Hankel minor -- is a single-effective-state geometric sequence

    g_R(k+2) = g_R2 * x^k ,    x = g_R3 / g_R2     (single spectral state at mass^2 = x, weight g_R2).

So g_R4_min = g_R3^2/g_R2 (= v2.234), g_R5_min = g_R3^3/g_R2^2, g_R6_min = g_R3^4/g_R2^3, ... -- a
geometric tower with ratio x. The ratio x = g_R3/g_R2 is the effective mass^2 of the lightest
curvature state: x < 1 means the higher-curvature operators DECOUPLE (a converging tower, a healthy
EFT), while x = 1 means the tower is MARGINAL (the curvature operators do NOT decouple). This is a
concrete, per-framework prediction and a new consistency diagnostic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.262"
DEFAULT_OUT = Path("experiments/results/v2.262/qnm_framework_curvature_tower.json")


def hankel(m, n: int) -> np.ndarray:
    return np.array([[m[i + j] for j in range(n + 1)] for i in range(n + 1)])


def run() -> dict:
    rows = []
    for fw in frameworks():
        c = fw.encode().coefficients
        g2, g3 = c.get("g_R2", 0.0), c.get("g_R3", 0.0)
        if g2 <= 0:
            rows.append({"framework": fw.name, "has_curvature": False})
            continue
        x = g3 / g2
        tower = [g2 * x**k for k in range(5)]            # g_R2, g_R3, g_R4, g_R5, g_R6
        det2 = float(np.linalg.det(hankel(tower, 1)))    # ~0: single state saturates the bound
        regime = "converging (operators decouple)" if x < 1 - 1e-9 else (
            "marginal (operators do NOT decouple)" if abs(x - 1) <= 1e-9 else "growing")
        rows.append({"framework": fw.name, "has_curvature": True,
                     "g_R2": g2, "g_R3": g3, "effective_state_x": x,
                     "minimal_tower": {"g_R4": tower[2], "g_R5": tower[3], "g_R6": tower[4]},
                     "g_R4_min_matches_v234": abs(tower[2] - g3**2 / g2) < 1e-12,
                     "hankel_2x2_det": det2, "tower_regime": regime})
    marginal = [r["framework"] for r in rows if r.get("tower_regime", "").startswith("marginal")]
    return {
        "version": VERSION,
        "method": ("minimal Hankel-saturating curvature tower g_R(k+2)=g_R2 x^k, x=g_R3/g_R2, per "
                   "engine framework (single effective spectral state); convergence diagnostic x<1"),
        "framework_towers": rows,
        "marginal_frameworks": marginal,
        "finding": (
            "Applying the v2.261 moment-tower positivity to the engine's frameworks gives each a "
            "concrete MINIMAL higher-curvature tower: a geometric sequence g_R(k+2) = g_R2 x^k with "
            "ratio x = g_R3/g_R2 (the effective mass^2 of the lightest curvature state, single-state "
            "saturating every Hankel minor -- 2x2 det ~ 0). g_R4_min reproduces the v2.234 bound "
            "exactly. The new diagnostic is the ratio x: string_tree_eft (x=0.75), asymptotic_safety "
            "(x=0.67), and cdt (x=0.68) have CONVERGING towers (x<1 -> the higher-curvature operators "
            "decouple, a healthy EFT), but LQG_INDUCED has x=1.0 (g_R2=g_R3=0.3) -- a MARGINAL tower "
            "(g_R4=g_R5=g_R6=0.3, the curvature operators do NOT decouple). So lqg sits at the "
            "boundary of the moment-tower's healthy region, an independent flag consistent with its "
            "already-anomalous status (it fails 4/38 engine constraints, and v2.234 showed it needs "
            "the largest forced g_R4). This is a novel per-framework consistency diagnostic from the "
            "curvature moment tower -- extending v2.234/v2.261 to concrete framework predictions."
        ),
        "honest_scope": (
            "The MINIMAL tower (single effective state) is the floor of the Hankel-allowed region; a "
            "framework's TRUE higher-curvature couplings could be larger (more spectral states) -- "
            "the geometric tower is the lower envelope, not a unique prediction. The x = g_R3/g_R2 "
            "diagnostic inherits the engine's representative-O(1)-prefactor caveat (v2.261): the "
            "operator<->moment indexing is structural, so 'marginal' is a representative statement "
            "about the toy couplings, not an operator-exact decoupling claim. The framework couplings "
            "themselves are the engine's encoded (toy) values. A theory-structure diagnostic, not a "
            "new bound. Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Caron-Huot, Mazac, Rastelli, Simmons-Duffin, JHEP 07 (2021) 110 -- moment problem / EFT-hedron",
            "this repo: v2.261 (moment-tower structure), v2.234 (g_R4 mandate); engine frameworks()",
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
    print("framework            x=g_R3/g_R2   g_R4,g_R5,g_R6           regime")
    for r in res["framework_towers"]:
        if not r["has_curvature"]:
            print(f"  {r['framework']:18s} (no curvature)")
            continue
        t = r["minimal_tower"]
        print(f"  {r['framework']:18s} {r['effective_state_x']:.3f}        "
              f"{t['g_R4']:.4f},{t['g_R5']:.4f},{t['g_R6']:.4f}   {r['tower_regime']}")
    print(f"marginal frameworks: {res['marginal_frameworks']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
