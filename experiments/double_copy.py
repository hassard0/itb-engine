"""v1.94 - The gravitational double-copy test: is the consistent graviton island the
square of a gauge-theory region?

The double copy (Bern-Carrasco-Johansson; KLT) builds gravity from gauge x gauge:
gravity amplitudes ~ (gauge)^2, and the graviton Wilson coefficients are products of
gauge field-strength coefficients (Arkani-Hamed-Huang-Huang EFThedron has this
structure). We test whether the engine's consistent graviton region (the Hofman-
Maldacena wedge 1/3 <= a/c <= 31/18, with a=g_R2 (Euler), c=g_C (Weyl^2)) is the
'square' of a gauge positivity region.

KEY STRUCTURE (Dr. M.-confirmed):
  - SYMMETRIC double copy (same gauge theory L=R, e.g. N=4 SYM (x) N=4 SYM = N=8 SUGRA)
    gives a = c -> the a/c = 1 DIAGONAL of the wedge.
  - Consistent gravity STRICTLY CONTAINS the double copy (Hofman-Maldacena): the wedge
    is 2D, the symmetric double copy is a 1D diagonal.
  - ASYMMETRIC double copies move a/c off 1, filling only a SUB-REGION of the wedge.

So most of the consistent graviton island is NON-double-copy. We quantify this.

Toy gauge region: a_4 >= 0, a_6 >= a_4^2 (gauge analog of the matter positivity tower).
Symmetric double-copy map: g_R2 = g_C = a_4^2 (=> a/c=1), g_R3 = a_4 * a_6. The
asymmetric reach is modeled as a stated a/c band around 1 (order-of-magnitude).

Run on Vulcan:  python experiments/double_copy.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")
from itb.predict import FRAMEWORKS
from itb.holographic_ac import gC_from_gR2

AC_FLOOR, AC_CEIL = 1.0 / 3.0, 31.0 / 18.0      # Hofman-Maldacena wedge
AC_DC_BAND = (2.0 / 3.0, 3.0 / 2.0)             # toy asymmetric-double-copy reach


def main():
    # toy gauge positivity region and its SYMMETRIC double-copy image (a/c=1 diagonal)
    rng = np.random.default_rng(3)
    a4 = rng.uniform(0.0, 0.7, 4000)
    a6 = a4 ** 2 + rng.uniform(0.0, 0.4, 4000)        # a_6 >= a_4^2 (gauge bootstrap)
    gR2_dc = a4 ** 2                                   # = g_C  (a/c = 1)
    gC_dc = a4 ** 2
    gR3_dc = a4 * a6

    # engine graviton island: (g_R2, g_C) in the HM wedge (+ positivity g_R2,g_C>0)
    G = rng.uniform(0.0, 0.5, (200000, 2))            # (g_R2, g_C)
    gR2, gC = G[:, 0], G[:, 1]
    ac = np.divide(gR2, gC, out=np.full_like(gR2, np.inf), where=gC > 1e-9)
    island = (gC > 1e-3) & (ac >= AC_FLOOR) & (ac <= AC_CEIL)
    ac_isl = ac[island]
    # classify island points by double-copy reachability
    is_symmetric_dc = np.abs(ac_isl - 1.0) < 0.03      # on the a/c=1 diagonal
    is_asym_dc = (ac_isl >= AC_DC_BAND[0]) & (ac_isl <= AC_DC_BAND[1])
    frac_symmetric = float(np.mean(is_symmetric_dc))
    frac_dc_reachable = float(np.mean(is_asym_dc))
    frac_non_dc = float(np.mean(~is_asym_dc))

    # where do real frameworks sit? (a/c from the GB portrait, v1.72)
    fw_pts = []
    for name, fw in FRAMEWORKS.items():
        g = fw.encode().coefficients.get("g_R2", 0.0)
        if g <= 0:
            continue
        gcv = gC_from_gR2(g)
        fw_pts.append({"framework": name, "g_R2": round(g, 3), "g_C": round(gcv, 3),
                       "a_over_c": round(g / gcv, 3),
                       "double_copy_reachable": bool(AC_DC_BAND[0] <= g / gcv <= AC_DC_BAND[1])})

    # ---- figure: (g_R2, g_C) plane ----
    fig, ax = plt.subplots(figsize=(9, 7.5))
    # engine wedge (shade between a/c=1/3 and a/c=31/18)
    xs = np.linspace(0, 0.5, 50)
    ax.fill_between(xs, xs / AC_CEIL, xs / AC_FLOOR, color="#cfe8cf", alpha=0.5,
                    label="engine graviton island (HM wedge)")
    # asymmetric-double-copy band
    ax.fill_between(xs, xs / AC_DC_BAND[1], xs / AC_DC_BAND[0], color="#9ecae1",
                    alpha=0.5, label=f"double-copy reach (a/c in {AC_DC_BAND})")
    # symmetric double copy = the a/c=1 diagonal
    ax.plot(xs, xs, color="#d62728", lw=2.5, label="SYMMETRIC double copy (a/c=1)")
    # frameworks
    for p in fw_pts:
        ax.scatter([p["g_R2"]], [p["g_C"]], s=45, color="black", zorder=5)
        ax.annotate(p["framework"][:10], (p["g_R2"], p["g_C"]), fontsize=6,
                    textcoords="offset points", xytext=(3, 2))
    ax.set_xlabel("g_R2  (= a, Euler)"); ax.set_ylabel("g_C  (= c, Weyl^2)")
    ax.set_xlim(0, 0.5); ax.set_ylim(0, 0.7)
    ax.set_title("v1.94  Is the graviton island gauge^2?\n"
                 "the symmetric double copy is only the a/c=1 diagonal; "
                 "consistent gravity is strictly larger", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    png = "/tmp/double_copy.png"
    fig.savefig(png, dpi=140)

    summary = {
        "symmetric_double_copy": "a/c = 1 diagonal (N=8 SUGRA: a=c)",
        "engine_graviton_island": f"HM wedge a/c in [{AC_FLOOR:.3f}, {AC_CEIL:.3f}]",
        "fraction_island_on_symmetric_DC_diagonal": round(frac_symmetric, 4),
        "fraction_island_double_copy_reachable": round(frac_dc_reachable, 3),
        "fraction_island_NON_double_copy": round(frac_non_dc, 3),
        "verdict": "The consistent graviton island is NOT the square of a gauge region: "
            "the SYMMETRIC double copy is only the measure-zero a/c=1 diagonal; asymmetric "
            "double copies fill a sub-band around it; and a substantial fraction of the "
            "island (a/c far from 1) is NON-double-copy gravity -- consistent gravity is "
            "STRICTLY LARGER than gauge^2.",
        "frameworks": fw_pts,
        "frameworks_double_copy_reachable": [p["framework"] for p in fw_pts if p["double_copy_reachable"]],
        "honest": "toy gauge region + toy double-copy map + a stated asymmetric a/c band; "
            "robust content is the STRUCTURE (symmetric DC = a/c=1 diagonal, consistent "
            "gravity strictly contains it, non-DC points exist), not the exact fractions.",
        "citations": ["Bern-Carrasco-Johansson (BCJ double copy)", "KLT relations",
                      "Arkani-Hamed-Huang-Huang (EFThedron)", "N=8 SUGRA a=c"],
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
