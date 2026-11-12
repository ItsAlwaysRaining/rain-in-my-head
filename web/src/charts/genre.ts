// Vega-Lite spec for the Genre page's "Share of tagged plays" chart (openspec/specs/genre-page).
// Layout follows Figma 263:2051.
import type { TopLevelSpec } from "vega-lite";
import { capitalize } from "../format";
import { GENRE_COLORS, RAIN } from "./config";

type Point = { start: string; share: number; plays: number };

/** The genre's colour: its Overview line colour when it's in the top 6, else Rain. */
export const genreColor = (colorIndex: number | null) => (colorIndex === null ? RAIN : GENRE_COLORS[colorIndex]);

/** Area of the genre's share per step, in its colour, with the peak labelled ("13% in Jul"). */
export function shareArea(points: Point[], grain: string, color: string): TopLevelSpec {
  const values = points.map((p) => ({ ...p, start: `${p.start.slice(0, 10)}T00:00:00` }));
  const stepFormat = grain === "week" ? "%d %b" : "%b";
  return {
    data: { values },
    height: 220,
    encoding: {
      x: { field: "start", type: "temporal", title: null, axis: { labelOverlap: "greedy", format: stepFormat, tickCount: { interval: grain === "week" ? "week" : "month", step: 1 } } },
      y: { field: "share", type: "quantitative", title: null, axis: { format: "%", tickCount: 3 } },
      tooltip: [
        { field: "start", type: "temporal", title: capitalize(grain), format: "%d %b %Y" },
        { field: "share", type: "quantitative", format: ".1%", title: "Share" },
        { field: "plays", type: "quantitative", title: "Plays" },
      ],
    },
    layer: [
      { mark: { type: "area", color, fillOpacity: 0.45, line: { color, strokeWidth: 2 } } },
      // The first highest point only, labelled to its right.
      {
        transform: [
          { window: [{ op: "row_number", as: "rank" }], sort: [{ field: "share", order: "descending" }] },
          { filter: "datum.rank === 1" },
          { calculate: `format(datum.share, ".0%") + " in " + timeFormat(datum.start, "${stepFormat}")`, as: "label" },
        ],
        layer: [
          { mark: { type: "point", filled: true, color, size: 50 } },
          { mark: { type: "text", align: "left", dx: 8, color: "#E2E7F0", fontSize: 12 }, encoding: { text: { field: "label", type: "nominal" } } },
        ],
      },
    ],
  } as TopLevelSpec;
}
