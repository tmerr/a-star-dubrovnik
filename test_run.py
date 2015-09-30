from run import *

def test_elevation_idx():
    assert elevation_idx(43, 18) == 0
    assert elevation_idx(42.5, 18.5) == 1800*3601 + 1800
