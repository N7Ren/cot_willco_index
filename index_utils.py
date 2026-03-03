DEFAULT_LOW = 10
DEFAULT_HIGH = 90

def clamp(value, lower, upper):
    return max(lower, min(value, upper))

def normalize_thresholds(low, high):
    low = clamp(low, 0, 100)
    high = clamp(high, 0, 100)
    if low >= high:
        return DEFAULT_LOW, DEFAULT_HIGH
    return low, high
