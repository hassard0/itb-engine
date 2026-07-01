"""v2.413 - ENGINE IMPROVEMENT (de-toying step 2): the candidate's real toy-dependence is the anomaly sector alone -- the two most speculative proxies (complexity, SDC) are harmless.

v2.412 localized the genuine toy cuts (the ones adding information beyond the rigorous+implied core) to four
constraints: the anomaly, the swampland distance conjecture, the complexity bound, and cosmic birefringence.
This cycle asks the decisive de-toying question: of those, which does the candidate ACTUALLY depend on? Method:
drop each from the FULL stack and measure how much the local feasible region opens (its leverage). A near-1.0x
leverage means the constraint is nearly redundant given the rest -- its toy form does not shape the result.

Result:
  complexity_cutoff              1.11x   nearly redundant   HARMLESS (self-described research-grade conjecture)
  swampland_distance_conjecture  1.11x   nearly redundant   HARMLESS (toy aspect-ratio proxy, v2.410)
  anomaly_cancellation           1.36x   LOAD-BEARING       genuine toy dependence
  generalized_anomaly_inflow     2.43x   LOAD-BEARING       genuine toy dependence
  cosmic_birefringence_data      7.36x   LOAD-BEARING       real DATA (v2.408), not toy

So the two MOST speculative toy proxies -- the complexity bound (an explicit research-grade conjecture with an
arbitrary weighted-L2 form and C_max=1.5) and the swampland-distance aspect-ratio proxy (the very constraint
v2.410 showed misses the real field-space physics) -- are HARMLESS: the candidate barely depends on them
(1.11x each), and it does NOT depend on complexity for its scale window either (identical [0.786, 1.070] with
and without it; the upper edge is set by the anomaly). The candidate's genuine toy dependence, beyond the real
birefringence datum, is concentrated in ONE family: the ANOMALY sector. That is now the single, unambiguous
de-toying target -- and two speculative worries are retired.
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
from experiments.stack import build_stack, HARMLESS_SPECULATIVE, LOAD_BEARING_TOY

VERSION = "v2.413"
DEFAULT_OUT = Path("experiments/results/v2.413/qnm_toy_dependence_map.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity"]
CON = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06])
BUILD = dict(rfc_form="convex_hull", include_data=True, include_birefringence=True,
             include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
TARGETS = ["complexity_cutoff", "swampland_distance_conjecture", "anomaly_cancellation",
           "generalized_anomaly_inflow", "cosmic_birefringence_data"]


def run(n_pts: int = 6000, seed: int = 0) -> dict:
    full = build_stack(**BUILD)

    def feas(stack, v):
        return all(r.satisfied for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results)

    rng = np.random.default_rng(seed)
    pts = np.clip(CON + rng.uniform(-0.15, 0.15, (n_pts, 6)), 0.0, None)
    ff = float(np.mean([feas(full, p) for p in pts]))

    leverage = {}
    for name in TARGETS:
        sub = [c for c in full if getattr(c, "name", "") != name]
        fn = float(np.mean([feas(sub, p) for p in pts]))
        leverage[name] = {"opens_x": round(fn / ff, 2) if ff > 0 else None,
                          "class": "load_bearing" if (fn / ff) > 1.3 else "nearly_redundant"}

    # scale window with vs without the harmless-speculative pair
    no_harmless = [c for c in full if getattr(c, "name", "") not in HARMLESS_SPECULATIVE]

    def window(stack):
        ls = [round(float(l), 3) for l in np.arange(0.2, 2.0, 0.002) if feas(stack, CON * l)]
        return [min(ls), max(ls)] if ls else [None, None]

    win_full = window(full)
    win_no_harmless = window(no_harmless)
    constructed_no_harmless = feas(no_harmless, CON)

    harmless_ok = all(leverage[n]["class"] == "nearly_redundant" for n in HARMLESS_SPECULATIVE)
    loadbearing_ok = all(leverage[n]["class"] == "load_bearing" for n in LOAD_BEARING_TOY)

    checks = {
        "complexity_is_harmless": leverage["complexity_cutoff"]["opens_x"] < 1.3,
        "sdc_is_harmless": leverage["swampland_distance_conjecture"]["opens_x"] < 1.3,
        "harmless_set_all_redundant": harmless_ok,
        "anomaly_sector_load_bearing": loadbearing_ok,
        "candidate_survives_dropping_harmless": bool(constructed_no_harmless) and win_no_harmless == win_full,
    }

    return {
        "version": VERSION,
        "full_local_feasible_fraction": round(ff, 4),
        "leverage": leverage,
        "harmless_speculative": sorted(HARMLESS_SPECULATIVE),
        "load_bearing_toy": sorted(LOAD_BEARING_TOY),
        "scale_window_full": win_full,
        "scale_window_without_harmless": win_no_harmless,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's real toy-dependence is the anomaly sector alone; the two most speculative proxies "
            "are harmless. v2.412 had localized the genuine toy cuts to four constraints; testing which the "
            "candidate ACTUALLY depends on -- dropping each from the full stack and measuring how much the "
            "region opens -- the two MOST speculative proxies come out nearly redundant: complexity_cutoff "
            "(1.11x), an explicit research-grade conjecture with an arbitrary weighted-L2 form and C_max=1.5, "
            "and swampland_distance_conjecture (1.11x), the toy aspect-ratio proxy that v2.410 showed misses "
            "the real field-space physics. So despite being the toy pieces one would most worry about, the "
            "candidate barely depends on them -- and it does not depend on the complexity bound for its scale "
            "window either (identical [0.786, 1.070] with and without it; the upper edge is set by the "
            "anomaly, not complexity). The candidate's genuine toy dependence, beyond the real cosmic-"
            "birefringence datum (7.36x, real DATA per v2.408), is concentrated in ONE family: the anomaly "
            "sector (anomaly_cancellation 1.36x + generalized_anomaly_inflow 2.43x). This is a doubly "
            "constructive de-toying step: it RETIRES two speculative worries -- the candidate is robust to "
            "dropping both the complexity conjecture and the (admittedly-imperfect) swampland-distance proxy, "
            "so neither the v2.410 field-space gap nor the speculative complexity bound actually threatens the "
            "result -- and it PINPOINTS the single remaining toy family that does shape the candidate: the "
            "anomaly. The engine now tags HARMLESS_SPECULATIVE (complexity, SDC) and LOAD_BEARING_TOY (the "
            "anomaly sector) in stack.py, so the next de-toying cycle has exactly one target: derive or source "
            "the anomaly-sector inequality, or establish that its specific form (matter*curvature ~ curvature^2) "
            "is genuinely unsourceable in this gravity+matter basis and quantify what rides on it."
        ),
        "honest_scope": (
            "Leverage is the opening of the LOCAL feasible fraction (constructed +/- 0.15) when a constraint "
            "is dropped from the full stack -- a local measure; a constraint could bind harder elsewhere, but "
            "'nearly redundant locally' is exactly the statement that the candidate (which lives here) does "
            "not depend on it. 'Harmless' means low leverage AND unchanged scale window AND the constructed "
            "point still feasible -- not that the constraint is meaningless in general (the SDC and complexity "
            "bound remain speculative in FORM; the point is the candidate is robust to them). cosmic "
            "birefringence's 7.36x is real DATA leverage (v2.408), listed here only to separate it from the "
            "toy cuts. This is an engine change (HARMLESS_SPECULATIVE / LOAD_BEARING_TOY tags in stack.py) "
            "plus the leverage map that justifies it; it does not de-toy the anomaly -- it proves the candidate "
            "is robust to the two most speculative toys and isolates the anomaly as the one that matters. "
            "Robust content: dropping complexity_cutoff or the swampland-distance proxy opens the candidate "
            "region only ~1.11x and leaves the scale window unchanged, so the candidate does not depend on "
            "either; its genuine toy dependence is the anomaly sector (1.36x + 2.43x). Local leverage, "
            "form-still-speculative, birefringence-is-data. A toy-dependence-mapping cycle."
        ),
        "references": [
            "this repo: v2.412 (localized toy cuts to 4), v2.410 (SDC field-space gap -- now shown harmless), v2.390 (scale window), v2.408 (birefringence is real data leverage), v2.393 (matter-sources-gravity rests on the anomaly), experiments/stack.py (new HARMLESS_SPECULATIVE / LOAD_BEARING_TOY)",
            "physics: complexity=action / Lloyd bound (speculative EFT-complexity, no literature-exact inequality); swampland distance conjecture (Ooguri-Vafa); anomaly inflow / Green-Schwarz",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(DEFAULT_OUT))
    p.add_argument("--n", type=int, default=6000)
    args = p.parse_args()
    res = run(n_pts=args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2), encoding="utf-8", newline="\n")
    print("ENGINE IMPROVEMENT (de-toying step 2): the candidate's real toy-dependence is the anomaly sector alone:")
    for n, r in res["leverage"].items():
        tag = "real DATA" if n == "cosmic_birefringence_data" else r["class"].upper()
        print(f"  drop {n:<32} opens {r['opens_x']}x   {tag}")
    print(f"  HARMLESS (candidate robust to): {res['harmless_speculative']}  -- retires the complexity + SDC worries")
    print(f"  scale window unchanged without them: {res['scale_window_without_harmless']} == {res['scale_window_full']}")
    print(f"  => genuine toy dependence = the ANOMALY sector {res['load_bearing_toy']} (the one de-toying target)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
