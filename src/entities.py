from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Any, Optional
import numpy.typing as npt
from colorama import Fore, Style

from vec2 import vec2
from enums import Resource, Direction
import params


class Entity(ABC):
    auto_id: int = 1
    desc: str
    known_entities: dict[str, type[Entity]] = {}

    @abstractmethod
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, *, ent_id: Optional[int] = None, **kwargs):
        # by this point **kwargs should be empty as Entity MUST be the base class for everything else
        if ent_id is None:
            self.id = Entity.auto_id  # automatically assigns a unique ID to every entity
            Entity.auto_id += 1
        else:
            self.id = ent_id
        self.p_inv: Inventory = p_inv
        p_inv += self  # automatically add it to the player inventory
        self.player = p_inv.player
        self.game_params = game_params
        info = game_params.get_info(type(self))
        self.max_value: int = info.max_value
        self.max_health: int = info.max_health
        self.health: int = info.max_health
        self.pos: vec2 = pos
        # automatically add it to the map
        # NOTE: this means we can NEVER change the object that Game.game_map points to
        self.game_map = game_map
        # if there is on the map, add this object there, otherwise let the subclass handle it
        if game_map[pos] is None:
            game_map[pos] = self
        self._to_destroy = False

    def do_damage(self, amt: int):
        self.health -= amt
        if self.health <= 0:
            self._to_destroy = True
            self.health = 0

    def destroy(self, force: bool = False) -> bool:
        if self._to_destroy or force:
            self.p_inv -= self
            # if this is the object on the map, remove it, otherwise let the subclass handle it
            if self.game_map[self.pos] == self:
                self.game_map[self.pos] = None
            return True
        return False

    @property
    def value(self) -> int:
        return max((self.max_value * self.health) // self.max_health, 1)  # every entity has a value at least 1

    @property
    def symbol(self) -> str:
        color = Fore.BLUE if self.player == 1 else Fore.RED
        return color + self.desc + Style.RESET_ALL

    def min_repr(self) -> dict[str, Any]:
        """A minimal representation of the entity. Must be a dict"""
        return {'t': self.desc, 'i': str(self.id), 'h': self.health, 'p': self.player}

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, pos={self.pos}, pl={self.player})"

    def __init_subclass__(cls: type[Entity], desc: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if desc is not None:
            cls.desc = desc
            Entity.known_entities[desc] = cls

    @staticmethod
    def find_type(desc: str):
        return Entity.known_entities[desc]


class Attacker(Entity, ABC):
    attacks: tuple[type[Entity], ...]

    @abstractmethod
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)
        info = game_params.get_info(type(self))
        self.damage: int = info.damage
        self.range: int = info.range

    def __init_subclass__(cls, attacks: tuple[type[Entity]] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if attacks is not None:
            cls.attacks = attacks

    def attack_all(self) -> list[vec2]:
        # NOTE: Decide if ships should be allowed to attack from inside buildings (would enhance the value of Bases)
        # if self.game_map[self.pos] != self:
        #     return []  # a ship can only attack when it's not inside a building
        attacks: list[Entity] = []
        for pos in diamond(self.pos, self.range, self.game_map.shape[0], self.game_map.shape[1]):
            ent: Optional[Entity] = self.game_map[pos]
            if isinstance(ent, self.attacks) and self.player != ent.player:
                attacks.append(ent)
        if len(attacks) == 0:
            return []
        dmg = self.damage // len(attacks)
        for ent in attacks:
            ent.do_damage(dmg)
        return [ent.pos for ent in attacks]


class Ship(Entity, ABC):
    @abstractmethod
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)
        self.dir: Direction = Direction.UP  # only for visual representation purposes
        # if this ship was created on some building, put it in the building
        mo = game_map[pos]
        if isinstance(mo, Building):
            mo.add_ship(self)
        self.new_pos = pos  # this is required to handle collisions on movement

    def min_repr(self) -> dict[str, Any]:
        d = super().min_repr()
        d['d'] = self.dir.value
        return d

    def destroy(self, force: bool = False) -> bool:
        if super().destroy(force=force):
            # we have to check if we are in a building
            mo = self.game_map[self.pos]
            if isinstance(mo, Building):
                mo.remove_ship(self)
            return True
        return False

    def move(self, direction: Direction) -> Optional[str]:
        if direction == Direction.NONE:
            return None  # nothing to move
        new_pos = self.pos + direction.vec
        if not ((0 <= new_pos.x < self.game_map.shape[0]) and (0 <= new_pos.y < self.game_map.shape[1])):
            return None  # we stay where we are
        if isinstance(self.game_map[new_pos], ResourceDeposit):
            return None  # we stay where we are, can't move into a resource deposit
        # we only move out of our current position for now, and handle moving into the new position later
        self.new_pos = new_pos
        self.dir = direction  # update the direction we are facing in
        mo = self.game_map[self.pos]
        if mo == self:
            self.game_map[self.pos] = None
        else:
            assert isinstance(mo, Building)  # this should never fail
            assert mo.remove_ship(self)  # this should never fail either
        return direction.value

    def complete_move(self, collisions: set[vec2]):
        if self.new_pos in collisions and not isinstance(self.game_map[self.new_pos], Building):
            # if it is a building, it is handled separately
            self.destroy(force=True)  # we are in a spot with a collision, so destroy
            return
        # if we did not actually move, then we don't need to do anything
        if self.pos == self.new_pos:
            return
        self.pos = self.new_pos  # update our position
        mo = self.game_map[self.pos]
        if isinstance(mo, Building):
            if not mo.add_ship(self):
                # the building at the new position is already full, so we must destroy the ship
                self.destroy(force=True)
                collisions.add(self.new_pos)
        else:
            assert mo is None  # it HAS to be None, otherwise we have an error
            self.game_map[self.pos] = self  # move our ship to new location


