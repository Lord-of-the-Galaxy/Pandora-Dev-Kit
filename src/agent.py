from __future__ import annotations

from abc import ABC, abstractmethod

import numpy.typing as npt

from entities import Inventory
from action import Action


class Agent(ABC):
    @abstractmethod
    def __init__(self, player: int, **kwargs):
        self.player = player

    @abstractmethod
    def move(self, move_num: int, game_map: npt.NDArray[object], p1_inv: Inventory, p2_inv: Inventory) -> list[Action]:
        pass

    def close(self):
        pass


class NullPlayer(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def move(self, move_num: int, game_map: npt.NDArray[object], p1_inv: Inventory, p2_inv: Inventory) -> list[Action]:
        return []
