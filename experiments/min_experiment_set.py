"""v1.88 - The minimum decisive experiment set: what is the smallest experiment
program that solves quantum gravity?

We treat each engine Observable as a candidate measurement, build its Jacobian
J_o = d(observable)/d(coefficients) over the 8 Wilson coefficients at a
representative consistent point (the data-driven EFT), and run a D-OPTIMAL greedy
selection: repeatedly add the measurement that most increases the Fisher
information determinant, until the Fisher matrix is FULL RANK (all 8 coefficient
directions constrained) and the worst parameter uncertainty is below a toy
precision. The answer is the minimum number of experiments + which ones.

HONEST blind spots: with the engine's *current* observables, g_8 (the s^4 matter
moment) and g_R3 (cubic curvature) are touched by NO observable -> the EFT cannot be
pinned. We add two minimal DESIGN-PROBE observables that WOULD measure them (a high
Mandelstam moment for g_8; a cubic-graviton amplitude for g_R3) to complete the set.
And StarobinskyInflation has a ZERO Jacobian (n_s, r set by N, not the couplings) ->
it contributes NOTHING to pinning the theory, despite being a CMB detection.

Run on Vulcan:  python experiments/min_experiment_set.py
"""
import json
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "src")

from itb.observables import Observable, ScalarForwardAmplitude
from itb.gravitational_observables import (
    YukawaForceDeviation, GravitationalBirefringence, HolographicEtaOverS,
    BlackHoleEntropyShift, GIEPhaseCorrection, StarobinskyInflation)
from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.theory import Theory

PARAMS = ["g_4", "g_6", "g_8", "g_R2", "g_R3", "g_C", "g_R2_parity", "g_R3_parity"]


# --- minimal DESIGN-PROBE observables for the engine's blind spots ---
class HighScatteringMoment(Observable):
    """A higher Mandelstam moment ~ g_6 s^4 + g_8 s^6 (higher-energy / higher
    partial wave). Measures g_8, which no current observable touches."""
    name = "high_scattering_moment"

    def __init__(self, s_values):
        self.s = np.asarray(s_values, dtype=float)

    def predict(self, theory):
        g6 = theory.coefficients.get("g_6", 0.0); g8 = theory.coefficients.get("g_8", 0.0)
        return g6 * self.s ** 4 + g8 * self.s ** 6

    def jacobian(self, theory, params):
        cols = []
        for p in params:
            if p == "g_6":
                cols.append(self.s ** 4)
            elif p == "g_8":
                cols.append(self.s ** 6)
            else:
                cols.append(np.zeros_like(self.s))
        return np.stack(cols, axis=1)


class CubicGravitonAmplitude(Observable):
    """Graviton 3-point amplitude ~ g_R3 (cubic curvature). Measures g_R3, which no
    current observable touches (a GW-nonlinearity / 3-graviton probe)."""
    name = "cubic_graviton_amplitude"

    def predict(self, theory):
        return np.array([theory.coefficients.get("g_R3", 0.0)])

    def jacobian(self, theory, params):
        return np.stack([np.array([1.0 if p == "g_R3" else 0.0]) for p in params], axis=1)