class Building(Entity, ABC):
    @abstractmethod
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)
        info = game_params.get_info(type(self))
        self.vehicle_capacity: int = info.vehicle_capacity
        self.vehicles: list[Ship] = []

    def add_ship(self, ship: Ship) -> bool:
        if len(self.vehicles) < self.vehicle_capacity and ship.player == self.player:
            self.vehicles.append(ship)
            return True
        else:
            return False

    def remove_ship(self, ship: Ship) -> bool:
        # this does not cause an error if there is no such ship, and this is intentional
        if ship in self.vehicles:
            self.vehicles.remove(ship)
            return True
        else:
            return False

    def destroy(self, force: bool = False, destroy_ships: bool = True):
        if super().destroy(force=force) and destroy_ships:
            for v in self.vehicles:
                v.destroy(force=True)
            return True
        return False

    def min_repr(self) -> dict[str, Any]:
        d = super().min_repr()
        d['v'] = {v.id: v.min_repr() for v in self.vehicles}
        return d


class Constructable(Building, ABC):
    @abstractmethod
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)


class UnderConstruction(Building, desc='C'):
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, building_type: type[Constructable], **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)
        self.building_type: type[Building] = building_type
        self.ore: int = 0
        self.fuel: int = 0
        building_cost = game_params.get_info(building_type)
        self.total_ore_needed: int = building_cost.ore_cost
        self.total_fuel_needed: int = building_cost.fuel_cost

    def min_repr(self) -> dict[str, Any]:
        d = super().min_repr()
        d['b'] = self.building_type.desc
        progress = Resource.ORE.value * self.ore + Resource.FUEL.value * self.fuel
        total = Resource.ORE.value * self.total_ore_needed + Resource.FUEL.value * self.total_fuel_needed
        d['m'] = round(progress / total, 2)
        return d

    def build(self, resources: list[Resource]) -> list[Resource]:
        new_ore = resources.count(Resource.ORE)
        new_fuel = resources.count(Resource.FUEL)
        use_ore = min(self.total_ore_needed - self.ore, new_ore)
        use_fuel = min(self.total_fuel_needed - self.fuel, new_fuel)
        self.ore += use_ore
        self.fuel += use_fuel
        for _ in range(use_ore):
            resources.remove(Resource.ORE)
        for _ in range(use_fuel):
            resources.remove(Resource.FUEL)

        # check if the building is done, and if so, replace with said building
        if self.ore == self.total_ore_needed and self.fuel == self.total_fuel_needed:
            self.destroy(force=True, destroy_ships=False)  # destroy this, but not the vehicles in it
            new_building = self.building_type(self.p_inv, self.game_map, self.pos, self.game_params)
            for v in self.vehicles:
                if not new_building.add_ship(v):
                    # uh oh, no space for the vehicle - we must destroy it
                    v.destroy(force=True)  # this is fine as Building.remove_ship() fails silently
            self.vehicles = []
        return resources


