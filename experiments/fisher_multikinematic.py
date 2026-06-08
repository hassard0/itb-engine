"""Can multi-kinematic observables break the matter-sector degeneracy? (v1.36)

v1.35 found g_4/g_6/g_8 observationally degenerate from a single forward
amplitude (monomials s^2,s^3,s^4 are collinear). Physics says the fix is
ANGULAR information: higher-derivative operators source higher partial waves.
We compare three observable designs by their matter-sector Fisher condition
number and the marginal resolution of g_8:

  A. forward only, s in [0.2,1.0]            (v1.35 baseline)
  B. forward only, WIDER s in [0.2,3.0]      (does energy reach help?)
  C. partial waves spin-0/2/4, s in [0.2,1.0]
       spin-0 a_0(s) = g_4 s^2 + g_6 s^3 + g_8 s^4   (all operators)
       spin-2 a_2(s) =          g_6 s^3 + g_8 s^4     (dim>=6 only)
       spin-4 a_4(s) =                    g_8 s^4      (dim-8 only)  <- isolates g_8

The spin structure is the standard statement that a 2k-derivative operator first
contributes to the spin-2k partial wave; the spin-4 wave is sourced ONLY by the
dimension-8 coupling g_8.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

MATTER = ["g_4", "g_6", "g_8"]
SIGMA = 0.02


def _fisher(rows):
    J = np.array(rows) / SIGMA
    F = J.T @ J
    evals = np.linalg.eigvalsh(F)
    cond = float(evals.max() / evals[evals > 1e-12].min()) if (evals > 1e-12).any() else float("inf")
    Finv = np.linalg.pinv(F)
    res = {k: float(np.sqrt(max(Finv[i, i], 0))) for i, k in enumerate(MATTER)}
    return cond, res


def design_forward(s_grid):
    # columns [g_4, g_6, g_8] = [s^2, s^3, s^4]
    return [[s ** 2, s ** 3, s ** 4] for s in s_grid]


def design_partial_waves(s_grid):
    rows = []
    for s in s_grid:
        rows.append([s ** 2, s ** 3, s ** 4])   # spin-0: all
        rows.append([0.0,    s ** 3, s ** 4])   # spin-2: dim>=6
        rows.append([0.0,    0.0,    s ** 4])    # spin-4: dim-8 only
    return rows


def main():
    designs = {
        "A_forward_narrow": design_forward(np.linspace(0.2, 1.0, 9)),
        "B_forward_wide":   design_forward(np.linspace(0.2, 3.0, 9)),
        "C_partial_waves":  design_partial_waves(np.linspace(0.2, 1.0, 9)),
    }
    freedom_g8 = 0.471
    out = {}
    print("=== matter-sector identifiability vs observable design ===")
    print(f"  (g_8 constraint-freedom range = {freedom_g8}; resolvable iff resolution << that)\n")
    print(f"  {'design':<20}{'cond#':>12}{'res g_4':>10}{'res g_6':>10}{'res g_8':>10}  g_8?")
    for name, rows in designs.items():
        cond, res = _fisher(rows)
        resolvable = "RESOLVED" if res["g_8"] < 0.2 * freedom_g8 else (
            "marginal" if res["g_8"] < freedom_g8 else "degenerate")
        out[name] = {"condition_number": cond, "resolution": res, "g_8_status": resolvable}
        print(f"  {name:<20}{cond:>12.1f}{res['g_4']:>10.3f}{res['g_6']:>10.3f}"
              f"{res['g_8']:>10.3f}  {resolvable}")

    with open("experiments/out_fisher_multikinematic.json", "w") as f:
        json.dump(out, f, indent=2)

    a, c = out["A_forward_narrow"], out["C_partial_waves"]
    print(f"\n  forward-only g_8 resolution: {a['resolution']['g_8']:.3f}  ->  "
          f"partial-waves: {c['resolution']['g_8']:.3f}  "
          f"({a['resolution']['g_8']/max(c['resolution']['g_8'],1e-9):.0f}x better)")
    print(f"  condition number: {a['condition_number']:.0f} -> {c['condition_number']:.1f}")
    print("\nwrote experiments/out_fisher_multikinematic.json")


if __name__ == "__main__":
    main()
