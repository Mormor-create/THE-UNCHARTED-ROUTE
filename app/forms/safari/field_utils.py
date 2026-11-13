"""Shared field coercion helpers for Safari forms."""

def coerce_optional_int(value):
    """Safely convert an optional select value to an integer."""
    if value is None or value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None