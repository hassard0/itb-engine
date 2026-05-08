import json

import plotly.graph_objects as go

from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.plotting import build_per_constraint_figure


def _sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=21,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=21,
        constraints=[
            ScalarPositivityG4(),
            ScalarPositivityG6(),
            ScalarConvexityG6vsG4(),
        ],
    )


def test_per_constraint_figure_is_plotly():
    fig = build_per_constraint_figure(_sweep())
    assert isinstance(fig, go.Figure)


def test_per_constraint_figure_has_legend_traces_for_each_binding_constraint():
    fig = build_per_constraint_figure(_sweep())
    legend_names = [trace.name for trace in fig.data if trace.name]
    # We expect at least: allowed, plus one trace per binding constraint
    assert "allowed" in legend_names
    assert any("g4" in n for n in legend_names)
    assert any("g6" in n for n in legend_names)
    assert any("convexity" in n for n in legend_names)


def test_per_constraint_figure_serializes():
    fig = build_per_constraint_figure(_sweep())
    payload = json.loads(fig.to_json())
    assert "data" in payload
