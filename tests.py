from lab1 import *

def test_elevation_idx():
    assert elevation_idx(43, 18) == 0
    assert elevation_idx(42.5, 18.5) == 1800*3601 + 1800


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

    (optimal_path, cost) = a_star(id_digraph, id_to_data, 'A', 'E')
    assert optimal_path == ['A', 'B', 'D', 'E']
