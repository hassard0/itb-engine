import json

import plotly.graph_objects as go

from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.mapper import sweep_2d
from itb.plotting import build_allowed_region_figure


def _sample_sweep():
    return sweep_2d(
        x_param="g_4", x_range=(-1.0, 1.0), x_steps=5,
        y_param="g_6", y_range=(-1.0, 1.0), y_steps=5,
        constraints=[ScalarPositivityG4(), ScalarPositivityG6()],
    )


def test_figure_is_plotly():
    fig = build_allowed_region_figure(_sample_sweep())
    assert isinstance(fig, go.Figure)


def test_figure_contains_heatmap():
    fig = build_allowed_region_figure(_sample_sweep())
    types = {trace.type for trace in fig.data}
    assert "heatmap" in types


def test_figure_axis_labels():
    fig = build_allowed_region_figure(_sample_sweep())
    assert fig.layout.xaxis.title.text == "g_4"
    assert fig.layout.yaxis.title.text == "g_6"


def test_figure_serialises_to_json():
    fig = build_allowed_region_figure(_sample_sweep())
    payload = fig.to_json()
    parsed = json.loads(payload)
    assert "data" in parsed
    assert "layout" in parsed
