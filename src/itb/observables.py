"""Observable interface: a function from Theory to numerical predictions plus
its Jacobian with respect to parameters. Used to compute Fisher information
metrics on theory space.

The toy `ScalarForwardAmplitude` predicts the leading EFT contribution to the
forward 2->2 amplitude M(s, t=0) = g_4 * s^2 + g_6 * s^4 at a chosen set of
kinematic points. Future observables (graviton scattering, holographic
entropy) will share this protocol."""

from abc import ABC, abstractmethod

import numpy as np

from itb.theory import Theory


class Observable(ABC):
    name: str = ""

    @abstractmethod
    def predict(self, theory: Theory) -> np.ndarray: ...

    @abstractmethod
    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray: ...


class ScalarForwardAmplitude(Observable):
    name = "scalar_forward_amplitude"

    def __init__(self, s_values: np.ndarray):
        self.s_values = np.asarray(s_values, dtype=float)

    def predict(self, theory: Theory) -> np.ndarray:
        g4 = theory.coefficients.get("g_4", 0.0)
        g6 = theory.coefficients.get("g_6", 0.0)
        s = self.s_values
        return g4 * s ** 2 + g6 * s ** 4

    def jacobian(self, theory: Theory, params: list[str]) -> np.ndarray:
        s = self.s_values
        cols = []
        for p in params:
            if p == "g_4":
                cols.append(s ** 2)
            elif p == "g_6":
                cols.append(s ** 4)
            else:
                cols.append(np.zeros_like(s))
        return np.stack(cols, axis=1)
