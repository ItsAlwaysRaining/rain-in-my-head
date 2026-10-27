// Playlist Generator: the TypeScript twin of dashboard/views/playlists.py. The form has the same controls,
// defaults and help text; the preview and the Spotify matching come from rain_in_my_head.playlist
// through the API, so both apps list the same tracks. Laid out as in the Figma prototype, with two more
// tabs, AI (#32) and SQL (#31), that show what's coming.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { Fragment, useEffect, useState, type ReactNode } from "react";
import { useSearchParams } from "react-router";
import {
  createPlaylist, fetchPlaylistsMeta, fetchSpotifyStatus, previewPlaylist,
  type BingeOrder, type CreateEvent, type PlaylistKind, type PlaylistPreview, type PlaylistRequest, type PlaylistsMeta,
} from "../api";
import { DataTable, type Column } from "../components/DataTable";
import { ComingSoon } from "../components/ComingSoon";
import { Chips, Field, RangeSlider, Slider } from "../components/Form";
import { Button, ChipGroup, ErrorState, Loading, Notice, PageHeader, Tabs } from "../components/ui";
import { formatDayMonthYear } from "../format";
import styles from "./Playlists.module.css";

const KINDS: Record<PlaylistKind, string> = { slot: "Time Slot", discoveries: "Discovery", binges: "Binge" };
type Tab = PlaylistKind | "ai" | "sql";
const TABS: Tab[] = ["slot", "discoveries", "binges", "ai", "sql"];

/** The **bold** and *italic* that the shared notices use. */
function inline(text: string): ReactNode {
  return text.split(/(\*\*[^*]+\*\*|\*[^*]+\*)/).map((part, i) =>
    part.startsWith("**") ? <strong key={i}>{part.slice(2, -2)}</strong> : part.startsWith("*") ? <em key={i}>{part.slice(1, -1)}</em> : <Fragment key={i}>{part}</Fragment>,
  );
}

function useDebounced<T>(value: T, ms = 250): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), ms);
    return () => clearTimeout(t);
  }, [value, ms]);
  return debounced;
}

/** The form's starting values: the Streamlit defaults. */
function defaults(meta: PlaylistsMeta): Record<PlaylistKind, PlaylistRequest> {
  const first = Number(meta.first.slice(0, 4));
  const last = Number(meta.last.slice(0, 4));
  return {
    slot: { kind: "slot", days: ["Friday"], hours: [17, 19], span: "All time", since: meta.first, until: meta.last, size: 50, min_plays: 3 },
    discoveries: { kind: "discoveries", year: last - 1 >= first ? last - 1 : last, rank_by: "year", order: "Ranking", size: 50, min_plays: 2 },
    binges: { kind: "binges", years: [first, last], window_days: 7, min_plays: 8, size: 50, binge_order: "oldest" },
  };
}

export default function Playlists() {
  const meta = useQuery({ queryKey: ["playlists-meta"], queryFn: fetchPlaylistsMeta });
  const [params, setParams] = useSearchParams();
  const tab = TABS.includes(params.get("type") as Tab) ? (params.get("type") as Tab) : "slot";
  const form = (kind: PlaylistKind) =>
    meta.error ? <ErrorState error={meta.error} /> : !meta.data ? <Loading /> : <PlaylistsForm key={kind} kind={kind} meta={meta.data} />;

  return (
    <>
      <PageHeader title="Create a playlist">Pick a type, set the filters, then create it on Spotify.</PageHeader>
      <Tabs<Tab>
        active={tab}
        onChange={(type) => setParams({ type }, { replace: true })}
        tabs={[
          ...(Object.keys(KINDS) as PlaylistKind[]).map((k) => ({ key: k, label: KINDS[k], content: form(k) })),
          {
            key: "ai",
            label: "AI",
            content: (
              <ComingSoon title="Describe a playlist in your own words" issue={32}>
                Ask for a mood, a time or a memory, like “songs I binged at the end of 2023 but haven't played since”, and get a playlist built only from your
                own listening history, with a reason for every track.
              </ComingSoon>
            ),
          },
          {
            key: "sql",
            label: "SQL",
            content: (
              <ComingSoon title="Build a playlist from a query" issue={31}>
                Paste a query from the Analyst page that returns <code>artist</code> and <code>track</code> columns, preview the songs, and create the playlist on
                Spotify.
              </ComingSoon>
            ),
          },
        ]}
      />
    </>
  );
}

/** Each type keeps its own form while you switch tabs (the forms live in this module, not the tab). */
const saved: Partial<Record<PlaylistKind, PlaylistRequest>> = {};

