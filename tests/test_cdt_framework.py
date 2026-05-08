from itb.frameworks.cdt import CausalDynamicalTriangulation
from itb.theory import Theory


def test_cdt_returns_theory():
    fw = CausalDynamicalTriangulation()
    theory = fw.encode()
    assert isinstance(theory, Theory)


def test_cdt_is_parity_conserving():
    theory = CausalDynamicalTriangulation().encode()
    assert theory.coefficients["g_R2_parity"] == 0.0
    assert theory.coefficients["g_R3_parity"] == 0.0


def test_cdt_g4_larger_than_string():
    """CDT has stronger short-distance matter fluctuations than tree-level
    string, so its effective g_4 is larger."""
    from itb.frameworks.string_tree_eft import StringTreeEFT
    string_g4 = StringTreeEFT().encode().coefficients["g_4"]
    cdt_g4 = CausalDynamicalTriangulation().encode().coefficients["g_4"]
    assert cdt_g4 > string_g4


def test_cdt_g_R3_smaller_than_lqg():
    """CDT lacks spin-foam vertex amplification → smaller g_R3 than LQG."""
    from itb.frameworks.lqg_induced import LQGInduced
    lqg_gR3 = LQGInduced().encode().coefficients["g_R3"]
    cdt_gR3 = CausalDynamicalTriangulation().encode().coefficients["g_R3"]
    assert cdt_gR3 < lqg_gR3


def test_cdt_passes_full_v17_constraint_stack():
    """Full v1.7 stack (without v1.8 intersection):"""
    from itb.constraints.anomaly import AnomalyCancellation
    from itb.constraints.anomaly_flow import (
        GeneralizedAnomalyInflow, tHooftAnomalyMatching,
    )
    from itb.constraints.bekenstein_tight import BekensteinTight
    from itb.constraints.causality import CausalityBound
    from itb.constraints.complexity_cutoff import ComplexityCutoff
    from itb.constraints.cubic_parity import ParityViolatingCubicBound
    from itb.constraints.dispersion_tower import (
        DispersionTowerCauchySchwarz, ScalarPositivityG8,
    )
    from itb.constraints.eft_validity import EFTValidityBox
    from itb.constraints.graviton_eft import GravitonMixedPositivity
    from itb.constraints.graviton_self_coupling import (
        CubicCurvaturePositivity, CubicGravitonMatterBound,
    )
    from itb.constraints.holographic_entropy import (
        BNOSSWMonogamy, HolographicSubadditivity,
    )
    from itb.constraints.ligo_graviton_mass import LIGOGravitonMassBound
    from itb.constraints.parity_violation import (
        LIGOBirefringenceBound, LeftHandedGravitonPositivity,
        ParityViolatingPositivity, RightHandedGravitonPositivity,
    )
    from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
    from itb.constraints.scalar_positivity import (
        ScalarPositivityG4, ScalarPositivityG6,
    )
    from itb.constraints.swampland import WeakGravityConjecture
    from itb.engine import check

    constraints = [
        ScalarPositivityG4(), ScalarPositivityG6(), ScalarPositivityG8(),
        ScalarConvexityG6vsG4(), DispersionTowerCauchySchwarz(),
        GravitonMixedPositivity(), CubicCurvaturePositivity(),
        CubicGravitonMatterBound(kappa=1.0),
        BekensteinTight(), HolographicSubadditivity(), BNOSSWMonogamy(),
        ParityViolatingPositivity(kappa=1.0),
        LeftHandedGravitonPositivity(kappa=1.0),
        RightHandedGravitonPositivity(kappa=1.0),
        ParityViolatingCubicBound(kappa=1.0),
        LIGOBirefringenceBound(bound=0.1),
        EFTValidityBox(box=2.0), CausalityBound(gamma=1.0),
        AnomalyCancellation(c_anom=1.0, tolerance=0.2),
        GeneralizedAnomalyInflow(rho=0.06),
        tHooftAnomalyMatching(rho_match=0.5, slack=0.02),
        WeakGravityConjecture(alpha=1.0),
        LIGOGravitonMassBound(bound=0.5),
        ComplexityCutoff(c_max=1.5),
    ]
    theory = CausalDynamicalTriangulation().encode()
    report = check(theory, constraints)
    assert report.feasible is True, (
        f"CDT failed: binding={report.binding}; "
        f"violations={[(r.constraint_name, r.margin) for r in report.results if not r.satisfied]}"
    )
