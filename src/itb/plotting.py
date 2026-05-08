"""Plotly figure builders for sweep results."""

import numpy as np
import plotly.graph_objects as go

from itb.mapper import SweepResult


def build_allowed_region_figure(sweep: SweepResult) -> go.Figure:
    z = sweep.feasibility_grid.astype(int).T
    fig = go.Figure(
        data=go.Heatmap(
            x=sweep.x_values,
            y=sweep.y_values,
            z=z,
            colorscale=[[0, "#cf3535"], [1, "#3da34d"]],
            zmin=0,
            zmax=1,
            showscale=False,
            hovertemplate=(
                f"{sweep.x_param}=%{{x:.3f}}<br>"
                f"{sweep.y_param}=%{{y:.3f}}<br>"
                "feasible=%{z}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Allowed theory region (green) vs excluded (red)",
        xaxis_title=sweep.x_param,
        yaxis_title=sweep.y_param,
        template="plotly_white",
    )
    return fig


_CLASS_COLORS = {
    "": "#3da34d",
    "amplitude_bootstrap": "#cf3535",
    "information_theoretic": "#1f6feb",
    "gravitational_universality": "#b35900",
}
_CLASS_INTS = {k: i for i, k in enumerate(_CLASS_COLORS.keys())}


def build_binding_class_figure(sweep: SweepResult) -> go.Figure:
    cls = sweep.binding_class_grid
    z = np.vectorize(lambda v: _CLASS_INTS.get(v, 0))(cls).astype(int).T
    n = max(len(_CLASS_INTS) - 1, 1)
    colorscale = [[i / n, _CLASS_COLORS[k]] for k, i in _CLASS_INTS.items()]
    fig = go.Figure(
        data=go.Heatmap(
            x=sweep.x_values,
            y=sweep.y_values,
            z=z,
            colorscale=colorscale,
            zmin=0,
            zmax=n,
            showscale=False,
            hovertemplate=(
                f"{sweep.x_param}=%{{x:.3f}}<br>"
                f"{sweep.y_param}=%{{y:.3f}}<br>"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Binding constraint by class (green=allowed)",
        xaxis_title=sweep.x_param,
        yaxis_title=sweep.y_param,
        template="plotly_white",
    )
    return fig