function PlaylistsForm({ kind, meta }: { kind: PlaylistKind; meta: PlaylistsMeta }) {
  const [form, setForm] = useState(() => saved[kind] ?? defaults(meta)[kind]);
  const set = (changes: Partial<PlaylistRequest>) =>
    setForm((f) => {
      const next = { ...f, ...changes };
      saved[kind] = next;
      return next;
    });

  const request = useDebounced(form);
  const preview = useQuery({
    queryKey: ["playlist-preview", request],
    queryFn: () => previewPlaylist(request),
    placeholderData: keepPreviousData,
  });

  return (
    <div className={styles.page}>
      {kind === "slot" && <SlotForm meta={meta} form={form} set={set} />}
      {kind === "discoveries" && <DiscoveriesForm meta={meta} form={form} set={set} />}
      {kind === "binges" && <BingesForm meta={meta} form={form} set={set} />}

      {preview.error ? (
        <ErrorState error={preview.error} />
      ) : !preview.data || preview.data.title === undefined ? (
        <Loading text={kind === "binges" ? "Finding binges…" : undefined} />
      ) : (
        <div className={preview.isFetching ? styles.stale : undefined}>
          <Preview data={preview.data} />
          {!preview.data.warning && <CreateOnSpotify request={request} preview={preview.data} />}
        </div>
      )}
    </div>
  );
}

type FormProps = { meta: PlaylistsMeta; form: PlaylistRequest; set: (changes: Partial<PlaylistRequest>) => void };

const hour = (h: number) => `${h}:00`;
const songs = (n: number) => `${n} songs`;

function SlotForm({ meta, form, set }: FormProps) {
  return (
    <>
      <p className={styles.intro}>
        Tracks you play <em>more than usual</em> in a time slot, compared with your listening overall. Tracks with only a few plays are weighted down so one-offs don't
        dominate.
      </p>
      <div className={styles.columns}>
        <Chips label="Day of week" options={meta.weekdays} value={form.days!} onChange={(days) => set({ days })} />
        <div className={styles.stack}>
          <ChipGroup label="Listening from" options={meta.spans} value={form.span!} onChange={(span) => set({ span })} />
          {form.span === "Custom" && (
            <Field label="Dates">
              <div className={styles.dates}>
                <input type="date" className={styles.input} value={form.since} min={meta.first} max={form.until} onChange={(e) => e.target.value && set({ since: e.target.value })} />
                <span>–</span>
                <input type="date" className={styles.input} value={form.until} min={form.since} max={meta.last} onChange={(e) => e.target.value && set({ until: e.target.value })} />
              </div>
            </Field>
          )}
        </div>
      </div>
      <div className={styles.sliders}>
        <RangeSlider label="Hours (local time)" help="End is exclusive: 17–19 means 5:00pm to 6:59pm." min={0} max={24} value={form.hours!} format={hour} onChange={(hours) => set({ hours })} />
        <Slider label="Min. plays in the slot" help="Higher = only tracks you've played in this slot repeatedly." min={1} max={10} value={form.min_plays} onChange={(min_plays) => set({ min_plays })} />
        <Slider label="Playlist length" min={10} max={100} step={5} value={form.size} format={songs} onChange={(size) => set({ size })} />
      </div>
    </>
  );
}

function DiscoveriesForm({ meta, form, set }: FormProps) {
  const first = Number(meta.first.slice(0, 4));
  const last = Number(meta.last.slice(0, 4));
  const years = Array.from({ length: last - first + 1 }, (_, i) => last - i);
  return (
    <>
      <p className={styles.intro}>Songs you heard for the first time in a given year.</p>
      <div className={styles.columns}>
        <div className={styles.stack}>
          <Field label="Year">
            <select className={styles.input} value={form.year} onChange={(e) => set({ year: Number(e.target.value) })}>
              {years.map((y) => (
                <option key={y}>{y}</option>
              ))}
            </select>
          </Field>
          <ChipGroup label="Pick the songs" options={["year", "ever"] as const} format={(r) => meta.rank_by[r]} value={form.rank_by!} onChange={(rank_by) => set({ rank_by })} />
        </div>
        <ChipGroup label="Playlist order" options={meta.discovery_orders} value={form.order!} onChange={(order) => set({ order })} />
      </div>
      <div className={styles.sliders}>
        <Slider label="Min. plays" help="Drop songs you only heard once." min={1} max={10} value={form.min_plays} onChange={(min_plays) => set({ min_plays })} />
        <Slider label="Playlist length" min={10} max={100} step={5} value={form.size} format={songs} onChange={(size) => set({ size })} />
      </div>
    </>
  );
}

function BingesForm({ meta, form, set }: FormProps) {
  const windows = meta.windows.map(String);
  return (
    <>
      <p className={styles.intro}>Songs you played on repeat in a short burst. Every binge is listed with its dates.</p>
      <div className={styles.columns}>
        <ChipGroup label="Binge window" options={windows} format={(d) => (d === "1" ? "1 day" : `${d} days`)} value={String(form.window_days)} onChange={(d) => set({ window_days: Number(d) })} />
        <ChipGroup
          label="Playlist order"
          options={Object.keys(meta.binge_orders) as BingeOrder[]}
          format={(o) => meta.binge_orders[o]}
          value={form.binge_order!}
          onChange={(binge_order) => set({ binge_order })}
        />
      </div>
      <div className={styles.sliders}>
        <RangeSlider label="Years" min={Number(meta.first.slice(0, 4))} max={Number(meta.last.slice(0, 4))} value={form.years!} onChange={(years) => set({ years })} />
        <Slider label="Min. plays in the window" help="A binge = at least this many plays of one song within the window." min={3} max={30} value={form.min_plays} onChange={(min_plays) => set({ min_plays })} />
        <Slider label="Playlist length" min={10} max={100} step={5} value={form.size} format={songs} onChange={(size) => set({ size })} />
      </div>
    </>
  );
}

