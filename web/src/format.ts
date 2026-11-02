// Text formatting shared by the pages. Dates arrive as local "YYYY-MM-DD" strings and are formatted
// without going through Date, so time zones can't shift them. Labels match the Streamlit captions.
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-03-01" -> "01 Mar 2026" */
export function formatDate(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${d} ${MONTHS[Number(m) - 1]} ${y}`;
}

/** "2025-01-11T01:50:09" -> "11 Jan 2025" (Streamlit's "D MMM YYYY": no leading zero) */
export function formatDayMonthYear(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${Number(d)} ${MONTHS[Number(m) - 1]} ${y}`;
}

/** "2026-10-12T17:11:10" -> "12 Oct 2026 17:11" */
export function formatDateTime(iso: string): string {
  return `${formatDate(iso)} ${iso.slice(11, 16)}`;
}

/** 12345.6 -> "12,346" */
export const formatCount = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 }).format;

export const percent = (x: number) => `${Math.round(x * 100)}%`;

/** "month" -> "Month" */
export const capitalize = (s: string) => s[0].toUpperCase() + s.slice(1);

/** 4320 -> "1h 12m", 95 -> "1m", 40 -> "40s" (time on site is an estimate, so no finer than this) */
export function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours) return `${hours}h ${String(minutes).padStart(2, "0")}m`;
  return minutes ? `${minutes}m` : `${seconds}s`;
}
