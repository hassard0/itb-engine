"""v2.259 - The cosmological constant problem: 'the worst prediction in physics', and the QG angle.

A fresh fundamental-QG cycle, connecting to the engine's cc_naturalness experiment. The observed dark
energy has the density of a ~2.3 meV scale,

    rho_Lambda ~ (2.3 meV)^4 ,

but quantum field theory predicts a vacuum energy of order the UV cutoff to the fourth power,
rho_vac ~ M_cutoff^4. The mismatch is enormous and grows with the cutoff -- at the Planck scale it is
~1e122, the largest discrepancy between theory and observation in the history of physics. Even at the
lowest reasonable cutoff (the electron mass) it is still ~1e33. A consistent quantum-gravity theory
must explain why the vacuum energy is ~120 orders of magnitude smaller than its natural value (and
why it is nonzero and positive at all).

The quantum-gravity / swampland angle: the de Sitter conjecture (Obied-Ooguri-Spodyneiko-Vafa 2018)
holds that a stable positive cosmological constant (de Sitter vacuum) may be FORBIDDEN in quantum
gravity, |grad V| >= c V / M_Pl -- so the observed acceleration would be QUINTESSENCE (a rolling
field), not a true Lambda. This ties the CC problem to the Swampland Distance Conjecture (v2.255) and
the engine's swampland sector.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VERSION = "v2.259"
DEFAULT_OUT = Path("experiments/results/v2.259/qnm_cosmological_constant_problem.json")
RHO_L_QUARTER_eV = 2.3e-3        # dark-energy density scale (eV), (2.3 meV)^4
M_PL_eV = 1.22e28


def overshoot(cutoff_eV: float) -> float:
    """rho_vac/rho_Lambda = (M_cutoff / rho_Lambda^{1/4})^4."""
    return (cutoff_eV / RHO_L_QUARTER_eV) ** 4


def run() -> dict:
    cutoffs = [("Planck", M_PL_eV), ("GUT", 2e25), ("electroweak (TeV)", 1e12),
               ("QCD (0.2 GeV)", 2e8), ("electron mass", 5.11e5)]
    rows = [{"cutoff": name, "cutoff_eV": M, "overshoot_ratio": overshoot(M)} for name, M in cutoffs]
    return {
        "version": VERSION,
        "method": ("observed rho_Lambda ~ (2.3 meV)^4 vs QFT vacuum estimate rho_vac ~ M_cutoff^4; "
                   "overshoot = (M_cutoff/rho_Lambda^{1/4})^4; de Sitter swampland conjecture"),
        "dark_energy_scale_meV": RHO_L_QUARTER_eV * 1e3,
        "vacuum_energy_overshoot": rows,
        "planck_overshoot": overshoot(M_PL_eV),
        "de_sitter_conjecture": {
            "statement": "|grad V| >= c V / M_Pl -- a stable positive CC may be forbidden in QG",
            "implication": "dark energy as QUINTESSENCE (rolling field), not a true Lambda",
            "links": "Swampland Distance Conjecture (v2.255); engine swampland sector",
        },
        "finding": (
            "The cosmological constant problem is the largest theory-vs-observation gap in physics. "
            "The observed dark energy is a ~2.3 meV scale, but the QFT vacuum energy ~M_cutoff^4 "
            f"overshoots it by ~{overshoot(M_PL_eV):.0e} at the Planck cutoff (the famous ~1e122), "
            f"~{overshoot(1e12):.0e} even at the electroweak scale, and still ~{overshoot(5.11e5):.0e} "
            "at the electron mass -- there is NO cutoff at which naive QFT gets it remotely right. A "
            "consistent quantum-gravity theory must explain this ~120-order suppression (and the "
            "small positive value). The QG/swampland angle sharpens it: the de Sitter conjecture "
            "suggests a true positive Lambda is forbidden in quantum gravity, so the acceleration "
            "would be quintessence (a rolling field obeying |grad V| >= c V/M_Pl) rather than a "
            "constant -- a falsifiable prediction (a time-varying dark-energy equation of state w != "
            "-1) that ties the CC problem to the Swampland Distance Conjecture (v2.255) and the "
            "engine's cc_naturalness / swampland sector. The CC problem is thus both the sharpest "
            "QG naturalness puzzle and a place where the swampland program makes contact with "
            "observation."
        ),
        "honest_scope": (
            "The vacuum-energy estimate rho_vac ~ M_cutoff^4 is the NAIVE QFT scaling -- the true "
            "story involves cancellations, the cosmological-constant renormalization, SUSY (which "
            "would soften it to the SUSY-breaking scale, still ~1e60 off), and the measure/anthropic "
            "and sequestering proposals; the ~1e122 is the famous order-of-magnitude statement of "
            "the problem, not a precise prediction. The de Sitter conjecture is CONTROVERSIAL (its "
            "constant c and even its validity are debated; many string constructions claim metastable "
            "dS). The observed rho_Lambda is well-measured. Self-contained reconstruction of a "
            "standard fundamental puzzle and its QG framing, not a new result. Parity-odd g_R4_c3 "
            "stays dark (v2.209)."
        ),
        "references": [
            "Weinberg, Rev. Mod. Phys. 61 (1989) 1 -- the cosmological constant problem",
            "Obied, Ooguri, Spodyneiko, Vafa (2018); Agrawal, Obied, Steinhardt, Vafa (2018) -- de Sitter conjecture",
            "this repo: v2.255 (Swampland Distance Conjecture); engine cc_naturalness",
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
    print(f"dark-energy scale: rho_Lambda^(1/4) = {res['dark_energy_scale_meV']:.1f} meV")
    print("QFT cutoff           vacuum-energy overshoot")
    for r in res["vacuum_energy_overshoot"]:
        print(f"  {r['cutoff']:20s} {r['overshoot_ratio']:.1e}")
    print(f"de Sitter conjecture -> {res['de_sitter_conjecture']['implication']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
