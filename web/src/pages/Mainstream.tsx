// Mainstream vs. niche: the artists in one Last.fm listener band, opened from the Overview's bar chart with
// ?bucket=&start=&end=. Lists come from /api/mainstream (rain_in_my_head.overview.listener_band_artists).
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useSearchParams } from "react-router";
import { fetchMainstream, type MainstreamArtist, type MainstreamParams } from "../api";
import { DataTable, type Column } from "../components/DataTable";
import { BackLink, ErrorState, Loading, Notice, PageHeader } from "../components/ui";
import { formatDayMonthYear, percent } from "../format";

// The same five labels as LISTENER_LABELS in rain_in_my_head/overview.py and the Overview chart.
const LISTENER_BANDS = ["<10k", "10k–100k", "100k–1M", "1M–5M", "5M+"];

// The page shows this many of the most played artists in the band; the API returns them all.
const TOP = 100;

const columns: Column<MainstreamArtist>[] = [
  { key: "name", label: "Artist" },
  { key: "listeners", label: "Last.fm listeners", kind: "number" },
  { key: "plays", label: "Your plays", kind: "number" },
];

export function Mainstream() {
  const [params] = useSearchParams();
  const asked: MainstreamParams = {
    bucket: params.get("bucket") ?? "",
    start: params.get("start") ?? undefined,
    end: params.get("end") ?? undefined,
  };
  const known = LISTENER_BANDS.includes(asked.bucket);
  const query = useQuery({
    queryKey: ["mainstream", asked.bucket, asked.start, asked.end],
    queryFn: () => fetchMainstream(asked),
    placeholderData: keepPreviousData,
    enabled: known,
  });
  const data = query.data;

  const frame = (body: ReactNode, subtitle?: ReactNode) => (
    <>
      <BackLink />
      <PageHeader title="Mainstream vs. niche">{subtitle}</PageHeader>
      {body}
    </>
  );

  if (!known) return frame(<Notice tone="warning">There is no listener band called “{asked.bucket}”.</Notice>);
  if (query.error) return frame(<ErrorState error={query.error} />);
  if (!data) return frame(<Loading />);

  const range = data.start && data.end ? `${formatDayMonthYear(data.start)} – ${formatDayMonthYear(data.end)}` : "";
  return frame(
    data.artists.length === 0 ? (
      <Notice tone="warning">No artists in the {asked.bucket} band for this range.</Notice>
    ) : (
      <>
        <DataTable rows={data.artists.slice(0, TOP)} columns={columns} maxHeight={640} />
        {data.artists.length > TOP && (
          <p className="caption">
            Showing the top {TOP} of {data.artists.length.toLocaleString("en-GB")} artists.
          </p>
        )}
      </>
    ),
    <>
      Artists with {asked.bucket} Last.fm listeners · {percent(data.share)} of your plays · {range}
    </>,
  );
}
