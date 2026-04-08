from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListYearsQuery:
    active_only: bool = True
