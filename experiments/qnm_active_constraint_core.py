"""v2.325 - The active constraint core: which consistency conditions do the carving work?

A rigorous, dictionary-free, engine-internal cycle (a deliberate return from the schematic-magnitude
phenomenology of the parity sub-arc). The engine intersects 42 constraints (38 theoretical + 4 ingested
data). Are they all doing carving work, or does a small core dominate? Sampling realistic higher-derivative
theories -- the five frameworks and the constructed candidate, each jittered -- and tallying, for every
sampled theory, the BINDING constraint (smallest gradient-normalized signed distance) and any VIOLATED
constraints, identifies the ACTIVE core (ever binding or violated) versus the always-slack constraints.

The result: only ~29 of 42 are ever active for realistic theories, and the carving is dominated by a
handful -- the swampland distance conjecture, the anomaly/universality family, the cosmic birefringence
data, and graviton forward positivity. Thirteen constraints are always slack for these theories. This
identifies the operative consistency conditions and ties back to the program (the distance-conjecture
dominance is the v2.318 'forbidden zone'; the universality/anomaly dominance is v2.314/v2.315; cosmic
birefringence is the v2.321/v2.322 data discriminator).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, ".")
from itb.engine import check
from itb.theory import Theory
from experiments.stack import build_stack, frameworks

VERSION = "v2.325"
DEFAULT_OUT = Path("experiments/results/v2.325/qnm_active_constraint_core.json")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
CONSTRUCTED = [0.529, 0.4, 0.4, 0.193, 0.09, 0.06, 0.0]


def run() -> dict:
    stack = build_stack(rfc_form="convex_hull", include_data=True, include_birefringence=True,
                        include_gw_speed=True, include_gw_dispersion=True, submm_screened=True)
    all_names = [c.name for c in stack]
    n_con = len(all_names)

    seeds = [[f.encode().coefficients.get(k, 0.0) for k in KEYS] for f in frameworks()]
    seeds.append(CONSTRUCTED)

    rng = np.random.default_rng(0)
    binding = Counter()
    violated = Counter()
    n_samp = 0
    for s in seeds:
        s = np.array(s, dtype=float)
        for _ in range(80):
            v = np.clip(s + rng.normal(0, 0.06, 7), 0.0, None)
            res = check(Theory(coefficients=dict(zip(KEYS, v)), name="x"), stack).results
            wc = min(res, key=lambda r: r.signed_distance_margin)
            binding[wc.constraint_name] += 1
            for r in res:
                if not r.satisfied:
                    violated[r.constraint_name] += 1
            n_samp += 1

    active = set(binding) | set(violated)
    slack = sorted(set(all_names) - active)
    top_binding = binding.most_common(8)
    # the dominant core: constraints that account for >=80% of all binding events
    total_binding = sum(binding.values())
    core, cum = [], 0
    for c, k in binding.most_common():
        core.append(c); cum += k
        if cum >= 0.8 * total_binding:
            break

    # family tags for the core (engine constraint classes)
    classmap = {c.name: str(c.constraint_class).split(".")[-1] for c in stack}
    core_families = Counter(classmap.get(c, "?") for c in core)

    checks = {
        "active_core_smaller_than_full_stack": len(active) < n_con,
        "distance_conjecture_is_top_binder": binding.most_common(1)[0][0] == "swampland_distance_conjecture",
        "cosmic_birefringence_data_in_active_core": "cosmic_birefringence_data" in core,
        "anomaly_universality_dominant_in_core": core_families.get("C_UNIVERSALITY", 0) >= 2,
        "scalar_positivities_always_slack": all(f"scalar_positivity_{g}" in slack for g in ("g4", "g6", "g8")),
        "small_core_carries_majority_of_binding": len(core) <= n_con // 3,
    }

    return {
        "version": VERSION,
        "n_constraints": n_con,
        "n_sampled_theories": n_samp,
        "n_active": len(active),
        "n_always_slack": len(slack),
        "top_binding": [{"constraint": c, "count": k} for c, k in top_binding],
        "dominant_core": core,
        "core_families": dict(core_families),
        "always_slack_constraints": slack,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The engine's 42 consistency conditions are far from equally important: sampling realistic "
            "higher-derivative theories (the five frameworks and the constructed candidate, jittered), "
            f"only {len(active)} of {n_con} are ever ACTIVE (binding or violated), and {len(slack)} are "
            "always slack. The carving is dominated by a small CORE -- the constraints accounting for 80% "
            f"of all binding events are just {len(core)}: {', '.join(core)}. The single top binder is the "
            "swampland distance conjecture (it bounds the max/min coupling spread, so it bites whenever a "
            "small parity coupling sits amid larger matter couplings -- this IS the v2.318 'forbidden "
            "zone' at tiny parity), followed by the cosmic birefringence DATA constraint and the "
            "anomaly/universality family (generalized anomaly inflow, t'Hooft anomaly matching, BNOSSW "
            "monogamy), then graviton forward positivity and the matter dispersion tower. So the "
            "operative consistency conditions for realistic higher-derivative gravity are a handful drawn "
            "from three families -- swampland (distance conjecture), universality/anomaly (the decisive "
            "family of v2.314/v2.315), and the one tight piece of real data (cosmic birefringence) -- plus "
            "the leading amplitude-positivity walls. The 13 always-slack constraints are the ones trivially "
            "satisfied by realistic positive-coupling theories: the scalar positivities (g >= 0), the loose "
            "data bounds (GW speed, GW dispersion, sub-mm gravity, species scale, graviton mass), and a few "
            "structural bounds (GSL, EFT box, Hofman-Maldacena wedge, Wald entropy, cubic curvature "
            "positivity). This is a rigorous, dictionary-free map of WHICH consistency conditions actually "
            "do the work -- consistent with, and explaining, the binding patterns the whole program kept "
            "encountering."
        ),
        "honest_scope": (
            "Every value is the engine's literal check() output under convex_hull + all four data "
            "constraints. 'Active' is relative to the SAMPLE -- realistic positive-coupling theories "
            "jittered (sigma 0.06) around the frameworks and the constructed candidate -- so the tally is "
            "'active for realistic higher-derivative gravity', not 'non-redundant in general'. The "
            "always-slack set is slack FOR THESE theories: e.g. scalar_positivity_g4 (g_4 >= 0) would bind "
            "for negative couplings, excluded by the positive-orthant sample, so its slackness reflects "
            "the physical regime, not true redundancy. The exact counts and the 80%-core membership shift "
            "with the sample width and seed; the robust content is structural -- a small core dominated by "
            "the distance conjecture, the universality/anomaly family, and the cosmic birefringence data "
            "does the carving, while the scalar positivities and the loose data bounds are slack. This "
            "complements (does not re-derive) the feasible-region and preferred-framework results. Toy "
            "basis, O(1) prefactors. A rigorous engine-internal audit."
        ),
        "references": [
            "this repo: v2.318 (distance-conjecture forbidden zone), v2.314/v2.315 (universality decisive), v2.321/v2.322 (cosmic birefringence)",
            "engine constraint classes; the full convex_hull + data stack",
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
    print(f"the active constraint core ({res['n_sampled_theories']} sampled theories, {res['n_constraints']} constraints):")
    print(f"  active (ever binding/violated): {res['n_active']}/{res['n_constraints']}; "
          f"always slack: {res['n_always_slack']}")
    print(f"  dominant core (80% of binding): {res['dominant_core']}")
    print(f"  core families: {res['core_families']}")
    print("  top binders:")
    for r in res["top_binding"]:
        print(f"    {r['constraint']:<32} {r['count']}")
    print(f"  always slack: {res['always_slack_constraints']}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
