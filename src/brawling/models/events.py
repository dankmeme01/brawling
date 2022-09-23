from dataclasses import dataclass
from datetime import datetime, timezone
import dateutil.parser

from .base import BaseModel

__all__ = [
    "Event",
    "EventSlot",
    "EventRotation",
]

@dataclass
class Event(BaseModel):
    id: int
    mode: str
    map: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id mode map")

@dataclass
class EventSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    slot_id: int
    event: Event

    @classmethod
    def from_json(cls, obj):
        return cls(
            dateutil.parser.isoparse(obj["startTime"]),
            dateutil.parser.isoparse(obj["endTime"]),
            obj["slotId"],
            Event.from_json(obj["event"])
        )

@dataclass
class EventRotation(BaseModel):
    events: list[EventSlot]
    next_change: datetime

    @classmethod
    def from_json(cls, obj: list):
        events = [EventSlot.from_json(x) for x in obj]

        next_change = events[0].end_time
        for event in events:
            next_change = min(next_change, event.end_time)

        return cls(events, next_change)
