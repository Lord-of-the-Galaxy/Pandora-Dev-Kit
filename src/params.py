from __future__ import annotations

from dataclasses import dataclass, field
from typing import overload

import entities
from enums import Resource


# TODO: Add docstrings to everything

@dataclass
class ResourceInfo:
    ore: int = 2
    fuel: int = 5


# NOTE: <Name>Info is a dataclass that provides information about <Name> objects
#  The entities themselves will have class <Name>

@dataclass
class EntityInfo:  # everything you can control is an entity in the game
    max_value: int  # value (points) of the entity at full health
    max_health: int  # maximum health (the entity starts with this much health)


@dataclass
class EntityCostInfo:  # most entities have an associated cost to build them
    ore_cost: int  # ore needed to build the entity
    fuel_cost: int  # fuel needed to build the entity


@dataclass
class AttackerInfo(EntityInfo):  # some entities can attack other entities
    damage: int  # the total damage dealt by the entity to enemy entities (split evenly among the enemy entities)
    range: int  # the maximum range at which it can deal damage (taxicab metric)


@dataclass
class BuildingInfo(EntityInfo):  # buildings do not move, and can hold ships
    vehicle_capacity: int  # the maximum number of ships the building can hold
    # trying to move more ships into the building will result in the ships being destroyed


@dataclass
class ConstructableInfo(BuildingInfo, EntityCostInfo):  # a constructable is a building that can be built by the player
    pass


@dataclass
class UnderConstructionInfo(BuildingInfo):  # this is used for buildings still being constructed
    # default values:
    max_value: int = 1
    max_health: int = 2000
    vehicle_capacity: int = 1


@dataclass
class BaseInfo(ConstructableInfo):  # this is a base, check the website for more details about it
    # default values:
    max_value: int = 75
    max_health: int = 10000
    vehicle_capacity: int = 30
    ore_cost: int = 30
    fuel_cost: int = 6


@dataclass
class TurretInfo(ConstructableInfo, AttackerInfo):  # this is a turret, check the website for more details about it
    # default values:
    max_value: int = 45
    max_health: int = 8000
    vehicle_capacity: int = 4
    ore_cost: int = 20
    fuel_cost: int = 5
    damage: int = 900
    range: int = 4


@dataclass
class ShipInfo(EntityInfo, EntityCostInfo):  # a ship can move one step in any direction on every turn
    pass


@dataclass
class MinerInfo(ShipInfo, AttackerInfo):  # this is a miner, check the website for more details about it
    # default values:
    max_value: int = 20
    max_health: int = 2000
    ore_cost: int = 8
    fuel_cost: int = 2
    damage: int = 300
    range: int = 2
    cargo_space: int = 4


@dataclass
class FighterInfo(ShipInfo, AttackerInfo):  # this is a fighter, check the website for more details about it
    # default values:
    max_value: int = 25
    max_health: int = 3000
    ore_cost: int = 10
    fuel_cost: int = 3
    damage: int = 600
    range: int = 3


@dataclass
class StartParams:  # this is for internal use, players will not need to understand it
    """Various miscellaneous parameters used at game start"""
    miners: int = 10
    fighters: int = 3
    min_len: int = 400
    max_len: int = 600
    min_w: int = 48
    max_w: int = 52
    min_h: int = 23
    max_h: int = 27
    base_off: int = 3
    clear: int = 3


@dataclass
class DepositParams:  # this is for internal use, players will not need to understand it
    """Parameters for creation of deposits of some particular type"""
    resource: Resource
    min_num: int
    max_num: int
    min_size: int
    max_size: int
    min_start_amt: int
    max_start_amt: int
    min_inc_amt: int
    max_inc_amt: int
    max_amt: int
    left_offset: int
    right_offset: int


def default_deposit_ore():
    return DepositParams(Resource.ORE, 6, 9, 5, 9, 7, 9, 3, 5, 25, 0, 6)


def default_deposit_fuel():
    return DepositParams(Resource.FUEL, 4, 6, 3, 6, 4, 6, 2, 3, 15, 8, 0)


# read the comments alongside the class definitions above for more information
@dataclass
class GameParams:
    """All parameters used by the game"""
    resources: ResourceInfo = field(default_factory=ResourceInfo)
    under_construction: UnderConstructionInfo = field(default_factory=UnderConstructionInfo)
    bases: BaseInfo = field(default_factory=BaseInfo)
    turrets: TurretInfo = field(default_factory=TurretInfo)
    miners: MinerInfo = field(default_factory=MinerInfo)
    fighters: FighterInfo = field(default_factory=FighterInfo)
    start: StartParams = field(default_factory=StartParams)
    ore_deposits: DepositParams = field(default_factory=default_deposit_ore)
    fuel_deposits: DepositParams = field(default_factory=default_deposit_fuel)

    @overload
    def get_info(self, entity_type: type[entities.UnderConstruction]) -> UnderConstructionInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Base]) -> BaseInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Turret]) -> TurretInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Constructable]) -> ConstructableInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Building]) -> BuildingInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Fighter]) -> FighterInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Miner]) -> MinerInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Ship]) -> ShipInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Attacker]) -> AttackerInfo:
        ...

    @overload
    def get_info(self, entity_type: type[entities.Entity]) -> EntityInfo:
        ...

    def get_info(self, entity_type: type[entities.Entity]) -> EntityInfo:
        type_to_info: dict[type[entities.Entity], EntityInfo] = {
            entities.UnderConstruction: self.under_construction,
            entities.Base: self.bases,
            entities.Turret: self.turrets,
            entities.Miner: self.miners,
            entities.Fighter: self.fighters
        }
        return type_to_info[entity_type]


@dataclass
class TimeLimits:
    """Time limits (in seconds) for players"""
    INIT: int = 30  # the maximum time that may be used by your Player class's constructor
    MAIN: int = 120  # this is the main time (total time) you start with on your clock
    INCREMENT: int = 2  # this is the increment added to your clock for each move
    DELAY: int = 1  # this delay is used to compensate for various delays
    # between the time when your code returns and the time when the game can process your move
    # you should not try to use up this time as it will likely result in a timeout (and thus a loss)
