 # Gudni Natan Gunnarsson, 2016
from Constants import *


class Path:
    def __init__(self, nodes, total_cost):
        self.nodes = nodes
        self.totalCost = total_cost

    def getNodes(self):
        return self.nodes

    def getTotalMoveCost(self):
        return self.totalCost


class Node:
    def __init__(self, value, move_cost, parent=0):
        self.value = value
        self.move_cost = move_cost
        self.score = 0
        self.parent = parent
        self.tuple = tuple(value)


class AStar:
    def __init__(self):
        self.open_list = list()
        self.open_set = set()
        self.closed_set = set()
        self.nodes = list()

    def handleNode(self, nodeindex):
        node = self.nodes[nodeindex]
        self.passcount += 1
        if nodeindex == -1 or not node:
            return None
        self.open_list.pop(nodeindex)
        self.nodes.pop(nodeindex)
        self.closed_set.add(node.tuple)
        self.open_set.remove(node.tuple)
        nodes = self.handler.create_adjacent_nodes(node)
        for n in nodes:
            if n[0].value == self.goal:
                return n[0]
            elif n[0].tuple in self.closed_set:
                # already closed, skip this
                continue
            else:
                index = -1
                for i in range(len(self.nodes)):
                    if self.nodes[i].value == n[0].value:
                        index = i
                        break
                if index != -1:  # Already opened
                    if n[0].move_cost < self.nodes[index].move_cost:
                        self.nodes[index].move_cost = n[1] + node.move_cost
                        self.nodes[index].parent = node
                    continue
                goal = self.goal
                start = self.start
                dx1 = n[0].value[0] - goal[0]
                dy1 = n[0].value[1] - goal[1]
                dx2 = start[0] - goal[0]
                dy2 = start[1] - goal[1]
                cross = abs(dx1*dy2 - dx2*dy1)
                heuristic = 10 * (abs(dx1) + abs(dy1)) + (14 - 2 * 10) * min(abs(dx1), abs(dy1))
                heuristic += cross*0.001
                distance = n[0].move_cost
                priority = distance + heuristic
                self.nodes.append(n[0])
                self.open_list.append(priority)
                self.open_set.add(n[0].tuple)

    def trace_path(self, node):
        nodes = []
        totalCost = node.move_cost
        p = node.parent
        nodes.insert(0, node)

        while 1:
            if not p.parent:
                break
            nodes.insert(0, p)
            p = p.parent

        return Path(nodes, totalCost)

    def getHighestPriorityNodeIndex(self, open_list):
        if not open_list:
            return None
        index_min = min(xrange(len(open_list)), key=open_list.__getitem__)
        return index_min

    def find_path(self, grid, start, goal, search_range=-1):
        if search_range != -1 and abs(sum(start) - sum(goal)) * 10 > search_range * 14:
            return None
        self.open_list = list()
        self.open_set = set()
        self.closed_set = set()
        self.nodes = list()
        self.handler = GridHandler(grid)
        self.goal = goal
        self.start = start
        self.passcount = 0
        first_node = self.handler.create_node(start, 0)
        if first_node is None:
            return None
        if goal == start:
            return Path([first_node], 0)
        self.open_list.append([first_node, 0])
        self.open_set.add(first_node.tuple)
        self.nodes.append(first_node)
        index = 0
        while index is not None:
            finish = self.handleNode(index)
            if self.passcount > 250 or (search_range != -1 and self.passcount > search_range * 10):
                break
            if finish:
                if finish is None:
                    break
                path = self.trace_path(finish)
                if search_range != -1 and len(path.nodes) > search_range:
                    break
                return self.trace_path(finish)
            index = self.getHighestPriorityNodeIndex(self.open_list)
        return None


class GridHandler:
    def __init__(self, grid):
        self.grid = grid

    def create_node(self, location, move_cost, parent=0):
        grid = list(self.grid.grid)
        val = location
        if (0 <= val[0] < self.grid.grid_size[0] and 0 <= val[1] < self.grid.grid_size[1] ) and grid[val[0]][val[1]] == 0:
            if not parent:
                return Node(val, move_cost, parent)
            if grid[parent.value[0]][val[1]] or grid[val[0]][parent.value[1]]:
                return
            return Node(val, move_cost, parent)

    def create_adjacent_nodes(self, node):
        result = []
        loc = node.value
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                move_cost = 10 if (i + j) % 2 == 1 else 14
                n = self.create_node([loc[0] + i, loc[1] + j], node.move_cost + move_cost, node)
                if n:
                    result.append([n, move_cost])
        return result
