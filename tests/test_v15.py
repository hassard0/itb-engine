import numpy as np

from itb.constraints.cmb_s4 import CMBS4Forecast
from itb.constraints.cubic_parity import ParityViolatingCubicBound
from itb.first_disagreement import first_disagreement, render_disagreement_report
from itb.frameworks.asymptotic_safety import AsymptoticSafety
from itb.frameworks.lqg_induced import LQGInduced
from itb.frameworks.string_tree_eft import StringTreeEFT
from itb.observables import ScalarForwardAmplitude
from itb.theory import Theory


def test_cubic_parity_satisfied():
    c = ParityViolatingCubicBound(kappa=1.0)
    # g_4 = 0.5 → 0.25; g_R3^2 + g_R3_parity^2 = 0.0225 + 0.0001 = 0.0226 ✓
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R3": 0.15, "g_R3_parity": 0.01,
    }))
    assert r.satisfied is True


def test_cubic_parity_violated_when_parity_too_large():
    c = ParityViolatingCubicBound(kappa=1.0)
    # 0.04 + 0.36 = 0.4 > 0.25
    r = c.evaluate(Theory(coefficients={
        "g_4": 0.5, "g_R3": 0.2, "g_R3_parity": 0.6,
    }))
    assert r.satisfied is False


def test_cmb_s4_forecast_inherits_measurement():
    c = CMBS4Forecast()
    # Default: central_value=0, sigma=0.03, threshold=2σ → reach 0.06 from origin
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert r.satisfied is False  # 0.5 is much greater than 2σ = 0.06
    r2 = c.evaluate(Theory(coefficients={"g_4": 0.04}))
    assert r2.satisfied is True


def test_first_disagreement_best_pair():
    frameworks = [StringTreeEFT(), AsymptoticSafety(), LQGInduced()]
    observables = {
        "forward_amplitude_low_s": ScalarForwardAmplitude(s_values=np.array([0.5, 1.0])),
        "forward_amplitude_high_s": ScalarForwardAmplitude(s_values=np.array([2.0, 3.0])),
    }
    report = first_disagreement(frameworks, observables, sigma=0.05)
    assert report.best_pair is not None
    assert report.best_pair.max_signal_to_noise > 0


def test_first_disagreement_render():
    frameworks = [StringTreeEFT(), LQGInduced()]
    observables = {"obs": ScalarForwardAmplitude(s_values=np.array([0.5, 1.0]))}
    report = first_disagreement(frameworks, observables, sigma=0.05)
    md = render_disagreement_report(report)
    assert "First-disagreement" in md
    assert "string_tree_eft" in md
    assert "lqg_induced" in md


def test_first_disagreement_high_s_more_distinguishing():
    """At higher s, frameworks differ more (g_4*s^2 + g_6*s^4 grows fast)
    so high-s observables should win."""
    frameworks = [StringTreeEFT(), AsymptoticSafety()]
    observables = {
        "low_s": ScalarForwardAmplitude(s_values=np.array([0.3])),
        "high_s": ScalarForwardAmplitude(s_values=np.array([2.5])),
    }
    report = first_disagreement(frameworks, observables, sigma=0.05)
    # The high_s observable has larger signal in absolute terms
    high_s_scores = [p for p in report.pair_scores if p.observable == "high_s"]
    low_s_scores = [p for p in report.pair_scores if p.observable == "low_s"]
    assert high_s_scores[0].signal > low_s_scores[0].signal
