// Overview: the TypeScript twin of dashboard/views/overview.py. Every number comes from
// /api/overview (rain_in_my_head.overview); this file only decides how it looks.
// Behaviour follows openspec/specs/dashboard-overview/spec.md; layout follows the Figma prototype
// (specs/005-prototype-redesign). Unlike Streamlit, there's no Loved tracks section and the new
// artists list is its own page.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router";
import { fetchOverview, type Grain, type NamePlays, type OverviewFull, type Preset } from "../api";
import * as charts from "../charts/overview";
import { GENRE_COLORS } from "../charts/config";
import { DataTable, type Column } from "../components/DataTable";
import { Button, Card, ChipGroup, ErrorState, Kpi, Loading, Notice, PageHeader, rememberDashboardsSearch, SegmentedControl, Tabs } from "../components/ui";
import { VegaChart } from "../components/VegaChart";
import { capitalize, formatDate, formatDateTime, percent } from "../format";
import styles from "./Overview.module.css";

const PRESETS: Record<Preset, string> = {
  last30: "Last 30 days",
  ytd: "This year",
  last12m: "Last 12 months",
  all: "All time",
  custom: "Custom",
};
const GRAINS = ["week", "month", "year"] as const;
const MEASURES = ["scrobbles", "hours"] as const;
type Measure = (typeof MEASURES)[number];

const oneOf = <T extends string>(value: string | null, options: readonly T[], fallback: T): T =>
  options.includes(value as T) ? (value as T) : fallback;

/** "YYYY-MM" of a clicked temporal value (Vega gives a timestamp or a date string). */
const monthOf = (value: unknown) => {
  const d = new Date(value as string | number);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
};

/** A top list's columns: its name and plays, most played first. */
function topColumns<T extends NamePlays>(label: string): Column<T>[] {
  return [
    { key: "name", label },
    { key: "plays", label: "Plays", kind: "number" },
  ];
}

