from __future__ import annotations

import json
from dataclasses import asdict
from random import Random

import numpy as np
import numpy.typing as npt

from vec2 import vec2
from enums import Resource, enum_encoder
from entities import Inventory, Base, Turret, Miner, Fighter, ResourceDeposit, diamond, Attacker, Entity, Ship, Building
from params import GameParams, TimeLimits, DepositParams
from action import Action
from agent import Agent


LOG_DIR = "./game_logs"


# noinspection PyPep8Naming,PyProtectedMember
class Game:
    """Class encapsulating a single game"""

    def __init__(self, game_id: int, player_1: type[Agent], player_2: type[Agent], *, seed: int = 0,
                 time_limits: TimeLimits = TimeLimits(), game_params: GameParams = GameParams()):
        self.game_id: int = game_id
        self.game_over: bool = False
        self.time_limits: TimeLimits = time_limits
        self.params: GameParams = game_params
        self.rand: Random = Random(seed)
        self.game_length: int = self.rand.randrange(game_params.start.min_len, game_params.start.max_len + 1)
        self.move_num: int = 0

        self.p1_inv = Inventory(1, game_params)
        self.p2_inv = Inventory(2, game_params)

        # map generation
        self.w: int
        self.h: int
        self.game_map: npt.NDArray[object]
        self.deposits: dict[vec2, ResourceDeposit] = {}
        self.generate_map()

        # starting ships
        base_1 = self.p1_inv.bases[0]
        base_2 = self.p2_inv.bases[0]
        for _ in range(game_params.start.miners):
            Miner(self.p1_inv, self.game_map, base_1.pos, game_params)
            Miner(self.p2_inv, self.game_map, base_2.pos, game_params)
        for _ in range(game_params.start.fighters):
            Fighter(self.p1_inv, self.game_map, base_1.pos, game_params)
            Fighter(self.p2_inv, self.game_map, base_2.pos, game_params)

        # initialise agents
        game_info = {
            'game_params': game_params,
            'time_limits': time_limits,
            'map_w': self.w,
            'map_h': self.h,
            'game_map': self.game_map
        }

        self.player_1: Agent = player_1(1, **game_info)
        self.player_2: Agent = player_2(2, **game_info)

    def play(self, log: bool = False, log_p: bool = False):
        if self.game_over:
            return
        frames = []
        if log_p:
            print('=' * (self.w * 2 - 1))
            print(str(self))
            print('=' * (self.w * 2 - 1))

        while not self.game_over:
            min_map = [[self.game_map[x, y].min_repr() if self.game_map[x, y] is not None else {'t': 'E'}
                        for y in range(self.h)] for x in range(self.w)]
            info = [self.p1_inv.min_repr(), self.p2_inv.min_repr()]
            moves, collisions, attacks, destroyed = self.step()
            frame = {
                'info': info,
                'map': min_map,
                'moves': moves,
                'collisions': collisions,
                'attacks': attacks,
                'destroyed': destroyed
            }
            frames.append(frame)
            if log_p:
                print(str(self))
                print('=' * (self.w * 2 - 1))
            elif self.move_num % 50 == 0:
                print(f"Move {self.move_num} [{info[0]['points']} vs {info[1]['points']}]")
        min_map = [[self.game_map[x, y].min_repr() if self.game_map[x, y] is not None else {'t': 'E'}
                    for y in range(self.h)] for x in range(self.w)]
        info = [self.p1_inv.min_repr(), self.p2_inv.min_repr()]
        frame = {
            'info': info,
            'map': min_map,
            'moves': {},
            'collisions': [],
            'attacks': [],
            'destroyed': []
        }
        frames.append(frame)
        if log:
            logs = {
                'info': {
                    'game_id': self.game_id,
                    'game_length': self.game_length,
                    'map_w': self.w,
                    'map_h': self.h,
                    'game_params': asdict(self.params)
                },
                'frames': frames
            }

            print("Saving game logs...")
            with open(f"{LOG_DIR}/game_{self.game_id}.plog", 'w') as f:
                json.dump(logs, f, default=enum_encoder)

    def step(self) -> tuple[dict[str, str], list[vec2], list[tuple[vec2, vec2, int]], list[vec2]]:
        if self.game_over:
            return {}, [], [], []
        self.move_num += 1
        if self.move_num == self.game_length:
            self.game_over = True
        # we assume that the actions we have received here are already validated
        actions1: list[Action] = self.player_1.move(self.move_num, self.game_map, self.p1_inv, self.p2_inv)
        actions2: list[Action] = self.player_2.move(self.move_num, self.game_map, self.p1_inv, self.p2_inv)
        actions = actions1 + actions2
        # first comes mining
        self.execute_mining(actions)
        # then cargo
        for a in actions:
            a.execute_cargo()
        # then building new ships and buildings
        for a in actions:
            a.execute_build()
        # now we can get to moving the ships
        moves, collisions = self.execute_movement(actions)
        # and finally execute the attacks, and destroy entities as needed
        attacks, destroyed = self.execute_attacks()

        if len(self.p1_inv.bases) == 0 or len(self.p2_inv.bases) == 0:
            self.game_over = True  # someone lost all their bases

        # print(f"c - {collisions}, a - {attacks}, d - {destroyed}")
        return moves, collisions, attacks, destroyed

    def execute_mining(self, actions: list[Action]):
        for a in actions:
            a.execute_mine()
        keys = list(self.deposits.keys())
        for pos in keys:
            dep = self.deposits[pos]
            if dep.complete_mining():
                self.game_map[pos] = None
                self.deposits.pop(pos)

    def execute_movement(self, actions: list[Action]) -> tuple[dict[str, str], list[vec2]]:
        moves: dict[str, str] = {}
        for a in actions:
            m = a.execute_move()
            if m is not None:
                moves[str(a.entity.id)] = m
        ships = self.p1_inv.ships + self.p2_inv.ships
        new_pos: dict[vec2, list[Ship]] = {}
        for s in ships:
            if s.new_pos in new_pos:
                new_pos[s.new_pos].append(s)
            else:
                new_pos[s.new_pos] = [s]
        collisions: set[vec2] = {p for p in new_pos if
                                 len(new_pos[p]) > 1 and not isinstance(self.game_map[p], Building)}
        for s in ships:
            s.complete_move(collisions)
        return moves, list(collisions)

    def execute_attacks(self) -> tuple[list[tuple[vec2, vec2, int]], list[vec2]]:
        attackers: list[Attacker] = self.p1_inv.attackers + self.p2_inv.attackers
        attacks: list[tuple[vec2, vec2, int]] = []
        a_idx: dict[tuple[vec2, vec2], int] = {}
        for a in attackers:
            na = a.attack_all()
            for v in na:
                if (a.pos, v) in a_idx:
                    pass  # this pair is already there
                elif (v, a.pos) in a_idx:  # the reverse attack exists
                    attacks[a_idx[(v, a.pos)]] = (v, a.pos, 0)
                else:  # no attacks between these two positions yet
                    a_idx[(a.pos, v)] = len(attacks)
                    attacks.append((a.pos, v, a.player))

        # destroy everything that needs to be destroyed
        entities: list[Entity] = self.p1_inv.entities + self.p2_inv.entities
        destroyed: list[vec2] = [e.pos for e in entities if e.destroy()]
        return attacks, destroyed

    # noinspection PyAttributeOutsideInit
    def generate_map(self):
        self.w = self.rand.randrange(self.params.start.min_w, self.params.start.max_w + 1)
        self.h = self.rand.randrange(self.params.start.min_h, self.params.start.max_h + 1)
        self.game_map = np.ndarray((self.w, self.h), dtype=object)

        base_x = self.rand.randrange(self.params.start.clear, self.params.start.clear + self.params.start.base_off + 1)
        base_y = self.rand.randrange((self.h - 1) // 2 - self.params.start.base_off,
                                     self.h // 2 + self.params.start.base_off + 1)
        base_pos = vec2(base_x, base_y)
        base_pos_2 = vec2(self.w - base_x - 1, base_y)

        Base(self.p1_inv, self.game_map, base_pos, self.params)
        Base(self.p2_inv, self.game_map, base_pos_2, self.params)

        # now we mark the space around the first base to ensure no deposits are formed too close to it
        CLEAR = 'CLEAR'
        for pos in diamond(base_pos, self.params.start.clear, self.w, self.h):
            self.game_map[pos] = CLEAR  # we only clear on one side due to the way generate_deposit works
        # now we can generate deposits
        # determine number of deposits of each type
        num_ore = self.rand.randrange(self.params.ore_deposits.min_num, self.params.ore_deposits.max_num + 1)
        num_fuel = self.rand.randrange(self.params.fuel_deposits.min_num, self.params.fuel_deposits.max_num + 1)
        # generate them
        for _ in range(num_ore):
            self.generate_deposit(Resource.ORE, self.params.ore_deposits)
        for _ in range(num_fuel):
            self.generate_deposit(Resource.FUEL, self.params.fuel_deposits)
        # now we can remove the 'CLEAR' marks
        for pos in diamond(base_pos, self.params.start.clear, self.w, self.h):
            self.game_map[pos] = None  # nothing should have overwritten any of these locations so nothing can be lost

    def generate_deposit(self, resource: Resource, params: DepositParams, retry_count=0):
        # this will ONLY put deposits in locations that currently have nothing (None)
        # we will pretend we cannot go beyond half the map, and then simply reflect the map around the middle
        # this ensures the two sides are mirrored for equality between the agents
        w = (self.w + 1) // 2
        h = self.h
        dx = self.rand.randrange(params.left_offset, w - params.right_offset)  # deposit start x position
        dy = self.rand.randrange(0, h)  # deposit start y position
        dp = vec2(dx, dy)
        if self.game_map[dp] is not None:  # if the spot is already occupied, simply retry
            if retry_count < 10:
                self.generate_deposit(resource, params, retry_count=retry_count + 1)
            return  # give up - should be VERY unlikely
        # not occupied, so make a deposit there
        amt = self.rand.randrange(params.min_start_amt, params.max_start_amt + 1)
        self.game_map[dp] = ResourceDeposit(amt, resource)
        self.deposits[dp] = self.game_map[dp]
        mdp = vec2(self.w - dp.x - 1, dp.y)
        self.game_map[mdp] = ResourceDeposit(amt, resource)  # mirror it
        self.deposits[mdp] = self.game_map[mdp]
        # size of deposit
        ds: int = self.rand.randrange(params.min_size, params.max_size + 1)
        # keep track of which tiles the deposit can grow from, and the size of the deposit
        # noinspection SpellCheckingInspection
        cdep: list[vec2] = [dp]
        n: int = 0
        # now we grow the deposit
        while n < ds and len(cdep) > 0:
            dp = self.rand.choice(cdep)  # pick position to grow from
            pnp = [ndp for ndp in diamond(dp, 1, w, h) if self.game_map[ndp] is None]  # possible new positions
            if len(pnp) == 0:
                cdep.remove(dp)  # can't grow in any direction from here
                continue
            ndp = self.rand.choice(pnp)  # pick new position, make deposit there
            amt = self.rand.randrange(params.min_start_amt, params.max_start_amt + 1)
            self.game_map[ndp] = ResourceDeposit(amt, resource)
            self.deposits[ndp] = self.game_map[ndp]
            mndp = vec2(self.w - ndp.x - 1, ndp.y)
            self.game_map[mndp] = ResourceDeposit(amt, resource)
            self.deposits[mndp] = self.game_map[mndp]
            cdep.append(ndp)  # we can also grow from here now
            n += 1
            inc = self.rand.randrange(params.min_inc_amt, params.max_inc_amt + 1)
            self.game_map[dp].amount += inc  # grow the point from which we spawned
            self.game_map[(self.w - dp.x - 1, dp.y)].amount += inc
            if self.game_map[dp].amount > params.max_amt:  # can't grow too big
                self.game_map[dp].amount = params.max_amt
                self.game_map[(self.w - dp.x - 1, dp.y)].amount = params.max_amt

    def __str__(self):
        s: str = ''
        for j in range(self.h):
            for i in range(self.w):
                mo = self.game_map[(i, j)]
                s += ('.' if mo is None else mo.symbol) + ' '
            s += '\n'
        return s[:-1]
