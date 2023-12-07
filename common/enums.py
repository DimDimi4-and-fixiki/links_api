from __future__ import annotations

import typing as t
from enum import Enum


class ExtendedEnum(Enum):
    @classmethod
    def list(cls: t.Iterable):
        return list(map(lambda c: c.value, cls))


class Environment(str, Enum):
    STAGE = 'stage'
    PRE = 'pre'
    PROD = 'prod'
    LOCAL = 'local'
    UNKNOWN = 'unknown'

    def is_local(self) -> bool:
        return self in (Environment.UNKNOWN, Environment.LOCAL)

    @classmethod
    def from_str(cls, param: str) -> Environment:
        try:
            return cls(param.lower())
        except ValueError:
            return cls.UNKNOWN


class Platform(str, ExtendedEnum):
    Linux = 'Linux'
    Mac = 'Darwin'
    Windows = 'Windows'
    Unknown = 'Unknown'

    @classmethod
    def from_str(cls, param: str) -> Platform:
        for name in cls.list():
            if param == name:
                return cls(name)

        return cls(cls.Unknown)
