from dataclasses import dataclass

from .base import BaseModel

__all__ = [
    "BrawlerGear",
    "BrawlerAccessory",
]

@dataclass
class BrawlerGear(BaseModel):
    id: int
    name: str
    level: int

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id", "name", "level")

@dataclass
class BrawlerAccessory(BaseModel):
    id: int
    name: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id", "name")
