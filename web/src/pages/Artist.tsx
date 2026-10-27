// Artist: the TypeScript twin of dashboard/views/artist.py. Data comes from /api/artist
// (rain_in_my_head.artist). Opened from the Overview's "New artists" list with ?artist=&start=&end=;
// not in the menu. Contract: specs/001-new-artist-page/contracts/artist-page.md
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useSearchParams } from "react-router";
import { fetchArtist, NO_ART, type ArtistSong } from "../api";
import { songColumns } from "../components/columns";
import { DataTable } from "../components/DataTable";
import { BackToOverview, ErrorState, Loading, Notice } from "../components/ui";
import { formatCount } from "../format";
import styles from "./Artist.module.css";

export default function Artist() {
  const [params] = useSearchParams();
  const asked = {
    artist: params.get("artist") ?? undefined,
    start: params.get("start") ?? undefined,
    end: params.get("end") ?? undefined,
  };
  const query = useQuery({
    queryKey: ["artist", asked.artist, asked.start, asked.end],
    queryFn: () => fetchArtist(asked),
    enabled: asked.artist !== undefined,
  });
  const data = query.data;

  if (asked.artist === undefined || data?.found === false || query.error)
    return (
      <>
        <BackToOverview />
        <h1 className={styles.title}>Artist</h1>
        {query.error ? (
          <ErrorState error={query.error} />
        ) : (
          <Notice>No plays found for this artist. Open one from the “New artists” list on the Overview.</Notice>
        )}
      </>
    );
  if (!data) return <Loading />;

  return (
    <>
      <BackToOverview />
      <div className={styles.header}>
        <img className={styles.cover} src={data.cover ?? NO_ART} alt="" />
        <div>
          <h1 className={styles.title}>{data.name}</h1>
          <p className="caption">
            {data.period === null
              ? `${formatCount(data.all_time_plays)} plays · all time`
              : `${formatCount(data.period_plays)} plays in ${data.period.label} · ${formatCount(data.all_time_plays)} all time`}
          </p>
        </div>
      </div>

      <h2 className={styles.subheader}>Songs</h2>
      {data.songs.length === 0 ? (
        <Notice>
          No plays by {data.name} in {data.period?.label}.
        </Notice>
      ) : (
        <Songs songs={data.songs} />
      )}
    </>
  );
}

function Songs({ songs }: { songs: ArtistSong[] }) {
  const rows = useMemo(() => songs.map((s) => ({ ...s, thumb: s.thumb ?? NO_ART })), [songs]);
  return <DataTable rows={rows} columns={songColumns()} maxHeight={640} />;
}
