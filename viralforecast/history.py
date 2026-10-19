"""Strict account/platform CSV boundary. Outcome windows are never features."""
import csv
from datetime import timedelta

from .analysis import rules
from .common import ForecastError, date, number

FEATURES = ("duration_seconds", "cut_rate", "title_length", "text_length", "question_count", "hashtag_count")
TARGETS = ("views_24h", "views_7d")
COUNTS = ("likes_7d", "comments_7d", "shares_7d", "saves_7d")
REQUIRED = ("content_id", "account_id", "platform", "published_at") + FEATURES + TARGETS + COUNTS


def load_history(path, account, platform):
    rules(platform)
    try:
        with open(path, encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
                raise ForecastError("Empty CSV or duplicate column names")
            missing = set(REQUIRED) - set(reader.fieldnames)
            if missing:
                raise ForecastError(f"CSV missing columns: {', '.join(sorted(missing))}")
            result, seen = [], set()
            for line, r in enumerate(reader, 2):
                if None in r or any(r[k] is None for k in REQUIRED):
                    raise ForecastError(f"Malformed CSV row {line}")
                if r["account_id"] != account or r["platform"] != platform:
                    continue
                if not r["content_id"].strip() or r["content_id"] in seen:
                    raise ForecastError(f"Empty or duplicate content_id at row {line}")
                seen.add(r["content_id"])
                r["published_at"] = date(r["published_at"])
                for k in FEATURES + TARGETS + COUNTS:
                    r[k] = number(r[k], f"row {line} {k}", .001 if k == "duration_seconds" else 0)
                if r["views_7d"] < r["views_24h"]:
                    raise ForecastError(f"views_7d must be >= views_24h at row {line}")
                for k in COUNTS:
                    if r[k] > r["views_7d"]:
                        raise ForecastError(f"{k} > views_7d at row {line}; normalize metric definitions first")
                if r.get("data_source") not in (None, "", "real", "synthetic"):
                    raise ForecastError("data_source must be real or synthetic")
                result.append(r)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise ForecastError(f"Cannot read CSV: {exc}") from exc
    if not result:
        raise ForecastError("CSV has no rows for selected account and platform")
    return sorted(result, key=lambda r: (r["published_at"], r["content_id"]))


def eligible(rows, as_of):
    # Seven-day labels must have fully matured BEFORE the prediction timestamp.
    cutoff = date(as_of) if isinstance(as_of, str) else as_of
    return [r for r in rows if r["published_at"] + timedelta(days=7) < cutoff]


def provenance(rows):
    labels = {r.get("data_source") or "unspecified" for r in rows}
    return "synthetic" if labels == {"synthetic"} else "mixed_or_unspecified" if labels != {"real"} else "user_declared_real_unverified"
