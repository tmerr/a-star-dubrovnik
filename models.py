import csv
import numpy as np
import random
import astar

def read_examples(csv_fname, id_digraph, id_to_data):
    '''Return [((x1, x2), target), ... ]'''
    with open(csv_fname, newline ='') as f:
        reader = csv.reader(f, delimiter=' ', quotechar='|')
        for row in reader:
            *path, hours, minutes, name, group = row
            total_minutes = hours*60 + minutes
            pass




def partition_examples(examples, seed):
    '''
    Break 70% of the examples into a training set and 30% into a
    test set. Returns a tuple (training, test).

    This is done randomly but reproducibly using the seed which is any
    hashable object.
    '''
    r = random.Random()
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
    return lambda xs: sum([w*x for w, x in zip(ws, xs)])


def nearest_neighbor_model():
    '''
    Take examples: [([x1, ..., xn], target), ...] and return the
    model function [x1, ..., xn] -> result.
    '''
    pass
