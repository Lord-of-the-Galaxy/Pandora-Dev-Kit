import traceback
from time import perf_counter_ns
from typing import Iterator, Optional

import numpy as np
import numpy.typing as npt
from colorama import Fore, Style

from action import Action
from agent import Agent
from entities import Inventory, Ship, ResourceDeposit, Building, Miner, Fighter, Base
from enums import Direction, Resource
from params import GameParams, TimeLimits
from vec2 import vec2
from path_finding import cleanup_reservations, clear_reservations, space_time_astar

DEPTH = 20  # this is how far the path finding planning happens (each ship re-computes paths every half this many steps)


class Player(Agent):
    # NOTE: the dev-kit lacks most of the validation code, and assumes your agent will behave well
    #  not doing so can break it, but such an agent will simply fail and forfeit the game when submitted and run by us

    # the player argument is compulsory, everything else should be a keyword-only argument (as order is not guaranteed)
    # various keyword-only arguments are passed to the constructor, you can use whichever you need
    # the list (with brief descriptions) follows:
    #    ~ game_params - check the class definition (in params.py) for details
    #    ~ time_limits - check the class definition (in params.py) for details
    #    ~ map_w - width of the map
    #    ~ map_h - height of the map
    #    ~ game_map - a numpy array of shape (map_w, map_h) giving initial state of the map (explained later)
    # simply let **kwargs collect all remaining arguments that you do not want to use
    def __init__(self, player: int, *, game_params: GameParams, time_limits: TimeLimits,
                 map_w: int, map_h: int, game_map: npt.NDArray[object], **kwargs):
        super().__init__(player, **kwargs)
        self.params = game_params
        self.time = time_limits
        self.w = map_w
        self.h = map_h
        # keep in mind that the game_map object may change every move, so keeping a reference to it is pointless

        self.all_goals: set[vec2] = set()  # a set of all goals currently being targeted
        self.goals: dict[int, tuple[vec2, int]] = {}  # maps ship ids to (goal, pause)
        self.reached_goal: dict[int, int] = {}  # maps ship ids to the time they reached their goals
        self.next_reset: dict[int, int] = {}  # maps ship id to the time when their path needs to be re-computed
        self.reserved: dict[int, dict[vec2, list[int]]] = {}  # this is a reservation table for path finding purposes
        self.paths: dict[int, dict[int, vec2]] = {}  # maps ship ids to paths, where a path maps time to position

        self.time_logs: dict[int, int] = {}  # maps move number to time taken to complete

    def move(self, time: int, game_map: npt.NDArray[object], p1_inv: Inventory, p2_inv: Inventory) -> list[Action]:
        try:
            return self._move(time, game_map, p1_inv, p2_inv)
        except Exception as e:
            print(Fore.RED + "Error" + Style.RESET_ALL)
            print(traceback.format_exc())
            return []

    # time - the move number (self-explanatory)
    # game_map - this is a numpy array of shape (map_w, map_h).
    #           Every entry in it is either None, an Entity, or a ResourceDeposit
    #               ~ None means the cell/tile is empty
    #               ~ A ResourceDeposit has an amount (int) and resource (Resource.ORE or Resource.FUEL)
    #               ~ An Entity may be one of the following:
    #                   ~ Base - can be commanded to build new ships (Miners or Fighters)
    #                   ~ Turret - does not accept any commands
    #                   ~ Miner - can be commanded to move, mine, transfer cargo, or build new buildings
    #                   ~ Fighter - can only be commanded to move
    #                   ~ UnderConstruction - does not accept any commands
    # p1_inv - the Inventory for player 1, it consists of:
    #           ~ ore: int - amount of ore owned by the player
    #           ~ fuel: int - amount of ore owned by the player
    #           ~ bases: list[Base] - list of Bases owned by the player
    #           ~ turrets: list[Turret] - list of turrets owned by the player
    #           ~ miners: list[Miner] - list of miners owned by the player
    #           ~ fighters: list[Fighter] - list of fighters owned by the player
    # p2_inv - the Inventory for player 2
    #
    # your function must return a list of Actions
    # to create an action, use Action(entity) where entity is the Entity that must take the action
    # then call any of these functions to add a component to the action:
    #   ~ move(direction: Direction) - move in specified direction (only for Miners and Fighters)
    #   ~ mine(direction: Direction = Direction.NONE) - mine in the specified direction (only for Miners)
    #                                                   if unspecified, a direction is picked for you
    #   ~ cargo(new_cargo: list[Resources]) - transfer cargo (if possible) between a miner and a base (only for Miners)
    #                                         new_cargo is the cargo left in the Miner after the transfer
    #                                         the command will only work if the Miner is on a Base
    #                                         the player will also need to own enough ore and/or fuel for the transfer
    #   ~ build(build_type: type[Entity]) - build a new Entity of type build_type (only for Miners and Bases)
    #                                       Bases can only build Miners and Fighters, and build instantly
    #                                       Miners can only build Bases and Turrets, and need to transfer cargo to
    #                                       the location in order to build (thus taking many turns)
    def _move(self, time: int, game_map: npt.NDArray[object], p1_inv: Inventory, p2_inv: Inventory) -> list[Action]:
        start_time = perf_counter_ns() // 1000  # microsecond accuracy more than enough for us and keeps numbers smaller
        moves: dict[int, Action] = {}  # maps ids to moves
        p_inv = p1_inv if self.player == 1 else p2_inv

        ships = p_inv.ships  # get a list of all ships
        for s in ships:  # create an action for every ship
            moves[s.id] = Action(s)

        for s in ships:  # for every ship, check if it has reached its goal
            if s.id in self.goals and s.pos == self.goals[s.id][0]:
                self.handle_goal(s, game_map, moves[s.id], time)  # handle the goal
            if s.id not in self.goals:  # allot a goal to every ship that doesn't have one
                self.allot_goal(s, p_inv, game_map, time)

        # compute paths (if needed) and moves for all ships
        self.compute_paths_and_moves(ships, time, moves, game_map)

        other_actions: list[Action] = []
        # see if we can and should build a ship
        if p_inv.ore >= self.params.miners.ore_cost and p_inv.fuel >= self.params.miners.fuel_cost:
            num_miners = len(p_inv.miners)
            if num_miners < 20:  # 20 miners should be enough for us
                a = Action(p_inv.bases[0]).build(Miner)
                other_actions.append(a)

        time_used = perf_counter_ns() // 1000 - start_time
        self.time_logs[time] = time_used // 1000  # ms accuracy

        return list(moves.values()) + other_actions

    def compute_paths_and_moves(self, ships: list[Ship], time: int, moves: dict[int, Action],
                                game_map: npt.NDArray[object]):
        p_map = self.process_map(game_map, self.player)  # do we actually _need_ to process the map every time? no
        # but it only takes a few ms to do so, so we don't really care
        # now we compute paths for every ship that needs it
        for s in ships:
            s_id = s.id
            if s_id not in self.next_reset:
                continue  # no entry for it, so just ignore it
            if self.next_reset[s_id] > time:
                continue  # we don't need to compute a path for it yet
            # we need to find the path for this ship
            if s_id not in self.goals:
                continue  # no goal for this ship (this probably should never happen, but IDK)
            target, pause = self.goals[s_id]
            # print(f"Finding path to {target} for {s_id} ({self.player})")
            # clear its old reservations
            clear_reservations(self.reserved, s_id)
            path = space_time_astar(s_id, s.pos, target, time, p_map, self.reserved, DEPTH, pause)
            if len(path) == 0:
                continue  # we found no path, so nothing really to do here
            # the path needs to be recomputed after some time, for two reasons
            #    - we may have reached the goal and stayed there for the allotted time already
            #    - the game map is dynamic, so using the same path for too long could be bad
            self.next_reset[s_id] = time + min(len(path) + pause, DEPTH // 2) - 1
            # set the path for this ship
            self.paths[s_id] = {}
            t = time
            for p in path:
                self.paths[s_id][t] = p
                t += 1

        # compute and set move
        for s in ships:
            if s.id in self.paths and time + 1 in self.paths[s.id]:
                dp = self.paths[s.id][time + 1] - self.paths[s.id][time]
                moves[s.id].move(Direction.from_vec(dp))

        # some cleanup for any destroyed ships
        ship_ids: set[int] = {s.id for s in ships}  # set for performance
        # cleanup goals
        goals_clean = [s_id for s_id in self.goals.keys() if s_id not in ship_ids]
        for s_id in goals_clean:
            goal: vec2 = self.goals[s_id][0]
            if goal in self.all_goals:
                self.all_goals.remove(goal)
            if s_id in self.reached_goal:
                self.reached_goal.pop(s_id)
            self.goals.pop(s_id)
        # no longer have to worry about resetting paths for a dead ship
        keys = list(self.next_reset.keys())
        for s_id in keys:
            if s_id not in ship_ids:
                self.next_reset.pop(s_id)
        # dead ships have no paths
        keys = list(self.paths.keys())
        for s_id in keys:
            if s_id not in ship_ids:
                self.paths.pop(s_id)
        # finally cleanup old reservations
        cleanup_reservations(self.reserved, time)

    def allot_goal(self, s: Ship, p_inv: Inventory, game_map: npt.NDArray[object], time: int):
        g = None
        p = 0
        if isinstance(s, Miner):
            if len(s.cargo) < s.cargo_space:  # can still mine
                g = self.find_mining_goal(game_map, s.pos)
                p = s.cargo_space - len(s.cargo) - 1  # number of cargo spots left - 1
                # at the last turn we don't pause as we can mine and then just move
            else:  # cargo full, deposit it
                g = p_inv.bases[0].pos  # we must have at least one base - we lose if we don't
                p = 0
        elif isinstance(s, Fighter):
            pass  # TODO: get the fighters to do something?
        if g is None:
            return
        self.goals[s.id] = (g, p)
        self.next_reset[s.id] = time
        self.all_goals.add(g)

    def handle_goal(self, s: Ship, game_map: npt.NDArray[object], action: Action, time: int):
        r_time = time
        if s.id in self.reached_goal:
            r_time = self.reached_goal[s.id]
        else:
            self.reached_goal[s.id] = r_time
        g, p = self.goals[s.id]
        if time - r_time >= p:  # we have been at this goal long enough, so we are done
            self.goals.pop(s.id)
            self.reached_goal.pop(s.id)
            if g in self.all_goals:
                self.all_goals.remove(g)
        if isinstance(s, Miner):  # we only need to do anything for miners right now
            if isinstance(game_map[s.pos], Base):  # this is a base, so the goal was to drop-off cargo
                action.cargo([])
            else:  # right now the only other possibility is that the goal was to mine
                action.mine()

    def find_mining_goal(self, game_map: npt.NDArray[object], pos: vec2) -> Optional[vec2]:
        # find the nearest mining spot to pos
        for d in range(1, self.w + self.h):
            for p in at_distance(pos, d, self.w, self.h):
                if p in self.all_goals:
                    continue  # already a goal
                if game_map[p] is not None:
                    continue  # something is already there
                res = [adj for adj in at_distance(p, 1, self.w, self.h) if isinstance(game_map[adj], ResourceDeposit)]
                if len(res) > 0:
                    # we found something
                    return p
        return None  # hopefully never happens

    # this returns an array where each entry is the number of ships the corresponding position on the game_map can hold
    @staticmethod
    def process_map(game_map: npt.NDArray[object], player: int) -> npt.NDArray[np.integer]:
        p_map = np.ones(game_map.shape, dtype=np.intc)  # everything starts at 1
        for i in range(p_map.shape[0]):
            for j in range(p_map.shape[1]):
                p = vec2(i, j)
                mo = game_map[p]
                if isinstance(mo, ResourceDeposit):
                    # no ships can go on a resource deposit
                    p_map[p] = 0
                elif isinstance(mo, Building):
                    if mo.player == player:
                        p_map[p] = mo.vehicle_capacity
                    else:
                        p_map[p] = 0
        return p_map

    def close(self):
        # this function will be called after the end of the game, use it to close any resources your agent uses
        # don't actually do what this agent does, anything your agent prints is simply discarded
        # but this may be useful for debug purposes
        if True:
            times = list(self.time_logs.values())
            moves = len(self.time_logs.keys())
            max_time = max(times)
            total_time = sum(times)
            mean_time = total_time // moves
            print(f"Moves: {moves}, Total Time: {total_time}, Time Per Move: {mean_time}, Max Move Time: {max_time}")


def at_distance(pos: vec2, size: int, width: int, height: int) -> Iterator[vec2]:
    for i in range(max(-size, -pos.x), min(size + 1, width - pos.x)):
        j1 = -size + abs(i)
        j2 = size - abs(i)
        if 0 <= (j1 + pos.y) < height:
            yield pos + vec2(i, j1)
        if j1 != j2 and 0 <= (j2 + pos.y) < height:
            yield pos + vec2(i, j2)
