from dataclasses import dataclass

from .base import BaseModel

__all__ = [
    "BrawlerGear",
    "BrawlerAccessory",
    "Brawler",
]

@dataclass
class BrawlerGear(BaseModel):
    id: int
    name: str
    level: int

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id name level")

@dataclass
class BrawlerAccessory(BaseModel):
    id: int
    name: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id name")

@dataclass
class Brawler(BaseModel):
    id: int
    name: str
    gadgets: list[BrawlerAccessory]
    star_powers: list[BrawlerAccessory]

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["id"],
            obj["name"],
            [BrawlerAccessory.from_json(x) for x in obj["gadgets"]],
            [BrawlerAccessory.from_json(x) for x in obj["starPowers"]],
        )
