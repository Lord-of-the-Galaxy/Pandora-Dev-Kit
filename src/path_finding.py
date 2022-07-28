from __future__ import annotations

from dataclasses import dataclass
import heapq
from typing import Optional

import numpy as np
import numpy.typing as npt

from vec2 import vec2


# A* code from: https://gist.github.com/ryancollingwood/32446307e976a11a1185a5394d6657bc
# for Space-Time-A*, refer to: https://www.davidsilver.uk/wp-content/uploads/2020/03/coop-path-AIWisdom.pdf

# I hope this works, it's not been tested much (or at all)

@dataclass(eq=False)
class Node:
    parent: Optional[Node]
    pos: vec2
    g: int = 0
    h: int = 0

    def __eq__(self, other: Node):
        return self.pos == other.pos

    def __lt__(self, other: Node):
        return self.f < other.f

    def __gt__(self, other: Node):
        return self.f > other.f

    @property
    def f(self):
        return self.g + self.h


@dataclass(eq=False)
class TimeNode:
    parent: Optional[TimeNode]
    pos: vec2
    time: int
    removed: bool = False
    g: int = 0
    h: int = 0

    def __eq__(self, other: TimeNode):
        return self.pos == other.pos and self.time == other.time

    def __lt__(self, other: TimeNode):
        return self.f < other.f

    def __gt__(self, other: TimeNode):
        return self.f > other.f

    @property
    def f(self):
        return self.g + self.h


def adjacent(pos: vec2, maze: npt.NDArray[np.integer]) -> list[vec2]:
    l: list[vec2] = [pos + vec2(1, 0), pos + vec2(-1, 0), pos + vec2(0, 1), pos + vec2(0, -1)]
    l: list[vec2] = [p for p in l if 0 <= p.x < maze.shape[0] and 0 <= p.y < maze.shape[1]]
    return l


def compute_path(node: Node | TimeNode) -> list[vec2]:
    path = []
    while node is not None:
        path.append(node.pos)
        node = node.parent
    path.reverse()  # reverse the path
    return path


class AStarMap:  # builds a map of g values from start to many points on grid using A* to a target
    def __init__(self, start: vec2, target: vec2, maze: npt.NDArray[np.integer]):
        self.nodes: dict[vec2, Node] = {}
        self.open_nodes: list[Node] = []
        self.closed_nodes: set[vec2] = set()

        self.maze = maze
        self.start = Node(None, start)
        self.nodes[start] = self.start
        self.target = target
        self.max_iterations = maze.shape[0] * maze.shape[1]  # can't take long than this

        heapq.heapify(self.open_nodes)
        heapq.heappush(self.open_nodes, self.start)

        self.find(target)

    @staticmethod
    def h(start: vec2, end: vec2) -> int:
        return abs(start - end)

    def find(self, pos: vec2) -> Optional[Node]:
        if pos in self.closed_nodes:
            # we already found the shortest path to this node
            return self.nodes[pos]  # .g is the total cost to get to the node
        # so we don't have the distance to the node yet, and must use A* to find it
        idx = 0
        while len(self.open_nodes) > 0:  # still something left ot search
            idx += 1
            if idx == self.max_iterations:
                break  # no path can exist
            c_node = heapq.heappop(self.open_nodes)
            if c_node.pos in self.closed_nodes:
                continue  # already done with it
            self.closed_nodes.add(c_node.pos)
            children = [Node(c_node, p) for p in adjacent(c_node.pos, self.maze)
                        if self.maze[p] > 0 and p not in self.closed_nodes]
            for child in children:
                child.g = c_node.g + 1
                child.h = self.h(child.pos, self.target)  # this is not great at finding <pos>, but necessary
                if child.pos not in self.nodes or child.g < self.nodes[child.pos].g:
                    # we only do the check above as we can do it quickly (O(log n))
                    self.nodes[child.pos] = child
                    heapq.heappush(self.open_nodes, child)

            if c_node.pos == pos:
                return c_node  # .g is the total cost to get to the node
        return None  # couldn't find

    def get_h(self, pos: vec2):
        n = self.find(pos)
        if n is None:
            return 0  # better to underestimate than overestimate
        return n.g


def astar(start_pos: vec2, target_pos: vec2, maze: npt.NDArray[np.integer]) -> list[vec2]:
    a_map = AStarMap(start_pos, target_pos, maze)
    return compute_path(a_map.find(target_pos))


def space_time_astar(agent_id: int, start: vec2, target: vec2, time: int, maze: npt.NDArray[np.integer],
                     reserved: dict[int, dict[vec2, list[int]]], depth: int, pause: int = 0) -> list[vec2]:
    a_map = AStarMap(target, start, maze)

    open_nodes: list[TimeNode] = []
    closed_nodes: set[tuple[vec2, int]] = set()
    heapq.heapify(open_nodes)
    start_node = TimeNode(None, start, time)
    heapq.heappush(open_nodes, start_node)

    idx = 0
    max_iterations = depth*4  # this should be OK almost all the time

    path: list[vec2] = [start]  # in case no path is found, we just stay put

    while len(open_nodes) > 0:
        idx += 1
        c_node = heapq.heappop(open_nodes)
        if (c_node.pos, c_node.time) in closed_nodes:
            continue  # already covered this node
        closed_nodes.add((c_node.pos, c_node.time))
        if idx > max_iterations or c_node.pos == target:  # found goal or ran out of time
            path = compute_path(c_node)
            break

        children = [TimeNode(c_node, pos, c_node.time+1) for pos in adjacent(c_node.pos, maze) if maze[pos] > 0]
        children.append(TimeNode(c_node, c_node.pos, c_node.time+1))  # staying put is also a valid move
        children = [c for c in children if (c.pos, c.time) not in closed_nodes]  # remove closed nodes
        children = [c for c in children if c.time not in reserved or c.pos not in reserved[c.time]
                    or len(reserved[c.time][c.pos]) < maze[c.pos]]  # make sure the spot isn't fully reserved yet

        for child in children:
            child.g = c_node.g + 1
            child.h = a_map.get_h(child.pos)  # this gets true distance if no other agents were to exist
            heapq.heappush(open_nodes, child)  # even if this (pos, time) is already in the list, it'll be ignored later

    # we have found a path, so make reservations
    for i in range(min(len(path)+pause, depth)):
        # we reserve at most depth-many steps
        # the agent may wish to pause at its goal for some time, so provision for that as well
        idx = min(i, len(path)-1)
        t = time + i
        p = path[idx]
        if t not in reserved:
            reserved[t] = {}
        if p not in reserved[t]:
            reserved[t][p] = [agent_id]
        else:
            reserved[t][p].append(agent_id)

    return path


# this clears the reservation table at time <time>
def cleanup_reservations(reserved: dict[int, dict[vec2, list[int]]], time: int):
    if time in reserved:
        reserved.pop(time)


# clears all reservations for agent agent_id
def clear_reservations(reserved: dict[int, dict[vec2, list[int]]], agent_id: int):
    for t in reserved:
        for p in reserved[t]:
            if agent_id in reserved[t][p]:
                reserved[t][p].remove(agent_id)
        keys = list(reserved[t].keys())
        for p in keys:
            if len(reserved[t][p]) == 0:
                reserved[t].pop(p)
