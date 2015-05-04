from astar import *

def test_a_star():
    id_digraph = {
        'A': ['B', 'G'],
        'B': ['A', 'C', 'G', 'D'],
        'C': ['B', 'D'],
        'D': ['C', 'B', 'F', 'E'],
        'E': ['D', 'F'],
        'F': ['E', 'D', 'G'],
        'G': ['A', 'B', 'F']
    }

    id_to_data = {
        'A': nodedata(0, 0, 0),
        'B': nodedata(0, 1, 0),
        'C': nodedata(0, 2, 0),
        'D': nodedata(2, 2, 0),
        'E': nodedata(3, 2, 0),
        'F': nodedata(2, -1, 0),
        'G': nodedata(1, 0, 0),
    }

    (optimal_path, cost) = astar(toblers, toblers_heuristic, id_digraph, id_to_data, 'A', 'E')
    assert optimal_path == ['A', 'B', 'D', 'E']
