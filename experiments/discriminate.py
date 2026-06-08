"""Honest experiment guidance via first-disagreement (v1.30).

v1.29 showed the exclusion-count priority metric saturates. The engine's
first_disagreement machinery gives the honest, non-saturating alternative: for
each pair of *surviving* frameworks, which physical observable separates them
most (largest signal in coefficient space, hence highest S/N at fixed
precision)? That is a real experimental recommendation — "to tell A from B,
measure this" — and it does not depend on an arbitrary forecast central value.

Observables (forward 2->2 amplitudes over an energy grid, each sector isolated):
  matter    M_m(s)  = g_4 s^2 + g_6 s^3 + g_8 s^4
  graviton  M_g(s)  = g_R2 s^2 + g_R3 s^3
  parity    M_p(s)  = g_R2_parity s^2 + g_R3_parity s^3
"""

import json
import sys

import numpy as np

from itb.first_disagreement import first_disagreement
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.observables import Observable

sys.path.insert(0, ".")

S = np.linspace(0.2, 1.0, 9)


class SectorAmplitude(Observable):
    def __init__(self, terms):
        # terms: list of (coeff_key, power)
        self.terms = terms

    def predict(self, theory):
        out = np.zeros_like(S)
        for key, p in self.terms:
            out = out + theory.coefficients.get(key, 0.0) * S ** p
        return out

    def jacobian(self, theory, params):
        return np.zeros((len(S), len(params)))


OBSERVABLES = {
    "matter_forward_amplitude": SectorAmplitude([("g_4", 2), ("g_6", 3), ("g_8", 4)]),
    "graviton_forward_amplitude": SectorAmplitude([("g_R2", 2), ("g_R3", 3)]),
    "parity_amplitude": SectorAmplitude([("g_R2_parity", 2), ("g_R3_parity", 3)]),
}
SIGMA = 0.02  # reference measurement precision


def main():
    survivors = [StringTreeEFT(), AsymptoticSafety(), CausalDynamicalTriangulation()]
    rep = first_disagreement(survivors, OBSERVABLES, sigma=SIGMA)

    # best discriminator per pair
    best_per_pair = {}
    for s in rep.pair_scores:
        key = (s.framework_a, s.framework_b)
        if key not in best_per_pair or s.max_signal_to_noise > best_per_pair[key].max_signal_to_noise:
            best_per_pair[key] = s

    print(f"=== Honest experiment guidance: best observable per surviving-framework pair "
          f"(sigma={SIGMA}) ===")
    out = {"sigma": SIGMA, "pairs": []}
    for (a, b), s in sorted(best_per_pair.items(), key=lambda kv: -kv[1].max_signal_to_noise):
        print(f"  {a:<18} vs {b:<18}: measure {s.observable:<28} "
              f"signal={s.signal:.3f}  S/N={s.max_signal_to_noise:.1f}")
        out["pairs"].append({"a": a, "b": b, "observable": s.observable,
                             "signal": s.signal, "snr": s.max_signal_to_noise})

    # also: LQG vs each survivor (what would confirm LQG if it somehow held)
    print("\n  (reference) LQG vs each survivor — what most separates the excluded LQG:")
    for surv in survivors:
        rep2 = first_disagreement([LQGInduced(), surv], OBSERVABLES, sigma=SIGMA)
        s = rep2.best_pair
        print(f"    LQG vs {surv.name:<18}: {s.observable:<28} signal={s.signal:.3f}  S/N={s.max_signal_to_noise:.1f}")

    with open("experiments/out_discriminate.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote experiments/out_discriminate.json")


if __name__ == "__main__":
    main()
