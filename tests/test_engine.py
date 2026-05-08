from itb.engine import check, EngineReport
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.frameworks.pure_gr import PureGR
from itb.theory import Theory


def test_engine_returns_report():
    theory = PureGR().encode()
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert isinstance(report, EngineReport)


def test_engine_pure_gr_passes_positivity():
    theory = PureGR().encode()
    report = check(theory, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert report.feasible is True
    assert all(r.satisfied for r in report.results)


def test_engine_negative_g4_fails():
    bad = Theory(coefficients={"g_4": -1.0, "g_6": 0.5})
    report = check(bad, [ScalarPositivityG4(), ScalarPositivityG6()])
    assert report.feasible is False


def test_engine_records_binding_constraint():
    bad = Theory(coefficients={"g_4": -1.0, "g_6": 0.5})
    report = check(bad, [ScalarPositivityG4(), ScalarPositivityG6()])
    binding = [r for r in report.results if not r.satisfied]
    assert len(binding) == 1
    assert binding[0].constraint_name == "scalar_positivity_g4"


def test_engine_empty_constraints_is_feasible():
    theory = PureGR().encode()
    report = check(theory, [])
    assert report.feasible is True
    assert report.results == []
