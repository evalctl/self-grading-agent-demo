def median(values):
    """Return the median of a non-empty list of numbers."""
    if not values:
        raise ValueError("median() arg is an empty sequence")
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid]
