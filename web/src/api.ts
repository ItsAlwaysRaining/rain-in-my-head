// Typed access to the JSON API (src/listening/api.py). Shapes follow
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
  const url = query.size ? `${path}?${query}` : path;
  let response: Response;
  try {
    response = await fetch(url);
  } catch {
    throw new ApiError("unreachable", "The data service isn't running.");
  }
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
