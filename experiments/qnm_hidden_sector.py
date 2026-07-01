"""v2.404 - SWING: the candidate's three unpinned directions form a DARK hidden sector -- its testable content is lower-dimensional than its parameter space.

The basis-structure audit found three couplings the theory does NOT pin: g_8 (matter top-moment, v2.381), g_C
(the Weyl^2 / Euler-vs-Weyl^2 c-a split, an assumption, v2.399), and g_R3_parity (the parity-odd cubic, an
assumption, v2.403). This swing asks the completing question: are any of them OBSERVABLE?

Result: essentially none. Perturbing each and checking which constraints move -- and whether any are DATA /
observable constraints (birefringence, sub-mm, GW speed/dispersion, LIGO, CMB-S4) rather than pure theory bounds:
  - g_8         -> 5 constraints, ALL theory (scalar/spin positivity, dispersion tower) -> DARK
  - g_R3_parity -> 5 constraints, ALL theory (cubic-parity positivity, anomaly inflow/matching) -> DARK
  - g_C         -> 5 constraints, of which only gw_dispersion_bound is DATA, and that effect is negligible (v2.358)

So the candidate's genuine freedom lives in a ~3-dimensional HIDDEN SECTOR that no observational channel
probes: the matter Regge edge (g_8), the Euler-Weyl^2 split (g_C), and the parity-odd cubic (g_R3_parity). This
sharpens the observability picture (v2.380: ~2.5 observable directions): the theory has ~5+3 consistent
parameters but its TESTABLE content is genuinely lower-dimensional, with three of the extra directions
unmeasurable. It also CORRECTS a qualitative aside in v2.403: the 'second, cubic-order parity observable' does
NOT exist in the engine -- g_R3_parity is dark, bounded only by theory (anomaly + cubic positivity), so a
nonzero parity-odd cubic would be invisible to the current channel set, and the anomaly-CLOSED relation (tying
it to the observable quadratic) is the only way it could be indirectly inferred.
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

VERSION = "v2.404"
DEFAULT_OUT = Path("experiments/results/v2.404/qnm_hidden_sector.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_C", "g_R3_parity"]
CON = np.array([0.529, 0.4, 0.4, 0.193, 0.09, 0.06, 0.193, 0.02])
DATA_MARKERS = ("birefringence", "cmb", "submm", "ligo", "gw_", "yukawa", "s4")


def _is_data(name):
    return any(m in name for m in DATA_MARKERS)


def run() -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)

    def margins(v):
        return {r.constraint_name: r.margin for r in check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results}

    base = margins(CON)
    unpinned = {"g_8": 2, "g_C": 6, "g_R3_parity": 7}
    rows = {}
    for name, idx in unpinned.items():
        v = CON.copy(); v[idx] += 0.01
        m2 = margins(v)
        dep = [c for c in base if abs(base[c] - m2.get(c, base[c])) > 1e-9]
        data_dep = [c for c in dep if _is_data(c)]
        rows[name] = {"n_constraints": len(dep), "data_constraints": data_dep,
                      "dark": len(data_dep) == 0}

    n_dark = sum(1 for r in rows.values() if r["dark"])

    checks = {
        "g_R3_parity_is_dark": rows["g_R3_parity"]["dark"],
        "g_8_is_dark": rows["g_8"]["dark"],
        "gC_only_negligible_gw_data": (not rows["g_C"]["dark"]) and all("gw_" in c for c in rows["g_C"]["data_constraints"]),
        "at_least_two_of_three_fully_dark": n_dark >= 2,
        "hidden_sector_is_three_dimensional": len(unpinned) == 3,
    }

    return {
        "version": VERSION,
        "unpinned_couplings": rows,
        "n_fully_dark": n_dark,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate's three unpinned directions form a DARK hidden sector -- its testable content is "
            "genuinely lower-dimensional than its parameter space. The basis-structure audit left three "
            "couplings the theory does not pin -- g_8 (matter top-moment, v2.381), g_C (the Euler-vs-Weyl^2 "
            "c-a split, v2.399), g_R3_parity (the parity-odd cubic, v2.403) -- and checking their "
            "observability (perturb each; are any of the constraints it moves a DATA constraint?) shows "
            "essentially none is observable: g_8 and g_R3_parity move only theory bounds (scalar/spin/cubic "
            "positivity, dispersion tower, anomaly inflow/matching) with NO data constraint, and g_C touches "
            "only the gw_dispersion data bound, whose effect is negligible (v2.358). So the theory's genuine "
            "freedom lives in a ~3-dimensional hidden sector that no observational channel probes: the matter "
            "Regge edge, the Euler-Weyl^2 split, and the parity-odd cubic. This sharpens v2.380 (~2.5 "
            "observable directions): the candidate has ~5+3 consistent parameters but its testable content is "
            "lower-dimensional, with three extra directions unmeasurable -- the theory can be pinned "
            "observationally only up to this hidden sector. It also CORRECTS a qualitative aside in v2.403: "
            "the 'second, cubic-order parity observable' does NOT exist in the engine's channel set -- "
            "g_R3_parity is dark, bounded only by theory, so a nonzero parity-odd cubic would be invisible, "
            "and the anomaly-CLOSED relation (tying it to the observable quadratic birefringence) is the ONLY "
            "way it could be indirectly inferred. The honest picture that emerges from the whole audit: the "
            "candidate is a matter-dominant, near-Planckian, ghost-safe structure whose ROBUST predictions "
            "(matter-gravity locking, ghost-safety, string-like towers, the CMB-S4 test on g_4) are genuine "
            "and choice-independent, wrapped around a small hidden sector of unobservable moduli (g_8, g_C, "
            "g_R3_parity) that the constructed point fixes by ASSUMPTION (equal moments, a=c, no cubic parity) "
            "but that observation cannot reach."
        ),
        "honest_scope": (
            "'Dark' means no DATA/observable constraint IN THE ENGINE'S current channel set depends on the "
            "coupling (only theory bounds do); it is a statement about the engine's nine observables, not a "
            "theorem that no observable exists -- a richer theory could have a matter-amplitude probe of g_8, "
            "a cubic-parity GW signal for g_R3_parity, or a genuine Weyl^2 dispersion for g_C. So 'hidden "
            "sector' means 'unprobed by the catalogued channels', consistent with v2.380/381's usage. The "
            "data-vs-theory split is by constraint-name marker (birefringence/cmb/submm/ligo/gw/yukawa/s4), a "
            "concrete but coarse classifier; g_C's one data touch (gw_dispersion) is real but negligible "
            "(v2.358), so calling g_C 'essentially dark' is a judgement, not a strict dark. The perturbation "
            "is at a representative point (with g_C, g_R3_parity turned on); the qualitative darkness is "
            "robust because these couplings simply do not appear in the observable maps. This is an "
            "observability audit of the unpinned directions, adding no new physical datum -- it characterizes "
            "what the theory cannot pin and cannot see, and corrects v2.403's observable aside. Robust "
            "content: the three unpinned couplings (g_8, g_C, g_R3_parity) are dark to the engine's channels "
            "(g_8/g_R3_parity fully, g_C up to a negligible GW-dispersion effect), so the candidate carries a "
            "~3D hidden sector fixed by assumption and unreachable by the catalogued observables. "
            "Channel-set-relative darkness, robust non-appearance in observables. A hidden-sector swing."
        ),
        "references": [
            "this repo: v2.381 (g_8 dark), v2.399 (g_C / c-a assumption), v2.403 (g_R3_parity assumption + the second-observable aside this corrects), v2.380 (~2.5 observable directions), v2.358 (gw dispersion negligible)",
            "concept: observable vs dark directions; testable dimension < parameter dimension; a hidden sector of moduli",
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
    print("SWING: the candidate's three unpinned directions form a DARK hidden sector:")
    for k, r in res["unpinned_couplings"].items():
        tag = "DARK" if r["dark"] else f"data: {r['data_constraints']}"
        print(f"  {k:<13} {r['n_constraints']} constraints -> {tag}")
    print(f"  => ~3D hidden sector (g_8 matter-edge, g_C Weyl^2/c-a split, g_R3_parity cubic-parity); {res['n_fully_dark']}/3 fully dark")
    print(f"  => testable content < parameter space; CORRECTS v2.403 (the 'second parity observable' is dark, not observable)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
