from dataclasses import dataclass
from enum import Enum, auto

from .base import BaseModel
from .players import PlayerIcon, Player

__all__ = [
    "ClubMember",
    "ClubRole",
    "ClubType",
    "Club"
]

class ClubRole(Enum):
    MEMBER = "member"
    SENIOR = "senior"
    VICE_PRESIDENT = "vicePresident"
    PRESIDENT = "president"

class ClubType(Enum):
    OPEN = "open"
    INVITE_ONLY = "inviteOnly"
    CLOSED = "closed"

@dataclass
class ClubMember(BaseModel):
    tag: str
    name: str
    name_color: str
    role: ClubRole
    trophies: int
    icon: PlayerIcon

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["tag"],
            obj["name"],
            obj["nameColor"],
            ClubRole(obj["role"]),
            obj["trophies"],
            PlayerIcon.from_json(obj["icon"])
        )

    def fetch_player(self, client):
        """Utility method to fetch this member's account data"""
        return client.get_player(self.tag)

@dataclass
class Club(BaseModel):
    tag: str
    name: str
    description: str
    type: ClubType
    badge_id: int
    required_trophies: int
    trophies: int
    members: list[ClubMember]

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["tag"],
            obj["name"],
            obj["description"],
            ClubType(obj["type"]),
            obj["badgeId"],
            obj["requiredTrophies"],
            obj["trophies"],
            [ClubMember.from_json(x) for x in obj["members"]]
        )