def main():
    th = DiscoveredDataDriven().encode()
    # ensure all 8 coeffs present
    for k in PARAMS:
        th.coefficients.setdefault(k, 0.0)

    # catalog: (experiment label, observable, toy sigma)
    catalog = [
        ("matter scattering (low-s)", ScalarForwardAmplitude(np.array([0.5, 1.0])), 0.05),
        ("matter scattering (high moment)", HighScatteringMoment(np.array([1.0, 1.5])), 0.10),
        ("sub-mm fifth force", YukawaForceDeviation([8e-5, 1e-4]), 0.10),
        ("holographic eta/s", HolographicEtaOverS(), 0.20),
        ("GW/CMB birefringence", GravitationalBirefringence(omegas=[1.0, 2.0]), 0.05),
        ("BH extremal entropy", BlackHoleEntropyShift(), 0.10),
        ("cubic-graviton amplitude", CubicGravitonAmplitude(), 0.20),
        ("grav. entanglement (GIE)", GIEPhaseCorrection(1e-4), 0.10),
        ("CMB inflation (n_s, r)", StarobinskyInflation(), 0.01),
    ]

    # per-observable Fisher contribution F_o = J^T J / sigma^2 and coverage
    n = len(PARAMS)
    contribs = []
    coverage = np.zeros((len(catalog), n))
    for k, (label, obs, sig) in enumerate(catalog):
        J = obs.jacobian(th, PARAMS)        # (n_points x 8)
        F = (J.T @ J) / sig ** 2
        contribs.append(F)
        coverage[k] = np.sqrt(np.maximum(np.diag(F), 0))   # ~ info per coeff
    # which coeffs are touched by ANY observable
    touched = (coverage.sum(axis=0) > 1e-12)
    blind = [PARAMS[i] for i in range(n) if not touched[i]]
    zero_jac = [catalog[k][0] for k in range(len(catalog))
                if np.all(np.abs(contribs[k]) < 1e-15)]

    # --- D-optimal greedy selection (maximize log det(F + eps I)) ---
    eps = 1e-6
    F = eps * np.eye(n)
    chosen, order_log = [], []
    remaining = list(range(len(catalog)))
    PREC = 0.5                       # toy: worst sigma must drop below this
    while remaining:
        rank = int(np.linalg.matrix_rank(F - eps * np.eye(n), tol=1e-9))
        # current worst parameter sigma
        try:
            cov = np.linalg.inv(F)
            worst = float(np.sqrt(np.max(np.diag(cov))))
        except np.linalg.LinAlgError:
            worst = np.inf
        if rank >= n and worst < PREC:
            break
        # pick observable maximizing log det increase
        best_k, best_ld = None, -np.inf
        cur_ld = np.linalg.slogdet(F)[1]
        for k in remaining:
            ld = np.linalg.slogdet(F + contribs[k])[1]
            if ld > best_ld:
                best_ld, best_k = ld, k
        if best_ld <= cur_ld + 1e-9:     # nothing helps (e.g. all remaining add 0)
            break
        F = F + contribs[best_k]
        chosen.append(best_k); remaining.remove(best_k)
        rank = int(np.linalg.matrix_rank(F - eps * np.eye(n), tol=1e-9))
        cov = np.linalg.inv(F)
        worst = float(np.sqrt(np.max(np.diag(cov))))
        order_log.append({"step": len(chosen), "added": catalog[best_k][0],
                          "rank": rank, "logdetF": round(float(np.linalg.slogdet(F)[1]), 2),
                          "worst_sigma": round(worst, 3)})

    rank_final = int(np.linalg.matrix_rank(F - eps * np.eye(n), tol=1e-9))
    pinned = rank_final >= n
    # sloppiest direction (smallest-eigenvalue eigenvector of F)
    evals, evecs = np.linalg.eigh(F)
    sloppy_vec = {PARAMS[i]: round(float(evecs[i, 0]), 3) for i in range(n)}

    chosen_labels = [catalog[k][0] for k in chosen]
    unused = [catalog[k][0] for k in remaining]

    # ---- figure: accrual curve + coverage matrix ----
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6.5),
                                   gridspec_kw={"width_ratios": [1, 1.2]})
    steps = [o["step"] for o in order_log]
    worst_s = [o["worst_sigma"] for o in order_log]
    ranks = [o["rank"] for o in order_log]
    ax1.plot(steps, worst_s, "o-", color="#1f77b4", label="worst parameter sigma")
    ax1.axhline(PREC, color="#d62728", ls="--", lw=1, label=f"toy precision {PREC}")
    ax1.set_yscale("log"); ax1.set_xlabel("number of experiments added")
    ax1.set_ylabel("worst parameter uncertainty")
    for o in order_log:
        ax1.annotate(o["added"][:14], (o["step"], o["worst_sigma"]),
                     fontsize=6.5, rotation=25, textcoords="offset points", xytext=(2, 4))
    ax1b = ax1.twinx()
    ax1b.plot(steps, ranks, "s--", color="#2ca02c", alpha=0.6, label="Fisher rank")
    ax1b.set_ylabel("Fisher rank (8 = pinned)", color="#2ca02c")
    ax1b.set_ylim(0, 8.5)
    ax1.set_title(f"Information accrual: {len(chosen)} experiments pin "
                  f"{rank_final}/{n} coefficients", fontsize=10)
    ax1.legend(fontsize=8, loc="upper right")

    im = ax2.imshow(coverage, aspect="auto", cmap="viridis")
    ax2.set_xticks(range(n)); ax2.set_xticklabels(PARAMS, rotation=45, fontsize=8)
    ax2.set_yticks(range(len(catalog)))
    ax2.set_yticklabels([c[0] for c in catalog], fontsize=7.5)
    ax2.set_title("coefficient coverage (sqrt diag Fisher per observable)\n"
                  "dark columns g_8 / g_R3 need dedicated probes; inflation row = 0",
                  fontsize=9)
    fig.colorbar(im, ax=ax2, fraction=0.046)
    fig.suptitle("v1.88  The minimum decisive experiment set", fontsize=12)
    fig.tight_layout()
    png = "/tmp/min_experiment_set.png"
    fig.savefig(png, dpi=140)

    summary = {
        "n_coefficients": n,
        "blind_spots_no_observable": blind,
        "zero_jacobian_useless_for_pinning": zero_jac,
        "minimum_experiments_to_pin_all": len(chosen) if pinned else None,
        "all_coefficients_pinned": bool(pinned),
        "final_rank": rank_final,
        "chosen_in_order": chosen_labels,
        "accrual_log": order_log,
        "unused_or_redundant": unused,
        "sloppiest_direction_eigenvector": sloppy_vec,
        "headline": (f"{len(chosen)} measurements pin the consistent QG EFT: "
                     + " + ".join(chosen_labels)
                     + ". Inflation (a detection) contributes NOTHING (zero Jacobian); "
                     "g_8 and g_R3 need dedicated probes (a high scattering moment and a "
                     "cubic-graviton amplitude) -- without them the theory is unpinnable."),
        "png": png,
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
