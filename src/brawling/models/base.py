from dataclasses import dataclass

__all__ = [
    "BaseModel"
]

@dataclass
class BaseModel:
    @classmethod
    def from_json(cls, obj):
        raise NotImplementedError()
