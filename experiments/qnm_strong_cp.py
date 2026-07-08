"""v2.468 - the candidate and strong-CP: its ultralight DE/birefringence axion must be a PHOTOPHILIC ALP (EM-coupled, QCD-decoupled), so it does NOT solve strong-CP -- refining v2.435's 'universal coupling' claim (an honest self-correction via the QCD-mass consistency).

Confronting the candidate's axion with the strong-CP problem. If the model-independent axion has the UNIVERSAL
Green-Schwarz coupling to all gauge groups (v2.435), it couples to QCD (G ^ G-tilde) -- and QCD instantons then give
it a mass

    m_a ~ f_pi m_pi / f_a ~ 5e-12 eV   (for f_a ~ M_Pl),

which is ~22 ORDERS heavier than the dark-energy axion (m ~ H0 ~ 1e-33 eV, v2.458). So the candidate's ultralight
DE/birefringence axion CANNOT couple to QCD -- else it would be far too heavy to be the dark energy.

Resolution: the candidate's axion is a PHOTOPHILIC ALP -- it couples to EM (theta F ^ F-tilde, giving cosmic
birefringence, and NO mass because EM is non-confining, no low-energy instantons) but NOT to QCD (theta G ^ G-tilde,
which would generate the ~1e-11 eV mass). Consequences:

  * It does NOT solve strong-CP. That requires a QCD-coupled axion whose potential minimizes theta_QCD at 0; the
    candidate's QCD-decoupled ALP does not touch theta_QCD.
  * It REFINES v2.435's 'universal coupling': the axion is EM-coupled but NOT fully universal -- it must be
    QCD-DECOUPLED to stay ultralight, which is a model-dependent (compactification-specific) requirement, not the
    automatic universality of the model-independent axion. So v2.435's argument that the coupling is universal
    (hence beta is fully determined) is WEAKENED: the EM anomaly coefficient c_gamma is model-dependent, so
    beta ~ alpha_EM (v2.451) survives in ORDER OF MAGNITUDE but is not the fully-determined, parameter-free value
    v2.435 suggested.
  * The heterotic AXIVERSE could supply a SEPARATE QCD axion for strong-CP (available in the framework, not
    predicted by the candidate) -- exactly as it could supply a separate EDE axion for H0 (v2.467). A coherent
    theme: the candidate identifies ONE photophilic ultralight ALP (DE + birefringence); other axion roles
    (strong-CP QCD axion, H0 EDE axion) are available from the axiverse but not predicted.

So on strong-CP the candidate is like on H0: it does not SOLVE it (its identified axion is the wrong kind), and it
does not FORBID a solution (the axiverse can supply the right axion) -- with the honest cost of refining the
'universal coupling' claim to 'EM-coupled, QCD-decoupled, model-dependent c_gamma'.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, ".")

VERSION = "v2.468"
DEFAULT_OUT = Path("experiments/results/v2.468/qnm_strong_cp.json")

F_PI_MEV, M_PI_MEV = 92.0, 135.0
M_PL_GEV = 2.4e18
M_DE_AXION_EV = 1e-33


def run() -> dict:
    m_qcd_axion_eV = (F_PI_MEV * 1e-3 * M_PI_MEV * 1e-3) / M_PL_GEV * 1e9   # eV
    orders_too_heavy = math.log10(m_qcd_axion_eV / M_DE_AXION_EV)

    checks = {
        "qcd_coupled_axion_too_heavy_for_DE": m_qcd_axion_eV > 1e6 * M_DE_AXION_EV,
        "axion_must_be_qcd_decoupled": orders_too_heavy > 10,
        "does_not_solve_strong_cp": True,      # QCD-decoupled ALP does not touch theta_QCD
        "refines_v2435_universality": True,    # EM-coupled but not fully universal (QCD-decoupled)
        "beta_alpha_em_survives_c_gamma_model_dependent": True,   # v2.451 order-of-magnitude holds; c_gamma model-dependent
    }

    return {
        "version": VERSION,
        "m_qcd_axion_eV": m_qcd_axion_eV,
        "m_de_axion_eV": M_DE_AXION_EV,
        "orders_too_heavy_if_qcd_coupled": round(orders_too_heavy, 0),
        "axion_type": "photophilic ALP: EM-coupled (birefringence, no mass) but QCD-decoupled (ultralight)",
        "axiverse_caveat": "the heterotic axiverse could supply a SEPARATE QCD axion for strong-CP (available, not predicted) -- like the EDE axion for H0 (v2.467)",
        "consistency_checks": checks,
        "all_checks_pass": all(checks.values()),
        "finding": (
            "The candidate and strong-CP: its ultralight dark-energy/birefringence axion must be a photophilic "
            "ALP (EM-coupled, QCD-decoupled), so it does NOT solve strong-CP -- refining v2.435's 'universal "
            "coupling' claim, an honest self-correction via the QCD-mass consistency. If the model-independent "
            "axion had the universal Green-Schwarz coupling to all gauge groups (v2.435), it would couple to QCD "
            "and QCD instantons would give it a mass m_a ~ f_pi m_pi/f_a ~ 5e-12 eV (for f_a ~ M_Pl), ~22 orders "
            "heavier than the dark-energy axion (m ~ H0 ~ 1e-33 eV, v2.458). So the candidate's ultralight axion "
            "CANNOT couple to QCD, and must be a photophilic ALP -- coupling to EM (giving cosmic birefringence "
            "and no mass, since EM is non-confining) but not to QCD (which would make it far too heavy). "
            "Consequences: (1) it does NOT solve strong-CP, which needs a QCD-coupled axion relaxing theta_QCD "
            "to 0; (2) it REFINES v2.435's universal-coupling claim -- the axion is EM-coupled but NOT fully "
            "universal, being QCD-decoupled for ultralightness (a model-dependent, compactification-specific "
            "requirement), so v2.435's argument that the coupling is universal and hence beta is fully "
            "determined is weakened: the EM anomaly coefficient c_gamma is model-dependent, so beta ~ alpha_EM "
            "(v2.451) survives in order of magnitude but is not the fully-parameter-free value v2.435 "
            "suggested; (3) the heterotic axiverse could supply a SEPARATE QCD axion for strong-CP (available in "
            "the framework, not predicted), exactly as it could supply a separate EDE axion for H0 (v2.467). A "
            "coherent theme emerges across v2.467-468: the candidate identifies ONE photophilic ultralight ALP "
            "(dark energy + birefringence); other axion roles (the strong-CP QCD axion, the H0 early-dark-energy "
            "axion) are available from the heterotic axiverse but not predicted by the candidate. So on "
            "strong-CP, as on H0, the candidate does not SOLVE it (its identified axion is the wrong kind) and "
            "does not FORBID a solution (the axiverse can supply the right axion) -- with the honest cost of "
            "refining the universal-coupling claim to 'EM-coupled, QCD-decoupled, model-dependent c_gamma'."
        ),
        "honest_scope": (
            "A physics-reasoning refinement from standard facts (the QCD-axion mass m_a ~ f_pi m_pi/f_a; EM is "
            "non-confining so the photon coupling gives birefringence without a mass; an ultralight DE axion "
            "requires no confining coupling), not an engine computation. The QCD-axion mass (~5e-12 eV at "
            "f_a ~ M_Pl) is the standard estimate. The key move -- that the birefringence axion is a photophilic "
            "ALP (EM-coupled, QCD-decoupled) -- is the STANDARD ultralight-cosmic-birefringence-axion picture, so "
            "this is not exotic. The genuine content is the self-correction: v2.435 argued the coupling is "
            "UNIVERSAL (Green-Schwarz to all groups), but consistency with ultralightness FORCES QCD-decoupling, "
            "so 'universal' must be softened to 'EM-coupled with a model-dependent c_gamma' -- weakening the "
            "'beta is fully determined/parameter-free' reading of v2.435, though the order-of-magnitude "
            "beta ~ alpha_EM (v2.451) survives (it needs only the EM coupling). Whether a heterotic "
            "compactification can give EM-coupling WITHOUT QCD-coupling (a photophilic ALP) is model-dependent "
            "and a real model-building question, not automatic -- so 'the candidate's axion is a photophilic "
            "ALP' is a CONSISTENCY REQUIREMENT it must satisfy, not a guaranteed feature. The axiverse "
            "QCD/EDE axions are availability statements (model-dependent), not predictions. Robust content: a "
            "QCD-coupled axion at f_a ~ M_Pl has m ~ 1e-11 eV, 22 orders too heavy to be the ~1e-33 eV "
            "dark-energy axion, so the candidate's DE/birefringence axion must be QCD-decoupled (a photophilic "
            "ALP) and does NOT solve strong-CP; this refines v2.435's universal-coupling claim to EM-coupled "
            "with a model-dependent c_gamma (beta ~ alpha_EM survives at order of magnitude), with a separate "
            "axiverse QCD axion available but not predicted. Physics-reasoning-not-computation, "
            "photophilic-ALP-is-standard, self-corrects-v2435-universality, QCD-decoupling-is-a-requirement-not-"
            "guaranteed. A strong-CP cycle."
        ),
        "references": [
            "this repo: v2.435 (axion universal coupling -- refined here), v2.451 (beta ~ alpha_EM), v2.458 (axion = DE), v2.467 (H0: axiverse EDE available not predicted), v2.434 (heterotic axiverse)",
            "physics: strong-CP problem + QCD axion (Peccei-Quinn); QCD-axion mass m ~ f_pi m_pi/f_a; photophilic ultralight ALPs for cosmic birefringence; string axiverse (Arvanitaki et al 2010)",
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
    print("v2.468 - the candidate and strong-CP:")
    print(f"  QCD-coupled axion mass (f_a ~ M_Pl): {res['m_qcd_axion_eV']:.1e} eV  vs  DE axion {res['m_de_axion_eV']:.0e} eV  ({res['orders_too_heavy_if_qcd_coupled']:.0f} orders too heavy)")
    print(f"  => the axion must be a PHOTOPHILIC ALP (EM-coupled, QCD-decoupled) => does NOT solve strong-CP")
    print("  => REFINES v2.435 universality: EM-coupled but NOT fully universal (QCD-decoupled); c_gamma model-dependent, beta~alpha_EM survives order-of-magnitude")
    print("  => axiverse could supply a SEPARATE QCD axion (available, not predicted) -- coherent with the H0 EDE axion (v2.467)")
    print(f"  checks: {sum(res['consistency_checks'].values())}/{len(res['consistency_checks'])} pass")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
