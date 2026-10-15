// Date labels that match the Streamlit captions ("01 Mar 2026"). Dates arrive as local
// "YYYY-MM-DD" strings and are formatted without going through Date, so time zones can't shift them.
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/** "2026-03-01" -> "01 Mar 2026" */
export function formatDate(iso: string): string {
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${d} ${MONTHS[Number(m) - 1]} ${y}`;
}

/** "2026-10-12T17:11:10" -> "12 Oct 2026 17:11" */
export function formatDateTime(iso: string): string {
  return `${formatDate(iso)} ${iso.slice(11, 16)}`;
}

export const percent = (x: number) => `${Math.round(x * 100)}%`;
