"""Project all theories onto the (g_8, |parity|) plane (v1.38).

g_8 is the loosest direction of consistent theory space (v1.33) and the parity
sector is the top testable new-physics signal (v1.35). This projects the three
populations onto that plane:
  - catalogued frameworks (string, AS, LQG, CDT, Pure GR)
  - engine-discovered theories (the 3 encoders)
  - the 79 catalog extreme points (v1.32)
and shows that the catalogued frameworks cluster at parity=0 / mid-g8 while the
consistent frontier fans out in both g_8 and parity.
"""

import json
import sys

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT

sys.path.insert(0, ".")


def pt(theory):
    c = theory.encode().coefficients
    return c.get("g_8", 0.0), abs(c.get("g_R2_parity", 0.0)) + abs(c.get("g_R3_parity", 0.0))


def main():
    catalogued = [PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
                  CausalDynamicalTriangulation()]
    discovered = [DiscoveredNovel(), DiscoveredParityViolating(), DiscoveredHighG8()]

    pts = {"catalogued": {fw.name: pt(fw) for fw in catalogued},
           "discovered": {fw.name: pt(fw) for fw in discovered},
           "catalog_extreme": []}
    try:
        cat = json.load(open("experiments/results/out_catalog.json"))["catalog"]
        for e in cat:
            c = e["coeffs"]
            pts["catalog_extreme"].append([c["g_8"],
                                           abs(c["g_R2_parity"]) + abs(c["g_R3_parity"])])
    except Exception:
        pass

    with open("experiments/out_projection.json", "w") as f:
        json.dump(pts, f, indent=2)

    # ASCII scatter: x = g_8 in [0,0.7], y = |parity| in [0,0.16]
    W, H = 56, 16
    grid = [[" "] * W for _ in range(H)]

    def place(g8, par, ch):
        x = min(W - 1, max(0, int(g8 / 0.7 * (W - 1))))
        y = min(H - 1, max(0, int(par / 0.16 * (H - 1))))
        grid[H - 1 - y][x] = ch

    for g8, par in pts["catalog_extreme"]:
        place(g8, par, ".")
    for nm, (g8, par) in pts["catalogued"].items():
        place(g8, par, "F")
    for nm, (g8, par) in pts["discovered"].items():
        place(g8, par, "D")

    print("  (g_8, |parity|) projection   F=catalogued framework  D=discovered  .=catalog-extreme")
    print("  |parity|")
    print("  0.16 +" + "-" * W)
    for r, row in enumerate(grid):
        print(f"       |{''.join(row)}")
    print("  0.00 +" + "-" * W)
    print("       0.0" + " " * (W - 6) + "g_8 0.7")

    print("\n  catalogued frameworks (all at |parity|=0 except LQG):")
    for nm, (g8, par) in pts["catalogued"].items():
        print(f"    {nm:<20} g_8={g8:.3f}  |parity|={par:.3f}")
    print("  discovered theories:")
    for nm, (g8, par) in pts["discovered"].items():
        print(f"    {nm:<28} g_8={g8:.3f}  |parity|={par:.3f}")
    npv = sum(1 for _, p in pts["catalog_extreme"] if p > 0.03)
    print(f"\n  catalog extremes: {len(pts['catalog_extreme'])} points, "
          f"{npv} parity-violating; g_8 spans "
          f"[{min(g for g,_ in pts['catalog_extreme']):.2f}, "
          f"{max(g for g,_ in pts['catalog_extreme']):.2f}]")
    print("\nwrote experiments/out_projection.json")


if __name__ == "__main__":
    main()
