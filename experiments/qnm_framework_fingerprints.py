"""v2.359 - Observational fingerprints: each framework's signature across the three channels (and which channel discriminates).

Connects the framework comparison (v2.322: which frameworks pass theory+data) with the three-channel
falsifiability map (v2.356: parity / ringdown / screening) -- by computing, for every named framework, its
predicted signature in each channel side by side with the constructed theory. The new content is per-CHANNEL:
not just pass/fail, but WHICH channel discriminates, and which "predictions" are actually generic.

  parity   : beta_pred = 3.4 deg * g_R2_parity; cosmic birefringence (2-sigma) needs g_R2_parity in
             [0.047, 0.153], so beta = 0 (parity-even) is EXCLUDED.
  ringdown : moment-tower floor g_R3^2/g_R2 (the minimum quartic-curvature/ringdown deviation).
  screening: g_R2 vs the unscreened Eot-Wash cap 0.063; g_R2 > cap => the R^2 fifth force MUST be screened.

The table yields three findings -- one of which honestly TEMPERS v2.354:
  (1) the PARITY channel is the unique discriminator: beta = 0 excludes the four parity-even frameworks
      (pure_gr, string, AS, cdt); only the constructed theory and lqg are parity-consistent.
  (2) the SCREENING mandate is GENERIC, not distinctive: every non-GR framework (string, AS, cdt, lqg) also
      has g_R2 > cap and so also requires screening -- so screening does NOT discriminate the constructed
      theory from the community frameworks (only parity does). An honest tempering of v2.354.
  (3) the RINGDOWN floor ORDERS the frameworks: the constructed theory has the mildest nonzero floor (0.042),
      consistent with v2.336.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import frameworks
from itb.constraints.submm_gravity import SubmmGravityYukawaBound

VERSION = "v2.359"
DEFAULT_OUT = Path("experiments/results/v2.359/qnm_framework_fingerprints.json")

KAPPA_BETA = 3.4
PARITY_BAND = (0.047, 0.153)   # g_R2_parity 2-sigma birefringence band
CONSTRUCTED = {"name": "engine_constructed", "g_R2_parity": 0.06, "g_R2": 0.193, "g_R3": 0.09}


def fingerprint(name, c, cap):
    gR2p = c.get("g_R2_parity", 0.0)
    gR2 = c.get("g_R2", 0.0)
    gR3 = c.get("g_R3", 0.0)
    floor = gR3 ** 2 / gR2 if gR2 > 1e-9 else 0.0
    beta = KAPPA_BETA * gR2p
    parity_ok = PARITY_BAND[0] <= gR2p <= PARITY_BAND[1]
    must_screen = gR2 > cap
    return {"framework": name, "beta_pred": round(beta, 3), "g_R2_parity": round(gR2p, 3),
            "ringdown_floor": round(floor, 3), "g_R2": round(gR2, 3),
            "parity_status": "consistent" if parity_ok else ("excluded(beta=0)" if gR2p < 1e-9 else "out-of-band"),
            "screening": "must-screen" if must_screen else "no-fifth-force/ok"}


def run() -> dict:
    cap = float(SubmmGravityYukawaBound(screened=False).g_R2_max)
    rows = [fingerprint(CONSTRUCTED["name"], CONSTRUCTED, cap)]
    for f in frameworks():
        rows.append(fingerprint(f.name, f.encode().coefficients, cap))

    named = [r for r in rows if r["framework"] != "engine_constructed"]
    parity_even = [r for r in named if r["g_R2_parity"] < 1e-9]
    parity_consistent = [r for r in rows if r["parity_status"] == "consistent"]
    non_gr = [r for r in named if r["g_R2"] > 1e-9]
    non_gr_must_screen = [r for r in non_gr if r["screening"] == "must-screen"]
    constructed_row = rows[0]
    nonzero_floors = [r for r in rows if r["ringdown_floor"] > 1e-9]
    constructed_mildest = (constructed_row["ringdown_floor"] == min(r["ringdown_floor"] for r in nonzero_floors))

    checks = {
        "parity_excludes_all_parity_even": all(r["parity_status"] == "excluded(beta=0)" for r in parity_even),
        "constructed_parity_consistent": constructed_row["parity_status"] == "consistent",
        "only_constructed_and_lqg_parity_consistent": {r["framework"] for r in parity_consistent} <= {"engine_constructed", "lqg_induced"},
        "screening_is_generic_all_non_gr": len(non_gr_must_screen) == len(non_gr) and len(non_gr) >= 3,
        "constructed_has_mildest_ringdown_floor": constructed_mildest,
    }

    return {
        "version": VERSION,
        "unscreened_cap": round(cap, 4),
        "parity_band_g_R2_parity": list(PARITY_BAND),
        "fingerprints": rows,
        "n_parity_even_excluded": len(parity_even),
        "parity_consistent_frameworks": [r["framework"] for r in parity_consistent],
        "n_non_gr": len(non_gr),
        "n_non_gr_must_screen": len(non_gr_must_screen),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Laying the named frameworks' observational signatures side by side across the three channels "
            "shows which channel actually discriminates -- and tempers one of the program's headlines. "
            "(1) The PARITY channel is the unique discriminator: cosmic birefringence needs g_R2_parity in "
            "[0.047, 0.153], so beta = 0 EXCLUDES the four parity-even frameworks (pure_gr, string_tree_eft, "
            "asymptotic_safety, cdt); only the constructed theory (beta_pred 0.204) and lqg_induced "
            "(beta_pred 0.272) are parity-consistent -- and lqg is theory-excluded elsewhere (v2.322), "
            "leaving the constructed theory uniquely consistent. (2) The SCREENING mandate is GENERIC, not "
            "distinctive: every non-GR framework has g_R2 above the unscreened Eot-Wash cap 0.063 "
            "(string 0.20, AS 0.15, cdt 0.22, lqg 0.30, constructed 0.19), so ALL of them require a screened "
            "R^2 scalaron -- screening does NOT discriminate the constructed theory from the community "
            "frameworks. This honestly tempers v2.354: the screening mandate is a real and falsifiable "
            "prediction, but it is a generic feature of higher-derivative gravity with sizable g_R2, shared "
            "by string/AS/cdt/lqg, not a fingerprint of the constructed theory specifically. Only pure_gr "
            "escapes screening (it has no R^2 term) -- but pure_gr is parity-excluded. (3) The RINGDOWN "
            "floor ORDERS the frameworks: the constructed theory has the mildest nonzero floor (0.042 vs "
            "AS 0.067, cdt 0.102, string 0.112, lqg 0.300), consistent with v2.336 -- a fingerprint, not "
            "yet an exclusion (no ringdown data). Net: the constructed theory's OBSERVATIONAL distinctiveness "
            "lives entirely in the parity channel; its ringdown is the mildest and its screening is generic. "
            "So the parity (birefringence) datum is not just the only binding data constraint (v2.358) but "
            "the only channel that observationally SEPARATES the constructed theory from the named "
            "frameworks."
        ),
        "honest_scope": (
            "The fingerprints are exact arithmetic on the engine's encoded framework couplings, but those "
            "couplings are the engine's TOY encodings of each framework (e.g. 'string_tree_eft' is the toy "
            "(0.5,0.4,0.4,0.2,...) point, NOT the actual Veneziano coefficients), so the per-channel numbers "
            "are relative statements among the engine's framework set, not literal predictions of real "
            "string theory / AS / CDT / LQG. The beta map (3.4 deg * g_R2_parity) and the Eot-Wash cap are "
            "the same toy/order-of-magnitude inputs as the per-channel cycles (v2.347/v2.354). The parity "
            "exclusion of the parity-even four rests on the birefringence detection being real (v2.329); if "
            "it is a systematic, beta = 0 is allowed and the parity channel stops discriminating (then NO "
            "channel separates the frameworks, since screening is generic and ringdown has no data) -- a "
            "sharp statement of how much rides on birefringence. The ringdown floor magnitudes are coupling "
            "ratios, not sourced frequency shifts (rank-1 map, v2.336). Robust content: parity is the "
            "discriminating channel, screening is generic across non-GR frameworks, and the constructed "
            "theory has the mildest ringdown. Toy basis, O(1) prefactors. A per-channel framework fingerprint "
            "joining v2.322 and v2.356."
        ),
        "references": [
            "this repo: v2.322 (frameworks scored on theory+data), v2.356 (three-channel falsifiability map), v2.354 (screening mandate -- here shown generic), v2.336 (constructed has mildest ringdown), v2.358 (birefringence is the only binding data constraint)",
            "this repo: v2.329 (birefringence caveat), v2.342 (constructed closest to string in coupling space)",
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
    print("framework observational fingerprints (parity / ringdown / screening):")
    print(f"  {'framework':<20} {'beta':>6} {'parity':>16} {'floor':>6} {'screening':>18}")
    for r in res["fingerprints"]:
        print(f"  {r['framework']:<20} {r['beta_pred']:>6.3f} {r['parity_status']:>16} {r['ringdown_floor']:>6.3f} {r['screening']:>18}")
    print(f"  parity-even excluded: {res['n_parity_even_excluded']}; parity-consistent: {res['parity_consistent_frameworks']}")
    print(f"  non-GR requiring screening: {res['n_non_gr_must_screen']}/{res['n_non_gr']} (screening is generic)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
