#!/usr/bin/env python3
import json
import pathlib
import sys
import urllib.request
from datetime import datetime, timezone

SOURCE_URL = "https://nextendo.network/api/online-counts"
DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "population.json"


def fetch_counts() -> dict[str, int]:
    with urllib.request.urlopen(SOURCE_URL, timeout=15) as resp:
        body = json.load(resp)
    counts = body.get("counts", {})
    return {k: int(v) for k, v in counts.items() if isinstance(v, (int, float))}


def load_data() -> dict:
    if DATA_PATH.exists():
        return json.loads(DATA_PATH.read_text())
    return {"updated_utc": None, "games": {}}


def empty_hours() -> list[dict]:
    return [{"avg": 0.0, "samples": 0} for _ in range(24)]


def main() -> int:
    try:
        counts = fetch_counts()
    except Exception as exc:  # network hiccups shouldn't fail the workflow loudly
        print(f"fetch failed: {exc}", file=sys.stderr)
        return 0

    now = datetime.now(timezone.utc)
    hour = now.hour

    data = load_data()
    games = data.setdefault("games", {})

    for title_id, count in counts.items():
        game = games.setdefault(title_id, {"hours": empty_hours()})
        bucket = game["hours"][hour]
        # Running average: new_avg = old_avg + (sample - old_avg) / new_count
        bucket["samples"] += 1
        bucket["avg"] += (count - bucket["avg"]) / bucket["samples"]

    data["updated_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    DATA_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"updated {len(counts)} title(s) for hour {hour} UTC")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
