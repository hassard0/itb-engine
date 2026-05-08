import numpy as np

from itb.fisher import fisher_metric
from itb.observables import ScalarForwardAmplitude
from itb.theory import Theory


def test_fisher_metric_shape_matches_param_count():
    obs = ScalarForwardAmplitude(s_values=np.array([0.5, 1.0]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 1.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=0.1,
    )
    assert g.shape == (2, 2)


def test_fisher_metric_is_symmetric():
    obs = ScalarForwardAmplitude(s_values=np.array([0.3, 0.7, 1.1]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.5, "g_6": 0.2}),
        params=["g_4", "g_6"],
        sigma=0.05,
    )
    np.testing.assert_allclose(g, g.T)


def test_fisher_metric_positive_definite():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0, 1.5]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=0.1,
    )
    eigs = np.linalg.eigvalsh(g)
    assert (eigs > 0).all()


def test_fisher_metric_value_for_simple_case():
    obs = ScalarForwardAmplitude(s_values=np.array([1.0]))
    g = fisher_metric(
        observable=obs,
        theory=Theory(coefficients={"g_4": 0.0, "g_6": 0.0}),
        params=["g_4", "g_6"],
        sigma=1.0,
    )
    np.testing.assert_allclose(g, np.array([[1.0, 1.0], [1.0, 1.0]]))