type Row = Record<string, string | number | null>;

function Preview({ data }: { data: PlaylistPreview }) {
  const columns: Column<Row>[] = (data.columns ?? []).map((c) => ({
    key: c.key,
    label: c.label,
    help: c.help ?? undefined,
    kind: c.kind === "number" ? "number" : undefined,
    align: c.kind === "lift" ? "right" : undefined,
    render:
      c.kind === "lift"
        ? (r) => (r[c.key] === null ? "" : `${(r[c.key] as number).toFixed(1)}×`)
        : c.kind === "date"
          ? (r) => (r[c.key] === null ? "" : formatDayMonthYear(r[c.key] as string))
          : undefined,
  }));
  return (
    <div className={styles.stack}>
      {data.note && <Notice>{inline(data.note)}</Notice>}
      <div>
        <h2>Results</h2>
        {!data.warning && <p className={styles.intro}>{data.title ? `${data.title} · ${data.caption}` : data.caption}</p>}
      </div>
      {data.warning ? (
        <Notice tone="warning">{data.warning}</Notice>
      ) : (
        <>
          {data.info && <Notice>{inline(data.info)}</Notice>}
          <DataTable rows={data.rows!} columns={columns} maxHeight={420} />
        </>
      )}
    </div>
  );
}

type CreateState =
  | { status: "idle" }
  | { status: "running"; fraction: number; message: string }
  | { status: "done"; event: Extract<CreateEvent, { event: "done" }> }
  | { status: "error"; message: string };

function CreateOnSpotify({ request, preview }: { request: PlaylistRequest; preview: PlaylistPreview }) {
  const spotify = useQuery({ queryKey: ["spotify-status"], queryFn: fetchSpotifyStatus });
  const [name, setName] = useState(preview.name!);
  const [isPublic, setPublic] = useState(false);
  const [state, setState] = useState<CreateState>({ status: "idle" });

  // A new default name (another slot, year or span) replaces the typed one, as Streamlit's keyed input does.
  useEffect(() => setName(preview.name!), [preview.name]);

  const create = () => {
    setState({ status: "running", fraction: 0, message: "Matching tracks on Spotify…" });
    createPlaylist({ ...request, name, public: isPublic }, (e) => {
      if (e.event === "progress") setState({ status: "running", fraction: e.fraction, message: e.message });
      else if (e.event === "done") setState({ status: "done", event: e });
      else setState({ status: "error", message: e.message });
    }).catch((e: Error) => setState({ status: "error", message: e.message }));
  };

  return (
    <div className={`${styles.stack} ${styles.section}`}>
      {spotify.error ? (
        <ErrorState error={spotify.error} />
      ) : !spotify.data ? null : !spotify.data.connected ? (
        <Notice>
          Connect Spotify once from the terminal: add <code>SPOTIFY_CLIENT_ID</code> to <code>.env</code>, then run <code>uv run rain-in-my-head spotify-login</code>. See the
          README for creating the Spotify app.
        </Notice>
      ) : (
        <>
          <div className={styles.createBar}>
            <div className={styles.createTitle}>
              <strong>{preview.title}</strong>
              <span className="caption">{preview.rows?.length ?? 0} songs</span>
            </div>
            <input className={styles.input} aria-label="Playlist name" value={name} onChange={(e) => setName(e.target.value)} />
            <label className={styles.toggle}>
              <input type="checkbox" role="switch" checked={isPublic} onChange={(e) => setPublic(e.target.checked)} />
              Public playlist
            </label>
            <Button variant="primary" onClick={create} disabled={state.status === "running" || !name.trim()}>
              Create on Spotify
            </Button>
          </div>
          {state.status === "running" && (
            <div className={styles.progress} role="progressbar" aria-valuenow={Math.round(state.fraction * 100)} aria-valuemin={0} aria-valuemax={100}>
              <span className="caption">{state.message}</span>
              <div className={styles.bar}>
                <span style={{ width: `${state.fraction * 100}%` }} />
              </div>
            </div>
          )}
          {state.status === "error" && <Notice tone="error">{state.message}</Notice>}
          {state.status === "done" && (
            <>
              <Notice tone="success">
                Created <strong>{state.event.name}</strong> with {state.event.count} tracks:{" "}
                <a href={state.event.url} target="_blank" rel="noreferrer">
                  open in Spotify
                </a>
              </Notice>
              {state.event.misses.length > 0 && (
                <details className={styles.expander}>
                  <summary>{state.event.misses.length} tracks had no Spotify match and were skipped</summary>
                  <DataTable
                    rows={state.event.misses}
                    columns={[
                      { key: "artist", label: "artist" },
                      { key: "track", label: "track" },
                    ]}
                    maxHeight={300}
                  />
                </details>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
