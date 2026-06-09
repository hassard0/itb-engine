"""Unified framework predictions (v1.63).

One call -> a framework's full falsifiable fingerprint: scope verdict, the
forward-positivity ratio, and every observable signature the program developed
(sub-mm R^2-Yukawa range, GW birefringence, CMB-EB / cosmic-birefringence sibling,
chiral Hellings-Downs circular polarization), plus the inference-relevant
coefficients. Self-contained in src/itb (no experiments/ dependency); feasibility
against the full research stack lives in experiments/stack.py.

Powers the `itb predict <framework>` CLI subcommand.
"""

import math

from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.causal_set import CausalSet
from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.frameworks.discovered import (
    DiscoveredHighG8, DiscoveredNovel, DiscoveredParityViolating,
)
from itb.frameworks.data_driven import DiscoveredDataDriven
from itb.frameworks.emergent_gravity import EmergentGravity
from itb.frameworks.group_field_theory import GroupFieldTheory
from itb.frameworks.horava_lifshitz import HoravaLifshitz
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.pure_gr import PureGR
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.scope import engine_validity

HBARC_eV_m = 1.973e-7
E_LAMBDA_DE = 2.4e-3          # dark-energy gravitational cutoff (v1.44)

FRAMEWORKS = {fw.name: fw for fw in [
    PureGR(), StringTreeEFT(), AsymptoticSafety(), LQGInduced(),
    CausalDynamicalTriangulation(), GroupFieldTheory(), HoravaLifshitz(),
    CausalSet(), EmergentGravity(), DiscoveredNovel(), DiscoveredParityViolating(),
    DiscoveredHighG8(), DiscoveredDataDriven()]}


def predict(name: str) -> dict:
    if name not in FRAMEWORKS:
        raise KeyError(f"unknown framework '{name}'. Known: {sorted(FRAMEWORKS)}")
    fw = FRAMEWORKS[name]
    c = fw.encode().coefficients
    from itb.gravitational_observables import HolographicEtaOverS, BlackHoleEntropyShift
    gR2 = c.get("g_R2", 0.0); gR3 = c.get("g_R3", 0.0)
    eta_s = float(HolographicEtaOverS().predict(fw.encode())[0])
    delta_S_ext = float(BlackHoleEntropyShift().predict(fw.encode())[0])
    parity = abs(c.get("g_R2_parity", 0.0)) + abs(c.get("g_R3_parity", 0.0))
    sc = engine_validity(fw)
    # sub-mm Yukawa range at the dark-energy cutoff (lambda_Y = hbar c / m0, m0 = E/sqrt(6 g_R2))
    lamY_um = (math.sqrt(6 * gR2) * HBARC_eV_m / E_LAMBDA_DE * 1e6) if gR2 > 0 else None
    return {
        "framework": name,
        "citation": fw.citation,
        "coefficients": {k: round(v, 4) for k, v in c.items()},
        "scope": {"in_scope": sc.in_scope, "violations": sc.violations, "note": sc.note},
        "forward_positivity_ratio_gR2_over_gR3": (round(gR2 / gR3, 3) if gR3 > 1e-9 else None),
        "observables": {
            "submm_yukawa_range_um_at_DE_scale": (round(lamY_um, 1) if lamY_um else None),
            "gw_birefringence_g_R2_parity": round(abs(c.get("g_R2_parity", 0.0)), 4),
            "chiral_HD_circular_polarization_pct": [round(parity * 0.3 * 100, 1),
                                                    round(parity * 1.0 * 100, 1)],
            "cosmic_birefringence_sibling": ("parity-violating (EM birefringence expected)"
                                             if parity > 0.02 else "parity-conserving (no EB)"),
            "holographic_eta_over_s_KSS_units": round(eta_s, 3),
            "bh_entropy_shift_delta_S_ext": round(delta_S_ext, 4),
        },
        "parity_violating": parity > 0.02,
    }


def render(name: str) -> str:
    p = predict(name)
    L = []
    L.append(f"=== ITB prediction fingerprint: {name} ===")
    L.append(f"  {p['citation']}")
    L.append("")
    sc = p["scope"]
    L.append(f"  SCOPE: {'IN SCOPE' if sc['in_scope'] else 'OUT OF SCOPE'}"
             + ("" if sc["in_scope"] else f"  ({', '.join(sc['violations'])})"))
    if not sc["in_scope"]:
        L.append(f"    -> {sc['note']}")
    L.append("")
    L.append("  coefficients: " + ", ".join(f"{k}={v}" for k, v in p["coefficients"].items()))
    L.append(f"  forward-positivity ratio g_R2/g_R3: {p['forward_positivity_ratio_gR2_over_gR3']}")
    L.append("")
    o = p["observables"]
    L.append("  OBSERVABLE FINGERPRINT:")
    L.append(f"    sub-mm Yukawa range (dark-energy cutoff):  {o['submm_yukawa_range_um_at_DE_scale']} um")
    L.append(f"    GW birefringence |g_R2_parity|:            {o['gw_birefringence_g_R2_parity']}")
    L.append(f"    chiral Hellings-Downs circ. pol. Pi_V:     {o['chiral_HD_circular_polarization_pct'][0]}-{o['chiral_HD_circular_polarization_pct'][1]}%")
    L.append(f"    cosmic-birefringence (EM sibling):         {o['cosmic_birefringence_sibling']}")
    L.append(f"    holographic eta/s (KSS units, <1 = KSS-violated): {o['holographic_eta_over_s_KSS_units']}")
    L.append(f"    BH extremal entropy shift Delta S_ext (>0 = WGC): {o['bh_entropy_shift_delta_S_ext']}")
    return "\n".join(L)
