def is_prime(n: int) -> bool:
    """Return whether n is a prime number."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 2
    return True


def is_even(n: int) -> bool:
    """Return whether n is an even number."""
    return n % 2 == 0


def percentage(part: float, whole: float) -> float:
    """Return part as a percentage of whole, e.g. percentage(42, 56) -> 75.0"""
    return part / whole * 100

def stress_category(stress: int) -> str:
    """Return "low" (1-2), "medium" (3-5) or "high" (6-7) for a stress rating."""
    if stress <= 2:
        return "low"
    elif stress <= 5:
        return "medium"
    else:
        return "high"


def greet(name: str, language: str = "en") -> str:
    """Return a greeting for name in English ("en") or German ("de")."""
    if language == "de":
        return f"Hallo {name}!"
    return f"Hello {name}!"


