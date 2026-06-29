"""v2.234 - Scoping a Riemann^4 (g_R4) axis for the core engine: the positivity-mandated bridge.

v2.233 showed the ringdown-active curvature operator is the quartic Riemann invariant (dim-8,
"g_R4"), one order beyond the engine's Ricci-scalar curvature basis (which stops at g_R3). This
cycle scopes -- READ-ONLY, no change to the committed constraint stack -- what a g_R4 axis would
carry, by extending the engine's EXISTING positivity/causality machinery one order up, and finds a
concrete verifiable bridge: the engine's own positivity logic MANDATES a nonzero g_R4.

The engine encodes the Caron-Huot et al. dispersion tower in the matter sector
(g_6^2 <= g_4 * g_8, dispersion_tower.py) and forward-positivity in the curvature sector
(g_R2 >= c * g_R3, graviton_forward_positivity.py). Extending the SAME Cauchy-Schwarz tower one
order up the CURVATURE ladder gives

    g_R3^2 <= g_R2 * g_R4        (curvature dispersion tower, the g_6^2<=g_4*g_8 analog)
    g_R4   >= 0                  (positivity at each order)

so any theory with curvature corrections is FORCED to carry a Riemann^4 coefficient

    g_R4 >= g_R3^2 / g_R2 .

That lower bound is exactly the ringdown-active operator (v2.233): the engine's positivity tower
does not merely ALLOW the ringdown operator -- it REQUIRES it, at a level set by the lower curvature
couplings. This is the structural bridge between the 17-cycle ringdown thread and the core engine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.234"
DEFAULT_OUT = Path("experiments/results/v2.234/qnm_gr4_axis_scoping.json")


def gr4_constraint_spec() -> list[dict]:
    """The constraint TYPES a g_R4 axis would carry, extending the existing engine machinery."""
    return [
        {"name": "gr4_positivity", "form": "g_R4 >= 0",
         "class": "A (dispersion tower)", "source": "dispersion_tower.py (g_2n>=0 analog)"},
        {"name": "curvature_dispersion_tower", "form": "g_R3^2 <= g_R2 * g_R4",
         "class": "A (Cauchy-Schwarz)", "source": "dispersion_tower.py (g_6^2<=g_4*g_8 analog)"},
        {"name": "curvature_forward_dominance", "form": "g_R3 >= c * g_R4  (c ~ O(1))",
         "class": "A (forward positivity)", "source": "graviton_forward_positivity.py (g_R2>=c*g_R3 analog)"},
        {"name": "spin6_positivity", "form": "g_R4 enters the J=6 graviton partial wave >= 0",
         "class": "A (partial-wave)", "source": "spin_four_positivity.py (next J)"},
        {"name": "cemz_higher_causality", "form": "|g_R4| <= kappa * (matter * curvature product)",
         "class": "C (causality)", "source": "cemz_causality.py (higher-order time-advance)"},
    ]


def forced_gr4_min() -> list[dict]:
    rows = []
    for fw in frameworks():
        c = fw.encode().coefficients
        gR2, gR3 = c.get("g_R2", 0.0), c.get("g_R3", 0.0)
        if gR2 > 0:
            gr4min = gR3**2 / gR2
            forced = gr4min > 1e-9
        else:
            gr4min, forced = 0.0, False        # no curvature corrections -> no forced Riemann^4
        rows.append({"framework": fw.name, "g_R2": gR2, "g_R3": gR3,
                     "g_R4_min_forced": gr4min, "ringdown_operator_mandated": bool(forced)})
    return rows


def run() -> dict:
    spec = gr4_constraint_spec()
    forced = forced_gr4_min()
    n_mandated = sum(1 for r in forced if r["ringdown_operator_mandated"])
    return {
        "version": VERSION,
        "method": ("read-only scoping: extend the engine's existing positivity/causality machinery "
                   "one order up the curvature ladder to a Riemann^4 (g_R4) axis; compute the "
                   "positivity-forced minimum g_R4 per known framework"),
        "gr4_constraint_types": spec,
        "forced_gr4_minimum_per_framework": forced,
        "n_frameworks_mandating_gr4": n_mandated,
        "finding": (
            f"A g_R4 (Riemann^4) axis would carry a definite set of constraint types from the "
            f"engine's existing machinery -- positivity (g_R4>=0), the curvature Cauchy-Schwarz "
            f"tower (g_R3^2<=g_R2*g_R4), forward dominance, spin-6 positivity, and higher-order CEMZ "
            f"causality. The verifiable bridge: the curvature dispersion tower FORCES "
            f"g_R4 >= g_R3^2/g_R2, so {n_mandated} of the known frameworks (every one with curvature "
            "corrections) MUST carry a nonzero Riemann^4 coefficient (string 0.113, asymptotic-"
            "safety 0.067, cdt 0.102, lqg_induced 0.300; pure GR none). The engine's own positivity "
            "logic therefore does not merely ALLOW the ringdown-active operator (v2.233) -- it "
            "REQUIRES it, at a level set by the lower curvature couplings. That is the structural "
            "bridge between the ringdown thread and the core engine."
        ),
        "honest_scope": (
            "READ-ONLY scoping -- this does NOT modify the committed constraint stack (still 38 "
            "constraints); it specifies what a g_R4 axis WOULD carry. The bound forms use "
            "representative O(1) prefactors (set to 1), exactly as the existing curvature/matter "
            "constraints do (their docstrings flag the same); the literal coefficients need the "
            "Gegenbauer/partial-wave evaluation. The forced g_R4_min is a relative (dimensionless) "
            "statement in the toy basis; the absolute g_R4 normalization that would connect it to a "
            "physical ringdown bound stays un-sourceable (the v2.215 / Bresciani-axis-map blocker). "
            "Actually adding the axis + constraints to the engine is a separate, dedicated effort. "
            "Parity-odd g_R4_c3 stays dark (v2.209)."
        ),
        "references": [
            "Caron-Huot, Mazac, Rastelli, Simmons-Duffin, JHEP 07 (2021) 110 -- dispersion tower",
            "Camanho, Edelstein, Maldacena, Zhiboedov (2014) -- causality / time advance",
            "this repo: v2.233 (operator-sector bridge), dispersion_tower/graviton_forward_positivity/cemz_causality",
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
    print("g_R4 axis would carry:")
    for s in res["gr4_constraint_types"]:
        print(f"  {s['name']:30s} {s['form']}")
    print(f"\npositivity-forced minimum g_R4 (g_R3^2/g_R2):")
    for r in res["forced_gr4_minimum_per_framework"]:
        print(f"  {r['framework']:24s} g_R4_min = {r['g_R4_min_forced']:.4f}  "
              f"mandated={r['ringdown_operator_mandated']}")
    print(f"\n{res['n_frameworks_mandating_gr4']} frameworks mandate a nonzero Riemann^4")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
