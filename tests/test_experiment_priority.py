import pytest

from itb.constraints.bekenstein_tight import BekensteinTight
from itb.constraints.scalar_convexity import ScalarConvexityG6vsG4
from itb.constraints.scalar_positivity import (
    ScalarPositivityG4,
    ScalarPositivityG6,
)
from itb.experiment_priority import (
    ExperimentForecast,
    ExperimentRanking,
    rank_experiments,
    render_priority_list,
)


def _baseline_constraints():
    return [
        ScalarPositivityG4(),
        ScalarPositivityG6(),
        ScalarConvexityG6vsG4(),
        BekensteinTight(),
    ]


def test_rank_returns_list():
    rankings = rank_experiments(
        base_constraints=_baseline_constraints(),
        experiments=[
            ExperimentForecast(
                label="LIGO_O5", coefficient_name="g_R2",
                central_value=0.0, sigma=0.05,
            ),
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=11,
        fixed_coefficients={"g_R2": 0.3},
    )
    assert len(rankings) == 1
    assert isinstance(rankings[0], ExperimentRanking)


def test_tighter_experiment_excludes_more():
    rankings = rank_experiments(
        base_constraints=_baseline_constraints(),
        experiments=[
            ExperimentForecast(label="loose", coefficient_name="g_R2",
                               central_value=0.0, sigma=1.0),
            ExperimentForecast(label="tight", coefficient_name="g_R2",
                               central_value=0.0, sigma=0.05),
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=11,
        fixed_coefficients={"g_R2": 0.3},
    )
    # tight experiment has tighter sigma → ranked first (more excluded)
    assert rankings[0].label == "tight"


def test_ranking_sorted_by_cells_excluded():
    rankings = rank_experiments(
        base_constraints=_baseline_constraints(),
        experiments=[
            ExperimentForecast(label=f"exp_{i}", coefficient_name="g_R2",
                               central_value=0.0, sigma=s)
            for i, s in enumerate([1.0, 0.05, 0.5])
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=11,
        fixed_coefficients={"g_R2": 0.3},
    )
    cells = [r.cells_excluded for r in rankings]
    assert cells == sorted(cells, reverse=True)


def test_render_priority_list_outputs_markdown():
    rankings = rank_experiments(
        base_constraints=_baseline_constraints(),
        experiments=[
            ExperimentForecast(label="LIGO_O5", coefficient_name="g_R2",
                               central_value=0.0, sigma=0.05),
            ExperimentForecast(label="CMB_S4", coefficient_name="g_4",
                               central_value=0.5, sigma=0.1),
        ],
        x_param="g_4", x_range=(0.0, 2.0), x_steps=11,
        y_param="g_6", y_range=(0.0, 2.0), y_steps=11,
        fixed_coefficients={"g_R2": 0.3},
    )
    md = render_priority_list(rankings)
    assert "Experimental priority ranking" in md
    assert "LIGO_O5" in md
    assert "CMB_S4" in md
