// Form controls the Playlists page needs, in the shapes Streamlit offers: a slider, a two-thumb
// range slider, a multi-select of chips, and a labelled field wrapper with optional help.
import type { ReactNode } from "react";
import styles from "./Form.module.css";

export function Field({ label, help, children }: { label: string; help?: string; children: ReactNode }) {
  return (
    <div className={styles.field}>
      <div className={styles.label}>
        {label}
        {help && (
          <span className={styles.help} title={help} aria-label={help}>
            ?
          </span>
        )}
      </div>
      {children}
    </div>
  );
}

export function Slider({
  label, help, min, max, step = 1, value, onChange, format = String,
}: {
  label: string; help?: string; min: number; max: number; step?: number; value: number;
  onChange: (v: number) => void; format?: (v: number) => string;
}) {
  return (
    <Field label={label} help={help}>
      <div className={styles.slider}>
        <output className={styles.value}>{format(value)}</output>
        <input type="range" min={min} max={max} step={step} value={value} aria-label={label} onChange={(e) => onChange(Number(e.target.value))} />
        <div className={styles.ends}>
          <span>{format(min)}</span>
          <span>{format(max)}</span>
        </div>
      </div>
    </Field>
  );
}

export function RangeSlider({
  label, help, min, max, value, onChange, format = String,
}: {
  label: string; help?: string; min: number; max: number; value: [number, number];
  onChange: (v: [number, number]) => void; format?: (v: number) => string;
}) {
  const [lo, hi] = value;
  const pct = (v: number) => ((v - min) / (max - min || 1)) * 100;
  return (
    <Field label={label} help={help}>
      <div className={styles.slider}>
        <output className={styles.value}>
          {format(lo)} – {format(hi)}
        </output>
        <div className={styles.range} style={{ ["--lo" as string]: `${pct(lo)}%`, ["--hi" as string]: `${pct(hi)}%` }}>
          <input type="range" min={min} max={max} value={lo} aria-label={`${label} from`} onChange={(e) => onChange([Math.min(Number(e.target.value), hi), hi])} />
          <input type="range" min={min} max={max} value={hi} aria-label={`${label} to`} onChange={(e) => onChange([lo, Math.max(Number(e.target.value), lo)])} />
        </div>
        <div className={styles.ends}>
          <span>{format(min)}</span>
          <span>{format(max)}</span>
        </div>
      </div>
    </Field>
  );
}

export function Chips({ label, options, value, onChange }: { label: string; options: string[]; value: string[]; onChange: (v: string[]) => void }) {
  return (
    <Field label={label}>
      <div className={styles.chips} role="group" aria-label={label}>
        {options.map((o) => {
          const on = value.includes(o);
          return (
            <button
              key={o}
              type="button"
              aria-pressed={on}
              className={on ? styles.chipOn : styles.chip}
              // Kept in the options' order; the playlist doesn't depend on the order they were picked in.
              onClick={() => onChange(on ? value.filter((v) => v !== o) : options.filter((x) => x === o || value.includes(x)))}
            >
              {o}
            </button>
          );
        })}
      </div>
    </Field>
  );
}
