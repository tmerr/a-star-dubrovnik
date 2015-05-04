from collections import defaultdict, namedtuple
from heapq import heappush, heappop
import math


nodedata = namedtuple('NodeData', 'x_m y_m z_m')


def build_path(id_digraph, start, goal, history):
    lst = [goal]
    while lst[-1] != start:
        lst.append(history[lst[-1]])
    return lst[::-1]


def toblers(a, b):
    '''Use Tobler's Hiking Function to estimate the amount of time it takes to travel from a to b'''
    xy_dist = math.sqrt((b.x_m - a.x_m)**2 + (b.y_m - a.y_m)**2)
    if xy_dist == 0:
        return 0
    slope = (b.z_m - a.z_m)/xy_dist
    km_per_h = 6*math.exp(-3.5 * abs(slope + 0.05))
    km_per_min = km_per_h / 60
    m_per_min = km_per_min * 1000
    minutes = xy_dist / m_per_min
    return minutes


def toblers_heuristic(a, b):
    '''
    toblers never exceeds 6 km/h
    so an admissible heuristic is 6 km/h in a straight line
    '''
    xy_m = math.sqrt((b.x_m - a.x_m)**2 + (b.y_m - a.y_m)**2)
    m_per_min = 6000/60
    minutes = xy_m/m_per_min
    return minutes


def astar(costfunc, heuristic, id_digraph, id_to_data, start, goal):
    """Return the tuple (path, path_cost), or None if no path is found."""
    history = {}
    frontier = [(0, start)] # a priority queue [(cost, node), ...] 
    path_costs = defaultdict(int) # updated throughout search

    while len(frontier) != 0:
        (cost, cur_node) = heappop(frontier)
        if cur_node == goal:
            path =  build_path(id_digraph, start, goal, history)
            return (path, path_costs[goal])

        for successor in id_digraph[cur_node]:
            new_path_cost = path_costs[cur_node] + costfunc(id_to_data[cur_node], id_to_data[successor])
            if successor not in history or new_path_cost < path_costs[successor]:
                history[successor] = cur_node
                path_costs[successor] = new_path_cost
                total_cost = path_costs[successor] + heuristic(id_to_data[successor], id_to_data[goal])
                
                heappush(frontier, (total_cost, successor))
                
    return None
