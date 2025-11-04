from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4

from domain.events.base import BaseEvent


@dataclass
class BaseEntity(ABC):
    oid: str = field(
        default_factory=lambda: str(uuid4()),
        kw_only=True,
    )
    _events: list[BaseEvent] = field(
        default_factory=list,
        kw_only=True,
    )
    created_at: datetime = field(
        default_factory=datetime.now,
        kw_only=True,
    )

    def __hash__(self) -> int:
        return hash(self.oid)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, BaseEntity):
            return NotImplemented
        return self.oid == __value.oid

    def register_event(self, event: BaseEvent) -> None:
        self._events.append(event)

    def clear_events(self) -> None:
        self._events.clear()

    @property
    def events(self) -> List[BaseEvent]:
        return self._events.copy()
