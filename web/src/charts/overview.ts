// Vega-Lite specs for the Overview, first ported from the Altair charts in dashboard/views/overview.py,
// then laid out to match the Figma prototype (specs/005-prototype-redesign). Titles live in the cards
// around the charts, not in the specs.
import type { TopLevelSpec } from "vega-lite";
import type { GenrePanel, InnerGrain, OverTimeRow } from "../api";
import { capitalize } from "../format";
import { GENRE_COLORS, NIGHT, PAGE, RAIN, RAIN_DIM, RAIN_RAMP } from "./config";

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const LISTENER_LABELS = ["<10k", "10k–100k", "100k–1M", "1M–5M", "5M+"];
const BAR = { type: "bar", cornerRadiusEnd: 4, color: RAIN } as const;
const LABEL = { type: "text", color: "#A6AEC2", fontSize: 12 } as const;
// Short month names ("Oct"), as in the prototype; "Oct 2026" style labels crowd a 12-month axis.
const MONTH_AXIS = { format: "%b", labelOverlap: "greedy", tickCount: { interval: "month", step: 1 } } as const;

/** "YYYY-MM-DD" as local midnight; a bare date would be read as UTC and could show the day before. */
const localDates = <T extends { start: string }>(rows: T[]) =>
  rows.map((r) => ({ ...r, start: r.start.length === 10 ? `${r.start}T00:00:00` : r.start }));

export function overTime(rows: OverTimeRow[], measure: "scrobbles" | "hours", grain: string, selected: string | null): TopLevelSpec {
  return {
    data: { values: rows },
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
      y: { field: measure, type: "quantitative", title: null, axis: { format: "~s" } },
      color: { condition: { param: "pick", value: RAIN }, value: RAIN_DIM },
      tooltip: [
        { field: "period", type: "ordinal", title: capitalize(grain) },
        { field: measure, type: "quantitative", format: ",.0f", title: capitalize(measure) },
      ],
    },
  };
}

/** Plays by weekday and hour. Clicking a square selects its weekday and hour. */
export function heatmap(rows: { weekday: string; hour: number; plays: number }[]): TopLevelSpec {
  return {
    data: { values: rows },
    height: 200,
    params: [{ name: "pick", select: { type: "point", fields: ["weekday", "hour"], on: "click" } }],
    mark: { type: "rect", stroke: PAGE, strokeWidth: 2, cornerRadius: 2, cursor: "pointer" },
    encoding: {
      x: { field: "hour", type: "ordinal", title: null, axis: { labelAngle: 0, values: [0, 6, 12, 18, 23], labelExpr: "datum.value + 'h'" } },
      y: { field: "weekday", type: "ordinal", sort: WEEKDAYS, title: null, axis: { labelOverlap: false, domain: false, ticks: false } },
      color: { field: "plays", type: "quantitative", title: "Plays", scale: { range: RAIN_RAMP }, legend: null },
      tooltip: [
        { field: "weekday", type: "ordinal" },
        { field: "hour", type: "ordinal" },
        { field: "plays", type: "quantitative" },
      ],
    },
  };
}

/** New artists per step. Clicking a point selects its start date. */
export function newArtists(rows: { start: string; count: number }[], grain: InnerGrain): TopLevelSpec {
  return {
    data: { values: localDates(rows) },
    height: 200,
    encoding: {
      x: { field: "start", type: "temporal", title: null, axis: MONTH_AXIS },
      y: { field: "count", type: "quantitative", title: null, axis: { tickCount: 4 } },
      tooltip: [
        { field: "start", type: "temporal", title: capitalize(grain) },
        { field: "count", type: "quantitative", title: "New artists" },
      ],
    },
    layer: [
      { mark: { type: "line", color: NIGHT, strokeWidth: 2 } },
      {
        mark: { type: "point", filled: true, color: NIGHT, size: 64, cursor: "pointer" },
        // `nearest` makes a click anywhere near the line pick the closest month.
        params: [{ name: "pick", select: { type: "point", fields: ["start"], on: "click", nearest: true } }],
      },
    ],
  } as TopLevelSpec;
}

/** Every top genre's share of tagged plays, one coloured line each. Clicking a line selects its genre. */
export function genreLines(panels: GenrePanel[], grain: InnerGrain): TopLevelSpec {
  const values = panels.flatMap((p) => localDates(p.points).map((pt) => ({ ...pt, genre: p.genre })));
  return {
    data: { values },
    height: 260,
    encoding: {
      x: { field: "start", type: "temporal", title: null, axis: MONTH_AXIS },
      y: { field: "share", type: "quantitative", title: null, axis: { format: "%", tickCount: 3 } },
      color: { field: "genre", type: "nominal", sort: panels.map((p) => p.genre), scale: { range: GENRE_COLORS }, legend: null },
      tooltip: [
        { field: "genre", type: "nominal", title: "Genre" },
        { field: "start", type: "temporal", title: capitalize(grain) },
        { field: "share", type: "quantitative", format: ".1%", title: "Share" },
        { field: "plays", type: "quantitative", title: "Plays" },
      ],
    },
    layer: [
      { mark: { type: "line", strokeWidth: 2 } },
      // Invisible points with `nearest` make a click anywhere pick the closest genre, not just the thin line.
      {
        mark: { type: "point", opacity: 0, cursor: "pointer" },
        params: [{ name: "pick", select: { type: "point", fields: ["genre"], on: "click", nearest: true } }],
      },
    ],
  } as TopLevelSpec;
}

/** Share of plays per listener band, labelled on the bars. Clicking a bar selects its band. */
export function listenerBuckets(rows: { bucket: string; share: number }[]): TopLevelSpec {
  return {
    data: { values: rows },
    height: 220,
    encoding: {
      x: { field: "bucket", type: "nominal", sort: LISTENER_LABELS, title: null, axis: { labelAngle: 0, ticks: false } },
      y: { field: "share", type: "quantitative", title: null, axis: null },
      tooltip: [
        { field: "bucket", type: "nominal", title: "Last.fm listeners" },
        { field: "share", type: "quantitative", format: ".1%", title: "Share of your plays" },
      ],
    },
    layer: [
      {
        mark: { ...BAR, cursor: "pointer" },
        params: [{ name: "pick", select: { type: "point", fields: ["bucket"], on: "click" } }],
      },
      { mark: { ...LABEL, baseline: "bottom", dy: -4 }, encoding: { text: { field: "share", type: "quantitative", format: ".0%" } } },
    ],
  } as TopLevelSpec;
}
