import os


def _get_str(key: str, default=None, required=False) -> str | None:
    value = os.environ.get(key, None)
    if value is None or value.strip() == "":
        if required:
            raise ValueError(f"Missing required environment variable: {key}")
        return default
    return value.strip()

def _get_int(key: str, default=None, required=False) -> int | None:
    value = _get_str(key, default, required)
    if value is None:
        return default
    try:
        value = int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer for {key}: {value}") from exc
    return value

def _get_float(key: str, default=None, required=False) -> float | None:
    value = _get_str(key, default, required)
    if value is None:
        return default
    try :
        value = float(value)
    except ValueError as exc:
        raise ValueError(f"Invalid float for {key}: {value}") from exc
    return value