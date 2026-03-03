import pytest
from index_utils import clamp, normalize_thresholds, DEFAULT_LOW, DEFAULT_HIGH

def test_clamp_within_range():
    assert clamp(50, 0, 100) == 50

def test_clamp_below_range():
    assert clamp(-10, 0, 100) == 0

def test_clamp_above_range():
    assert clamp(110, 0, 100) == 100

def test_clamp_at_boundaries():
    assert clamp(0, 0, 100) == 0
    assert clamp(100, 0, 100) == 100

def test_normalize_thresholds_valid():
    assert normalize_thresholds(20, 80) == (20, 80)

def test_normalize_thresholds_out_of_bounds():
    # clamp( -10, 0, 100) -> 0
    # clamp( 110, 0, 100) -> 100
    assert normalize_thresholds(-10, 110) == (0, 100)

def test_normalize_thresholds_low_greater_than_high():
    # Should return DEFAULT_LOW, DEFAULT_HIGH
    assert normalize_thresholds(80, 20) == (DEFAULT_LOW, DEFAULT_HIGH)

def test_normalize_thresholds_low_equal_to_high():
    # Should return DEFAULT_LOW, DEFAULT_HIGH
    assert normalize_thresholds(50, 50) == (DEFAULT_LOW, DEFAULT_HIGH)

def test_normalize_thresholds_with_clamping_causing_overlap():
    # If after clamping, low >= high
    # e.g. low = 110 (clamped to 100), high = 105 (clamped to 100)
    assert normalize_thresholds(110, 105) == (DEFAULT_LOW, DEFAULT_HIGH)
