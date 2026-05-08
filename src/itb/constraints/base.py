"""Base protocol for consistency constraints.

Each constraint is a self-contained module. To add a new constraint:
  1. Create a new file in this package.
  2. Subclass `Constraint` with the required class attributes.
  3. Implement `evaluate(theory) -> ConstraintResult`.
The engine will discover and use it automatically (see engine.py).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

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
    details: dict[str, Any] = field(default_factory=dict)


class Constraint(ABC):
    """Abstract base class. Subclasses must set name, citation, constraint_class."""

    name: str = ""
    citation: str = ""
    constraint_class: ConstraintClass = ConstraintClass.A_AMPLITUDE

    @abstractmethod
    def evaluate(self, theory: Theory) -> ConstraintResult:
        ...
