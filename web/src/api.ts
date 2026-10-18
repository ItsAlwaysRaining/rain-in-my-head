// Typed access to the JSON API (src/rain_in_my_head/api.py). Shapes follow
// specs/003-typescript-dashboard/data-model.md; dates are local "YYYY-MM-DD".

export type ApiErrorKind = "no_database" | "unreachable" | "http";

export class ApiError extends Error {
  constructor(
    public kind: ApiErrorKind,
    message: string,
  ) {
    super(message);
  }
}

export async function getJson<T>(path: string, params: Record<string, string | undefined> = {}): Promise<T> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value) query.set(key, value);
  return request<T>(query.size ? `${path}?${query}` : path);
}

/** POST/PUT/DELETE with an optional JSON body. A 204 resolves to undefined. */
export function sendJson<T>(method: "POST" | "PUT" | "DELETE", path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method,
    headers: body === undefined ? undefined : { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch {
    throw new ApiError("unreachable", "The data service isn't running.");
  }
  if (response.status === 204) return undefined as T;
  // Vite's dev proxy answers 502/504 (or an HTML page) when the API is down.
  if ([502, 503, 504].includes(response.status) || !response.headers.get("content-type")?.includes("json")) {
    const body = await response.json().catch(() => null);
    if (body?.error === "no_database") throw new ApiError("no_database", body.message);
    throw new ApiError("unreachable", "The data service isn't running.");
  }
  const body = await response.json();
  if (!response.ok) throw new ApiError("http", typeof body?.detail === "string" ? body.detail : JSON.stringify(body));
  return body as T;
}

// ---- Overview ----------------------------------------------------------------

export type Preset = "last30" | "last12m" | "ytd" | "all" | "custom";
export type Grain = "week" | "month" | "year";
export type InnerGrain = Grain | "day";

export interface OverviewRange {
  start: string;
  end: string;
  base_start: string;
  base_end: string;
  data_first: string;
  data_last: string;
  data_through: string;
}

export interface OverTimeRow {
  period: string;
  start: string;
  scrobbles: number;
  hours: number;
}

export interface Kpi {
  label: string;
  value: number;
  delta: number | null;
}

export interface NamePlays {
  name: string;
  plays: number;
}

export interface GenrePanel {
  genre: string;
  points: { start: string; share: number; plays: number }[];
}

interface OverviewBase {
  range: OverviewRange;
  grain: Grain;
  selected: { label: string; start: string; end: string } | null;
  inner_grain: InnerGrain;
  over_time: OverTimeRow[];
}

export interface OverviewEmpty extends Partial<OverviewBase> {
  empty: true;
  reason: "no_scrobbles" | "no_plays_in_range";
}

export interface OverviewFull extends OverviewBase {
  empty: false;
  kpis: Kpi[];
  top: { artists: NamePlays[]; tracks: NamePlays[]; albums: NamePlays[] };
  top_per_year: { year: number; artist: string; plays: number; share: number }[];
  heatmap: { weekday: string; hour: number; plays: number }[];
  new_artists: { start: string; count: number }[];
  new_share: number;
  genres: { y_max: number; panels: GenrePanel[] } | null;
  listener_buckets: { bucket: string; share: number }[] | null;
  loved: { artist: string; track: string; plays: number }[];
  coverage: { check: string; coverage: number }[];
}

export type Overview = OverviewEmpty | OverviewFull;

export interface OverviewParams {
  preset: Preset;
  start?: string;
  end?: string;
  grain: Grain;
  period?: string;
}

export const fetchOverview = (p: OverviewParams) =>
  getJson<Overview>("/api/overview", { ...p, start: p.preset === "custom" ? p.start : undefined, end: p.preset === "custom" ? p.end : undefined });

// ---- Genre -------------------------------------------------------------------

export interface GenreArtist {
  artist_key: string;
  name: string;
  art: string | null;
  thumb: string | null;
  plays: number;
}

export type Genre =
  | { genres: []; genre: null; reason: "no_tags" }
  | { genres: string[]; genre: string; range_label: string; plays: number; artists: GenreArtist[] };

export interface GenreSongs {
  artist: { name: string; art: string | null; plays: number };
  songs: { track_key: string; name: string; album: string | null; art: string | null; thumb: string | null; plays: number }[];
}

export interface GenreParams {
  genre?: string;
  start?: string;
  end?: string;
}

export const fetchGenre = (p: GenreParams) => getJson<Genre>("/api/genre", { ...p });
export const fetchGenreSongs = (p: GenreParams & { artist_key: string }) => getJson<GenreSongs>("/api/genre/songs", { ...p });

// ---- SQL ---------------------------------------------------------------------

export interface SqlMeta {
  examples: Record<string, string>;
  schema: { object: string; column: string; type: string }[];
}

export type SqlCell = string | number | null;
export type SqlResult = { columns: string[]; float_columns: number[]; rows: SqlCell[][]; row_count: number } | { error: string };

export const fetchSqlMeta = () => getJson<SqlMeta>("/api/sql/meta");
export const runSql = (sql: string) => sendJson<SqlResult>("POST", "/api/sql", { sql });

// ---- Schema ------------------------------------------------------------------

export interface SchemaColumn {
  name: string;
  type: string;
  required: boolean;
  key: boolean;
  link: boolean;
  meaning: string | null;
}

export interface SchemaObject {
  name: string;
  kind: "table" | "view";
  title: string;
  source: string | null;
  description: string | null;
  rows: number | null;
  columns: SchemaColumn[];
}

export type Point = { x: number; y: number };
export type Positions = Record<string, Point>;

export interface SchemaData {
  objects: SchemaObject[];
  links: { from: [string, string]; to: [string, string]; label: string }[];
  lineage: [string, string][];
  positions: Positions;
  defaults: Positions;
  size: { w: number; h: number };
}

export const fetchSchema = () => getJson<SchemaData>("/api/schema");
export const saveSchemaLayout = (positions: Positions) => sendJson<void>("PUT", "/api/schema/layout", { positions });
export const resetSchemaLayout = () => sendJson<{ positions: Positions }>("DELETE", "/api/schema/layout");

// ---- Playlists ---------------------------------------------------------------

export interface PlaylistsMeta {
  first: string;
  last: string;
  weekdays: string[];
  spans: string[];
  rank_by: Record<"year" | "ever", string>;
  discovery_orders: string[];
  windows: number[];
  binge_orders: Record<BingeOrder, string>;
}

export type PlaylistKind = "slot" | "discoveries" | "binges";
export type BingeOrder = "oldest" | "newest" | "biggest";

export interface PlaylistRequest {
  kind: PlaylistKind;
  size: number;
  min_plays: number;
  days?: string[];
  hours?: [number, number];
  span?: string;
  since?: string;
  until?: string;
  year?: number;
  rank_by?: "year" | "ever";
  order?: string;
  years?: [number, number];
  window_days?: number;
  binge_order?: BingeOrder;
}

export interface PreviewColumn {
  key: string;
  label: string;
  kind: "text" | "number" | "lift" | "date";
  help: string | null;
}

export interface PlaylistPreview {
  title: string | null;
  note: string | null;
  warning: string | null;
  info?: string | null;
  caption?: string;
  name?: string;
  description?: string;
  columns?: PreviewColumn[];
  rows?: Record<string, string | number | null>[];
  candidate_count?: number;
}

export type CreateEvent =
  | { event: "progress"; fraction: number; message: string }
  | { event: "done"; url: string; name: string; count: number; misses: { artist: string; track: string }[] }
  | { event: "error"; message: string };

export const fetchPlaylistsMeta = () => getJson<PlaylistsMeta>("/api/playlists/meta");
export const fetchSpotifyStatus = () => getJson<{ connected: boolean }>("/api/playlists/spotify");
export const previewPlaylist = (body: PlaylistRequest) => sendJson<PlaylistPreview>("POST", "/api/playlists/preview", body);

/** Creates the playlist, calling `onEvent` for each server-sent event until `done` or `error`. */
export async function createPlaylist(body: PlaylistRequest & { name: string; public: boolean }, onEvent: (e: CreateEvent) => void) {
  let response: Response;
  try {
    response = await fetch("/api/playlists/create", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  } catch {
    throw new ApiError("unreachable", "The data service isn't running.");
  }
  if (!response.ok || !response.body) {
    const detail = await response.json().then((b) => b?.detail, () => null);
    throw new ApiError("http", typeof detail === "string" ? detail : `Request failed (${response.status})`);
  }
  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    let end: number;
    while ((end = buffer.indexOf("\n\n")) >= 0) {
      const block = buffer.slice(0, end);
      buffer = buffer.slice(end + 2);
      const event = /^event: (.*)$/m.exec(block)?.[1];
      const data = /^data: (.*)$/m.exec(block)?.[1];
      if (event && data) onEvent({ event, ...JSON.parse(data) } as CreateEvent);
    }
  }
}
