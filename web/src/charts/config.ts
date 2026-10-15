// Shared Vega-Lite config: the dark theme for every chart. Colours are the tokens in theme.css.
import type { Config } from "vega-lite";

export const IRIS = "#7F77D6";
export const TEAL = "#0E9A94";
export const IRIS_RAMP = ["#1D1C34", "#2B284D", "#393567", "#484383", "#58519E", "#6B63BC", "#7F78D6", "#948FE8", "#AAA8F1", "#C2C1F7"];
export const IRIS_DIM = IRIS_RAMP[2]; // unselected bars while a period is selected
export const PAGE = "#18181C";

const TEXT = "#E4E4EA";
const MUTED = "#AAAAB4";
const GRID = "#2E2E36";
const FONT = '"Source Sans 3", "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

export const chartConfig: Config = {
  background: "transparent",
  font: FONT,
  padding: { left: 0, right: 0, top: 4, bottom: 0 },
  view: { stroke: null },
  title: { color: TEXT, fontSize: 16, fontWeight: 600, anchor: "start", offset: 12, font: FONT },
  axis: {
    labelColor: MUTED,
    titleColor: MUTED,
    labelFontSize: 12,
    titleFontSize: 12,
    titleFontWeight: 400,
    gridColor: GRID,
    domainColor: GRID,
    tickColor: GRID,
    labelFont: FONT,
    titleFont: FONT,
  },
  axisX: { grid: false },
  legend: { labelColor: MUTED, titleColor: MUTED, labelFontSize: 12, titleFontSize: 12, titleFontWeight: 400 },
  range: { category: [IRIS, TEAL, "#CD6153"], ramp: IRIS_RAMP },
  bar: { color: IRIS },
  line: { color: IRIS },
};
