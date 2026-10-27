// Shared Vega-Lite config: the dark theme for every chart. Colours are the tokens in theme.css.
import type { Config } from "vega-lite";

export const RAIN = "#05A0CF";
export const NIGHT = "#736EE1";
export const BOLT = "#B39105";
// Genre lines only (TypeScript dashboard; see specs/005-prototype-redesign/plan.md).
export const GENRE_COLORS = [RAIN, NIGHT, BOLT, "#C25BB8", "#2FA36B", "#D0662E"];
export const RAIN_RAMP = ["#104F81", "#176396", "#1C77AC", "#238BC1", "#2BA0D6", "#32B6EB", "#51CBF9", "#8BDDFB", "#BDEDFD", "#F0FBFE"];
export const RAIN_DIM = RAIN_RAMP[2]; // unselected bars while a period is selected
export const PAGE = "#141A2A";

const TEXT = "#E2E7F0";
const MUTED = "#A6AEC2";
const GRID = "#283049";
const FONT = '"Lexend", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';

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
  range: { category: [RAIN, NIGHT, BOLT], ramp: RAIN_RAMP },
  bar: { color: RAIN },
  line: { color: RAIN },
};
