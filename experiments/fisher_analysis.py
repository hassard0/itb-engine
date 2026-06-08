"""Fisher-information / sloppiness analysis of the observable set (v1.35).

v1.29 showed the exclusion-count priority metric saturates. The principled
replacement is the Fisher information metric: which COMBINATIONS of Wilson
coefficients can the observables actually resolve (stiff directions), and which
are observationally invisible (sloppy directions)?

The engine's forward amplitudes are LINEAR in the coefficients
  matter:   g_4 s^2 + g_6 s^3 + g_8 s^4
  graviton: g_R2 s^2 + g_R3 s^3
  parity:   g_R2_parity s^2 + g_R3_parity s^3
so the Jacobian J = d(observable)/d(coeff) is constant (theory-independent) and
the Fisher metric F = J^T J / sigma^2 is a single fixed matrix. Its eigenvalues
span many orders of magnitude (a "sloppy model"): large = well-measured stiff
direction, tiny = unmeasurable sloppy direction.

We then cross-reference with v1.33's freedom map: a coefficient that is both
LOOSE (constraints don't pin it) and STIFF (observations can resolve it) is the
ideal discriminator; loose + sloppy = an irreducible degeneracy.
"""

import json
import sys

import numpy as np

sys.path.insert(0, ".")

KEYS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_R2_parity", "g_R3_parity"]
S = np.linspace(0.2, 1.0, 9)

# each observable row-block: coeff -> power; sigma is that observable's precision
OBSERVABLES = {
    "matter":   ({"g_4": 2, "g_6": 3, "g_8": 4}, 0.02),
    "graviton": ({"g_R2": 2, "g_R3": 3}, 0.02),
    "parity":   ({"g_R2_parity": 2, "g_R3_parity": 3}, 0.005),
}


def build_jacobian():
    rows = []
    for terms, sigma in OBSERVABLES.values():
        for s in S:
            row = np.zeros(len(KEYS))
            for k, p in terms.items():
                row[KEYS.index(k)] = s ** p / sigma   # weight by 1/sigma
            rows.append(row)
    return np.array(rows)


def main():
    J = build_jacobian()
    F = J.T @ J                       # Fisher metric (sigma already folded in)
    evals, evecs = np.linalg.eigh(F)
    order = np.argsort(-evals)
    evals = evals[order]; evecs = evecs[:, order]

    # normalize for readability
    cond = float(evals[0] / evals[evals > 0].min()) if (evals > 0).any() else float("inf")

    modes = []
    for i in range(len(KEYS)):
        v = evecs[:, i]
        loadings = {k: round(float(v[j]), 2) for j, k in enumerate(KEYS)}
        dom = sorted(loadings.items(), key=lambda kv: -abs(kv[1]))[:3]
        modes.append({"eigenvalue": float(evals[i]),
                      "relative": float(evals[i] / evals[0]),
                      "dominant": dom})

    # per-coefficient measurability = diagonal of F^{-1} (variance) -> 1/sqrt = resolution
    Finv = np.linalg.pinv(F)
    resolution = {k: float(np.sqrt(Finv[i, i])) for i, k in enumerate(KEYS)}

    # freedom map (v1.33) for cross-reference
    freedom = {"g_8": 0.471, "g_6": 0.323, "g_4": 0.293, "g_R2": 0.237,
               "g_R3": 0.220, "g_R2_parity": 0.193, "g_R3_parity": 0.117}

    out = {"condition_number": cond, "modes": modes, "resolution": resolution,
           "freedom_range": freedom}
    with open("experiments/out_fisher.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"=== FISHER / SLOPPINESS ANALYSIS ===")
    print(f"  condition number (stiffest/sloppiest eigenvalue): {cond:.1f}  "
          f"(>>1 => sloppy model)")
    print("\n  eigen-modes (stiff -> sloppy):")
    for i, m in enumerate(modes, 1):
        tag = "STIFF" if m["relative"] > 0.1 else ("sloppy" if m["relative"] > 1e-3 else "INVISIBLE")
        dom = ", ".join(f"{k}={v:+.2f}" for k, v in m["dominant"])
        print(f"   mode {i} [{tag:9}] rel={m['relative']:.1e}  ({dom})")

    print("\n  per-coefficient: freedom (constraints) vs resolution (observations)")
    print(f"   {'coeff':<14}{'freedom-range':>14}{'obs-resolution':>16}  verdict")
    for k in sorted(KEYS, key=lambda k: -freedom[k]):
        fr = freedom[k]; res = resolution[k]
        # loose+well-resolved = good discriminator; loose+poorly-resolved = degeneracy
        if fr > 0.25 and res < 0.15:
            verd = "GOOD DISCRIMINATOR (loose & measurable)"
        elif fr > 0.25 and res >= 0.15:
            verd = "DEGENERACY (loose but unmeasurable)"
        elif fr <= 0.25 and res < 0.15:
            verd = "robust prediction (pinned & measurable)"
        else:
            verd = "pinned & hard to measure"
        print(f"   {k:<14}{fr:>14.3f}{res:>16.3f}  {verd}")
    print(f"\nwrote experiments/out_fisher.json")


if __name__ == "__main__":
    main()
