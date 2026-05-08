import json

import plotly.graph_objects as go

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.plotting import build_binding_class_figure


def _sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=11,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=11,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )


def test_binding_class_figure_is_plotly():
    fig = build_binding_class_figure(_sweep())
    assert isinstance(fig, go.Figure)


def test_binding_class_figure_has_traces():
    fig = build_binding_class_figure(_sweep())
    assert len(fig.data) >= 1


def test_binding_class_figure_serialises():
    fig = build_binding_class_figure(_sweep())
    payload = json.loads(fig.to_json())
    assert "data" in payload
