def is_short_night(hours):
    """Return True if the participant slept less than 6 hours."""
    return hours < 6


def mean(values):
    """Return the average of a list of numbers."""
    total = 0
    for v in values:
        total += v
    return total / len(values)


def is_compliant(answered, sent, threshold=0.75):
    """Return True if the share of answered prompts is at least `threshold`."""
    return answered / sent >= threshold
