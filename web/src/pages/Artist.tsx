// Artist: the TypeScript twin of dashboard/views/artist.py. Data comes from /api/artist
// (rain_in_my_head.artist). Opened from the New artists page with ?artist=&start=&end=;
// not in the menu. Contract: specs/001-new-artist-page/contracts/artist-page.md
// The "Plays per month" chart narrows the songs with ?month=YYYY-MM (openspec/changes/artist-detail-plays-chart).
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useSearchParams } from "react-router";
import { fetchArtist, NO_ART, type ArtistSong, type MonthPlays } from "../api";
import { songColumns } from "../components/columns";
import { DataTable } from "../components/DataTable";
import { VegaChart } from "../components/VegaChart";
import { BackLink, Button, ErrorState, Loading, Notice } from "../components/ui";
import { playsPerMonth, monthLabel } from "../charts/artist";
import { formatCount, formatDayMonthYear } from "../format";
import styles from "./Artist.module.css";

export default function Artist() {
  const [params, setParams] = useSearchParams();
  const asked = {
    artist: params.get("artist") ?? undefined,
    start: params.get("start") ?? undefined,
    end: params.get("end") ?? undefined,
    month: params.get("month") ?? undefined,
  };
  const query = useQuery({
    queryKey: ["artist", asked.artist, asked.start, asked.end, asked.month],
    queryFn: () => fetchArtist(asked),
    enabled: asked.artist !== undefined,
  });
  const data = query.data;

  const pickMonth = (month: string | null) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      if (month) next.set("month", month);
      else next.delete("month");
      return next;
    });

  if (asked.artist === undefined || data?.found === false || query.error)
    return (
      <>
        <BackLink />
        <h1 className={styles.title}>Artist</h1>
        {query.error ? (
          <ErrorState error={query.error} />
        ) : (
          <Notice>No plays found for this artist. Open one from the New artists page in Dashboards.</Notice>
        )}
      </>
    );
  if (!data) return <Loading />;

  return (
    <>
      <BackLink />
      <div className={styles.header}>
        <img className={styles.cover} src={data.cover ?? NO_ART} alt="" />
        <div>
          <h1 className={styles.title}>{data.name}</h1>
          <p className="caption">
            {data.period === null
              ? `${formatCount(data.all_time_plays)} plays · all time`
              : `${formatCount(data.period_plays)} plays in ${data.period.label} · ${formatCount(data.all_time_plays)} all time`}
            {data.first_played && ` · first played ${formatDayMonthYear(data.first_played)}`}
          </p>
        </div>
      </div>

      <h2 className={styles.subheader}>Plays per month</h2>
      <MonthChart monthly={data.monthly} selected={asked.month ?? null} onSelect={pickMonth} />

      <h2 className={styles.subheader}>Songs</h2>
      {asked.month && (
        <div className={styles.selection}>
          <p className="caption">{monthLabel(asked.month)} only</p>
          <Button onClick={() => pickMonth(null)}>Show every month</Button>
        </div>
      )}
      {data.songs.length === 0 ? (
        <Notice>
          {asked.month ? `No plays by ${data.name} in ${monthLabel(asked.month)}.` : `No plays by ${data.name} in ${data.period?.label}.`}
        </Notice>
      ) : (
        <Songs songs={data.songs} />
      )}
    </>
  );
}

function MonthChart({ monthly, selected, onSelect }: { monthly: MonthPlays[]; selected: string | null; onSelect: (month: string | null) => void }) {
  const spec = useMemo(() => playsPerMonth(monthly, selected), [monthly, selected]);
  return (
    <>
      <VegaChart spec={spec} param="pick" onSelect={(v) => onSelect(v ? String((v.month as string[])[0]) : null)} />
      {selected === null && <p className="caption">Click a month to show just its songs.</p>}
    </>
  );
}

function Songs({ songs }: { songs: ArtistSong[] }) {
  const rows = useMemo(() => songs.map((s) => ({ ...s, thumb: s.thumb ?? NO_ART })), [songs]);
  return <DataTable rows={rows} columns={songColumns()} maxHeight={640} />;
}
