"""Base protocol for consistency constraints.

Each constraint is a self-contained module. Subclasses provide:
  - evaluate(theory) -> ConstraintResult
  - gradient(theory) -> dict[str, float]      (partials w.r.t. each coefficient)

The gradient enables signed-distance interpretation of margins and
Newton-style boundary tracing in the mapper.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np

from itb.theory import Theory


class ConstraintClass(Enum):
    A_AMPLITUDE = "amplitude_bootstrap"
    B_INFORMATION = "information_theoretic"
    C_UNIVERSALITY = "gravitational_universality"


@dataclass
class ConstraintResult:
    constraint_name: str
    satisfied: bool
    margin: float
    signed_distance_margin: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class Constraint(ABC):
    name: str = ""
    citation: str = ""
    constraint_class: ConstraintClass = ConstraintClass.A_AMPLITUDE

    @abstractmethod
    def evaluate(self, theory: Theory) -> ConstraintResult: ...

    def gradient(self, theory: Theory) -> dict[str, float]:
        """Default: zero gradient. Override for differentiable constraints."""
        return {k: 0.0 for k in theory.coefficients}

    def _signed_distance(self, raw_margin: float, gradient: dict[str, float]) -> float:
        norm = float(np.linalg.norm(list(gradient.values()))) if gradient else 0.0
        if norm == 0.0:
            return raw_margin
        return raw_margin / norm
