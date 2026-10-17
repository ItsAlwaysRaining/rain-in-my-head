// Vega-Lite specs for the Overview, ported one to one from the Altair charts in
// dashboard/views/overview.py so the two dashboards start out looking alike.
import type { TopLevelSpec } from "vega-lite";
import type { GenrePanel, InnerGrain, NamePlays, OverTimeRow } from "../api";
import { RAIN, RAIN_DIM, RAIN_RAMP, PAGE, NIGHT } from "./config";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const LISTENER_LABELS = ["<10k", "10k–100k", "100k–1M", "1M–5M", "5M+"];
const BAR = { type: "bar", cornerRadiusEnd: 4, color: RAIN } as const;

const capitalize = (s: string) => s[0].toUpperCase() + s.slice(1);

/** "YYYY-MM-DD" as local midnight; a bare date would be read as UTC and could show the day before. */
export const localDates = <T extends { start: string }>(rows: T[]) =>
  rows.map((r) => ({ ...r, start: r.start.length === 10 ? `${r.start}T00:00:00` : r.start }));

export function overTime(rows: OverTimeRow[], measure: "scrobbles" | "hours", grain: string, selected: string | null): TopLevelSpec {
  return {
    data: { values: rows },
    title: `${capitalize(measure)} per ${grain}`,
    height: 260,
    params: [
      {
        name: "pick",
        select: { type: "point", fields: ["period"], on: "click" },
        ...(selected ? { value: [{ period: selected }] } : {}),
      },
    ],
    mark: { type: "bar", cornerRadiusTopLeft: 4, cornerRadiusTopRight: 4, cursor: "pointer" },
    encoding: {
      // Ordinal labels keep each bar centered under its own period.
      x: { field: "period", type: "ordinal", sort: null, title: null, scale: { paddingInner: 0.2 }, axis: { labelAngle: 0, labelOverlap: "greedy" } },
      y: { field: measure, type: "quantitative", title: capitalize(measure) },
      color: { condition: { param: "pick", value: RAIN }, value: RAIN_DIM },
      tooltip: [
        { field: "period", type: "ordinal", title: capitalize(grain) },
        { field: measure, type: "quantitative", format: ",.0f" },
      ],
    },
  };
}

export function topBar(rows: NamePlays[], title: string, label: string): TopLevelSpec {
  return {
    data: { values: rows },
    title,
    height: Math.max(200, 26 * rows.length),
    mark: BAR,
    encoding: {
      x: { field: "plays", type: "quantitative", title: "Plays" },
      y: { field: "name", type: "nominal", sort: "-x", title: null, axis: { labelLimit: 320, labelOverlap: false } },
      tooltip: [
        { field: "name", type: "nominal", title: label },
        { field: "plays", type: "quantitative" },
      ],
    },
  };
}

export function heatmap(rows: { weekday: string; hour: number; plays: number }[]): TopLevelSpec {
  return {
    data: { values: rows },
    title: "When you listen",
    height: 260,
    mark: { type: "rect", stroke: PAGE, strokeWidth: 2, cornerRadius: 2 },
    encoding: {
      x: { field: "hour", type: "ordinal", title: "Hour of day" },
      y: { field: "weekday", type: "ordinal", sort: WEEKDAYS, title: null, axis: { labelOverlap: false } },
      color: { field: "plays", type: "quantitative", title: "Plays", scale: { range: RAIN_RAMP } },
      tooltip: [
        { field: "weekday", type: "ordinal" },
        { field: "hour", type: "ordinal" },
        { field: "plays", type: "quantitative" },
      ],
    },
  };
}

export function newArtists(rows: { start: string; count: number }[], grain: InnerGrain): TopLevelSpec {
  return {
    data: { values: localDates(rows) },
    title: `New artists per ${grain}`,
    height: 260,
    mark: { type: "line", color: NIGHT, strokeWidth: 2, point: { color: NIGHT, size: 64 } },
    encoding: {
      x: { field: "start", type: "temporal", title: null },
      y: { field: "count", type: "quantitative", title: "Artists heard for the first time" },
      tooltip: [
        { field: "start", type: "temporal", title: capitalize(grain) },
        { field: "count", type: "quantitative", title: "new_artists" },
      ],
    },
  };
}

export function genrePanel(panel: GenrePanel, yMax: number, grain: InnerGrain): TopLevelSpec {
  const encoding = {
    x: { field: "start", type: "temporal", title: null, axis: { tickCount: 4, grid: false } },
    y: { field: "share", type: "quantitative", title: null, scale: { domain: [0, yMax] }, axis: { format: "%", tickCount: 3 } },
    tooltip: [
      { field: "start", type: "temporal", title: capitalize(grain) },
      { field: "share", type: "quantitative", format: ".1%", title: "Share" },
      { field: "plays", type: "quantitative", title: "Plays" },
    ],
  } as const;
  return {
    data: { values: localDates(panel.points) },
    title: { text: panel.genre, anchor: "start", fontSize: 13 },
    height: 140,
    encoding,
    layer: [
      { mark: { type: "area", line: { strokeWidth: 2, color: RAIN }, color: RAIN, opacity: 0.35 } },
      // Invisible points with `nearest` make a click anywhere in the panel select, not just on the thin area.
      {
        mark: { type: "point", opacity: 0, cursor: "pointer" },
        params: [{ name: "pick", select: { type: "point", on: "click", nearest: true } }],
      },
    ],
  } as TopLevelSpec;
}

export function listenerBuckets(rows: { bucket: string; share: number }[]): TopLevelSpec {
  return {
    data: { values: rows },
    title: "Mainstream vs. niche (artist's Last.fm listeners)",
    height: 300,
    mark: BAR,
    encoding: {
      x: { field: "bucket", type: "nominal", sort: LISTENER_LABELS, title: "Artist's global listeners", axis: { labelAngle: 0 } },
      y: { field: "share", type: "quantitative", title: "Share of your plays", axis: { format: "%" } },
      tooltip: [
        { field: "bucket", type: "nominal" },
        { field: "share", type: "quantitative", format: ".1%" },
      ],
    },
  };
}
