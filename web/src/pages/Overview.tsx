// Overview: the TypeScript twin of dashboard/views/overview.py. Every number comes from
// /api/overview (rain_in_my_head.overview); this file only decides how it looks.
// Behaviour follows openspec/specs/dashboard-overview/spec.md.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { fetchOverview, NO_ART, type Grain, type NewArtistList, type OverviewFull, type Preset } from "../api";
import { Sidebar } from "../App";
import * as charts from "../charts/overview";
import { artistColumns } from "../components/columns";
import { DataTable } from "../components/DataTable";
import { ErrorState, Kpi, Loading, Notice, RadioGroup, SegmentedControl, Tabs } from "../components/ui";
import { VegaChart } from "../components/VegaChart";
import { capitalize, formatDate, formatDateTime, percent } from "../format";
import styles from "./Overview.module.css";

const PRESETS: Record<Preset, string> = {
  last30: "Last 30 days",
  last12m: "Last 12 months",
  ytd: "This year",
  all: "All time",
  custom: "Custom",
};
const GRAINS = ["week", "month", "year"] as const;
const MEASURES = ["scrobbles", "hours"] as const;
type Measure = (typeof MEASURES)[number];

const oneOf = <T extends string>(value: string | null, options: readonly T[], fallback: T): T =>
  options.includes(value as T) ? (value as T) : fallback;

export default function Overview() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const preset = oneOf(params.get("preset"), Object.keys(PRESETS) as Preset[], "last12m");
  const grain = oneOf<Grain>(params.get("grain"), GRAINS, "month");
  const measure = oneOf<Measure>(params.get("measure"), MEASURES, "scrobbles");
  const period = params.get("period") ?? undefined;
  const start = params.get("start") ?? undefined;
  const end = params.get("end") ?? undefined;

  const query = useQuery({
    queryKey: ["overview", preset, start, end, grain, period],
    queryFn: () => fetchOverview({ preset, start, end, grain, period }),
    placeholderData: keepPreviousData,
  });
  const data = query.data;

  /** Update URL params; changing the range or grain drops the selected period. */
  const update = (changes: Record<string, string | undefined>) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      if ("preset" in changes || "grain" in changes || "start" in changes || "end" in changes) next.delete("period");
      for (const [k, v] of Object.entries(changes)) v === undefined ? next.delete(k) : next.set(k, v);
      return next;
    });

  // A period that no longer names a bar is ignored by the API; drop it from the URL too.
  useEffect(() => {
    if (period && data && !query.isPlaceholderData && data.selected === null) update({ period: undefined });
  });

  const range = data?.range;

  return (
    <>
      <Sidebar>
        <h2 className={styles.sidebarTitle}>Filters</h2>
        <div className={styles.filters}>
          <RadioGroup
            label="Range"
            options={Object.keys(PRESETS) as Preset[]}
            format={(p) => PRESETS[p]}
            value={preset}
            onChange={(p) =>
              update(p === "custom" && range ? { preset: p, start: range.base_start, end: range.base_end } : { preset: p, start: undefined, end: undefined })
            }
          />
          {preset === "custom" && range && (
            <div className={styles.dates}>
              <label>
                From
                <input type="date" value={start ?? range.base_start} min={range.data_first} max={end ?? range.data_last} onChange={(e) => e.target.value && update({ start: e.target.value })} />
              </label>
              <label>
                To
                <input type="date" value={end ?? range.base_end} min={start ?? range.data_first} max={range.data_last} onChange={(e) => e.target.value && update({ end: e.target.value })} />
              </label>
            </div>
          )}
          <RadioGroup label="Time grain" options={GRAINS} format={capitalize} value={grain} onChange={(g) => update({ grain: g })} horizontal />
        </div>
      </Sidebar>

      <h1>Rain in My Head</h1>
      {query.error ? (
        <div className={styles.section}>
          <ErrorState error={query.error} />
        </div>
      ) : !data ? (
        <Loading />
      ) : data.empty && data.reason === "no_scrobbles" ? (
        <div className={styles.section}>
          <Notice>
            The database has no scrobbles yet. Run <code>uv run rain-in-my-head fetch</code> and <code>uv run rain-in-my-head build</code>.
          </Notice>
        </div>
      ) : (
        <>
          <p className={`caption ${styles.caption}`}>
            {formatDate(data.range!.start)} – {formatDate(data.range!.end)} · data through {formatDateTime(data.range!.data_through)}
          </p>
          {data.empty ? (
            <Notice tone="warning">No scrobbles in this range.</Notice>
          ) : (
            <OverviewBody
              data={data}
              measure={measure}
              loading={query.isFetching}
              onMeasure={(m) => update({ measure: m })}
              onPeriod={(p) => update({ period: p ?? undefined })}
              onGenre={(genre) => navigate(`/genre?${new URLSearchParams({ genre, start: data.range.start, end: data.range.end })}`)}
            />
          )}
        </>
      )}
    </>
  );
}

