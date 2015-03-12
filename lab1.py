import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple
from heapq import heappush, heappop
from math import sin, cos, atan2, sqrt
import math
import array
import struct


m_per_lat = 111000
m_per_lon = 82000


nodedata = namedtuple('NodeData', 'x_m y_m z_m')


### XML parsing

def build_node_digraph(xml_root):
    digraph = defaultdict(list)

    for child in xml_root.iterfind('way'):
        if any((sub.get('k') == 'highway' for sub in child.iterfind('tag'))):
            nds = list(child.iterfind('nd'))
            for (n1, n2) in zip(nds, nds[1:]):
                ref1 = int(n1.get('ref'))
                ref2 = int(n2.get('ref'))
                digraph[ref1].append(ref2)
                digraph[ref2].append(ref1)

    return digraph


def build_ways(xml_root):
    ways = {}

    for child in xml_root.iterfind('way'):
        nds = [int(n.get('ref')) for n in child.iterfind('nd')]
        tags = child.iterfind('tag')

        if not any((sub.get('k') == 'highway' for sub in tags)):
            continue

        wayname = None
        for sub in tags:
            if sub.get('k') == 'name':
                wayname = sub.get('v').lower()

        if not wayname is None:
            ways[wayname] = nds

    return ways


def build_node_data(xml_root, elevation_data):
    node_data = {}

    for child in xml_root.iterfind('node'):
        node_id = int(child.get('id'))

        lat = float(child.get('lat'))
        lon = float(child.get('lon'))

        y_m = lat * m_per_lat
        x_m = lon * m_per_lon
        z_m = elevation_data[elevation_idx(lat, lon)]

        node_data[node_id] = nodedata(x_m, y_m, z_m)

    return node_data


def read_elevations(elevations_path):
    """Build an array of 3601x3601 shorts where each element is an elevation in meters"""
    with open(elevations_path, 'rb') as f:
        data = array.array('h')
        data.fromfile(f, 3601*3601)

    data.byteswap() # big endian -> little endian
    return data


def elevation_idx(lat, lon):
    """
    Get the index in the elevation array for the given latitude and longitude.

    The elevation array has indices corresponding to each seconds line from
    [43*60*60, 42*60*60] lat counting backward, and [18*60*60, 19*60*60] lon
    counting forward. An elevation outside these bounds will return an index on
    the edge closest to it.
    """
    lat_idx = int(max(0, min(3600, round(43*60*60 - lat*60*60))))
    lon_idx = int(max(0, min(3600, round(lon*60*60 - 18*60*60))))
    return lat_idx*3601 + lon_idx


def read_xml(xml_path, elevations_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    if root.tag != 'osm':
        raise IOError('Expected root xml tag to be named "osm", got "{}".'.format(osm_elem.tag))

    version = root.get('version')
    if version != '0.6':
        print('Warning: Expected osm api version "0.6", got "{}".'.format(version))

    graph = build_node_digraph(root)
    ways = build_ways(root)
    data = build_node_data(root, read_elevations(elevations_path))

    return (graph, ways, data)


### A* Algorithm

def build_path(id_digraph, start, goal, history):
    lst = [goal]
    while lst[-1] != start:
        lst.append(history[lst[-1]])
    return lst[::-1]


def dist(a, b):
    return sqrt((b.x_m - a.x_m)**2 + (b.y_m - a.y_m)**2)


# TODO: figure out if this is an admissible heuristic
def est_minutes(a, b):
    '''Use Tobler's Hiking Function to estimate the amount of time it takes to travel from a to b'''
    xy_dist = sqrt((b.x_m - a.x_m)**2 + (b.y_m - a.y_m)**2)
    if xy_dist == 0:
        return 0
    slope = (b.z_m - a.z_m)/xy_dist
    km_per_h = 6*math.exp(-3.5 * abs(slope + 0.05))
    km_per_min = km_per_h / 60
    m_per_min = km_per_min * 1000
    minutes = xy_dist / m_per_min
    return minutes


def a_star(id_digraph, id_to_data, start, goal):
    history = {}
    frontier = [(0, start)] # [(cost, node), ...] sorted least to greatest
    path_costs = defaultdict(int) # updated throughout search

    def heuristic(node_id):
        return est_minutes(id_to_data[node_id], id_to_data[goal])

    while len(frontier) != 0:
        (cost, cur_node) = heappop(frontier)
        for successor in id_digraph[cur_node]:
            if successor not in history:
                history[successor] = cur_node

                current_to_successor = est_minutes(id_to_data[cur_node], id_to_data[successor])
                path_costs[successor] = path_costs[cur_node] + current_to_successor

                total_cost = path_costs[successor] + heuristic(successor)
                
                heappush(frontier, (total_cost, successor))

    if goal in history:
        path =  build_path(id_digraph, start, goal, history)
        return (path, path_costs[goal])
    else:
        return None


def run():
    (id_digraph, ways, id_to_data) = read_xml('dbv.osm', 'N42E018.HGT')
    print(a_star(id_digraph, id_to_data, ways['gornji kono'.lower()][0], ways['bokeljska'][0]))


if __name__ == '__main__':
    run()
