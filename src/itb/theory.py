"""Theory: the parameterized object the engine evaluates constraints against.

A Theory is a vector of named Wilson coefficients plus optional metadata
(name, source citation). It is the primary data unit passed between
frameworks (which produce theories) and constraints (which evaluate them).
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Theory:
    coefficients: dict[str, float]
    name: str = ""
    source: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: float | None = None) -> float | None:
        return self.coefficients.get(key, default)

    def with_coefficient(self, key: str, value: float) -> "Theory":
        new_coeffs = dict(self.coefficients)
        new_coeffs[key] = value
        return Theory(
            coefficients=new_coeffs,
            name=self.name,
            source=self.source,
            metadata=dict(self.metadata),
        )
