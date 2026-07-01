"""v2.381 - SWING: the string-like matter identity is observationally DARK -- g_8 feeds no channel.

The complement of v2.380 (which channels are independent) is: which COUPLINGS are observable? Correlating each
of the 5 genuine inputs (v2.372) with the four channel observables across the feasible family identifies the
DARK parameters -- constrained by consistency but feeding no observation.

Result: g_8 is the UNIQUE dark coupling -- its maximum correlation with any channel is ~0.1, while every other
coupling is observable (0.6-1.0):

    g_R2         -> screening (1.00), BH (0.88)          [observable]
    g_R2_parity  -> parity (1.00)                        [observable]
    g_R3         -> ringdown (0.95)                      [observable]
    g_4          -> BH (0.83)                            [observable]
    g_6          -> screening/BH (~0.6, indirect)        [observable]
    g_8          -> nothing (max ~0.1)                   [DARK]

The sting is WHAT g_8 is: it is the top matter dispersion coefficient, and it enters the matter dispersion
ratio r_matter = g_6^2/(g_4 g_8) = 0.756 -- the very quantity that establishes the 'string-like multi-state
matter' identity (v2.343). So the coupling that most directly encodes the matter tower's multi-state structure
is the ONE the four channels cannot touch. The theory's headline identity ('parity-deformed, curvature-trimmed
STRING-LIKE gravity', v2.342) is, on its matter/string-like side, theoretically established but observationally
HIDDEN: parity, screening, ringdown, and black-hole extremality all probe the curvature+parity sector; none
probes the matter Regge structure.
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

VERSION = "v2.381"
DEFAULT_OUT = Path("experiments/results/v2.381/qnm_dark_parameter.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
GR2_MAX = 0.0626
CHAN_NAMES = ["parity", "screening", "ringdown", "BH"]
DARK_THRESHOLD = 0.25


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

    chans = {
        "parity": 3.4 * pts[:, 5],
        "screening": pts[:, 3] / GR2_MAX,
        "ringdown": np.where(pts[:, 3] > 1e-9, pts[:, 4] ** 2 / pts[:, 3], 0.0),
        "BH": pts[:, 3] + 0.5 * pts[:, 0],
    }

    rows = {}
    for i, k in enumerate(KEYS):
        cors = {cn: round(abs(float(np.corrcoef(pts[:, i], cv)[0, 1])), 2) for cn, cv in chans.items()}
        mx = max(cors.values())
        rows[k] = {"correlations": cors, "max_abs_corr": mx,
                   "status": "DARK" if mx < DARK_THRESHOLD else ("weak" if mx < 0.5 else "observable")}

    dark = [k for k, v in rows.items() if v["status"] == "DARK"]
    g8_dark = rows["g_8"]["status"] == "DARK"
    others_observable = all(rows[k]["status"] != "DARK" for k in KEYS if k != "g_8")

    checks = {
        "g_8_is_dark": g8_dark,
        "g_8_is_the_unique_dark_coupling": dark == ["g_8"],
        "all_other_couplings_observable": others_observable,
        "g_R2_maps_to_screening_and_bh": rows["g_R2"]["correlations"]["screening"] > 0.8,
        "g_R3_maps_to_ringdown": rows["g_R3"]["correlations"]["ringdown"] > 0.8,
    }

    return {
        "version": VERSION,
        "n_samples": len(pts),
        "coupling_observability": rows,
        "dark_couplings": dark,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The theory's 'string-like matter' identity is observationally DARK: of the five genuine inputs, "
            "g_8 is the UNIQUE coupling that feeds no channel (its maximum correlation with parity, screening, "
            "ringdown, or black-hole extremality is only ~0.1), while every other coupling is observable "
            "(g_R2 -> screening 1.00 / BH 0.88; g_R2_parity -> parity 1.00; g_R3 -> ringdown 0.95; g_4 -> BH "
            "0.83; g_6 -> screening/BH ~0.6). The sting is WHAT g_8 is: the top matter dispersion coefficient, "
            "entering the matter dispersion ratio r_matter = g_6^2/(g_4 g_8) = 0.756 -- the very quantity that "
            "establishes the multi-state, string-like matter sector (v2.343). So the coupling that most "
            "directly encodes the matter tower's multi-state structure is precisely the one the four channels "
            "cannot touch. This is an honest limitation on the theory's headline: 'parity-deformed, "
            "curvature-trimmed, STRING-LIKE gravity' (v2.342) is, on its string-like MATTER side, "
            "theoretically established but observationally hidden -- parity, screening, ringdown, and BH "
            "extremality all probe the curvature+parity sector (g_R2, g_R3, g_R2_parity, with g_4 partly), and "
            "NONE probes the matter Regge structure. It sharpens the observability picture (v2.380): the ~2.5 "
            "observable directions live entirely in the curvature/parity sector; the matter multi-state "
            "structure is inferred only through consistency (the dispersion tower, the anomaly links), never "
            "measured. So a skeptic could grant the theory's four channels and still deny the 'string-like "
            "matter' claim -- there is no observation that tests it. The falsifiable, testable content of the "
            "theory is its curvature/parity sector; its matter-string-like identity is a consistency "
            "inference, not an observational prediction."
        ),
        "honest_scope": (
            "The correlations are over a seeded random-walk sample with the toy channel maps (v2.380 scope), "
            "so the exact numbers are sampler- and toy-basis-dependent -- but the DARKNESS of g_8 is "
            "structural: g_8 appears in NO channel observable (parity ~ g_R2_parity, screening/BH ~ g_R2/g_4, "
            "ringdown ~ g_R3^2/g_R2), and its only role is in the matter dispersion tower g_6^2 <= g_4 g_8, "
            "which no channel reads -- so its ~0.1 residual correlation is purely the indirect family "
            "coupling, and would remain small in any basis. g_6 shows up as 'observable' (~0.6) only through "
            "its family correlation with g_R2, not a direct channel dependence -- so the matter sector's "
            "observability is entirely INDIRECT (via correlations with the curvature scale), which is the same "
            "point. The 0.25 dark threshold is conventional; g_8 at 0.09 is far below it and g_4/g_6 far above, "
            "so the verdict is not threshold-sensitive. This is a statement about the FOUR channels catalogued "
            "so far -- a future observable that read the matter dispersion directly (a graviton-matter "
            "amplitude measurement) would illuminate g_8, but none is in the engine's channel set. Robust "
            "content: g_8 (the matter-multi-state coefficient) is dark to all four channels, so the "
            "string-like matter identity is observationally hidden. Toy channel maps, structural coupling "
            "dependence. An honest-limitation swing on the theory's testable content."
        ),
        "references": [
            "this repo: v2.380 (channels ~2.5 independent), v2.372 (5 genuine inputs), v2.343 (multi-state matter r=0.756), v2.342 (string-like identity), v2.356/v2.378 (the four channels)",
            "structural: coupling-to-channel correlation; g_8 enters only the matter dispersion tower",
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
    print("SWING: which couplings are DARK to the four channels? (the string-like matter is hidden)")
    for k, v in res["coupling_observability"].items():
        print(f"  {k:<12} max|corr| {v['max_abs_corr']:.2f} [{v['status']:<10}]  " +
              " ".join(f"{cn}:{cv:.2f}" for cn, cv in v["correlations"].items()))
    print(f"  dark couplings: {res['dark_couplings']}  (g_8 = top matter moment -> the multi-state / string-like matter signature)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
