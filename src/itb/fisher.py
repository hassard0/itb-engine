"""Fisher information metric on theory space.

Given an observable that predicts a vector of values from a theory, and a
Gaussian noise model with std `sigma` on each prediction, the Fisher
information metric on parameter space is

    g_{ab}(theta) = sum_i (d M_i / d theta_a)(d M_i / d theta_b) / sigma^2
                  = J^T J / sigma^2

where J is the Jacobian. This is the natural metric for distinguishability
of theories under the chosen observable, and it is what experimentalists
care about when asking "are these theories observably different?"."""

import numpy as np

from itb.observables import Observable
from itb.theory import Theory


def fisher_metric(
    observable: Observable,
    theory: Theory,
    params: list[str],
    sigma: float,
) -> np.ndarray:
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    J = observable.jacobian(theory, params)
    return (J.T @ J) / (sigma ** 2)
