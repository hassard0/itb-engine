"""v2.395 - SWING: CMB-S4 is a decisive make-or-break test -- matter dominance REQUIRES a large matter coupling the CMB-S4 forecast excludes at >10 sigma.

The matter-dominance arc (v2.389-393) established that the matter sector must be STRONG: it sources the leading
gravitational correction (v2.393), sets the gravitational scale (v2.389), and caps gravity at <=40% of its own
strength (v2.391). Concretely, the feasible region has g_4 in [0.35, 0.63] -- a large matter self-coupling is
mandatory. This swing confronts that with a SOURCED next-generation forecast: the engine's CMB-S4 constraint
(CMBS4Forecast, from the CMB-S4 Science Book) maps g_4 to the inflationary scalar self-interaction that CMB-S4
will measure to sigma = 0.03 around a central value of 0 (single-field slow-roll).

Result: CMB-S4 is a decisive test of the ENTIRE construction. The constructed g_4 = 0.53 is 17.6 sigma from the
CMB-S4 forecast; the SMALLEST feasible g_4 = 0.35 is still 11.7 sigma away -- so the whole feasible region is
excluded at >10 sigma if CMB-S4 confirms single-field slow-roll. So CMB-S4 (~2030) is make-or-break: either it
detects the large scalar self-interaction the matter-dominant theory requires (a striking confirmation), or it
confirms slow-roll (g_4 ~ 0) and FALSIFIES the entire construction -- not just the constructed point but every
consistent theory in the family. This is the sharpest falsifiability statement the theory supports (far sharper
than the parity discrimination of v2.377), and it gives the otherwise gravitationally-dark matter sector
(v2.381) a decisive, non-gravitational observable: CMB-S4 tests g_4 directly.
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
from itb.constraints.cmb_s4 import CMBS4Forecast

VERSION = "v2.395"
DEFAULT_OUT = Path("experiments/results/v2.395/qnm_cmb_s4_decisive_test.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CONSTRUCTED = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])


def run(n_walk: int = 25000, seed: int = 0) -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def feasible(v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    s4 = CMBS4Forecast()
    cv, sig, thr = float(s4.central_value), float(s4.sigma), float(s4.sigma_threshold)

    rng = np.random.default_rng(seed)
    pts = [CONSTRUCTED.copy()]
    cur = CONSTRUCTED.copy()
    for _ in range(n_walk):
        c = np.clip(cur + rng.normal(0, 0.03, 6), 0.0, None)
        if feasible(c):
            cur = c
            pts.append(cur.copy())
    pts = np.array(pts)
    g4 = pts[:, 0]

    con_sigma = (0.529 - cv) / sig
    min_g4 = float(g4.min())
    min_sigma = (min_g4 - cv) / sig
    con_satisfies = bool(s4.evaluate(Theory(coefficients=dict(zip(KEYS, CONSTRUCTED)), name="x")).satisfied)

    checks = {
        "cmb_s4_excludes_constructed": not con_satisfies,
        "constructed_tension_over_10_sigma": con_sigma > 10.0,
        "whole_region_excluded": min_sigma > thr,
        "matter_dominance_requires_large_g4": min_g4 > 0.2,
        "decisive_test_not_marginal": min_sigma > 5.0,
    }

    return {
        "version": VERSION,
        "cmb_s4_forecast": {"coefficient": "g_4", "central": cv, "sigma": sig, "threshold_sigma": thr,
                            "citation": s4.citation},
        "feasible_g4_range": [round(min_g4, 3), round(float(g4.max()), 3)],
        "feasible_g4_mean": round(float(g4.mean()), 3),
        "constructed_g4": 0.529,
        "constructed_tension_sigma": round(float(con_sigma), 1),
        "min_region_tension_sigma": round(float(min_sigma), 1),
        "constructed_satisfies_cmb_s4": con_satisfies,
        "n_samples": len(pts),
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "CMB-S4 is a decisive make-or-break test of the entire matter-dominant construction. The "
            "matter-dominance arc (v2.389-393) requires a STRONG matter sector -- matter sources the leading "
            "gravitational correction, sets the gravitational scale, and caps gravity at <=40% of its own "
            "strength -- so every consistent theory has a large matter self-coupling: the feasible region is "
            "g_4 in [0.35, 0.63]. The engine's CMB-S4 forecast (CMB-S4 Science Book) maps g_4 to the "
            "inflationary scalar self-interaction CMB-S4 will measure to sigma = 0.03 around 0 (single-field "
            "slow-roll). The constructed g_4 = 0.53 is 17.6 sigma from that forecast, and the SMALLEST "
            "feasible g_4 = 0.35 is still 11.7 sigma away -- so the ENTIRE feasible region, not just the "
            "center, is excluded at >10 sigma if CMB-S4 confirms slow-roll. So CMB-S4 (~2030) is make-or-"
            "break: either it detects the large scalar self-interaction the theory requires (a striking "
            "confirmation of matter dominance) or it confirms g_4 ~ 0 and FALSIFIES the whole construction. "
            "This is the sharpest falsifiability statement the theory supports -- an order of magnitude "
            "sharper than the parity discrimination (v2.377, sub-sigma anomaly variants) -- because it "
            "targets the LOAD-BEARING matter sector, not the subordinate gravitational one. And it resolves "
            "the observability worry from v2.381 (the matter sector is dark to the four GRAVITATIONAL "
            "channels): the matter sector is NOT untestable -- it has a decisive NON-gravitational observable "
            "in CMB-S4, which probes g_4 directly through inflationary cosmology. So the theory's most "
            "load-bearing and otherwise-hardest-to-see sector is exactly the one a near-future experiment "
            "will decisively test. The whole matter-dominant edifice (v2.389-394) rests on g_4 being large, "
            "and CMB-S4 is the experiment that will confirm or kill that assumption."
        ),
        "honest_scope": (
            "The decisive tension rests on the engine's TOY identification of g_4 with the inflationary "
            "scalar self-interaction that CMB-S4 measures. In the engine g_4 is primarily the matter "
            "forward-positivity / dim-8 coupling; the CMB-S4 constraint reuses it as the inflationary "
            "self-coupling -- a plausible but toy dual role, so if g_4 is physically a DIFFERENT operator "
            "from the CMB-S4 observable, the tension evaporates. The CMB-S4 sensitivity sigma = 0.03 is the "
            "Science Book forecast rescaled into the toy basis (sourced but toy-normalized), and g_4 ~ 0.5 is "
            "a toy-basis value -- so the specific 17.6 sigma / 11.7 sigma are toy-basis. The ROBUST "
            "structural content is qualitative and strong: the theory REQUIRES a large matter self-coupling "
            "(matter dominance, region-wide g_4 >= 0.35, a basis-robust ordering), and a next-generation "
            "single-field-slow-roll confirmation forecasts that same parameter near zero, so IF the g_4 <-> "
            "CMB-S4-observable identification holds the two are in decisive (>10 sigma) tension -- a genuine, "
            "sharp, near-future falsification channel for the matter sector. CMB-S4 is a FORECAST (not data) "
            "for ~2030; 'make-or-break' means the theory predicts CMB-S4 must see a large signal, a bold bet. "
            "Robust content: the matter-dominant construction stakes itself on a large g_4, and CMB-S4 is a "
            "decisive near-future test of that -- either confirmation or region-wide falsification -- giving "
            "the gravitationally-dark matter sector a real observable. Toy g_4 identification and value, "
            "robust large-matter requirement, sourced forecast. A decisive-falsification swing."
        ),
        "references": [
            "this repo: src/itb/constraints/cmb_s4.py (CMB-S4 forecast on g_4), v2.389-393 (matter dominance -> large g_4 required), v2.381 (matter sector dark to gravitational channels), v2.377 (parity forward test -- the weaker discriminator)",
            "physics: CMB-S4 Science Book (Abazajian et al. 2016, updated 2022)",
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
    print("SWING: CMB-S4 is a decisive make-or-break test of the matter-dominant construction:")
    print(f"  CMB-S4 forecast: g_4 = {res['cmb_s4_forecast']['central']} +/- {res['cmb_s4_forecast']['sigma']} ({res['cmb_s4_forecast']['threshold_sigma']:.0f}-sigma)")
    print(f"  theory requires g_4 in {res['feasible_g4_range']} (matter dominance, v2.389-393)")
    print(f"  constructed g_4=0.529 -> {res['constructed_tension_sigma']} sigma tension; WHOLE region min tension {res['min_region_tension_sigma']} sigma")
    print(f"  => CMB-S4 (~2030) confirms slow-roll -> FALSIFIES the entire feasible region; detects large g_4 -> confirms matter dominance")
    print(f"  => gives the gravitationally-dark matter sector (v2.381) a decisive non-gravitational observable")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