export default function Overview() {
  const [params, setParams] = useSearchParams();
  const { search } = useLocation();
  const preset = oneOf(params.get("preset"), Object.keys(PRESETS) as Preset[], "last12m");
  const grain = oneOf<Grain>(params.get("grain"), GRAINS, "month");
  const measure = oneOf<Measure>(params.get("measure"), MEASURES, "scrobbles");
  const period = params.get("period") ?? undefined;
  const start = params.get("start") ?? undefined;
  const end = params.get("end") ?? undefined;

  useEffect(() => rememberDashboardsSearch(search), [search]);

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
      <PageHeader title="Overview">
        {range ? `${formatDate(range.start)} – ${formatDate(range.end)} · data through ${formatDateTime(range.data_through)}` : " "}
      </PageHeader>

      <div className={styles.filters}>
        <div>
          <ChipGroup
            label="Date range"
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
        </div>
        <ChipGroup label="Grain" options={GRAINS} format={capitalize} value={grain} onChange={(g) => update({ grain: g })} />
      </div>

      {query.error ? (
        <ErrorState error={query.error} />
      ) : !data ? (
        <Loading text="Fetching your scrobbles…" />
      ) : data.empty && data.reason === "no_scrobbles" ? (
        <Notice>
          The database has no scrobbles yet. Run <code>uv run rain-in-my-head fetch</code> and <code>uv run rain-in-my-head build</code>.
        </Notice>
      ) : data.empty ? (
        <Notice tone="warning">No scrobbles in this range.</Notice>
      ) : (
        <OverviewBody data={data} measure={measure} loading={query.isFetching} onMeasure={(m) => update({ measure: m })} onPeriod={(p) => update({ period: p ?? undefined })} />
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
}: {
  data: OverviewFull;
  measure: Measure;
  loading: boolean;
  onMeasure: (m: Measure) => void;
  onPeriod: (period: string | null) => void;
}) {
  const navigate = useNavigate();
  const { start, end } = data.range;
  const selected = data.selected?.label ?? null;
  const overTimeSpec = useMemo(() => charts.overTime(data.over_time, measure, data.grain, selected), [data.over_time, measure, data.grain, selected]);
  const heatSpec = useMemo(() => charts.heatmap(data.heatmap), [data.heatmap]);
  const newSpec = useMemo(() => charts.newArtists(data.new_artists, data.inner_grain), [data.new_artists, data.inner_grain]);
  const genreSpec = useMemo(() => (data.genres ? charts.genreLines(data.genres.panels, data.inner_grain) : null), [data.genres, data.inner_grain]);
  const bucketSpec = useMemo(() => (data.listener_buckets ? charts.listenerBuckets(data.listener_buckets) : null), [data.listener_buckets]);
  const maxPlays = Math.max(0, ...data.heatmap.map((h) => h.plays));

  const periodName = selected && (data.grain === "week" ? `the week of ${selected}` : selected);
  const openGenre = (genre: string) => navigate(`/dashboards/genre?${new URLSearchParams({ genre, start, end })}`);

  return (
    <div className={loading ? styles.loading : undefined}>
      <div className={styles.kpis}>
        {data.kpis.map((k) => (
          <Kpi key={k.label} {...k} help="Change vs. the previous period of equal length" />
        ))}
      </div>
      <p className={`caption ${styles.kpiNote}`}>Change vs. the previous period of equal length.</p>

      <Card
        title={`${capitalize(measure)} per ${data.grain}`}
        actions={<SegmentedControl label="Measure" options={MEASURES} format={capitalize} value={measure} onChange={onMeasure} />}
      >
        <VegaChart spec={overTimeSpec} onSelect={(v) => onPeriod(v ? String((v.period as string[])[0]) : null)} />
        {selected === null ? (
          <p className="caption">Click a bar to show just that {data.grain}.</p>
        ) : (
          <div className={styles.selection}>
            <p className="caption">Showing {periodName} only. Click the chart background or the button to show the whole range.</p>
            <Button onClick={() => onPeriod(null)}>Show whole range</Button>
          </div>
        )}
      </Card>

      <section className={styles.section}>
        <h2>Top</h2>
        <Card>
          <Tabs
            tabs={[
              {
                key: "artists",
                label: "Artists",
                content: (
                  <DataTable
                    rows={data.top.artists}
                    columns={topColumns("Artist")}
                    maxHeight={420}
                    onRowClick={(artist) => navigate(`/dashboards/artist?${new URLSearchParams({ artist: artist.artist_key, start, end })}`)}
                  />
                ),
              },
              { key: "tracks", label: "Tracks", content: <DataTable rows={data.top.tracks} columns={topColumns("Track")} maxHeight={420} /> },
              { key: "albums", label: "Albums", content: <DataTable rows={data.top.albums} columns={topColumns("Album")} maxHeight={420} /> },
              {
                key: "per-year",
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
          <p className="caption">Plays</p>
        </Card>
      </section>

      <div className={`${styles.section} ${styles.twoCol}`}>
        <Card title="When you listen">
          <VegaChart
            spec={heatSpec}
            onSelect={(v) =>
              v && navigate(`/dashboards/slot?${new URLSearchParams({ day: String((v.weekday as string[])[0]), hour: String((v.hour as number[])[0]), start, end })}`)
            }
          />
          <p className="caption">
            Plays by hour of day and weekday. Darkest is 0 plays, lightest is {maxPlays}. Click a square to see those tracks.
          </p>
        </Card>
        <Card title={`New artists per ${data.inner_grain}`}>
          <VegaChart spec={newSpec} onSelect={(v) => v && navigate(`/dashboards/new-artists?month=${monthOf((v.start as unknown[])[0])}`)} />
          <p className="caption">{percent(data.new_share)} of plays in this range were artists you first heard that same year.</p>
          <p className="caption">Click a point to see the artists you found that month.</p>
        </Card>
      </div>

      <section className={styles.section}>
        <h2>Genres and mainstream-ness</h2>
        {data.genres === null || genreSpec === null ? (
          <Notice>
            Run <code>uv run rain-in-my-head enrich</code> to add genres (Last.fm tags), durations and artist popularity.
          </Notice>
        ) : (
          <>
            <p className={styles.lede}>
              Share of tagged plays per {data.inner_grain} for your top {data.genres.panels.length} genres (artist's top Last.fm tag). Click a genre to see its
              artists.
            </p>
            <Card title="Genre share over time">
              <div className={styles.legend} role="list" aria-label="Genres">
                {data.genres.panels.map((p, i) => (
                  <button key={p.genre} role="listitem" className={styles.legendChip} onClick={() => openGenre(p.genre)}>
                    <span className={styles.swatch} style={{ background: GENRE_COLORS[i % GENRE_COLORS.length] }} aria-hidden />
                    {p.genre}
                    <span aria-hidden>›</span>
                  </button>
                ))}
              </div>
              <VegaChart spec={genreSpec} onSelect={(v) => v && openGenre(String((v.genre as string[])[0]))} />
            </Card>
          </>
        )}
      </section>

      <div className={`${styles.section} ${styles.twoCol}`}>
        {bucketSpec && (
          <Card title="Mainstream vs. niche (artist's Last.fm listeners)">
            <VegaChart
              spec={bucketSpec}
              onSelect={(v) => v && navigate(`/dashboards/mainstream?${new URLSearchParams({ bucket: String((v.bucket as string[])[0]), start, end })}`)}
            />
            <p className="caption">Share of your plays by the artist's global listener count. Click a bar to see those artists.</p>
          </Card>
        )}
        <Card title="Data quality">
          <DataTable
            rows={data.coverage}
            columns={[
              { key: "check", label: "Check" },
              { key: "coverage", label: "Coverage", kind: "progress" },
            ]}
          />
          <p className="caption">Hours are estimated: plays without a known duration count as 3.5 minutes.</p>
        </Card>
      </div>
    </div>
  );
}