function OverviewBody({
  data,
  measure,
  loading,
  onMeasure,
  onPeriod,
  onGenre,
}: {
  data: OverviewFull;
  measure: Measure;
  loading: boolean;
  onMeasure: (m: Measure) => void;
  onPeriod: (period: string | null) => void;
  onGenre: (genre: string) => void;
}) {
  const selected = data.selected?.label ?? null;
  const overTimeSpec = useMemo(() => charts.overTime(data.over_time, measure, data.grain, selected), [data.over_time, measure, data.grain, selected]);
  const topSpecs = useMemo(
    () => ({
      artists: charts.topBar(data.top.artists, "Top artists", "artist_name"),
      tracks: charts.topBar(data.top.tracks, "Top tracks", "track"),
      albums: charts.topBar(data.top.albums, "Top albums", "album"),
    }),
    [data.top],
  );
  const heatSpec = useMemo(() => charts.heatmap(data.heatmap), [data.heatmap]);
  const newSpec = useMemo(() => charts.newArtists(data.new_artists, data.inner_grain), [data.new_artists, data.inner_grain]);
  const genreSpecs = useMemo(
    () => data.genres?.panels.map((p) => ({ genre: p.genre, spec: charts.genrePanel(p, data.genres!.y_max, data.inner_grain) })) ?? [],
    [data.genres, data.inner_grain],
  );
  const bucketSpec = useMemo(() => (data.listener_buckets ? charts.listenerBuckets(data.listener_buckets) : null), [data.listener_buckets]);

  const periodName = selected && (data.grain === "week" ? `the week of ${selected}` : selected);

  return (
    <div className={loading ? styles.loading : undefined}>
      <div className={styles.kpis}>
        {data.kpis.map((k) => (
          <Kpi key={k.label} {...k} help="Change vs. the previous period of equal length" />
        ))}
      </div>

      <div className={styles.section}>
        <SegmentedControl label="Measure" options={MEASURES} value={measure} onChange={onMeasure} />
        <div className={styles.chart}>
          <VegaChart spec={overTimeSpec} onSelect={(v) => onPeriod(v ? String((v.period as string[])[0]) : null)} />
        </div>
        {selected === null ? (
          <p className="caption">Click a bar to show just that {data.grain}.</p>
        ) : (
          <div className={styles.selection}>
            <p className="caption">Showing {periodName} only. Click the chart background or the button to show the whole range.</p>
            <button className={styles.button} onClick={() => onPeriod(null)}>
              Show whole range
            </button>
          </div>
        )}
      </div>

      <section className={styles.section}>
        <h2>Top</h2>
        <Tabs
          tabs={[
            { label: "Artists", content: <VegaChart spec={topSpecs.artists} /> },
            { label: "Tracks", content: <VegaChart spec={topSpecs.tracks} /> },
            { label: "Albums", content: <VegaChart spec={topSpecs.albums} /> },
            {
              label: "#1 per year",
              content: (
                <DataTable
                  rows={data.top_per_year}
                  columns={[
                    { key: "year", label: "Year", kind: "year" },
                    { key: "artist", label: "Artist" },
                    { key: "plays", label: "plays", kind: "number" },
                    { key: "share", label: "Share of year", kind: "progress" },
                  ]}
                />
              ),
            },
          ]}
        />
      </section>

      <div className={`${styles.section} ${styles.twoCol}`}>
        <VegaChart spec={heatSpec} />
        <div>
          <VegaChart spec={newSpec} />
          <p className="caption">{percent(data.new_share)} of plays in this range were artists you first heard that same year.</p>
          <NewArtists list={data.new_artist_list} />
        </div>
      </div>

      <section className={styles.section}>
        <h2>Genres and mainstream-ness</h2>
        {data.genres === null ? (
          <Notice>
            Run <code>uv run rain-in-my-head enrich</code> to add genres (Last.fm tags), durations and artist popularity.
          </Notice>
        ) : (
          <>
            <p className="caption">
              Share of tagged plays per {data.inner_grain} for your top {data.genres.panels.length} genres (artist's top Last.fm tag). Click a chart to see its artists.
            </p>
            <div className={styles.genreGrid}>
              {genreSpecs.map(({ genre, spec }) => (
                <VegaChart key={genre} spec={spec} onSelect={(v) => v && onGenre(genre)} />
              ))}
            </div>
            {bucketSpec && (
              <div className={styles.twoCol}>
                <VegaChart spec={bucketSpec} />
              </div>
            )}
          </>
        )}
      </section>

      <div className={`${styles.section} ${styles.twoCol}`}>
        <section>
          <h2>Loved tracks</h2>
          <div className={styles.tableGap}>
            {data.loved.length === 0 ? (
              <p className="caption">No loved tracks in this range.</p>
            ) : (
              <DataTable
                rows={data.loved}
                maxHeight={300}
                columns={[
                  { key: "artist", label: "Artist" },
                  { key: "track", label: "Track" },
                  { key: "plays", label: "Plays", kind: "number" },
                ]}
              />
            )}
          </div>
        </section>
        <section>
          <h2>Data quality</h2>
          <div className={styles.tableGap}>
            <DataTable
              rows={data.coverage}
              columns={[
                { key: "check", label: "Check" },
                { key: "coverage", label: "Coverage", kind: "progress" },
              ]}
            />
          </div>
          <p className="caption">Hours are estimated: plays without a known duration count as 3.5 minutes.</p>
        </section>
      </div>
    </div>
  );
}

/** Artists first heard in the list's period (spec 001). Missing art shows the shared placeholder. */
function NewArtists({ list }: { list: NewArtistList }) {
  const navigate = useNavigate();
  const rows = useMemo(() => list.artists.map((a) => ({ ...a, thumb: a.thumb ?? NO_ART })), [list.artists]);
  return (
    <section className={styles.newArtists}>
      <h2>New artists in {list.label}</h2>
      {rows.length === 0 ? (
        <p className="caption">No new artists in this period.</p>
      ) : (
        <DataTable
          rows={rows}
          columns={artistColumns()}
          maxHeight={420}
          onRowClick={(a) => navigate(`/artist?${new URLSearchParams({ artist: a.artist_key, start: list.start, end: list.end })}`)}
        />
      )}
      {rows.length > 0 && <p className="caption">Click an artist to see your songs by them.</p>}
    </section>
  );
}
