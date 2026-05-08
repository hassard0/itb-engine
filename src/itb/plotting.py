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


_PER_CONSTRAINT_PALETTE = [
    "#cf3535",  # red
    "#1f6feb",  # blue
    "#b35900",  # orange
    "#7a3ea8",  # purple
    "#0a8b7a",  # teal
    "#c2185b",  # magenta
    "#5d4037",  # brown
]


def build_per_constraint_figure(sweep) -> go.Figure:
    """Render the sweep with one color per binding constraint (not class).

    Allowed cells are shown in light gray; each binding constraint gets its own
    color from a palette. Different constraints binding in different regions
    become visually distinct.
    """
    fig = go.Figure()

    # Allowed cells as a faint background heatmap
    allowed_z = sweep.feasibility_grid.astype(float).T
    fig.add_trace(
        go.Heatmap(
            x=sweep.x_values,
            y=sweep.y_values,
            z=allowed_z,
            colorscale=[[0, "#ffffff"], [1, "#e3f0e6"]],
            zmin=0,
            zmax=1,
            showscale=False,
            name="allowed",
            hovertemplate=(
                f"{sweep.x_param}=%{{x:.3f}}<br>"
                f"{sweep.y_param}=%{{y:.3f}}<br>"
                "feasible<extra></extra>"
            ),
        )
    )

    # Each unique binding-constraint name gets its own color trace via scatter
    binding = sweep.binding_grid
    unique_names = sorted({str(v) for v in binding.flatten() if v})
    color_map = {n: _PER_CONSTRAINT_PALETTE[i % len(_PER_CONSTRAINT_PALETTE)]
                 for i, n in enumerate(unique_names)}
    for name in unique_names:
        xs, ys = [], []
        for i, x in enumerate(sweep.x_values):
            for j, y in enumerate(sweep.y_values):
                if binding[i, j] == name:
                    xs.append(float(x))
                    ys.append(float(y))
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers",
                marker=dict(color=color_map[name], size=6, symbol="square"),
                name=name,
                hovertemplate=(
                    f"{sweep.x_param}=%{{x:.3f}}<br>"
                    f"{sweep.y_param}=%{{y:.3f}}<br>"
                    f"binding={name}<extra></extra>"
                ),
            )
        )

    fig.update_layout(
        title="Binding constraint per cell (gray=allowed)",
        xaxis_title=sweep.x_param,
        yaxis_title=sweep.y_param,
        template="plotly_white",
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


def build_fragility_figure(fmap) -> go.Figure:
    """Heatmap of distance-to-nearest-violation across the sweep."""
    z = fmap.distance_grid.T
    fig = go.Figure(
        data=go.Heatmap(
            x=fmap.x_values,
            y=fmap.y_values,
            z=z,
            colorscale="Viridis",
            colorbar=dict(title="distance"),
            hovertemplate=(
                f"{fmap.x_param}=%{{x:.3f}}<br>"
                f"{fmap.y_param}=%{{y:.3f}}<br>"
                "fragility_distance=%{z:.3f}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Fragility map: distance to nearest constraint violation",
        xaxis_title=fmap.x_param,
        yaxis_title=fmap.y_param,
        template="plotly_white",
    )
    return fig
