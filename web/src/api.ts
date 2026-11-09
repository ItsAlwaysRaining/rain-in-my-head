// Typed access to the JSON API (src/rain_in_my_head/api.py). Shapes follow
// specs/003-typescript-dashboard/data-model.md; dates are local "YYYY-MM-DD".

// "refused": the hosted site turned the request down (403, "This DJ doesn't take requests.").
// "locked": the hosted site wants a login (403 login_required): there's no session, or it was ended.
// "limited": this person has used up their heavy requests for now (429 rate_limited, specs/012-usage-tracking). The
// message says how long to wait.
export type ApiErrorKind = "no_database" | "unreachable" | "http" | "refused" | "locked" | "limited";

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

/** fetch(), with a network failure reported as the service being down. */
async function reach(url: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(url, init);
  } catch {
    throw new ApiError("unreachable", "The data service isn't running.");
  }
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await reach(url, init);
  if (response.status === 204) return undefined as T;
  // Vite's dev proxy answers 502/504 (or an HTML page) when the API is down.
  if ([502, 503, 504].includes(response.status) || !response.headers.get("content-type")?.includes("json")) {
    const body = await response.json().catch(() => null);
    if (body?.error === "no_database") throw new ApiError("no_database", body.message);
    if (body?.error === "unavailable" || body?.error === "not_configured") throw new ApiError("http", body.message);
    throw new ApiError("unreachable", "The data service isn't running.");
  }
  const body = await response.json();
  if (response.status === 403 && body?.error === "login_required") throw new ApiError("locked", body.message);
  if (response.status === 429 && body?.error === "rate_limited") throw new ApiError("limited", body.message);
  if (response.status === 403 && (body?.error === "refused" || body?.error === "not_available")) throw new ApiError("refused", body.message);
  if (!response.ok) {
    const text = typeof body?.detail === "string" ? body.detail : typeof body?.message === "string" ? body.message : JSON.stringify(body);
    throw new ApiError("http", text);
  }
  return body as T;
}

// ---- Login (specs/011-viewer-access, contracts/api.md) ----------------------------------------------------

/** Who is looking: `local` on your Mac (no login, every page), else logged in or not. */
export interface Me {
  local?: true;
  logged_in?: boolean;
  name?: string;
  tier?: "guest" | "trusted";
  pages?: string[];
}

export const fetchMe = () => getJson<Me>("/api/me");
export const login = (code: string) => sendJson<Me>("POST", "/api/login", { code });
export const logout = () => sendJson<void>("POST", "/api/logout");

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

/** A top artist; `artist_key` opens its Artist page. */
export interface TopArtist extends NamePlays {
  artist_key: string;
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

/** Missing album art, shared with Streamlit (web/public/no-art.svg). */
export const NO_ART = "/no-art.svg";

/** Artists first heard in the selected period, else the range's last month (rain_in_my_head.artist). */
export interface NewArtistList {
  label: string;
  start: string;
  end: string;
  artists: { artist_key: string; name: string; thumb: string | null; plays: number }[];
}

export interface OverviewEmpty extends Partial<OverviewBase> {
  empty: true;
  reason: "no_scrobbles" | "no_plays_in_range";
}

export interface OverviewFull extends OverviewBase {
  empty: false;
  kpis: Kpi[];
  top: { artists: TopArtist[]; tracks: NamePlays[]; albums: NamePlays[] };
  top_per_year: { year: number; artist: string; plays: number; share: number }[];
  heatmap: { weekday: string; hour: number; plays: number }[];
  new_artists: { start: string; count: number }[];
  new_share: number;
  new_artist_list: NewArtistList;
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

// ---- Artist ------------------------------------------------------------------

export interface ArtistSong {
  track_key: string;
  name: string;
  album: string | null;
  thumb: string | null;
  plays: number;
}

export type Artist =
  | { found: false }
  | {
      found: true;
      artist_key: string;
      name: string;
      cover: string | null;
      /** null means all time */
      period: { start: string; end: string; label: string } | null;
      period_plays: number;
      all_time_plays: number;
      songs: ArtistSong[];
    };

export interface ArtistParams {
  artist?: string;
  start?: string;
  end?: string;
}

export const fetchArtist = (p: ArtistParams) => getJson<Artist>("/api/artist", { ...p });

// ---- SQL ---------------------------------------------------------------------

export interface SqlMeta {
  examples: Record<string, string>;
  /** On the hosted site only these examples can run, by name; typed SQL is refused. */
  hosted: boolean;
  schema: { object: string; column: string; type: string }[];
}

export type SqlCell = string | number | null;
export type SqlResult = { columns: string[]; float_columns: number[]; rows: SqlCell[][]; row_count: number } | { error: string };

export const fetchSqlMeta = () => getJson<SqlMeta>("/api/sql/meta");
export const runSql = (sql: string) => sendJson<SqlResult>("POST", "/api/sql", { sql });
export const runSqlExample = (example: string) => sendJson<SqlResult>("POST", "/api/sql", { example });

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
  const response = await reach("/api/playlists/create", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  if (!response.ok || !response.body) {
    const body = await response.json().catch(() => null);
    // The hosted site refuses this on purpose: pass its message on as the refusal it is.
    if (response.status === 403 && body?.error === "refused") throw new ApiError("refused", body.message);
    throw new ApiError("http", typeof body?.detail === "string" ? body.detail : `Request failed (${response.status})`);
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

// ---- Usage reports (specs/012-usage-tracking, contracts/api.md) -------------------------------------------

export type UsageEvent =
  | { event: "open"; visit: string; page: string }
  | { event: "leave"; visit: string; page: string; seconds: number };

/**
 * Tell the site a page was opened or left. Fire and forget: the answer is always 204, a failure is dropped, and
 * nothing here ever reaches the page. A leave goes by `sendBeacon` so it survives the tab closing.
 */
export function sendEvent(body: UsageEvent): void {
  const json = JSON.stringify(body);
  try {
    if (body.event === "leave" && navigator.sendBeacon?.("/api/events", new Blob([json], { type: "application/json" }))) return;
    void fetch("/api/events", { method: "POST", headers: { "content-type": "application/json" }, body: json, keepalive: true }).catch(() => {});
  } catch {
    /* a lost report is fine */
  }
}

// ---- Visitors report (owner's Mac only; specs/012-usage-tracking, contracts/api.md) ------------------------

export type VisitorsEnv = "prod" | "dev";
export type VisitorsRange = "7d" | "30d" | "12m";

export interface VisitorPerson {
  name: string;
  tier: "guest" | "trusted";
  status: "active" | "revoked";
  last_login_at: string | null;
  visits: number;
  seconds: number;
  pages: { page: string; views: number; seconds: number }[];
  features: { feature: string; detail: string | null; uses: number }[];
  limit_hits: number;
}

export interface VisitorEvent {
  kind: "view" | "time" | "feature" | "limit";
  page: string | null;
  feature: string | null;
  detail: string | null;
  seconds: number | null;
  at: string;
}

export interface Visitors {
  env: VisitorsEnv;
  range: VisitorsRange;
  generated_at: string;
  people: VisitorPerson[];
  person: { name: string; events: VisitorEvent[] } | null;
  free_plan: {
    month: string;
    requests: number;
    heavy_page_seconds: number;
    requests_limit: number | null;
    database_bytes: number;
    database_limit_bytes: number | null;
    notes: string[];
  };
}

export const fetchVisitors = (p: { env: VisitorsEnv; range: VisitorsRange; person?: string }) =>
  getJson<Visitors>("/api/visitors", { env: p.env, range: p.range, person: p.person });
