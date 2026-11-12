// Listening slot: the tracks played in one weekday and hour, opened from the Overview's "When you listen"
// heatmap with ?day=Thu&hour=15&start=&end=. Data from /api/slot (rain_in_my_head.overview.slot_tracks).
// Behaviour follows openspec/specs/listening-slot/spec.md; design is Figma node 326-17685.
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { fetchSlot, type Preset, type SlotParams, type SlotTrack } from "../api";
import { DataTable, type Column } from "../components/DataTable";
import { PRESET_KEYS, RangePicker } from "../components/RangePicker";
import { BackLink, ErrorState, Loading, Notice, PageHeader } from "../components/ui";
import { formatCount } from "../format";
import styles from "./Slot.module.css";

// Short names match rain_in_my_head.overview.WEEKDAYS and the heatmap's rows.
const DAYS: Record<string, string> = {
  Mon: "Monday", Tue: "Tuesday", Wed: "Wednesday", Thu: "Thursday", Fri: "Friday", Sat: "Saturday", Sun: "Sunday",
};
const HOURS = Array.from({ length: 24 }, (_, h) => h);

const pad = (h: number) => String(h).padStart(2, "0");
/** 15 -> "15:00–16:00"; 23 -> "23:00–00:00". */
export const hourLabel = (h: number) => `${pad(h)}:00–${pad((h + 1) % 24)}:00`;

const columns: Column<SlotTrack>[] = [
  { key: "thumb", label: "", kind: "image", width: "64px" },
  { key: "name", label: "Song" },
  { key: "artist", label: "Artist" },
  { key: "plays", label: "Plays", kind: "number" },
];

export default function Slot() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();
  const rawPreset = params.get("preset");
  const asked: SlotParams = {
    day: params.get("day") ?? "",
    hour: params.get("hour") ?? "",
    // Dates without a preset are Custom (the heatmap link); the API treats a missing preset the same way.
    preset: PRESET_KEYS.includes(rawPreset as Preset) ? (rawPreset as Preset) : undefined,
    start: params.get("start") ?? undefined,
    end: params.get("end") ?? undefined,
  };
  const hour = /^\d{1,2}$/.test(asked.hour) ? Number(asked.hour) : NaN;
  const known = asked.day in DAYS && hour >= 0 && hour <= 23;
  const query = useQuery({
    queryKey: ["slot", asked.day, asked.hour, asked.preset, asked.start, asked.end],
    queryFn: () => fetchSlot(asked),
    placeholderData: keepPreviousData,
    enabled: known,
  });
  const data = query.data;

  const set = (changes: Record<string, string | undefined>) =>
    setParams((prev) => {
      const next = new URLSearchParams(prev);
      for (const [k, v] of Object.entries(changes)) v === undefined ? next.delete(k) : next.set(k, v);
      return next;
    });

  const frame = (body: ReactNode, title: ReactNode = "When you listen", subtitle?: ReactNode) => (
    <>
      <BackLink />
      <PageHeader title={title}>{subtitle}</PageHeader>
      {body}
    </>
  );

  if (!known) return frame(<Notice tone="warning">There is no listening slot for day “{asked.day}” and hour “{asked.hour}”.</Notice>);
  if (query.error) return frame(<ErrorState error={query.error} />);
  if (!data) return frame(<Loading />);

  const slotName = `${DAYS[data.day]}s, ${hourLabel(data.hour)}`;
  if (!data.range) return frame(<Notice>No scrobbles yet.</Notice>, slotName);
  const range = data.range;

  const summary = [
    data.range_label,
    `${formatCount(data.plays)} ${data.plays === 1 ? "play" : "plays"}`,
    `${formatCount(data.distinct_tracks)} different ${data.distinct_tracks === 1 ? "track" : "tracks"}`,
    ...(data.busiest ? ["your busiest hour of the week"] : []),
  ].join(" · ");

  return frame(
    <>
      <div className={styles.controls}>
        <RangePicker preset={range.preset} shown={range} onChange={(preset, start, end) => set({ preset, start, end })} />
        <div className={styles.pickers}>
          <label className={styles.select}>
            Day
            <select value={data.day} onChange={(e) => set({ day: e.target.value })}>
              {Object.entries(DAYS).map(([key, name]) => (
                <option key={key} value={key}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label className={styles.select}>
            Hour
            <select value={data.hour} onChange={(e) => set({ hour: e.target.value })}>
              {HOURS.map((h) => (
                <option key={h} value={h}>
                  {hourLabel(h)}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <h2 className={styles.subheader}>Tracks</h2>
      {data.tracks.length === 0 ? (
        <Notice tone="warning">No plays on {slotName} in this range.</Notice>
      ) : (
        <>
          <DataTable
            rows={data.tracks}
            columns={columns}
            maxHeight={640}
            onRowClick={(t) => navigate(`/dashboards/artist?${new URLSearchParams({ artist: t.artist_key, start: range.start, end: range.end })}`)}
          />
          <p className={`caption ${styles.hint}`}>
            Showing {formatCount(data.tracks.length)} of {formatCount(data.distinct_tracks)} tracks, most played first. Click a track to see the
            artist.
          </p>
        </>
      )}
    </>,
    slotName,
    summary,
  );
}
