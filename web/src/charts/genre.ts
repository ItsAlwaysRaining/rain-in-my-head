// Vega-Lite spec for the Genre page's "Share of tagged plays" chart (openspec/specs/genre-page).
import type { TopLevelSpec } from "vega-lite";
import { capitalize } from "../format";
import { GENRE_COLORS, RAIN } from "./config";

type Point = { start: string; share: number; plays: number };

/** The genre's colour: its Overview line colour when it's in the top 6, else Rain. */
export const genreColor = (colorIndex: number | null) =>
  colorIndex === null ? RAIN : GENRE_COLORS[colorIndex];

/** Area of the genre's share per step, in its colour, with the peak labelled. */
export function shareArea(
  points: Point[],
  grain: string,
  color: string,
): TopLevelSpec {
  const values = points.map((p) => ({
    ...p,
    start: `${p.start.slice(0, 10)}T00:00:00`,
  }));
  return {
    data: { values },
    height: 220,
    encoding: {
      x: {
        field: "start",
        type: "temporal",
        title: null,
        axis: {
          labelOverlap: "greedy",
          format: grain === "week" ? "%d %b" : "%b %Y",
        },
      },
      y: {
        field: "share",
        type: "quantitative",
        title: null,
        axis: { format: "%", tickCount: 3 },
      },
      tooltip: [
        {
          field: "start",
          type: "temporal",
          title: capitalize(grain),
          format: "%d %b %Y",
        },
        { field: "share", type: "quantitative", format: ".1%", title: "Share" },
        { field: "plays", type: "quantitative", title: "Plays" },
      ],
    },
    layer: [
      {
        mark: {
          type: "area",
          line: { color, strokeWidth: 2 },
          color: {
            gradient: "linear",
            x1: 0,
            y1: 1,
            x2: 0,
            y2: 0,
            stops: [
              { offset: 0, color: `${color}00` },
              { offset: 1, color: `${color}80` },
            ],
          },
        },
      },
      // The first highest point only.
      {
        transform: [
          {
            window: [{ op: "row_number", as: "rank" }],
            sort: [{ field: "share", order: "descending" }],
          },
          { filter: "datum.rank === 1" },
        ],
        layer: [
          { mark: { type: "point", filled: true, color, size: 50 } },
          {
            mark: {
              type: "text",
              dy: -12,
              color: "#E2E7F0",
              fontSize: 12,
              fontWeight: 600,
            },
            encoding: {
              text: { field: "share", type: "quantitative", format: ".0%" },
            },
          },
        ],
      },
    ],
  } as TopLevelSpec;
}
