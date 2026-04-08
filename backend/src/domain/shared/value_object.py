from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Base class for value objects. Equality is by value (all fields)."""
    pass
