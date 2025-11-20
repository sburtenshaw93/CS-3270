import pytest
from src.core import mean, median, mode, data_range



#-----------------------Testing the Mean---------------------------------------------
@pytest.mark.parametrize("value,expected", [
    ([2, 4, 6], 4.0),
    ([1], 1.0),
    ([-1, 1], 0.0),
])
def test_mean(value, expected):
    assert mean(value) == pytest.approx(expected)

def test_mean_empty_raises():
    with pytest.raises(ValueError):
        mean([])

#------------------Testing the Median--------------------------------------------------------
@pytest.mark.parametrize("value,expected", [
    ([1], 1),
    ([1, 3, 5], 3),
    ([1, 2, 3, 4], 2.5),
])
def test_median(value, expected):
    assert median(value) == expected

def test_median_empty_raises():
    with pytest.raises(ValueError):
        median([])

#----------------------Testing the Mode--------------------------------------------
def test_mode_tie_picks_smallest():
    assert mode([1, 1, 2, 2]) == 1

def test_mode_empty_raises():
    with pytest.raises(ValueError):
        mode([])

#--------------------------------------Testing the Data Range--------------------------------------------------
def test_data_range_basic():
    assert data_range([1, 9, 4]) == 8

def test_data_range_empty_raises():
    with pytest.raises(ValueError):
        data_range([])