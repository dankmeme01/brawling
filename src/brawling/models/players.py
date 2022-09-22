from .base import BaseModel
from dataclasses import dataclass
from datetime import datetime
import dateutil.parser

@dataclass
class BattleEvent(BaseModel):
    id: int
    mode: str
    map: str

    @classmethod
    def from_json(cls, obj):
        return cls(obj["id"], obj.get("mode", None), str(obj["map"]))

@dataclass
class BattleBrawler(BaseModel):
    id: int
    name: str
    power: int
    trophies: int

    @classmethod
    def from_json(cls, obj):
        return cls(obj["id"], obj["name"], obj["power"], obj["trophies"])

@dataclass
class BattlePlayer(BaseModel):
    tag: str
    name: str
    brawler: BattleBrawler

    @classmethod
    def from_json(cls, obj):
        return cls(obj["tag"], obj["name"], BattleBrawler.from_json(obj["brawler"]))

@dataclass
class BattleTeam(BaseModel):
    players: list[BattlePlayer]

    @classmethod
    def from_json(cls, obj: list[object]):
        return cls([BattlePlayer.from_json(x) for x in obj])

@dataclass
class Battle(BaseModel):
    battle_time: datetime
    event: BattleEvent
    mode: str
    type: str
    result: str
    duration: int
    trophy_change: int
    star_player: BattlePlayer
    teams: list[BattleTeam]

    @classmethod
    def from_json(cls, obj):
        battle = obj["battle"]
        return cls(
            dateutil.parser.isoparse(obj["battleTime"]),
            BattleEvent.from_json(obj["event"]),
            battle["mode"],
            battle["type"],
            battle["result"] if "result" in battle else battle["rank"],
            battle.get("duration", None),
            battle.get("trophyChange", None),
            BattlePlayer.from_json(battle["starPlayer"]) if 'starPlayer' in battle else None,
            [BattleTeam.from_json(x) for x in battle["teams"]]
        )
