"""v2.253 - Primordial gravitational waves: the direct observational window onto quantum gravity.

The QG-cosmology capstone of the spacetime/propagation thread (v2.251-v2.252). During inflation the
QUANTIZED graviton field's vacuum fluctuations are stretched to cosmological scales, seeding a
primordial gravitational-wave (tensor) background. Its amplitude relative to the scalar (density)
perturbations is the tensor-to-scalar ratio r, which fixes the energy scale of inflation:

    P_t = (2/pi^2)(H/M_Pl)^2 ,   r = P_t / P_s ,
    V^{1/4} = (3/2 pi^2 A_s r)^{1/4} M_Pl ,   H_inf = M_Pl pi sqrt(A_s r / 2) ,

with the measured scalar amplitude A_s ~ 2.1e-9 (Planck) and the reduced Planck mass M_Pl =
2.435e18 GeV. The current bound r < 0.036 (BICEP/Keck 2021) puts inflation near the GUT scale.

The QUANTUM-GRAVITY significance (Krauss & Wilczek 2014): the primordial tensor modes ARE the
zero-point fluctuations of the graviton -- they exist only if the gravitational field is QUANTIZED.
So a detection of r > 0 (primordial B-mode polarization) is direct experimental evidence for the
quantization of gravity, the one place where quantum gravity is observable in nature.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

VERSION = "v2.253"
DEFAULT_OUT = Path("experiments/results/v2.253/qnm_inflation_tensor_qg.json")
M_PL_GEV = 2.435e18         # reduced Planck mass
A_S = 2.1e-9               # Planck scalar amplitude
GUT_GEV = 2e16
LHC_GEV = 1.4e4


def V_quarter_gev(r: float) -> float:
    """Inflation energy scale V^{1/4} = (3/2 pi^2 A_s r)^{1/4} M_Pl."""
    return (1.5 * math.pi**2 * A_S * r) ** 0.25 * M_PL_GEV


def H_inflation_gev(r: float) -> float:
    """Inflationary Hubble rate H = M_Pl pi sqrt(A_s r / 2)."""
    return M_PL_GEV * math.pi * math.sqrt(A_S * r / 2)


def run() -> dict:
    targets = [
        {"r": 0.036, "context": "current bound (BICEP/Keck 2021)"},
        {"r": 0.01, "context": "Planck-era sensitivity"},
        {"r": 0.003, "context": "CMB-S4 target"},
        {"r": 0.001, "context": "LiteBIRD reach"},
    ]
    rows = [{**t, "V_quarter_GeV": V_quarter_gev(t["r"]),
             "H_inflation_GeV": H_inflation_gev(t["r"]),
             "V_quarter_over_GUT": V_quarter_gev(t["r"]) / GUT_GEV} for t in targets]
    return {
        "version": VERSION,
        "method": ("inflationary tensor spectrum: V^{1/4}=(3/2 pi^2 A_s r)^{1/4} M_Pl, "
                   "H=M_Pl pi sqrt(A_s r/2); A_s=2.1e-9, M_Pl=2.435e18 GeV"),
        "scalar_amplitude": A_S,
        "tensor_targets": rows,
        "energy_scale_context": {"GUT_GeV": GUT_GEV, "LHC_GeV": LHC_GEV,
                                 "inflation_over_LHC": V_quarter_gev(0.036) / LHC_GEV},
        "finding": (
            f"The tensor-to-scalar ratio fixes the inflation energy scale: the current bound r < "
            f"0.036 gives V^{{1/4}} < {V_quarter_gev(0.036):.2e} GeV ("
            f"{V_quarter_gev(0.036)/GUT_GEV:.2f} x the GUT scale) and H_inf < "
            f"{H_inflation_gev(0.036):.1e} GeV -- inflation probes physics ~"
            f"{V_quarter_gev(0.036)/LHC_GEV:.0e}x above the LHC. Next-generation experiments reach "
            f"r ~ 0.001 (V^{{1/4}} ~ {V_quarter_gev(0.001):.1e} GeV). The deep significance: the "
            "primordial tensor modes ARE the quantized graviton's zero-point fluctuations stretched "
            "across the sky, so a detection of r > 0 (primordial B-modes) is direct experimental "
            "evidence that the gravitational field is QUANTIZED (Krauss-Wilczek) -- the single place "
            "in nature where quantum gravity is directly observable. This is the cosmological "
            "counterpart of the session's local QG probes (black-hole horizon structure, "
            "superradiance, propagation/parity LIV): the early universe as the highest-energy QG "
            "laboratory."
        ),
        "honest_scope": (
            "Standard single-field slow-roll relations (the consistency between V^{1/4}, H, and r is "
            "exact at leading slow-roll order; A_s is measured, M_Pl fixed). The r BOUND is the "
            "published BICEP/Keck value; r is NOT detected (only bounded), so the graviton-"
            "quantization evidence is PROSPECTIVE -- the Krauss-Wilczek argument is what a future "
            "B-mode detection would establish, with the caveat that some alternatives (e.g. certain "
            "modified-gravity or non-inflationary sources) are debated. Reheating and the tensor tilt "
            "n_t are neglected. Self-contained reconstruction of the standard inflationary energy-"
            "scale relations and their QG meaning, not a new measurement. Parity-odd g_R4_c3 stays "
            "dark (v2.209)."
        ),
        "references": [
            "Krauss & Wilczek, PRD 89 (2014) 047501 -- primordial GWs prove gravity is quantized",
            "BICEP/Keck Collaboration, PRL 127 (2021) 151301 -- r < 0.036",
            "Planck 2018 (A_s); CMB-S4 / LiteBIRD science books -- future r reach",
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
    print("  r        V^{1/4} (GeV)    H_inf (GeV)    /GUT    context")
    for r in res["tensor_targets"]:
        print(f"  {r['r']:.3f}   {r['V_quarter_GeV']:.2e}     {r['H_inflation_GeV']:.2e}   "
              f"{r['V_quarter_over_GUT']:.2f}   {r['context']}")
    print(f"inflation probes ~{res['energy_scale_context']['inflation_over_LHC']:.0e}x above the LHC; "
          "r>0 detection = evidence gravity is quantized")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
