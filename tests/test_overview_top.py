"""The Overview's top lists: artists are grouped by artist_key so a row's count matches the Artist page."""

import pandas as pd

from rain_in_my_head.overview import top_lists


def _plays(rows: list[tuple[str, str, str, str | None]]) -> pd.DataFrame:
    """Rows of (artist_key, artist_name, track_name, album_name)."""
    return pd.DataFrame(rows, columns=["artist_key", "artist_name", "track_name", "album_name"])


def test_spellings_that_share_a_key_are_one_artist_row():
    df = _plays([
        ("hozier", "Hozier", "Too Sweet", "Hozier"),
        ("hozier", "HOZIER", "Too Sweet", "Hozier"),
        ("hozier", "Hozier", "Work Song", "Hozier"),
        ("geese", "Geese", "Au Pays du Cocaine", "Projector"),
    ])

    artists = top_lists(df)["artists"]

    hozier = artists[artists["artist_key"] == "hozier"]
    assert len(hozier) == 1
    assert hozier.iloc[0]["plays"] == 3
    assert hozier.iloc[0]["name"] == "Hozier"  # the first spelling seen


def test_artists_are_most_played_first_and_carry_the_key():
    df = _plays([
        ("geese", "Geese", "A", None),
        ("hozier", "Hozier", "B", None),
        ("hozier", "Hozier", "C", None),
    ])

    artists = top_lists(df)["artists"]

    assert list(artists["artist_key"]) == ["hozier", "geese"]
    assert list(artists["plays"]) == [2, 1]
    assert set(artists.columns) == {"artist_key", "name", "plays"}


def test_tracks_and_albums_keep_name_and_plays_only():
    df = _plays([
        ("hozier", "Hozier", "Too Sweet", "Hozier"),
        ("geese", "Geese", "Cobra", None),
    ])

    lists = top_lists(df)

    assert list(lists["tracks"].columns) == ["name", "plays"]
    assert list(lists["albums"].columns) == ["name", "plays"]
    assert list(lists["albums"]["name"]) == ["Hozier – Hozier"]  # plays without an album are left out
