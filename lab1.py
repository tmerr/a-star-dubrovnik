import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple
from heapq import heappush, heappop
from math import sin, cos, atan2, sqrt
import math
import array
import struct


m_per_lat = 111000
m_per_lon = 82


nodedata = namedtuple('NodeData', 'x_m y_m z_m')


def extract_info(xml_path, elevations_path):
    """
    Use the OpenStreetMaps XML file at the given path to build a tuple of:
    1. A node graph represented as a node_id -> [node_id, ...] dictionary
    2. A dictionary that maps node_id -> (x in meters, y in meters, elevation in meters)

    Blows up in your face with an exception if it fails to open or read the file.
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    if root.tag != 'osm':
        raise IOError('Expected root xml tag to be named "osm", got "{}".'.format(osm_elem.tag))

    version = root.get('version')
    if version != '0.6':
        print('Warning: Expected osm api version "0.6", got "{}".'.format(version))

    id_to_data = {}
    id_digraph = defaultdict(list)

    elevation_array = read_elevations(elevations_path)

    for child in root:
        if child.tag == 'node':
            node_id = int(child.get('id'))

            lat = float(child.get('lat'))
            lon = float(child.get('lon'))

            y_m = lat * m_per_lat
            x_m = lon * m_per_lon
            z_m = elevation_array[elevation_idx(lat, lon)]

            id_to_data[node_id] = nodedata(x_m, y_m, z_m)
        elif child.tag == 'way':
            if any((sub.get('k') == 'highway' for sub in child.iterfind('tag'))):
                nds = list(child.iterfind('nd'))
                for (n1, n2) in zip(nds, nds[1:]):
                    ref1 = int(n1.get('ref'))
                    ref2 = int(n2.get('ref'))
                    id_digraph[ref1].append(ref2)
                    id_digraph[ref2].append(ref1)
        elif child.tag == 'relation':
            pass

    return (id_digraph, id_to_data)


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
    lat_idx = int(max(0, min(3600, round(lat*60*60 - 42*60*60))))
    lon_idx = int(max(0, min(3600, round(lon*60*60 - 18*60*60))))
    return lat_idx*3601 + lon_idx


def build_path(id_digraph, start, goal, history):
    lst = [goal]
    while lst[-1] != start:
        lst.append(history[lst[-1]])
    return lst[::-1]


def dist(a, b):
    return sqrt((b.x_m - a.x_m)**2 + (b.y_m - a.y_m)**2)


def a_star(id_digraph, id_to_data, start, goal):
    history = {}
    frontier = [(0, start)] # [(cost, node), ...] sorted least to greatest
    path_costs = defaultdict(int) # updated throughout search

    def heuristic(node_id):
        return dist(id_to_data[node_id], id_to_data[goal])

    while len(frontier) != 0:
        (cost, cur_node) = heappop(frontier)
        for successor in id_digraph[cur_node]:
            if successor not in history:
                history[successor] = cur_node

                current_to_successor = dist(id_to_data[cur_node], id_to_data[successor])
                path_costs[successor] = path_costs[cur_node] + current_to_successor

                total_cost = path_costs[successor] + heuristic(successor)
                
                heappush(frontier, (total_cost, successor))

    path =  build_path(id_digraph, start, goal, history)
    return (path, path_costs[goal])


def run():
    (id_digraph, id_to_data) = extract_info('dbv.osm', 'N42E018.HGT')
    print(a_star(id_digraph, id_to_data, 1825110022, 1825110033))


if __name__ == '__main__':
    run()
