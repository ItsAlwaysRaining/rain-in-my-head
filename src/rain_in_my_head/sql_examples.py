"""Ad-hoc SQL against the listening database, shared by the Streamlit SQL view and the API.

Queries run on a read-only connection, so a stray UPDATE/DELETE can't damage the database.
"""

from __future__ import annotations

from contextlib import closing
from pathlib import Path

import pandas as pd

from .build import connect_readonly

EXAMPLES = {
    "Top artists this year": """SELECT artist_name, COUNT(*) AS plays, ROUND(SUM(est_minutes) / 60, 1) AS hours
FROM v_plays
WHERE year = CAST(strftime('%Y', 'now') AS INTEGER)
GROUP BY artist_name
ORDER BY plays DESC
LIMIT 25""",
    "Most-played track each year": """SELECT year, artist_name, track_name, plays FROM (
  SELECT year, artist_name, track_name, COUNT(*) AS plays,
         ROW_NUMBER() OVER (PARTITION BY year ORDER BY COUNT(*) DESC) AS rn
  FROM v_plays GROUP BY year, track_key
) WHERE rn = 1 ORDER BY year""",
    "Biggest listening days": """SELECT date(played_local) AS day, COUNT(*) AS plays
FROM v_plays GROUP BY day ORDER BY plays DESC LIMIT 20""",
    "Artists I've stopped listening to": """SELECT artist_name, COUNT(*) AS plays, MAX(date(played_local)) AS last_played
FROM v_plays GROUP BY artist_key
HAVING plays >= 100 AND last_played < date('now', '-2 years')
ORDER BY plays DESC""",
    "First play of my top 50 artists": """SELECT artist_name, MIN(date(played_local)) AS first_play, COUNT(*) AS plays
FROM v_plays GROUP BY artist_key ORDER BY plays DESC LIMIT 50""",
    "Plays by genre": """SELECT COALESCE(primary_genre, '(untagged)') AS genre, COUNT(*) AS plays
FROM v_plays GROUP BY genre ORDER BY plays DESC LIMIT 30""",
}


def _quote(name: str) -> str:
    """A table name as a quoted SQL identifier (the same rule as schema_info)."""
    return '"' + name.replace('"', '""') + '"'


def schema(db_path: Path) -> pd.DataFrame:
    """Every table and view with its columns: `object` ("name (kind)"), `column`, `type`."""
    with closing(connect_readonly(db_path)) as conn:
        objects = conn.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type DESC, name"
        ).fetchall()
        rows = []
        for name, kind in objects:
            for col in conn.execute(f"PRAGMA table_info({_quote(name)})"):
                rows.append({"object": f"{name} ({kind})", "column": col[1], "type": col[2]})
    return pd.DataFrame(rows)


def run_example(db_path: Path, name: str) -> pd.DataFrame:
    """One of EXAMPLES by name: the only queries the hosted site runs. KeyError for an unknown name."""
    return run_readonly(db_path, EXAMPLES[name])


def run_readonly(db_path: Path, sql: str) -> pd.DataFrame:
    """The query's result. Raises the database's error for invalid SQL or an attempted write."""
    with closing(connect_readonly(db_path)) as conn:
        return pd.read_sql(sql, conn)
