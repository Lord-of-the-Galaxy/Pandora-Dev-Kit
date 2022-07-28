from __future__ import annotations

from typing import Optional

from entities import Entity, Ship, Miner, Base, Turret, Constructable
from enums import Direction, Resource


class Action:
    def __init__(self, entity: Entity):
        self.entity = entity
        self._move: Direction = Direction.NONE
        self._mine: Optional[Direction] = None
        self._cargo: Optional[list[Resource]] = None
        self._build: bool = False
        self._build_type: Optional[type[Ship | Constructable]] = None

    def move(self, direction: Direction):
        if isinstance(self.entity, Ship):
            self._move = direction
        return self

    def execute_move(self) -> Optional[str]:
        if isinstance(self.entity, Ship):
            self.entity.move(self._move)
            return self._move.value
        return None

    def mine(self, direction: Direction = Direction.NONE):
        if isinstance(self.entity, Miner):
            self._mine = direction
            self._build = False
            self._cargo = None
        return self

    def execute_mine(self):
        # the second check is unnecessary, but the type checker complains without it
        if self._mine is not None and isinstance(self.entity, Miner):
            self.entity.mine(self._mine)

    def cargo(self, new_cargo: list[Resource]):
        if isinstance(self.entity, Miner) and len(new_cargo) <= self.entity.cargo_space:
            self._cargo = new_cargo
            self._mine = None
            self._build = False
        return self

    def execute_cargo(self):
        # the second check is unnecessary, but the type checker complains without it
        if self._cargo is not None and isinstance(self.entity, Miner):
            self.entity.change_cargo(self._cargo)

    def build(self, build_type: type[Ship | Constructable]):
        if isinstance(self.entity, Miner) and issubclass(build_type, Constructable):
            self._build = True
            self._build_type = build_type
            self._mine = None
            self._cargo = None
        elif isinstance(self.entity, Base) and issubclass(build_type, Ship):
            self._build = True
            self._build_type = build_type
        return self

    def execute_build(self):
        # the type checker will complain without this stupid bit of code
        if self._build and isinstance(self.entity, Miner):
            self.entity.build(self._build_type)
        elif self._build and isinstance(self.entity, Base):
            self.entity.build(self._build_type)

    def encode(self) -> str:
        s = self._move.value
        if self._mine is not None:
            s += 'M' + self._mine.value
        elif self._cargo is not None:
            s += 'C' + ''.join([res.value for res in self._cargo])
        elif self._build:
            s += 'B' + ('' if self._build_type is None else self._build_type.desc)
        return s

    def decode(self, s: str) -> Action:
        try:
            self._move = Direction(s[0])
            if s[1] == 'M' and isinstance(self.entity, Miner):
                self._mine = Direction(s[2])
            elif s[1] == 'C' and isinstance(self.entity, Miner):
                self._cargo = [Resource(c) for c in s[2:]]
            elif s[1] == 'B':
                build_type = Entity.find_type(s[2])
                if isinstance(self.entity, Base) and issubclass(build_type, Ship):
                    self._build = True
                    self._build_type = build_type
                elif isinstance(self.entity, Miner) and issubclass(build_type, Base | Turret):
                    self._build = True
                    self._build_type = build_type
        finally:
            # if we have an error, we don't care - even valid actions may cause an exception but still decode correctly
            return self
