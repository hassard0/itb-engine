"""Plotly figure builders for sweep results."""

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
