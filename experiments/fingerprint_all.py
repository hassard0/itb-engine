"""Observable-space fingerprint of all theories: catalogued + discovered (v1.34).

Places the 5 catalogued frameworks and the 3 engine-discovered theories in
observable space (sector forward amplitudes) and reports, for each pair, the
observable that separates them most and the overall observable distance. Answers
"where do the discovered theories sit relative to known physics, and what would
tell them apart?".
"""

import json
import sys

import numpy as np

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT

sys.path.insert(0, ".")

S = np.linspace(0.2, 1.0, 9)
SECTORS = {
    "matter": [("g_4", 2), ("g_6", 3), ("g_8", 4)],
    "graviton": [("g_R2", 2), ("g_R3", 3)],
    "parity": [("g_R2_parity", 2), ("g_R3_parity", 3)],
}
THEORIES = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
            CausalDynamicalTriangulation(), DiscoveredNovel(),
            DiscoveredParityViolating(), DiscoveredHighG8()]


def amp(theory, terms):
    c = theory.encode().coefficients
    return sum(c.get(k, 0.0) * S ** p for k, p in terms)


def main():
    names = [t.name for t in THEORIES]
    # full observable vector per theory (all sectors concatenated)
    vecs = {t.name: np.concatenate([amp(t, SECTORS[s]) for s in SECTORS]) for t in THEORIES}

    # pairwise observable distance + dominant discriminating sector
    pairs = []
    for i in range(len(THEORIES)):
        for j in range(i + 1, len(THEORIES)):
            a, b = THEORIES[i].name, THEORIES[j].name
            dist = float(np.linalg.norm(vecs[a] - vecs[b]))
            sect = max(SECTORS, key=lambda s: float(np.max(np.abs(
                amp(THEORIES[i], SECTORS[s]) - amp(THEORIES[j], SECTORS[s])))))
            pairs.append({"a": a, "b": b, "obs_distance": dist, "best_sector": sect})
    pairs.sort(key=lambda p: p["obs_distance"])

    # nearest observational neighbour of each discovered theory among catalogued
    catalogued = {"pure_gr", "string_tree_eft", "asymptotic_safety", "lqg_induced", "cdt"}
    neighbours = {}
    for disc in ("discovered_novel", "discovered_parity_violating", "discovered_high_g8"):
        dd = {nm: float(np.linalg.norm(vecs[disc] - vecs[nm])) for nm in catalogued}
        nn = min(dd, key=dd.get)
        neighbours[disc] = {"nearest_catalogued": nn, "distance": dd[nn]}

    out = {"pairs": pairs, "discovered_neighbours": neighbours}
    with open("experiments/out_fingerprint.json", "w") as f:
        json.dump(out, f, indent=2)

    print("=== Discovered theories: nearest catalogued framework in OBSERVABLE space ===")
    for disc, d in neighbours.items():
        print(f"  {disc:<28} nearest = {d['nearest_catalogued']:<16} obs-dist {d['distance']:.3f}")
    print("\n=== closest / most-degenerate theory pairs (hardest to tell apart) ===")
    for p in pairs[:4]:
        print(f"  {p['a']:<22} ~ {p['b']:<24} obs-dist {p['obs_distance']:.3f} "
              f"(best sector: {p['best_sector']})")
    print("\n=== most-separated pairs (easiest to tell apart) ===")
    for p in pairs[-4:]:
        print(f"  {p['a']:<22} vs {p['b']:<24} obs-dist {p['obs_distance']:.3f} "
              f"(best sector: {p['best_sector']})")
    print("\nwrote experiments/out_fingerprint.json")


if __name__ == "__main__":
    main()
