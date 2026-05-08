from itb.constraints.scalar_positivity_sdp import ScalarPositivityG4SDP
from itb.theory import Theory


def test_sdp_feasible_at_positive_value():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert r.satisfied is True


def test_sdp_infeasible_at_negative_value():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": -0.5}))
    assert r.satisfied is False


def test_sdp_feasibility_at_zero_with_default_tolerance():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.0}))
    assert r.satisfied is True


def test_sdp_records_solver_status_in_details():
    c = ScalarPositivityG4SDP()
    r = c.evaluate(Theory(coefficients={"g_4": 0.5}))
    assert "solver_status" in r.details


def test_sdp_lazy_imports_cvxpy():
    import itb.constraints.scalar_positivity_sdp as mod
    assert "cvxpy" not in mod.__dict__
    assert "cp" not in mod.__dict__
