from dataclasses import dataclass
from .base import BaseModel
from .players import PlayerIcon

__all__ = [
    "ClubRanking",
    "BrawlerRanking",
    "PlayerRankingClub",
    "PlayerRanking"
]

@dataclass
class ClubRanking(BaseModel):
    tag: str
    name: str
    badge_id: int
    trophies: int
    rank: int
    member_count: int

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "tag name badgeId trophies rank memberCount")

    def fetch_club(self, client):
        return client.get_club(self.tag)

@dataclass
class PlayerRankingClub(BaseModel):
    name: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "name")

@dataclass
class PlayerRanking(BaseModel):
    tag: str
    name: str
    name_color: str
    icon: PlayerIcon
    trophies: int
    rank: int
    club: PlayerRankingClub

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["tag"],
            obj["name"],
            obj["nameColor"],
            PlayerIcon.from_json(obj["icon"]),
            obj["trophies"],
            obj["rank"],
            PlayerRankingClub.from_json(obj["club"]) if "club" in obj else None
        )

    def fetch_player(self, client):
        return client.get_player(self.tag)

# Duplicate code is omitted, as all the fields are the same.

class BrawlerRanking(PlayerRanking):
    pass
