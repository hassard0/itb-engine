from itb.constraints.scalar_positivity import ScalarPositivityG4
from itb.mapper import trace_boundary_along_axis


def test_traces_boundary_for_g4_positivity():
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": 0.5, "g_6": 0.0},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"] - 0.0) < 1e-6
    assert point["g_6"] == 0.0


def test_returns_starting_point_if_already_on_boundary():
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": 0.0, "g_6": 1.0},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"]) < 1e-9


def test_traces_from_violation_back_to_boundary():
    point = trace_boundary_along_axis(
        constraint=ScalarPositivityG4(),
        start={"g_4": -0.7, "g_6": 0.5},
        max_iters=20,
        tol=1e-9,
    )
    assert abs(point["g_4"]) < 1e-6
