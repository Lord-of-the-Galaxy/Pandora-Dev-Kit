from __future__ import annotations
from typing import NamedTuple


# noinspection PyPep8Naming
class vec2(NamedTuple):
    """A very basic 2-tuple with addition"""
    x: int
    y: int

    def __add__(self, other: vec2):
        return vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: vec2):
        return vec2(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return vec2(-self.x, -self.y)

    def __mul__(self, other: int):
        return vec2(other*self.x, other*self.y)

    __rmul__ = __mul__

    def __abs__(self):
        return abs(self.x) + abs(self.y)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return f"{type(self).__name__}({self.x}, {self.y})"
