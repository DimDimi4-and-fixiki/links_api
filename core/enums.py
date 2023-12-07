from enum import Enum

__all__ = ['Environment']


class Environment(str, Enum):
    STAGE = 'stage'
    PRE = 'pre'
    PROD = 'prod'
    UNKNOWN = 'unknown'
    LOCAL = 'local'

    def is_local(self) -> bool:
        return self == Environment.UNKNOWN

    @classmethod
    def from_str(cls, param: str) -> 'Environment':
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN
