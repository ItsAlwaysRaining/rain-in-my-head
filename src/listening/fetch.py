"""Append new scrobbles to monthly JSONL files under data/raw/lastfm/.

The files are the source of truth (committed to git); the SQLite DB is rebuilt from them.
The first run backfills the whole account one year at a time, writing each window only
once it is complete, so an interrupted backfill resumes from the last finished window.
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .lastfm import LastfmClient

YEAR = 365 * 24 * 3600
# Re-read a little before the newest stored scrobble, in case late scrobbles arrived.
OVERLAP = 2 * 24 * 3600


def scrobble_key(s: dict) -> tuple:
    return (s["uts"], s["artist"], s["track"])


def load_existing(raw_dir: Path) -> tuple[set[tuple], int | None]:
    keys: set[tuple] = set()
    newest = None
    for path in sorted(raw_dir.glob("*.jsonl")):
        with path.open() as f:
            for line in f:
                if line.strip():
                    s = json.loads(line)
                    keys.add(scrobble_key(s))
                    newest = s["uts"] if newest is None else max(newest, s["uts"])
    return keys, newest


def append_scrobbles(raw_dir: Path, scrobbles: list[dict]) -> None:
    by_month: dict[str, list[dict]] = defaultdict(list)
    for s in sorted(scrobbles, key=lambda s: s["uts"]):
        month = datetime.fromtimestamp(s["uts"], tz=timezone.utc).strftime("%Y-%m")
        by_month[month].append(s)
    for month, rows in by_month.items():
        with (raw_dir / f"{month}.jsonl").open("a") as f:
            for s in rows:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")


def fetch(client: LastfmClient, raw_dir: Path) -> int:
    raw_dir.mkdir(parents=True, exist_ok=True)
    keys, newest = load_existing(raw_dir)
    now = int(time.time())

    if newest is None:
        # Scrobbles can predate registration (imports), so the first window starts at 0.
        start_windows_at = client.registered_at()
        windows = [(1, start_windows_at - 1)]
        print(f"No local data: backfilling from {_fmt(start_windows_at)}")
    else:
        start_windows_at = newest - OVERLAP
        windows = []
        print(f"Fetching scrobbles since {_fmt(start_windows_at)}")

    lo = start_windows_at
    while lo <= now:
        windows.append((lo, min(lo + YEAR - 1, now)))
        lo += YEAR

    added = 0
    for lo, hi in windows:
        new = []
        for s in client.recent_tracks(lo, hi):
            k = scrobble_key(s)
            if k not in keys:
                keys.add(k)
                new.append(s)
        append_scrobbles(raw_dir, new)
        added += len(new)
        if len(windows) > 1:
            print(f"  {_fmt(lo)} → {_fmt(hi)}: {len(new)} new")
    print(f"Added {added} scrobbles ({len(keys)} total)")
    return added


def _fmt(uts: int) -> str:
    return datetime.fromtimestamp(uts, tz=timezone.utc).strftime("%Y-%m-%d")
