"""v2.394 - SWING: the candidate theory's actual UV cutoff -- a Dvali species scale of ~0.72 M_Pl, tightly predicted.

After 27 swings characterizing the consistent region, one central quantity was never computed: the ACTUAL UV
cutoff of the candidate quantum-gravity EFT -- the energy where gravity goes strongly coupled and the EFT
breaks down. The engine encodes it via Dvali's species scale (species_scale_bound, class B/information): with N
light species below the cutoff, gravity becomes strongly coupled at

    Lambda_species / M_Pl = 1 / sqrt(N) ,   N = 1 + nu (|g_R2| + |g_C| + |g_R3|) ,  nu = 2, N_max = 3.

The couplings count the tower of light states (the same string-like tower of v2.375), and the bound N <= N_max
= 3 caps how low the cutoff can drop.

Result: the candidate theory is a NEAR-PLANCKIAN EFT. For the constructed couplings N = 1.95 species, so
Lambda_species = 0.72 M_Pl. Across the whole feasible family N in [1.37, 2.36], so the cutoff is TIGHTLY
predicted at Lambda_species / M_Pl in [0.65, 0.86] (mean 0.74) -- the gravitational EFT is valid up to ~0.7
M_Pl, where a tower of ~2 effective species makes gravity strong. The species bound is only ~62% saturated (N /
N_max ~ 0.62, max 0.79), so the theory keeps its cutoff comfortably below the strong-coupling floor 1/sqrt(3) =
0.577 M_Pl. This is consistent with ghost-safety (v2.385): the Weyl^2 ghost at 2.28x the cutoff sits at ~1.6
M_Pl, safely above. So the theory's validity ladder is: EFT good to ~0.72 M_Pl (species scale) < ghost/first
heavy recurrence ~1.6 M_Pl < M_Pl-scale physics -- a self-consistent, sub-Planckian-but-near-Planckian cutoff.
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

VERSION = "v2.394"
DEFAULT_OUT = Path("experiments/results/v2.394/qnm_species_scale_cutoff.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
NU, N_MAX = 2.0, 3.0


def _cutoff(gR2, gR3):
    N = 1.0 + NU * (2.0 * gR2 + gR3)   # g_C = g_R2 in the engine -> |g_R2|+|g_C| = 2 g_R2
    return N, 1.0 / np.sqrt(N)


def run(n_walk: int = 25000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    con_N, con_L = _cutoff(0.193, 0.09)
    con_N, con_L = float(con_N), float(con_L)
    min_L_from_Nmax = float(1.0 / np.sqrt(N_MAX))

    rng = np.random.default_rng(seed)
    pts = [CONSTRUCTED.copy()]
    cur = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 6), 0.0, None)
        if feasible(c):
            cur = c
            pts.append(cur.copy())
    pts = np.array(pts)
    Nf = 1.0 + NU * (2.0 * pts[:, 3] + pts[:, 4])
    Lf = 1.0 / np.sqrt(Nf)
    sat = Nf / N_MAX

    ghost_over_cutoff = 1.0 / np.sqrt(0.193)   # v2.385 m_g/Lambda
    ghost_scale = float(ghost_over_cutoff * con_L)

    checks = {
        "cutoff_sub_planckian": bool(con_L < 1.0),
        "cutoff_near_planckian": bool(con_L > 0.5),
        "cutoff_tightly_bounded": bool((float(Lf.max()) - float(Lf.min())) < 0.3),
        "species_bound_not_saturated": bool(float(sat.max()) < 1.0),
        "ghost_above_cutoff_consistent": bool(ghost_scale > float(Lf.max())),
    }

    return {
        "version": VERSION,
        "nu": NU, "N_max": N_MAX,
        "constructed_N_species": round(float(con_N), 3),
        "constructed_cutoff_over_Mpl": round(float(con_L), 3),
        "min_cutoff_from_Nmax": round(float(min_L_from_Nmax), 3),
        "family_N_species": {"mean": round(float(Nf.mean()), 3), "min": round(float(Nf.min()), 3), "max": round(float(Nf.max()), 3)},
        "family_cutoff_over_Mpl": {"mean": round(float(Lf.mean()), 3), "min": round(float(Lf.min()), 3), "max": round(float(Lf.max()), 3)},
        "species_bound_saturation": {"mean": round(float(sat.mean()), 2), "max": round(float(sat.max()), 2)},
        "ghost_scale_over_Mpl": round(ghost_scale, 2),
        "n_samples": len(pts),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate theory's actual UV cutoff -- the energy where gravity goes strongly coupled -- is a "
            "Dvali species scale of ~0.72 M_Pl, tightly predicted, and never computed in the prior 27 swings. "
            "With N light species the cutoff is Lambda_species/M_Pl = 1/sqrt(N), N = 1 + nu(|g_R2|+|g_C|+"
            "|g_R3|); the couplings count the same string-like tower (v2.375). For the constructed couplings N "
            "= 1.95, so Lambda_species = 0.72 M_Pl. Across the WHOLE feasible family N in [1.37, 2.36], so the "
            "cutoff is tightly bounded at Lambda_species/M_Pl in [0.65, 0.86] (mean 0.74) -- the theory is a "
            "NEAR-PLANCKIAN EFT, valid up to ~0.7 M_Pl before a tower of ~2 effective species makes gravity "
            "strong. The species bound (N <= 3) is only ~62% saturated (max 79%), so the theory keeps its "
            "cutoff comfortably above the strong-coupling floor 1/sqrt(3) = 0.577 M_Pl -- it does not push its "
            "tower to the maximum. This closes the EFT's validity ladder self-consistently: the cutoff ~0.72 "
            "M_Pl sits below the Weyl^2 ghost, which at 2.28x the cutoff (v2.385) is at ~1.6 M_Pl, safely "
            "above -- so the ghost is trans-cutoff exactly as required, and the species tower is what UV-"
            "completes the EFT at 0.72 M_Pl. This is the answer to 'where does this quantum-gravity EFT break "
            "down': not at M_Pl, but at ~0.7 M_Pl, lowered modestly by its own light tower -- a genuinely "
            "sub-Planckian but near-Planckian cutoff that the consistent region pins to a ~30% window. It also "
            "grounds the tower/species picture (v2.375/388): the ~2 species here are the low-lying end of the "
            "infinite log-convex tower, and the species bound is the information-theoretic (holographic, "
            "class-B) face of the same tower the moment conditions (class A/C) generate -- the one place the "
            "least-carving B sector (v2.374) sets a physical scale."
        ),
        "honest_scope": (
            "The species scale Lambda_species = M_Pl/sqrt(N) with N = 1 + nu(|g_R2|+|g_C|+|g_R3|) is the "
            "engine's TOY encoding of Dvali's species scale (nu = 2, N_max = 3 are toy O(1) parameters, and "
            "counting species by a linear sum of |couplings| is a proxy -- physically N is the number of tower "
            "STATES below the cutoff, not a coupling sum). So the specific 0.72 M_Pl and the [0.65, 0.86] "
            "window are toy-basis and scale with nu; g_C is identified with g_R2 (Weyl^2/Ricci^2). The ROBUST "
            "content is structural: the cutoff is sub-Planckian (N > 1 always, since the anomaly forces g_R2 > "
            "0, v2.393, so there is always at least a partial species tower) but near-Planckian (N stays O(1) "
            "because matter dominance + scale rigidity keep the couplings O(0.1), v2.389/390), and it is "
            "TIGHTLY bounded because the feasible couplings are tightly bounded -- a ~30% window, not a free "
            "cutoff. The ghost-ladder consistency (ghost at 2.28x cutoff = ~1.6 M_Pl) reuses v2.385's O(1)-"
            "schematic ghost-mass relation, so '~1.6 M_Pl' is schematic; the robust point is the ORDERING "
            "(cutoff < ghost). This is a computation within the toy species encoding, not a first-principles "
            "species-scale derivation. Robust content: the candidate is a near-Planckian EFT with a tightly-"
            "pinned sub-Planckian cutoff (~0.7 M_Pl in this encoding), set by its light tower, with the ghost "
            "safely above -- a self-consistent validity ladder. Toy nu/N_max, robust near-Planckian + tightly-"
            "bounded structure. A UV-cutoff swing."
        ),
        "references": [
            "this repo: src/itb/constraints/species_scale.py (Dvali species scale), v2.385 (ghost above cutoff), v2.375/388 (string-like tower / light-coupling count), v2.393 (anomaly forces g_R2>0 -> N>1), v2.389/390 (matter dominance / scale rigidity keep couplings O(0.1)), v2.374 (B/information sector carves least)",
            "physics: Dvali (species scale); van de Heisteeg, Vafa, Wiesner (species scale & the swampland)",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=25000)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    res = run(n_walk=args.n, seed=args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("SWING: the candidate theory's actual UV cutoff -- a Dvali species scale ~0.72 M_Pl:")
    print(f"  constructed: N = {res['constructed_N_species']} species -> Lambda_species/M_Pl = {res['constructed_cutoff_over_Mpl']}")
    print(f"  family: N {res['family_N_species']}; Lambda_species/M_Pl {res['family_cutoff_over_Mpl']} -- tightly bounded (near-Planckian)")
    print(f"  species bound saturation N/N_max: {res['species_bound_saturation']} (not saturated; floor 1/sqrt(3)={res['min_cutoff_from_Nmax']})")
    print(f"  validity ladder: cutoff {res['constructed_cutoff_over_Mpl']} M_Pl < Weyl^2 ghost ~{res['ghost_scale_over_Mpl']} M_Pl (v2.385) -- self-consistent")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
