// Genre: the TypeScript twin of dashboard/views/genre.py. Lists come from /api/genre
// (rain_in_my_head.genre). Behaviour follows openspec/specs/genre-page/spec.md. Opened from the
// Overview's genre chart with ?genre=&preset= (and &start=&end= for Custom).
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useSearchParams } from "react-router";
import { fetchGenre, fetchGenreSongs, type GenreArtist, type GenreParams, type Preset } from "../api";
import { genreColor, shareArea } from "../charts/genre";
import { artistColumns, songColumns } from "../components/columns";
import { DataTable } from "../components/DataTable";
import { PRESET_KEYS, RangePicker } from "../components/RangePicker";
import { VegaChart } from "../components/VegaChart";
import { BackLink, Card, ErrorState, Loading, Notice, PageHeader } from "../components/ui";
import { formatCount } from "../format";
import styles from "./Genre.module.css";

/** Python's str.title(): "hip-hop" -> "Hip-Hop". */
const title = (s: string) => s.replace(/[a-z]+/gi, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase());

export default function Genre() {
  const [params, setParams] = useSearchParams();
  const rawPreset = params.get("preset");
  const asked: GenreParams = {
    genre: params.get("genre") ?? undefined,
    // Dates without a preset are Custom (old links); the API treats a missing preset the same way.
    preset: PRESET_KEYS.includes(rawPreset as Preset) ? (rawPreset as Preset) : undefined,
    start: params.get("start") ?? undefined,
    end: params.get("end") ?? undefined,
  };
  const query = useQuery({
    queryKey: ["genre", asked.genre, asked.preset, asked.start, asked.end],
    queryFn: () => fetchGenre(asked),
    placeholderData: keepPreviousData,
  });
  const data = query.data;
  const share = data?.genre ? data.share : null;
  const shareSpec = useMemo(() => (share ? shareArea(share.points, share.grain, genreColor(share.color_index)) : null), [share]);

  /** Change the range; the genre stays. */
  const setRange = (preset: Preset, start?: string, end?: string) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      next.set("preset", preset);
      for (const [k, v] of Object.entries({ start, end })) v === undefined ? next.delete(k) : next.set(k, v);
      return next;
    });

  if (query.error)
    return (
      <>
        <h1>Genre</h1>
        <div className={styles.section}>
          <ErrorState error={query.error} />
        </div>
      </>
    );
  if (!data) return <Loading />;
  if (data.genre === null)
    return (
      <>
        <h1>Genre</h1>
        <div className={styles.section}>
          <Notice>
            Run <code>uv run rain-in-my-head enrich</code> to add genres (Last.fm tags).
          </Notice>
        </div>
      </>
    );

  // The resolved dates, so the songs list uses exactly the range shown.
  const range = { genre: data.genre, preset: "custom" as const, start: data.range.start, end: data.range.end };
  return (
    <>
      <BackLink />
      <PageHeader title={title(data.genre)}>
        {data.range_label} · {formatCount(data.plays)} plays · artists whose top Last.fm tag is “{data.genre}”
      </PageHeader>
      <div className={styles.controls}>
        <RangePicker preset={data.range.preset} shown={data.range} onChange={setRange} />
        <label className={styles.select}>
          Genre
          <select
            value={data.genre}
            onChange={(e) =>
              setParams((prev) => {
                const next = new URLSearchParams(prev);
                next.set("genre", e.target.value);
                return next;
              })
            }
          >
            {data.genres.map((g) => (
              <option key={g}>{g}</option>
            ))}
          </select>
        </label>
      </div>

      {data.artists.length > 0 && shareSpec && (
        <Card title="Share of tagged plays" className={styles.section}>
          <VegaChart spec={shareSpec} />
        </Card>
      )}

      {data.artists.length === 0 ? (
        <Notice tone="warning">No plays in this genre for this range.</Notice>
      ) : (
        // Keyed on genre and range, so a new list starts with nothing selected (as Streamlit's widget key does).
        <Columns key={`${data.genre}-${range.start}-${range.end}`} artists={data.artists} range={range} />
      )}
    </>
  );
}

function Columns({ artists, range }: { artists: GenreArtist[]; range: GenreParams & { genre: string } }) {
  const [picked, setPicked] = useState<number | null>(null);
  const artist = picked === null ? null : artists[picked];

  return (
    <div className={styles.columns}>
      <section>
        <h2 className={styles.subheader}>Artists</h2>
        <DataTable rows={artists} columns={artistColumns()} maxHeight={640} onRowClick={(_, i) => setPicked(i)} selectedIndex={picked} />
        <p className={`caption ${styles.hint}`}>Click an artist to see your songs by them.</p>
      </section>

      <section>
        {artist === null ? (
          <>
            <h2 className={styles.subheader}>Songs</h2>
            <Notice>Click an artist on the left.</Notice>
          </>
        ) : (
          <Songs artist={artist} range={range} />
        )}
      </section>
    </div>
  );
}

function Songs({ artist, range }: { artist: GenreArtist; range: GenreParams & { genre: string } }) {
  const query = useQuery({
    queryKey: ["genre-songs", range.genre, range.preset, range.start, range.end, artist.artist_key],
    queryFn: () => fetchGenreSongs({ ...range, artist_key: artist.artist_key }),
    placeholderData: keepPreviousData,
  });
  const data = query.data;
  const art = data?.artist.art;

  return (
    <>
      <div className={styles.artist}>
        <div className={styles.art}>{art && <img src={art} alt="" />}</div>
        <div>
          <h2 className={styles.subheader}>{artist.name}</h2>
          <p className="caption">
            {formatCount(artist.plays)} plays in {range.genre}
          </p>
        </div>
      </div>
      {query.error ? <ErrorState error={query.error} /> : !data ? <Loading /> : <DataTable rows={data.songs} columns={songColumns()} maxHeight={520} />}
    </>
  );
}
