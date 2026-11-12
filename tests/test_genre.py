"""The Genre page's share of tagged plays (rain_in_my_head.genre.genre_share)."""

from datetime import date

import pandas as pd

from rain_in_my_head.genre import genre_share, share_grain


def _plays(rows: list[tuple[str, str | None]]) -> pd.DataFrame:
    """Rows of (local timestamp, primary_genre)."""
    df = pd.DataFrame(rows, columns=["played_local", "primary_genre"])
    df["played_local"] = pd.to_datetime(df["played_local"])
    return df


def test_share_is_genre_plays_over_tagged_plays_per_step():
    df = _plays([
        ("2026-01-05", "indie"), ("2026-01-10", "rock"), ("2026-01-12", None),
        ("2026-02-03", "indie"), ("2026-02-04", "indie"),
    ])

    rank, share = genre_share(df, "indie", "Month")

    assert rank == 0
    assert list(share["plays"]) == [1, 2]
    assert list(share["share"]) == [0.5, 1.0]  # the untagged play is left out


def test_step_with_no_genre_plays_is_zero_not_missing():
    df = _plays([("2026-01-05", "indie"), ("2026-02-05", "rock"), ("2026-03-05", "indie")])

    _, share = genre_share(df, "indie", "Month")

    assert list(share["share"]) == [1.0, 0.0, 1.0]


def test_rank_is_none_outside_the_top_n():
    df = _plays([("2026-01-01", g) for g in ["a", "a", "b", "b", "c"]])

    assert genre_share(df, "b", "Month", n=2)[0] == 1
    assert genre_share(df, "c", "Month", n=2)[0] is None


def test_nothing_tagged():
    rank, share = genre_share(_plays([("2026-01-01", None)]), "indie", "Month")
    assert rank is None and share.empty


def test_grain_is_week_up_to_three_months():
    assert share_grain(date(2026, 1, 1), date(2026, 3, 31)) == "Week"
    assert share_grain(date(2025, 1, 1), date(2026, 1, 1)) == "Month"
