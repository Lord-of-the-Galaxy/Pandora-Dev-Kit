from enum import Enum, unique

from vec2 import vec2


@unique
class Resource(Enum):  # this also directly includes their descriptors as well
    ORE: str = 'O'
    FUEL: str = 'F'

    # this is completely, utterly useless, unnecessary, and probably evil
    # but PyCharm will complain without it (due to a bug)
    @property
    def value(self) -> str:
        return self._value_


@unique
class Direction(Enum):
    UP: str = 'U'
    DOWN: str = 'D'
    RIGHT: str = 'R'
    LEFT: str = 'L'
    NONE: str = 'N'

    @property
    def vec(self) -> vec2:
        if self == Direction.UP:
            return vec2(0, -1)
        elif self == Direction.DOWN:
            return vec2(0, 1)
        elif self == Direction.LEFT:
            return vec2(-1, 0)
        elif self == Direction.RIGHT:
            return vec2(1, 0)
        else:
            return vec2(0, 0)

    # this is completely, utterly useless, unnecessary, and probably evil
    # but PyCharm will complain without it (due to a bug)
    @property
    def value(self) -> str:
        return self._value_

    @staticmethod
    def from_vec(v: vec2):
        if v == vec2(0, -1):
            return Direction.UP
        elif v == vec2(0, 1):
            return Direction.DOWN
        elif v == vec2(-1, 0):
            return Direction.LEFT
        elif v == vec2(1, 0):
            return Direction.RIGHT
        else:
            return Direction.NONE


def enum_encoder(enum: Enum):  # this is a one-way encoder, cannot be decoded
    return enum.name


# these provide two-way functionality, both encodes and decodes
def full_enum_encoder(enum: Enum):
    return {'__enum__': enum.__class__.__name__, 'value': enum.value}


def full_enum_decoder(dct: dict):
    # for security reasons we will only decode the known types
    if '__enum__' in dct:
        if dct['__enum__'] == Resource.__name__:
            return Resource(dct['value'])
        elif dct['__enum__'] == Direction.__name__:
            return Direction(dct['value'])
    return dct
