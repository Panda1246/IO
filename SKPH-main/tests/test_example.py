import pytest


def inc(x):
    return x + 1


def test_inc_zero():
    assert inc(0) == 1


def test_inc_string():
    with pytest.raises(TypeError):
        inc('a')
