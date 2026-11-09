// Artist page charts. Colours come from the tokens in config.ts, like the Overview charts.
import type { TopLevelSpec } from "vega-lite";
import type { MonthPlays } from "../api";
import { formatDate } from "../format";
import { RAIN, RAIN_DIM } from "./config";

/** "2026-03" -> "Mar 2026" */
export const monthLabel = (month: string) => formatDate(`${month}-01`).slice(3);

/**
 * Plays per month as a line with a point per month. Clicking a point selects that month (param "pick",
 * field "month"); the selected point is full colour and the rest are dimmed, as the Overview bars are.
 */
export function playsPerMonth(rows: MonthPlays[], selected: string | null): TopLevelSpec {
  const values = rows.map((r) => ({ month: r.month, date: `${r.month}-01`, label: monthLabel(r.month), plays: r.plays }));
  return {
    data: { values },
    height: 220,
    encoding: {
      // A time scale spaces the labels for long histories; zero months still get a point.
      x: { field: "date", type: "temporal", timeUnit: "yearmonth", title: null, axis: { labelAngle: 0, format: "%b %Y", labelOverlap: "greedy" } },
      y: { field: "plays", type: "quantitative", title: null, axis: { format: "~s", tickMinStep: 1 } },
      tooltip: [
        { field: "label", type: "nominal", title: "Month" },
        { field: "plays", type: "quantitative", format: ",.0f", title: "Plays" },
      ],
    },
    layer: [
      { mark: { type: "line", color: RAIN, strokeWidth: 2 } },
      {
        // The selection lives on the point layer only: declaring it at the top level duplicates the signal per layer.
        mark: { type: "point", filled: true, size: 70, cursor: "pointer" },
        params: [
          {
            name: "pick",
            select: { type: "point", fields: ["month"], on: "click" },
            ...(selected ? { value: [{ month: selected }] } : {}),
          },
        ],
        encoding: { color: { condition: { param: "pick", value: RAIN }, value: RAIN_DIM } },
      },
    ],
  } as TopLevelSpec;
}
