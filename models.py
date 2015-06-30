import csv
import numpy as np
import random
import math
import astar


def construct_full_path(path, id_digraph, id_to_data):
    fullpath = []
    for l, r in zip(path, path[1:]):
        result = astar.astar(astar.toblers, astar.toblers_heuristic, id_digraph, id_to_data, l, r)
        if result is None:
            return None
        else:
            fullpath.extend(result[0])
    return fullpath


def read_walk_data(csv_fname, id_digraph, id_to_data):
    '''
    Read the walk data into a form we care about.
    Return [(full path, total minutes, name, group), ...]
    '''
    result = []
    with open(csv_fname, newline ='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        for idx, row in enumerate(reader):
            *path, minutes, seconds, name, group = row
            path = [int(p) for p in path]
            minutes = int(minutes)
            seconds = int(seconds)
            total_minutes = minutes + seconds/60.0
            fullpath = construct_full_path(path, id_digraph, id_to_data)
            if fullpath == None:
                print("***WARNING! The path in walk data row {} is impossible!***".format(idx))
                continue
            else:
                result.append((fullpath, total_minutes, name, group))
    return result


def partition_walks(examples, seed=None):
    '''
    Break 70% of the examples into a training set and 30% into a
    test set. Returns a tuple (training, test).

    This is done randomly but reproducibly using the seed which is any
    hashable object.
    '''
    r = random.Random()
    if not seed is None:
        r.seed(seed)
    exclone = examples[:]
    random.shuffle(exclone, random=r.random)
    boundary = round(.7 * len(exclone))
    training = exclone[:boundary]
    test = exclone[boundary:]
    return (training, test)


def linear_model(examples):
    '''
    Take examples: [([x1, ..., xn], target), ...] and return the
    model function [x1, ..., xn] -> result.

    Linear regression is accomplished through some closed form matrix math
    rather than gradient descent.
    '''
    X = np.matrix([xvec for (xvec, _) in examples])
    y = np.matrix([[e] for (_, e) in examples])
    ws = (X.T * X).I * X.T * y
    print(ws)
    return lambda xs: float(sum([w*x for w, x in zip(ws, xs)]))


def nearest_neighbor_model(examples):
    '''
    Take examples: [([dist, elev], target), ...] and return the
    model function [dist, elev] -> result.
    '''
    scalefactor = 5

    def model(xs):
        [dist, elev] = xs
        minimum = (float('inf'), None)
        for [dist2, elev2], y in examples:
            delta_dist = dist2 - dist
            delta_elev = elev2 - elev
            euclidean = math.sqrt(delta_dist**2 + (scalefactor*delta_elev)**2)
            minimum = min(minimum, (euclidean, y))
        return minimum[1]
    return model


def L2_loss(model, test_examples):
    return sum([(y - model(xs))**2 for (xs, y) in test_examples])


def stdev(model, test_examples):
    return math.sqrt(L2_loss(model, test_examples) / len(test_examples))


def path_dist(path, id_to_data):
    pathdata = [id_to_data[nid] for nid in path]
    xydistsum = sum([astar.euclidean(l, r) for l, r in zip(pathdata, pathdata[1:])])
    return xydistsum


def build_dist_examples(walks, id_to_data):
    '''Build example set with one feature: xy distance.'''
    return [([path_dist(path, id_to_data)], time) for path, time, _, _ in walks]


def build_dist_elev_examples(walks, id_to_data):
    '''Build example set with two features: xy distance and elevation'''
    result = []
    for path, time, _, _ in walks:
        dist = path_dist(path, id_to_data)
        delta_elev = id_to_data[path[-1]].z_m - id_to_data[path[0]].z_m
        result.append(([dist, delta_elev], time))
    return result


def build_dist_2elev_examples(walks, id_to_data):
    '''
    Build example set with three features: xy distance and total upward
    elevation change and total downward elevation change
    '''
    result = []
    for path, time, _, _ in walks:
        dist = path_dist(path, id_to_data)
        downhill = 0
        uphill = 0
        for l, r in zip(path, path[1:]):
            change = id_to_data[r].z_m - id_to_data[l].z_m
            if change > 0:
                uphill += change
            else:
                downhill -= change
        result.append(([dist, uphill, downhill], time))
    return result


def pw(wsz):
    ws = [w for w in wsz if w[-2] == 'tfm']
    wstest = [w for w in wsz if w[-2] != 'tfm']
    print(wstest)
    return ws, wstest

def compare_models(walks, id_to_data, sharedseed):
    trainingA, testA = partition_walks(build_dist_examples(walks, id_to_data), seed=sharedseed)
    trainingB, testB = partition_walks(build_dist_elev_examples(walks, id_to_data), seed=sharedseed)
    trainingC, testC = partition_walks(build_dist_2elev_examples(walks, id_to_data), seed=sharedseed)

    ma = linear_model(trainingA)
    mb = linear_model(trainingB)
    mc = linear_model(trainingC)
    md = nearest_neighbor_model(trainingB)

    print("Examples divided into training and test set using random seed: {}.".format(sharedseed))
    print("Standard deviation comparison of models' error on test set in minutes:")
    print("  {}\tLinear model. Features: [distance].".format(stdev(ma, testA)))
    print("  {}\tLinear model. Features: [distance, elevation].".format(stdev(mb, testB)))
    print("  {}\tLinear model. Features: [distance, uphill, downhill].".format(stdev(mc, testC)))
    print("  {}\tNearest neighbor.".format(stdev(md, testB)))
