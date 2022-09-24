from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import dateutil.parser

from .base import BaseModel
from .brawlers import *

__all__ = [
    "BattleEvent",
    "BattleBrawler",
    "BattlePlayer",
    "BattleTeam",
    "Battle",
    "SoloBattle",
    "TeamBattle",
    "PlayerIcon",
    "PlayerClub",
    "PlayerBrawler",
    "Player"
]

@dataclass
class BattleEvent(BaseModel):
    """Represents an event of a battle"""
    id: int
    mode: str
    map: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id mode map")

@dataclass
class BattleBrawler(BaseModel):
    """Represents a brawler of a player in a battle"""
    id: int
    name: str
    power: int
    trophies: int

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id name power trophies")

@dataclass
class BattlePlayer(BaseModel):
    """Represents a player that participated in a battle"""
    tag: str
    name: str
    brawler: BattleBrawler

    @classmethod
    def from_json(cls, obj):
        return cls(obj["tag"], obj["name"], BattleBrawler.from_json(obj["brawler"]))

    def fetch_player(self, client):
        """Utility method to fetch this player's account data"""
        return client.get_player(self.tag)

@dataclass
class BattleTeam(BaseModel):
    """Represents a team in a battle (list of players)"""
    players: list[BattlePlayer]

    @classmethod
    def from_json(cls, obj: list[object]):
        return cls([BattlePlayer.from_json(x) for x in obj])

@dataclass
class Battle(BaseModel):
    """Represents a battle that was played"""
    battle_time: datetime
    event: BattleEvent
    mode: str
    type: str
    result: str
    duration: Optional[int]
    trophy_change: Optional[int]
    star_player: Optional[BattlePlayer]

    @classmethod
    def from_json(cls, obj):
        battle = obj["battle"]
        return cls(
            dateutil.parser.isoparse(obj["battleTime"]),
            BattleEvent.from_json(obj["event"]),
            battle["mode"],
            battle.get("type", None),
            battle["result"] if "result" in battle else battle["rank"],
            battle.get("duration", None),
            battle.get("trophyChange", None),
            BattlePlayer.from_json(battle["starPlayer"]) if 'starPlayer' in battle else None,
        )

@dataclass
class SoloBattle(Battle):
    """Represents a match played in a solo mode"""
    players: list[BattlePlayer]

    @classmethod
    def from_json(cls, obj):
        items = Battle.from_json(obj).__dict__
        items.update({
            "players": [BattlePlayer.from_json(x) for x in obj["battle"]["players"]]
        })
        return cls(**items)

@dataclass
class TeamBattle(Battle):
    """Reperesents a match played in a mode with teams"""
    teams: list[BattleTeam]

    @classmethod
    def from_json(cls, obj):
        items = Battle.from_json(obj).__dict__
        items.update({
            "teams": [BattleTeam.from_json(x) for x in obj["battle"]["teams"]]
        })
        return cls(**items)

@dataclass
class PlayerIcon(BaseModel):
    """Represents a player's profile icon"""
    id: int

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "id")

@dataclass
class PlayerClub(BaseModel):
    """Represents a player's club"""
    tag: str
    name: str

    @classmethod
    def from_json(cls, obj):
        return cls._from_props(cls, obj, "tag name")

@dataclass
class PlayerBrawler(BaseModel):
    """Represents a player's personal brawler"""
    id: int
    name: str
    power_level: int
    rank: int
    trophies: int
    highest_trophies: int
    gears: list[BrawlerGear]
    gadgets: list[BrawlerAccessory]
    star_powers: list[BrawlerAccessory]

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["id"],
            obj["name"],
            obj["power"],
            obj["rank"],
            obj["trophies"],
            obj["highestTrophies"],
            [BrawlerGear.from_json(x) for x in obj["gears"]],
            [BrawlerAccessory.from_json(x) for x in obj["gadgets"]],
            [BrawlerAccessory.from_json(x) for x in obj["starPowers"]],
        )

@dataclass
class Player(BaseModel):
    """Represents a player's profile"""
    tag: str
    name: str
    name_color: str
    icon: PlayerIcon
    trophies: int
    highest_trophies: int
    xp_level: int
    xp_points: int
    qualified: bool
    victories_3v3: int
    victories_solo: int
    victories_duo: int
    best_robo_rumble_time: int
    best_time_as_big_brawler: int
    club: PlayerClub
    brawlers: list[PlayerBrawler]

    @classmethod
    def from_json(cls, obj):
        return cls(
            obj["tag"],
            obj["name"],
            obj["nameColor"],
            PlayerIcon.from_json(obj["icon"]),
            obj["trophies"],
            obj["highestTrophies"],
            obj["expLevel"],
            obj["expPoints"],
            obj["isQualifiedFromChampionshipChallenge"],
            obj["3vs3Victories"],
            obj["soloVictories"],
            obj["duoVictories"],
            obj["bestRoboRumbleTime"],
            obj["bestTimeAsBigBrawler"],
            PlayerClub.from_json(obj["club"]) if "club" in obj else None,
            [PlayerBrawler.from_json(x) for x in obj["brawlers"]]
        )

    def fetch_club(self, client):
        """Utility method to fetch this player's club"""
        return client.get_club(self.club.tag)
