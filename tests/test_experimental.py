import pytest

from itb.constraints.experimental import MeasuredWilsonCoefficient
from itb.theory import Theory


def test_satisfied_at_central_value():
    c = MeasuredWilsonCoefficient("g_R2", central_value=0.3, sigma=0.05)
    r = c.evaluate(Theory(coefficients={"g_R2": 0.3}))
    assert r.satisfied is True
    assert r.margin == 2.0  # 2σ threshold - 0σ deviation


def test_satisfied_within_two_sigma():
    c = MeasuredWilsonCoefficient("g_R2", central_value=0.3, sigma=0.05)
    r = c.evaluate(Theory(coefficients={"g_R2": 0.35}))  # 1σ away
    assert r.satisfied is True
    assert r.margin == pytest.approx(1.0)


def test_violated_beyond_two_sigma():
    c = MeasuredWilsonCoefficient("g_R2", central_value=0.3, sigma=0.05)
    r = c.evaluate(Theory(coefficients={"g_R2": 0.5}))  # 4σ away
    assert r.satisfied is False
    assert r.margin == pytest.approx(-2.0)


def test_string_eft_within_synthetic_measurement():
    from itb.engine import check
    from itb.frameworks.string_tree_eft import StringTreeEFT
    theory = StringTreeEFT().encode()
    # Simulate measurement compatible with string-eft prediction
    measurement = MeasuredWilsonCoefficient("g_R2", central_value=0.2, sigma=0.05)
    report = check(theory, [measurement])
    assert report.feasible is True


def test_experiment_distinguishes_frameworks():
    """A measurement at g_R2 = 0.4 ± 0.02 distinguishes string-EFT (g_R2=0.2)
    from LQG-induced (g_R2=0.3) from a hypothetical with g_R2≈0.4."""
    from itb.engine import check
    from itb.frameworks.lqg_induced import LQGInduced
    from itb.frameworks.string_tree_eft import StringTreeEFT

    measurement = MeasuredWilsonCoefficient(
        "g_R2", central_value=0.4, sigma=0.02
    )
    s_report = check(StringTreeEFT().encode(), [measurement])
    l_report = check(LQGInduced().encode(), [measurement])
    # Both string and LQG predict g_R2 too far from 0.4 (>=2σ)
    assert s_report.feasible is False
    assert l_report.feasible is False  # 0.3 is 5σ from 0.4
    # but the closer one (LQG) has less negative margin
    assert l_report.results[0].margin > s_report.results[0].margin


def test_metadata_includes_experiment_label():
    c = MeasuredWilsonCoefficient(
        "g_R2", central_value=0.3, sigma=0.05,
        experiment_label="LIGO_O5",
    )
    assert "LIGO_O5" in c.name
    assert "LIGO_O5" in c.citation
