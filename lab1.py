import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple
import math
import array
import sys
import argparse
import graphical
import astar

from astar import nodedata


m_per_lat = 111000
m_per_lon = 82000
only_highways = True


def build_node_digraph(xml_root):
    """Build a digraph of node ids"""

    digraph = defaultdict(list)

    for child in xml_root.iterfind('way'):
        if not only_highways or any((sub.get('k') == 'highway' for sub in child.iterfind('tag'))):
            nds = list(child.iterfind('nd'))
            for (n1, n2) in zip(nds, nds[1:]):
                ref1 = int(n1.get('ref'))
                ref2 = int(n2.get('ref'))
                digraph[ref1].append(ref2)
                digraph[ref2].append(ref1)

    return digraph


def build_ways(xml_root):
    """
    Build a map of way names to node ids contained within. Note that not all
    ways have names so only those that do are included.
    """

    ways = {}

    for child in xml_root.iterfind('way'):
        nds = [int(n.get('ref')) for n in child.iterfind('nd')]
        tags = child.iterfind('tag')

        if only_highways and not any((sub.get('k') == 'highway' for sub in tags)):
            continue

        wayname = None
        for sub in tags:
            if sub.get('k') == 'name':
                wayname = sub.get('v').lower()

        if not wayname is None:
            ways[wayname] = nds

    return ways


def build_node_data(xml_root, elevation_data):
    """Build a map from node ids to NodeDatas (named tuples) with x y and z in meters"""

    node_data = {}

    for child in xml_root.iterfind('node'):
        node_id = int(child.get('id'))

        lat = float(child.get('lat'))
        lon = float(child.get('lon'))

        y_m = lat * m_per_lat
        x_m = lon * m_per_lon
        z_m = lerped_elevation(elevation_data, lat, lon)

        node_data[node_id] = nodedata(x_m, y_m, z_m)

    return node_data


def read_elevations(elevations_path):
    """Build an array of 3601x3601 shorts where each element is an elevation in meters"""
    with open(elevations_path, 'rb') as f:
        data = array.array('h')
        data.fromfile(f, 3601*3601)

    data.byteswap() # big endian -> little endian
    return data


def lerped_elevation(elevs, lat, lon):
    '''
    Get the linearly interpolated elevation between the closest four.
    It does this by first interpolating the top two and bottom two separately,
    then interpolating between the resulting top and bottom.

    See
    http://transition.fcc.gov/ftp/Bureaus/Mass_Media/Databases/documents_collection/84-341.pdf
    '''

    lat_secs = max(0.001, min(3599.99, 43*60*60 - lat*60*60))
    lon_secs = max(0.001, min(3599.99, lon*60*60 - 18*60*60))

    lat1 = math.floor(lat_secs)
    lat2 = math.ceil(lat_secs)
    lon1 = math.floor(lon_secs)
    lon2 = math.ceil(lon_secs)

    points = [(lat1, lon1), (lat1, lon2), (lat2, lon1), (lat2, lon2)]

    elevations = [elevs[plat*3601 + plon] for (plat, plon) in points]

    def lerp(l, e1, e2):
        return (l % 1)*e2 + (1 - (l % 1))*e1

    lerped1 = lerp(lon_secs, elevations[0], elevations[1])
    lerped2 = lerp(lon_secs, elevations[2], elevations[3])
    lerpboth = lerp(lat_secs, lerped1, lerped2)

    return lerpboth


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
    """Return a tuple of (graph, ways, data)"""
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


def run(source, destination, show):
    (graph, ways, data) = read_xml('dbv.osm', 'N42E018.HGT')
    source = sys.argv[1].lower()
    dest = sys.argv[2].lower()

    try:
        source = int(source)
        assert source in graph
    except:
        if source in ways:
            source = ways[source][0]
        else:
            print('Source must be a valid node ID or a street name')
            return
    
    try:
        dest = int(dest)
        assert dest in graph
    except:
        if dest in ways:
            dest = ways[dest][0]
        else:
            print('Destination must be a valid node ID or a street name')
            return
    

    result = astar.astar(astar.toblers, astar.toblers_heuristic, graph, data, source, dest)
    if result is None:
        print('No path to destination found')

    pathstr = ', '.join((str(nd) for nd in result[0]))
    print('\npath: {}\n'.format(pathstr))
    print('time: {:.2f} minutes\n'.format(result[1]))

    if show:
        graphical.display(graph, data, result[0], result[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find the fastest walking paths through Dubrovnik.')
    parser.add_argument('source', type=str, nargs=1, help='The source node ID or street name')
    parser.add_argument('destination', type=str, nargs=1, help='The destination node ID or street name')
    parser.add_argument('--show', action='store_true', help='Show the best path on a graphical map')
    args = parser.parse_args()
    run(args.source, args.destination, args.show) 
