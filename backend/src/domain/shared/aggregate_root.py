from __future__ import annotations

from src.domain.shared.entity import Entity


class AggregateRoot(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._domain_events: list = []

    def add_domain_event(self, event) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> list:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    @property
    def domain_events(self) -> list:
        return self._domain_events.copy()
