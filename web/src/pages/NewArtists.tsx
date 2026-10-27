// New artists: the artists first heard in one month, opened from the Overview's "New artists per
// month" chart with ?month=YYYY-MM. No endpoint of its own: /api/overview over all time by month gives
// both the months to pick from (over_time) and the list (new_artist_list, rain_in_my_head.artist), so
// the numbers match the Overview. Streamlit shows this list inline on its Overview instead.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { fetchOverview, NO_ART, type OverviewFull } from "../api";
import { artistColumns } from "../components/columns";
import { DataTable } from "../components/DataTable";
import { BackLink, ErrorState, Loading, Notice, PageHeader } from "../components/ui";
import { formatCount } from "../format";
import styles from "./NewArtists.module.css";

const ALL_MONTHS = { preset: "all", grain: "month" } as const;

export default function NewArtists() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();

  // Without a period the list is the latest month's, and over_time lists every month.
  const months = useQuery({ queryKey: ["overview", "all", undefined, undefined, "month", undefined], queryFn: () => fetchOverview(ALL_MONTHS) });
  const all = months.data && !months.data.empty ? (months.data as OverviewFull) : null;
  const options = useMemo(() => (all ? [...all.over_time].reverse() : []), [all]);
  // An unknown or missing month falls back to the latest one.
  const picked = options.find((o) => o.start.startsWith(params.get("month") ?? "")) ?? options[0];
  const isLatest = picked !== undefined && picked === options[0];

  const month = useQuery({
    queryKey: ["overview", "all", undefined, undefined, "month", picked?.period],
    queryFn: () => fetchOverview({ ...ALL_MONTHS, period: picked!.period }),
    enabled: picked !== undefined && !isLatest,
    placeholderData: keepPreviousData,
  });
  const data = isLatest ? all : month.data && !month.data.empty ? (month.data as OverviewFull) : null;
  const list = data?.new_artist_list;
  const rows = useMemo(() => list?.artists.map((a) => ({ ...a, thumb: a.thumb ?? NO_ART })) ?? [], [list]);

  const error = months.error ?? month.error;
  return (
    <>
      <BackLink />
      <PageHeader title={`New artists${list ? ` · ${list.label}` : ""}`}>
        {list ? `${formatCount(rows.length)} artists you played for the first time in ${list.label}` : " "}
      </PageHeader>

      {error ? (
        <ErrorState error={error} />
      ) : months.data?.empty ? (
        <Notice>The database has no scrobbles yet.</Notice>
      ) : !all || !picked ? (
        <Loading />
      ) : (
        <>
          <label className={styles.select}>
            Month
            <select value={picked.start} onChange={(e) => setParams({ month: e.target.value.slice(0, 7) })}>
              {options.map((o) => (
                <option key={o.start} value={o.start}>
                  {o.period}
                </option>
              ))}
            </select>
          </label>

          <section className={`${styles.list} ${month.isFetching ? styles.loading : ""}`}>
            <h3>Artists</h3>
            {!list ? (
              <Loading />
            ) : rows.length === 0 ? (
              <Notice>No new artists in {list.label}.</Notice>
            ) : (
              <>
                <DataTable
                  rows={rows}
                  columns={artistColumns()}
                  maxHeight={640}
                  onRowClick={(a) => navigate(`/dashboards/artist?${new URLSearchParams({ artist: a.artist_key, start: list.start, end: list.end })}`)}
                />
                <p className="caption">
                  Showing {formatCount(rows.length)} artists, most played first. Click an artist to see your songs by them.
                </p>
              </>
            )}
          </section>
        </>
      )}
    </>
  );
}