class Base(Constructable, desc='B'):
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)

    def build(self, ship_type: type[Ship]):
        ship_info = self.game_params.get_info(ship_type)
        if self.p_inv.ore < ship_info.ore_cost or self.p_inv.fuel < ship_info.fuel_cost:
            return  # not enough resources
        if len(self.vehicles) >= self.vehicle_capacity:
            return  # no space for the vehicle
        # everything ok, so build
        ship_type(self.p_inv, self.game_map, self.pos, self.game_params)
        # and remove the resources
        self.p_inv.ore -= ship_info.ore_cost
        self.p_inv.fuel -= ship_info.fuel_cost


class Turret(Constructable, Attacker, desc='T', attacks=(Ship,)):
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)  # turrets only attack ships


class Miner(Ship, Attacker, desc='M', attacks=(Ship,)):
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)  # miners only attack ships
        self.cargo: list[Resource] = []
        self.cargo_space: int = game_params.miners.cargo_space

    def min_repr(self) -> dict[str, Any]:
        d = super().min_repr()
        d['c'] = "".join([res.value for res in self.cargo])
        return d

    def mine(self, mine_dir: Direction):
        possible = [v for v in diamond(self.pos, 1, self.game_map.shape[0], self.game_map.shape[1])
                    if isinstance(self.game_map[v], ResourceDeposit)]
        mine_pos = self.pos + mine_dir.vec
        if mine_dir == Direction.NONE and len(possible) > 0:
            mine_pos = possible[0]  # select first possible direction if none supplied
        if mine_pos in possible and len(self.cargo) < self.cargo_space:
            # possible to mine, so mine
            self.game_map[mine_pos].mine(self)

    def change_cargo(self, new_cargo: list[Resource]):
        # a bunch of things to check
        if not isinstance(self.game_map[self.pos], Base):
            return  # not in a base
        if len(new_cargo) > self.cargo_space:
            return  # can't put more than cargo_space resources into the cargo hold
        ore_diff = new_cargo.count(Resource.ORE) - self.cargo.count(Resource.ORE)
        fuel_diff = new_cargo.count(Resource.FUEL) - self.cargo.count(Resource.FUEL)
        if self.p_inv.ore < ore_diff or self.p_inv.fuel < fuel_diff:
            return  # not enough ore or fuel
        # everything OK, execute
        self.p_inv.ore -= ore_diff
        self.p_inv.fuel -= fuel_diff
        self.cargo = new_cargo.copy()

    def build(self, building_type: Optional[type[Constructable]] = None):
        mo = self.game_map[self.pos]
        if isinstance(mo, UnderConstruction):
            # we are on an already-under-construction building, so just build it more
            self.cargo = mo.build(self.cargo)
        if mo != self:
            return  # we aren't on an otherwise empty spot or on an already-under-construction building
        if building_type is None:
            return  # can't build without knowing WHAT to build
        self.game_map[self.pos] = None  # empty the spot to start building
        uc = UnderConstruction(self.p_inv, self.game_map, self.pos, self.game_params, building_type=building_type)
        uc.add_ship(self)
        self.cargo = uc.build(self.cargo)


class Fighter(Ship, Attacker, desc='K', attacks=(Entity,)):
    def __init__(self, p_inv: Inventory, game_map: npt.NDArray[object], pos: vec2,
                 game_params: params.GameParams, **kwargs):
        super().__init__(p_inv, game_map, pos, game_params, **kwargs)  # fighters attack everything


