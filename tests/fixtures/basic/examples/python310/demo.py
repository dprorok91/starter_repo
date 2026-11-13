"""Small application used to exercise the starter's runtime upgrade workflow."""


def greet(name: str) -> str:
    """Return a greeting, rejecting an empty name."""
    if not name.strip():
        raise ValueError('A name is required')
    return f'Hello, {name.strip()}!'
