"""Combined multi-experiment discrimination (v1.43).

Now that the gravitational observables are first-class (v1.42), compute the TOTAL
discriminating power of the full experimental program — matter forward amplitude
+ graviton amplitude + sub-mm Yukawa + gravitational birefringence — over the
candidate theories. For each framework pair, the separation in units of
measurement noise (S/N) summed over all observables, and which experiment
contributes most. Answers: does the full program resolve every theory, or do
degeneracies (e.g. string vs CDT) survive?
"""

import json
import sys
from itertools import combinations

import numpy as np

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.gravitational_observables import (
    GravitationalBirefringence, YukawaForceDeviation,
)
from itb.observables import Observable
from itb.theory import Theory

sys.path.insert(0, ".")


class SectorAmp(Observable):
    def __init__(self, terms, s):
        self.terms = terms; self.s = np.asarray(s, float)
    def predict(self, theory):
        return sum(theory.coefficients.get(k, 0.0) * self.s ** p for k, p in self.terms)
    def jacobian(self, theory, params):
        return np.zeros((len(self.s), len(params)))


S = np.linspace(0.2, 1.0, 9)
# observable -> (instance, measurement sigma)
OBS = {
    "matter_amplitude": (SectorAmp([("g_4", 2), ("g_6", 3), ("g_8", 4)], S), 0.02),
    "graviton_amplitude": (SectorAmp([("g_R2", 2), ("g_R3", 3)], S), 0.02),
    "submm_yukawa": (YukawaForceDeviation(np.linspace(40e-6, 150e-6, 9)), 0.01),  # 1% force
    "birefringence": (GravitationalBirefringence(np.linspace(0.5, 2.0, 6)), 0.01),
}

FW = [StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
      CausalDynamicalTriangulation(), DiscoveredNovel(),
      DiscoveredParityViolating(), DiscoveredHighG8()]
NAMES = [f.name for f in FW]


def snr_by_obs(a, b):
    """Per-observable S/N separating theories a,b; total = quadrature sum."""
    ta, tb = a.encode(), b.encode()
    per = {}
    for name, (obs, sigma) in OBS.items():
        d = np.asarray(obs.predict(ta)) - np.asarray(obs.predict(tb))
        per[name] = float(np.sqrt(np.sum((d / sigma) ** 2)))
    total = float(np.sqrt(sum(v ** 2 for v in per.values())))
    return total, per


def main():
    pairs = []
    for i, j in combinations(range(len(FW)), 2):
        total, per = snr_by_obs(FW[i], FW[j])
        dom = max(per, key=per.get)
        pairs.append({"a": NAMES[i], "b": NAMES[j], "total_snr": total,
                      "dominant_obs": dom, "per_obs": per})
    pairs.sort(key=lambda p: p["total_snr"])

    out = {"pairs": pairs}
    with open("experiments/out_combined_fisher.json", "w") as f:
        json.dump(out, f, indent=2)

    print("=== COMBINED DISCRIMINATION (full experimental program) ===")
    print("  total S/N per framework pair (quadrature over all 4 experiments),")
    print("  sorted hardest -> easiest; a pair is RESOLVED at total S/N > ~3:\n")
    for p in pairs:
        status = "RESOLVED" if p["total_snr"] > 3 else "degenerate"
        print(f"  {p['a']:<24} vs {p['b']:<24} S/N={p['total_snr']:7.1f} [{status:10}] "
              f"via {p['dominant_obs']}")
    n_res = sum(1 for p in pairs if p["total_snr"] > 3)
    print(f"\n  {n_res}/{len(pairs)} pairs resolved by the full program (S/N>3)")
    hardest = pairs[0]
    print(f"  hardest pair: {hardest['a']} vs {hardest['b']} (S/N {hardest['total_snr']:.1f}); "
          f"best handle: {hardest['dominant_obs']}")
    # which experiment is most often the decisive (dominant) one
    from collections import Counter
    dom = Counter(p["dominant_obs"] for p in pairs)
    print(f"  decisive-experiment tally across pairs: {dict(dom)}")
    print("\nwrote experiments/out_combined_fisher.json")


if __name__ == "__main__":
    main()
