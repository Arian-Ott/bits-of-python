import pytest
from dotproduct.vector import CVector
import random
import numpy as np
import time


@pytest.fixture
def vector_1():
    return CVector([9, 2, 7])


@pytest.fixture
def vector_2():
    return CVector([4, 8, 10])


def big_random_array():
    vector = [random.randint(0, 1000000) for _ in range(10000000)]
    vec = CVector(vector)
    return vec, np.array(vector, dtype=int)


def test_dot(vector_1, vector_2):
    result = vector_1 * vector_2
    print("result of v1 * v2", result)
    assert result == 122, "Invalid calculation"


def test_big_dot():
    vec1, np1 = big_random_array()
    vec2, np2 = big_random_array()
    print("length of big array", len(vec1.vector))
    n1 = time.time_ns()
    exp_res = np.dot(np1, np2)
    n2 = time.time_ns()
    res = vec1 * vec2
    n3 = time.time_ns()
    print("result of big dot", res)
    assert int(exp_res) == res
    print("numpy time", n2 - n1)
    print("Vec times", n3 - n2)
