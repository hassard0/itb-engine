"""v2.301 - Entanglement amplifies the irreducible ringdown: chaining monogamy with the moment tower.

A fresh swing combining the two new sectors. v2.300 showed the entanglement-monogamy bound caps the
leading curvature coupling, g_R2 <= 3 g_4 g_6/(g_4+g_6) (harmonic mean), complementary to the positivity
cap g_R2 <= sqrt(g_4 g_6) (geometric mean). v2.292 showed the curvature moment tower mandates the
ringdown-active Riemann^4 coefficient, g_R4 >= g_R3^2/g_R2. Chain them.

The MINIMUM g_R4 a consistent theory must carry (for a given g_R3) is found by maximizing g_R2 in the
moment-tower floor: g_R4 >= g_R3^2/g_R2 is largest when g_R2 is smallest, so the smallest FORCED g_R4 is

    g_R4_floor = g_R3^2 / g_R2_max ,   g_R2_max = min( entanglement_bound , positivity_bound ) .

Because entanglement caps g_R2 LOWER than positivity in the asymmetric-matter regime, it raises this
floor: entanglement structure AMPLIFIES the irreducible ringdown-active Riemann^4 coefficient. The
amplification over the positivity-only floor is

    g_R4_floor(entanglement) / g_R4_floor(positivity) = positivity_bound / entanglement_bound
        = (g_4 + g_6) / (3 sqrt(g_4 g_6)) = (2/3) * AM/GM(g_4, g_6) ,

which exceeds 1 exactly when the matter couplings are asymmetric enough (AM/GM > 1.5, the v2.300
crossover). So a consistent UV completion with an ASYMMETRIC matter sector is forced -- by entanglement
plus the moment tower together -- to carry a LARGER minimum ringdown deformation than unitarity/causality
(positivity) alone would require.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")
from experiments.stack import frameworks

VERSION = "v2.301"
DEFAULT_OUT = Path("experiments/results/v2.301/qnm_entanglement_amplified_ringdown.json")

PREF = 1.0 / 3.0


def entanglement_bound(g4, g6):
    return g4 * g6 / (PREF * (g4 + g6))


def positivity_bound(g4, g6, kappa=1.0):
    return math.sqrt(kappa * g4 * g6)


def gR4_floor(gR3, gR2_max):
    return gR3 * gR3 / gR2_max if gR2_max > 0 else float("inf")


def run() -> dict:
    rows = []
    for fw in frameworks():
        c = fw.encode().coefficients
        g4, g6, gR2, gR3 = c.get("g_4", 0.0), c.get("g_6", 0.0), c.get("g_R2", 0.0), c.get("g_R3", 0.0)
        if g4 <= 0 or g6 <= 0 or gR2 <= 0:
            continue
        eb, pb = entanglement_bound(g4, g6), positivity_bound(g4, g6)
        gR2_max = min(eb, pb)
        floor_combined = gR4_floor(gR3, gR2_max)
        floor_positivity = gR4_floor(gR3, pb)
        rows.append({"framework": fw.name, "g_4": g4, "g_6": g6, "g_R3": gR3,
                     "entanglement_bound": eb, "positivity_bound": pb,
                     "binding_sector": "entanglement" if eb < pb else "positivity",
                     "gR4_floor": floor_combined, "gR4_floor_positivity_only": floor_positivity,
                     "amplification": floor_combined / floor_positivity})

    # an asymmetric UV completion: entanglement binds -> amplified ringdown floor
    g4a, g6a, gR3a = 5.0, 0.5, 0.4
    eb, pb = entanglement_bound(g4a, g6a), positivity_bound(g4a, g6a)
    asym = {"g_4": g4a, "g_6": g6a, "g_R3": gR3a, "AM_over_GM": (g4a + g6a) / (2 * math.sqrt(g4a * g6a)),
            "entanglement_bound": eb, "positivity_bound": pb,
            "gR4_floor": gR4_floor(gR3a, min(eb, pb)),
            "gR4_floor_positivity_only": gR4_floor(gR3a, pb)}
    asym["amplification"] = asym["gR4_floor"] / asym["gR4_floor_positivity_only"]

    checks = {
        "frameworks_positivity_floored": all(r["binding_sector"] == "positivity" for r in rows),
        "frameworks_amplification_is_one": all(abs(r["amplification"] - 1.0) < 1e-9 for r in rows),
        "asymmetric_entanglement_binds": eb < pb,
        "asymmetric_amplification_exceeds_one": asym["amplification"] > 1.0 + 1e-9,
        "amplification_equals_AMoverGM_times_2_3": abs(
            asym["amplification"] - (2.0 / 3.0) * asym["AM_over_GM"]) < 1e-9,
    }

    return {
        "version": VERSION,
        "method": ("chain the v2.300 entanglement/positivity caps on g_R2 with the v2.292 moment-tower "
                   "floor g_R4>=g_R3^2/g_R2: the minimum forced g_R4 = g_R3^2/min(entanglement,positivity); "
                   "compute the entanglement amplification of the ringdown floor"),
        "framework_floors": rows,
        "asymmetric_test_point": asym,
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "Chaining entanglement monogamy with the curvature moment tower gives a concrete new "
            "prediction: entanglement structure AMPLIFIES the irreducible ringdown-active Riemann^4 "
            "coefficient for asymmetric UV completions. The moment tower forces g_R4 >= g_R3^2/g_R2, so "
            "the smallest g_R4 a consistent theory can carry is g_R3^2 divided by the LARGEST allowed "
            "g_R2 -- and g_R2 is capped by the tighter of entanglement (3 g_4 g_6/(g_4+g_6), harmonic) "
            "and positivity (sqrt(g_4 g_6), geometric). For the engine's frameworks, all mildly "
            "asymmetric, positivity is the binding cap, so their ringdown floor is the positivity value "
            "and entanglement adds no amplification (factor 1). But for an asymmetric matter sector "
            "(here g_4=5, g_6=0.5) entanglement is the tighter cap, so it RAISES the ringdown floor by "
            f"the factor (2/3) AM/GM(g_4,g_6) = {asym['amplification']:.3f} over the positivity-only "
            "floor -- entanglement forces a larger minimum Riemann^4 deformation than unitarity and "
            "causality alone require. So the information-theoretic and amplitude sectors do not just "
            "bound the leading curvature complementarily (v2.300); chained through the moment tower they "
            "make a sharper statement about the OBSERVABLE ringdown operator: in the asymmetric regime "
            "where entanglement bites, a consistent higher-curvature gravity must ring MORE than "
            "positivity predicts. This is the 'it from qubit' structure reaching the ringdown -- "
            "entanglement amplifying a gravitational-wave observable through the consistency chain."
        ),
        "honest_scope": (
            "An exact chaining of two of the engine's encoded bounds (BNOSSW monogamy prefactor 1/3, "
            "positivity kappa=1) with the v2.292/v2.234 moment-tower floor -- algebra, verified. The "
            "amplification factor (2/3) AM/GM is prefactor-ROBUST in form (AM/GM >= 1 always, so "
            "entanglement amplifies whenever it is the binding cap), though the threshold AM/GM = 1.5 "
            "and the crossover shift with the O(1) prefactors (as in v2.300). The 'ringdown floor' is on "
            "the dimensionless coupling g_R4; mapping it to an actual QNM deformation carries the v2.215 "
            "sensitivity and v2.209 dark-parity caveats and the EFT length-scale, so 'rings MORE' is the "
            "coupling-level statement, with the observable amplitude honestly uncertain. The engine's "
            "frameworks are positivity-floored (amplification 1); the amplification is realized only for "
            "asymmetric matter sectors. Toy basis, O(1) prefactors. A fresh-sector new-theory result "
            "chaining entanglement to the ringdown observable."
        ),
        "references": [
            "this repo: v2.300 (entanglement vs positivity), v2.292 (moment-tower g_R4 floor), v2.234 (g_R4 mandate)",
            "Bao et al, 'The Holographic Entropy Cone' (monogamy); Caron-Huot et al 2021 (positivity)",
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
    print("entanglement-amplified ringdown floor (g_R4_floor = g_R3^2 / g_R2_max):")
    print("  framework          binding sector   g_R4 floor   positivity-only   amplification")
    for r in res["framework_floors"]:
        print(f"  {r['framework']:18s} {r['binding_sector']:13s}    {r['gR4_floor']:.4f}      "
              f"{r['gR4_floor_positivity_only']:.4f}            {r['amplification']:.3f}")
    a = res["asymmetric_test_point"]
    print(f"  asymmetric (g4=5,g6=0.5): floor {a['gR4_floor']:.4f} vs positivity-only "
          f"{a['gR4_floor_positivity_only']:.4f} -> entanglement AMPLIFIES x{a['amplification']:.3f}")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
