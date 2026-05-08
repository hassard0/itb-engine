import numpy as np

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.fragility import fragility_map_2d, FragilityMap


def _three_constraints():
    return [ScalarPositivityG4(), ScalarPositivityG6(), ScalarConvexityG6vsG4()]


def test_fragility_returns_map_with_grid():
    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    assert isinstance(fmap, FragilityMap)
    assert fmap.distance_grid.shape == (11, 11)
    assert fmap.most_fragile_grid.shape == (11, 11)


def test_fragility_zero_in_excluded_region():
    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    # (-0.6, -0.6) -> indices (2, 2) -> infeasible -> distance 0
    assert fmap.distance_grid[2, 2] == 0.0


def test_fragility_positive_in_allowed_region():
    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    # (0.4, 0.8) -> indices (7, 9) -> well inside allowed region (g_6 > g_4^2)
    # The closest constraint is one of: g_4=0 (dist 0.4) or g_6=0 (dist 0.8) or
    # g_6=g_4^2 (dist 0.64 / sqrt(1+0.64) = ~0.64/1.28 = 0.5).
    # Smallest distance in this case is g_4 (0.4).
    assert fmap.distance_grid[7, 9] > 0
    assert fmap.most_fragile_grid[7, 9] != ""


def test_fragility_records_most_fragile_constraint():
    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=_three_constraints(),
    )
    # Pick a feasible cell and verify most_fragile_grid is non-empty there
    feasible = fmap.distance_grid > 0
    if feasible.any():
        i, j = np.argwhere(feasible)[0]
        assert fmap.most_fragile_grid[i, j] != ""


def test_fragility_axes_recorded():
    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=_three_constraints(),
    )
    np.testing.assert_allclose(fmap.x_values, np.linspace(-1.0, 1.0, 5))
    np.testing.assert_allclose(fmap.y_values, np.linspace(-1.0, 1.0, 5))


def test_fragility_figure_builds():
    import plotly.graph_objects as go
    from itb.plotting import build_fragility_figure

    fmap = fragility_map_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=_three_constraints(),
    )
    fig = build_fragility_figure(fmap)
    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text and "Fragility" in fig.layout.title.text
