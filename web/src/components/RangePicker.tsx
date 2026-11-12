// The date range chips and their Custom popup, shared by the Overview and Genre pages
// (openspec/specs/dashboard-overview, openspec/specs/genre-page).
import { useState } from "react";
import type { Preset } from "../api";
import { Button, ChipGroup } from "./ui";
import styles from "./RangePicker.module.css";

export const PRESETS: Record<Preset, string> = {
  last30: "Last 30 days",
  ytd: "This year",
  last12m: "Last 12 months",
  all: "All time",
  custom: "Custom",
};
export const PRESET_KEYS = Object.keys(PRESETS) as Preset[];

/** The range shown now, as the API resolved it. */
export interface ShownRange {
  start: string;
  end: string;
  data_first: string;
  data_last: string;
}

/**
 * Picking a preset calls `onChange(preset)` at once. Custom opens a popup on the range shown now;
 * nothing changes until Apply, which calls `onChange("custom", start, end)`.
 */
export function RangePicker({
  preset,
  shown,
  onChange,
}: {
  preset: Preset;
  shown: ShownRange | undefined;
  onChange: (preset: Preset, start?: string, end?: string) => void;
}) {
  const [draft, setDraft] = useState<{ start: string; end: string } | null>(null);

  return (
    <div className={styles.rangeField}>
      <ChipGroup
        label="Date range"
        options={PRESET_KEYS}
        format={(p) => PRESETS[p]}
        value={preset}
        onChange={(p) => {
          if (p !== "custom") return onChange(p);
          if (shown) setDraft({ start: shown.start, end: shown.end });
        }}
      />
      {draft && shown && (
        <div className={styles.customPopup} role="dialog" aria-label="Custom date range" onKeyDown={(e) => e.key === "Escape" && setDraft(null)}>
          <div className={styles.dates}>
            <label>
              From
              <input
                type="date"
                autoFocus
                value={draft.start}
                min={shown.data_first}
                max={draft.end}
                onChange={(e) => e.target.value && setDraft({ ...draft, start: e.target.value })}
              />
            </label>
            <label>
              To
              <input
                type="date"
                value={draft.end}
                min={draft.start}
                max={shown.data_last}
                onChange={(e) => e.target.value && setDraft({ ...draft, end: e.target.value })}
              />
            </label>
          </div>
          <div className={styles.popupActions}>
            <Button onClick={() => setDraft(null)}>Cancel</Button>
            <Button
              variant="primary"
              onClick={() => {
                onChange("custom", draft.start, draft.end);
                setDraft(null);
              }}
            >
              Apply
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
