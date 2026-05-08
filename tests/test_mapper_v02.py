from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d, boundary_cells


def _sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )


def test_binding_grid_shape_matches_feasibility():
    s = _sweep()
    assert s.binding_grid.shape == s.feasibility_grid.shape


def test_binding_grid_empty_string_inside_allowed_region():
    s = _sweep()
    assert s.binding_grid[8, 8] == ""


def test_binding_grid_records_g4_in_left_half():
    s = _sweep()
    assert s.binding_grid[2, 8] == "scalar_positivity_g4"


def test_binding_grid_records_g6_in_lower_half():
    s = _sweep()
    assert s.binding_grid[8, 2] == "scalar_positivity_g6"


def test_boundary_cells_are_on_axis_lines():
    s = _sweep()
    cells = boundary_cells(s)
    assert len(cells) > 0
    step = 0.2
    for (i, j) in cells:
        x = s.x_values[i]
        y = s.y_values[j]
        assert (abs(x) <= step + 1e-9) or (abs(y) <= step + 1e-9)
