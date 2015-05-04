from models import *


def test_read_examples():
    pass


def approx_eq(a, b):
    tolerance = 0.0000001
    return abs(a - b) < tolerance


def test_linear_model_with_slope1():
    examples = [([1], 1), ([3], 3), ([6], 6)]
    model = linear_model(examples)
    assert approx_eq(model([2]), 2)
    assert approx_eq(model([7]), 7)
    assert approx_eq(model([9]), 9)


def test_linear_model_with_bias():
    b = 1
    examples = [([1, b], 3), ([2, b], 5), ([4, b], 9)]
    model = linear_model(examples)
    assert approx_eq(model([3, b]), 7)


def test_partition_walks_lengths():
    examples = [x for x in range(100)]
    training, test = partition_walks(examples, 'seed')
    assert len(training) == 70
    assert len(test) == 30
    assert set(training + test) == set(examples)


def test_partition_walks_predictability():
    examples = [x for x in range(100)]
    a = partition_walks(examples, 'seed')
    b = partition_walks(examples, 'seed')
    assert a == b