# the next few are not strictly entities, but I think they're best off here

@dataclass
class ResourceDeposit:
    """A single resource deposit"""
    amount: int
    resource: Resource
    _miners: list[Miner] = field(default_factory=list)

    def mine(self, miner: Miner):
        self._miners.append(miner)  # we shall later determine if we have enough for the miner to mine it

    def complete_mining(self):
        remove = False
        if self.amount >= len(self._miners):
            # this deposit has enough to supply
            self.amount -= len(self._miners)
            for miner in self._miners:
                miner.cargo.append(self.resource)
            if self.amount == 0:  # is the deposit depleted?
                remove = True  # remove/destroy this deposit
        self._miners = []  # empty it for next step
        return remove

    def min_repr(self):
        return {'t': self.resource.value, 'a': self.amount}

    @property
    def symbol(self) -> str:
        color = Fore.GREEN if self.resource == Resource.ORE else Fore.YELLOW
        return color + self.resource.value + Style.RESET_ALL


@dataclass
class Inventory:
    """Represents the inventory of one player"""
    player: int
    game_params: params.GameParams
    ore: int = 0
    fuel: int = 0
    under_construction: list[UnderConstruction] = field(default_factory=list)
    bases: list[Base] = field(default_factory=list)
    turrets: list[Turret] = field(default_factory=list)
    miners: list[Miner] = field(default_factory=list)
    fighters: list[Fighter] = field(default_factory=list)

    @property
    def entities(self) -> list[Entity]:
        l: list[Entity] = []  # for the type checker to not complain
        return l + self.under_construction + self.bases + self.turrets + self.miners + self.fighters

    @property
    def attackers(self) -> list[Attacker]:
        l: list[Attacker] = []  # for the type checker to not complain
        return l + self.turrets + self.miners + self.fighters

    @property
    def buildings(self) -> list[Building]:
        l: list[Building] = []  # for the type checker to not complain
        return l + self.under_construction + self.bases + self.turrets

    @property
    def ships(self) -> list[Ship]:
        l: list[Ship] = []  # for the type checker to not complain
        return l + self.miners + self.fighters

    @property
    def score(self) -> int:
        total: int = self.ore * self.game_params.resources.ore + self.fuel * self.game_params.resources.fuel
        for entity in self.entities:
            total += entity.value
        return total

    def add(self, other: Entity):
        if isinstance(other, UnderConstruction):
            self.under_construction.append(other)
        elif isinstance(other, Base):
            self.bases.append(other)
        elif isinstance(other, Turret):
            self.turrets.append(other)
        elif isinstance(other, Miner):
            self.miners.append(other)
        elif isinstance(other, Fighter):
            self.fighters.append(other)

    def remove(self, other: Entity):
        if isinstance(other, UnderConstruction):
            self.under_construction.remove(other)
        elif isinstance(other, Base):
            self.bases.remove(other)
        elif isinstance(other, Turret):
            self.turrets.remove(other)
        elif isinstance(other, Miner):
            self.miners.remove(other)
        elif isinstance(other, Fighter):
            self.fighters.remove(other)

    def __iadd__(self, other: Entity):
        self.add(other)
        return self

    def __isub__(self, other):
        self.remove(other)
        return self

    def min_repr(self):
        return {'player': self.player, 'ore': self.ore, 'fuel': self.fuel, 'bases': len(self.bases),
                'turrets': len(self.turrets), 'under_construction': len(self.under_construction),
                'miners': len(self.miners), 'fighters': len(self.fighters), 'points': self.score}


# a helper function

def diamond(pos: vec2, size: int, width: int, height: int) -> Iterator[vec2]:
    """A generator that goes through everything within distance <size> of <pos> (taxicab metric) with constraints"""
    for i in range(max(-size, -pos.x), min(size + 1, width - pos.x)):
        for j in range(max(-size + abs(i), -pos.y), min(size + 1 - abs(i), height - pos.y)):
            if i == 0 and j == 0:
                continue
            yield pos + vec2(i, j)
