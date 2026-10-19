import json
import math
from datetime import datetime, timezone
from pathlib import Path


class ForecastError(ValueError):
    """An actionable input or environment error."""


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise ForecastError(f"Cannot read JSON {path}: {exc}") from exc


def date(value):
    try:
        d = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)
    except ValueError as exc:
        raise ForecastError(f"Invalid ISO date: {value}") from exc


def number(value, name, lower=0, upper=None):
    try:
        x = float(value)
    except (ValueError, TypeError) as exc:
        raise ForecastError(f"{name} must be numeric") from exc
    if not math.isfinite(x) or x < lower or (upper is not None and x > upper):
        raise ForecastError(f"{name} is outside allowed range")
    return x


def envelope(kind, **data):
    return {"schema_version": "1.0", "kind": kind, **data}
