import numpy as np

from itb.observables import Observable, ScalarForwardAmplitude
from itb.theory import Theory


def test_observable_returns_value_per_kinematic_point():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0]))
    theory = Theory(coefficients={"g_4": 1.0, "g_6": 0.0})
    values = obs.predict(theory)
    assert values.shape == (3,)
    np.testing.assert_allclose(values, np.array([0.01, 0.25, 1.0]), atol=1e-9)


def test_observable_jacobian_shape():
    obs = ScalarForwardAmplitude(s_values=np.array([0.1, 0.5, 1.0]))
    theory = Theory(coefficients={"g_4": 1.0, "g_6": 0.0})
    J = obs.jacobian(theory, ["g_4", "g_6"])
    assert J.shape == (3, 2)
    np.testing.assert_allclose(J[:, 0], [0.01, 0.25, 1.0])
    np.testing.assert_allclose(J[:, 1], [0.0001, 0.0625, 1.0])


def test_observable_protocol_attributes():
    obs = ScalarForwardAmplitude(s_values=np.array([0.5]))
    assert isinstance(obs, Observable)
    assert obs.name == "scalar_forward_amplitude"
