"""Command line entry point: `rain-in-my-head fetch | build | enrich | export-cache | publish | stats`, plus playlists."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from . import config


def _client():
    from .lastfm import LastfmClient

    return LastfmClient(*config.lastfm_credentials())


def cmd_fetch(args) -> None:
    from .fetch import fetch

    fetch(_client(), config.RAW_DIR)


def cmd_build(args) -> None:
    from .build import build

    build(config.RAW_DIR, config.DB_PATH, config.CACHE_DIR)


def cmd_export_cache(args) -> None:
    from .build import connect_readonly
    from .cache import ARTISTS_FILE, TRACKS_FILE, export

    if not config.DB_PATH.exists():
        raise SystemExit("No database yet. Run `rain-in-my-head build` first.")
    conn = connect_readonly(config.DB_PATH)
    try:
        tracks, artists = export(conn, config.CACHE_DIR, append=args.append)
    finally:
        conn.close()
    size = sum((config.CACHE_DIR / f).stat().st_size for f in (TRACKS_FILE, ARTISTS_FILE)) / 1e6
    print(f"Exported {tracks} tracks and {artists} artists to {config.CACHE_DIR} ({size:.1f} MB)")


def cmd_enrich(args) -> None:
    from .enrich import enrich

    enrich(_client(), config.DB_PATH, args.limit, config.CACHE_DIR if args.write_cache else None)


def cmd_publish(args) -> None:
    from .publish import publish

    out = Path(args.out)
    print(publish(config.DB_PATH, out, args.window_days, args.lag_days).line(out))


def cmd_stats(args) -> None:
    from .build import MIN_PLAYED_AT

    if not config.DB_PATH.exists():
        raise SystemExit("No database yet. Run `rain-in-my-head build` first.")
    conn = sqlite3.connect(config.DB_PATH)
    q = lambda sql: conn.execute(sql).fetchall()  # noqa: E731

    n, first, last = q(
        "SELECT COUNT(*), date(MIN(played_at),'unixepoch'), date(MAX(played_at),'unixepoch') FROM scrobbles"
    )[0]
    print(f"Scrobbles: {n}  ({first} → {last})")
    (bad,), = q(f"SELECT COUNT(*) FROM scrobbles WHERE played_at < {MIN_PLAYED_AT}")
    if bad:
        print(f"  {bad} have placeholder timestamps before 2000 and are excluded from v_plays/dashboard")
    (tracks, artists), = q("SELECT COUNT(DISTINCT track_key), COUNT(DISTINCT artist_key) FROM scrobbles")
    print(f"Unique tracks: {tracks}   unique artists: {artists}")

    (t_done, t_dur), = q("SELECT COUNT(*), COUNT(duration_ms) FROM tracks")
    (a_done,), = q("SELECT COUNT(*) FROM artists")
    (a_tagged,), = q("SELECT COUNT(DISTINCT artist_key) FROM artist_tags")
    print(f"Enriched tracks: {t_done}/{tracks} ({t_dur} with duration)")
    print(f"Enriched artists: {a_done}/{artists} ({a_tagged} with tags)")

    # Same track scrobbled 20+ times within 5 minutes is almost certainly junk.
    bursts = q(
        f"""SELECT datetime(MIN(played_at),'unixepoch'), artist_name, track_name, MAX(n) FROM (
             SELECT played_at, artist_name, track_name, track_key,
                    COUNT(*) OVER (PARTITION BY track_key ORDER BY played_at
                                   RANGE BETWEEN CURRENT ROW AND 300 FOLLOWING) AS n
             FROM scrobbles WHERE played_at >= {MIN_PLAYED_AT})
           WHERE n >= 20 GROUP BY track_key, played_at / 3600 ORDER BY 4 DESC LIMIT 10"""
    )
    if bursts:
        print("\nSuspicious bursts (≥20 plays of one track in 5 min):")
        for when, artist, track, count in bursts:
            print(f"  {when}  {artist} – {track}  ×{count}")
    conn.close()


def cmd_spotify_login(args) -> None:
    from .spotify import login

    login(config.spotify_client_id(), config.SPOTIFY_TOKEN_PATH)


def parse_days(text: str) -> list[int]:
    from .playlist import WEEKDAY_NAMES

    names = [d.lower() for d in WEEKDAY_NAMES]
    groups = {"all": range(7), "weekdays": range(5), "weekends": range(5, 7)}
    days: set[int] = set()
    for part in text.lower().replace(" ", "").split(","):
        if part in groups:
            days.update(groups[part])
        elif part[:3] in names:
            days.add(names.index(part[:3]))
        else:
            raise SystemExit(f"Unknown day {part!r}. Use e.g. fri, sat,sun, weekdays, weekends, all.")
    return sorted(days)


def parse_hours(text: str) -> tuple[int, int]:
    try:
        start, end = (int(h) for h in text.split("-"))
    except ValueError:
        raise SystemExit("--hours must look like 17-19 (24h clock; end is exclusive).")
    if not (0 <= start <= 23 and 1 <= end <= 24 and start != end):
        raise SystemExit("--hours must be within 0-24, e.g. 17-19 or 22-2.")
    return start, end


def _create_playlist(conn, ranked, size: int, name: str, description: str, reorder=None) -> None:
    """Match `ranked` on Spotify, create the playlist and print what happened."""
    from .playlist import create_on_spotify
    from .spotify import SpotifyClient

    client = SpotifyClient(config.spotify_client_id(), config.SPOTIFY_TOKEN_PATH)
    url, hits, misses = create_on_spotify(conn, client, ranked, size, name, description, reorder)
    for row in misses.itertuples():
        print(f"  no Spotify match: {row.artist} – {row.track}")
    print(f"Created playlist with {len(hits)} tracks: {url}")


def cmd_playlist(args) -> None:
    from datetime import date

    from .build import connect
    from .playlist import Slot, rank_tracks

    start, end = parse_hours(args.hours)
    slot = Slot(
        weekdays=parse_days(args.days), start_hour=start, end_hour=end,
        since=date.fromisoformat(args.since) if args.since else None,
        until=date.fromisoformat(args.until) if args.until else None,
    )
    conn = connect(config.DB_PATH)
    ranked = rank_tracks(conn, slot, args.min_plays)
    print(f"{slot.label()}: {len(ranked)} candidate tracks")
    if ranked.empty:
        return
    if args.dry_run:
        print(ranked.head(args.size)[["artist", "track", "slot_plays", "total_plays", "lift"]].to_string())
        return
    _create_playlist(conn, ranked, args.size, args.name or slot.label(), slot.describe())


def cmd_discoveries(args) -> None:
    from .build import connect
    from .playlist import discoveries, discoveries_description

    conn = connect(config.DB_PATH)
    ranked = discoveries(conn, args.year, args.min_plays, args.rank_by)
    print(f"Discovered in {args.year}: {len(ranked)} candidate tracks")
    if ranked.empty:
        return
    if args.dry_run:
        print(ranked.head(args.size)[["artist", "track", "first_played", "year_plays", "total_plays"]].to_string())
        return
    _create_playlist(
        conn, ranked, args.size,
        args.name or f"Discovered in {args.year}",
        discoveries_description(args.year, args.rank_by),
        reorder=(lambda hits: hits.sort_values("first_played")) if args.chronological else None,
    )


def cmd_binges(args) -> None:
    from .build import connect
    from .playlist import (
        binge_tracks, binges, binges_description, format_span, order_binge_episodes, order_binge_tracks,
    )

    conn = connect(config.DB_PATH)
    episodes = binges(conn, args.min_plays, args.window_days, args.since, args.until)
    ranked = binge_tracks(episodes)
    print(f"{len(episodes)} binges across {len(ranked)} songs ({args.min_plays}+ plays within {args.window_days} days)")
    if ranked.empty:
        return
    if args.dry_run:
        chosen = set(ranked.head(args.size)["track_key"])
        shown = order_binge_episodes(episodes[episodes["track_key"].isin(chosen)], args.order)
        for r in shown.itertuples():
            print(f"  {format_span(r.start, r.end):<26} {r.plays:>3} plays  {r.artist} – {r.track}")
        return
    # Match biggest binges first so misses are replaced by the next biggest, then apply the order.
    _create_playlist(
        conn, ranked, args.size,
        args.name or "Binged",
        binges_description(args.min_plays, args.window_days, args.order),
        reorder=lambda hits: order_binge_tracks(hits, args.order),
    )


def cmd_serve(args) -> None:
    try:
        import uvicorn  # in the `web` dependency group, so the sync install never needs it
    except ImportError:
        raise SystemExit("The dashboard API needs the web group: run `uv sync`.")
    print(f"Rain in My Head (TypeScript dashboard): http://{args.host}:{args.port}")
    uvicorn.run("rain_in_my_head.api:app", host=args.host, port=args.port, reload=args.dev,
                reload_dirs=[str(Path(__file__).parent)] if args.dev else None)


# ---- viewer: the owner's commands for invite codes (run on your Mac; specs/011-viewer-access) -------------------

def _viewer(args, work) -> None:
    """Print which database the command is using, run it, and turn a database or lookup error into one plain line."""
    from . import neon

    print(f"[{args.env}]", end=" ", flush=True)
    try:
        work()
    except neon.NeonError as e:
        raise SystemExit(f"\nThe database refused that: {e}")
    except neon.NeonUnavailable as e:
        raise SystemExit(f"\n{e}")


def cmd_viewer_init(args) -> None:
    from . import viewers

    def work():
        viewers.init_database(args.env)
        print(f"ready: {len(viewers.TABLES)} tables, role {viewers.APP_ROLE}")

    _viewer(args, work)


def main() -> None:
    parser = argparse.ArgumentParser(prog="rain-in-my-head", description="Personal listening analytics from Last.fm scrobbles")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch", help="append new scrobbles to data/raw/lastfm/").set_defaults(func=cmd_fetch)
    sub.add_parser("build", help="load raw scrobbles and the lookup cache into SQLite").set_defaults(func=cmd_build)
    p = sub.add_parser("enrich", help="cache track/artist info and tags from Last.fm")
    p.add_argument("--limit", type=int, default=None, help="max tracks and max artists to look up this run")
    p.add_argument("--write-cache", action="store_true",
                   help="also append each lookup to data/cache/ (used by the scheduled sync)")
    p.set_defaults(func=cmd_enrich)
    p = sub.add_parser("export-cache", help="write the database's Last.fm lookups to data/cache/ (one-time)")
    p.add_argument("--append", action="store_true", help="add after lookups already in data/cache/")
    p.set_defaults(func=cmd_export_cache)
    p = sub.add_parser("publish", help="build data/public.db, the two-year copy for the hosted site")
    p.add_argument("--window-days", type=int, default=730, help="days of plays to keep (default 730)")
    p.add_argument("--lag-days", type=int, default=7, help="leave out the newest N days (default 7)")
    p.add_argument("--out", default=str(config.ROOT / "data" / "public.db"), help="output file (default data/public.db)")
    p.set_defaults(func=cmd_publish)
    sub.add_parser("stats", help="summarize the database").set_defaults(func=cmd_stats)
    sub.add_parser("spotify-login", help="connect Spotify (for creating playlists)").set_defaults(
        func=cmd_spotify_login
    )
    p = sub.add_parser("playlist", help="make a Spotify playlist of tracks distinctive to a time slot")
    p.add_argument("--days", default="all", help="e.g. fri | sat,sun | weekdays | weekends | all")
    p.add_argument("--hours", default="0-24", help="local hours, end exclusive, e.g. 17-19 or 22-2")
    p.add_argument("--since", help="only plays on/after this date, YYYY-MM-DD")
    p.add_argument("--until", help="only plays on/before this date, YYYY-MM-DD")
    p.add_argument("--size", type=int, default=50, help="number of tracks (default 50)")
    p.add_argument("--min-plays", type=int, default=3, help="min plays in the slot (default 3)")
    p.add_argument("--name", help="playlist name (default: the slot, e.g. 'Fris 5pm–7pm')")
    p.add_argument("--dry-run", action="store_true", help="print the ranking without touching Spotify")
    p.set_defaults(func=cmd_playlist)
    p = sub.add_parser("discoveries", help="make a Spotify playlist of songs first heard in a given year")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--rank-by", choices=["year", "ever"], default="year",
                   help="year = most played that year (default); ever = most played since")
    p.add_argument("--size", type=int, default=50)
    p.add_argument("--min-plays", type=int, default=2)
    p.add_argument("--chronological", action="store_true", help="order the playlist by discovery date")
    p.add_argument("--name", help="playlist name (default: 'Discovered in <year>')")
    p.add_argument("--dry-run", action="store_true", help="print the ranking without touching Spotify")
    p.set_defaults(func=cmd_discoveries)
    p = sub.add_parser("binges", help="make a Spotify playlist of songs you played on repeat")
    p.add_argument("--min-plays", type=int, default=8, help="plays within the window to count as a binge (default 8)")
    p.add_argument("--window-days", type=int, default=7, help="binge window in days (default 7)")
    p.add_argument("--since", type=int, help="only binges starting in/after this year")
    p.add_argument("--until", type=int, help="only binges starting in/before this year")
    p.add_argument("--size", type=int, default=50)
    p.add_argument("--order", choices=["oldest", "newest", "biggest"], default="oldest",
                   help="playlist order: oldest binge first (default), newest first, or biggest first")
    p.add_argument("--name", help="playlist name (default 'Binged')")
    p.add_argument("--dry-run", action="store_true", help="list the binges without touching Spotify")
    p.set_defaults(func=cmd_binges)
    p = sub.add_parser("serve", help="run the TypeScript dashboard and its JSON API")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--dev", action="store_true", help="reload on Python changes (use with `npm run dev` in web/)")
    p.set_defaults(func=cmd_serve)
    p = sub.add_parser("viewer", help="invite codes for the hosted site (run on your Mac)")
    viewer = p.add_subparsers(dest="viewer_command", required=True)
    env_help = "which Neon branch: dev (default) or prod"
    q = viewer.add_parser("init", help="make the tables and the site's database role (safe to run twice)")
    q.add_argument("--env", choices=["dev", "prod"], default="dev", help=env_help)
    q.set_defaults(func=cmd_viewer_init)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
