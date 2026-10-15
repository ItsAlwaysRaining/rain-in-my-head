// Small building blocks: KPI, tabs, segmented control, notices, and the page-level error states.
import { useState, type ReactNode } from "react";
import { ApiError } from "../api";
import styles from "./ui.module.css";

const numberFormat = new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 });

export function Kpi({ label, value, delta, help }: { label: string; value: number; delta: number | null; help?: string }) {
  const rounded = delta === null ? null : Math.round(delta * 100);
  return (
    <div className={styles.kpi} title={help}>
      <div className={styles.kpiLabel}>{label}</div>
      <div className={styles.kpiValue}>{numberFormat.format(value)}</div>
      {rounded !== null && (
        <div className={`${styles.delta} ${delta! < 0 ? styles.down : styles.up}`}>
          {delta! < 0 ? "↓" : "↑"} {rounded > 0 ? "+" : ""}
          {rounded}%
        </div>
      )}
    </div>
  );
}

export function Tabs({ tabs }: { tabs: { label: string; content: ReactNode }[] }) {
  const [active, setActive] = useState(0);
  return (
    <div>
      <div className={styles.tabList} role="tablist">
        {tabs.map((t, i) => (
          <button key={t.label} role="tab" aria-selected={i === active} className={i === active ? styles.tabActive : styles.tab} onClick={() => setActive(i)}>
            {t.label}
          </button>
        ))}
      </div>
      <div role="tabpanel" className={styles.tabPanel}>
        {tabs[active].content}
      </div>
    </div>
  );
}

export function SegmentedControl<T extends string>({
  label,
  options,
  value,
  onChange,
  format = (o) => o,
}: {
  label?: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
  format?: (option: T) => string;
}) {
  return (
    <div className={styles.field}>
      {label && <div className={styles.fieldLabel}>{label}</div>}
      <div className={styles.segmented} role="radiogroup" aria-label={label}>
        {options.map((o) => (
          <button key={o} role="radio" aria-checked={o === value} className={o === value ? styles.segmentActive : styles.segment} onClick={() => onChange(o)}>
            {format(o)}
          </button>
        ))}
      </div>
    </div>
  );
}

export function RadioGroup<T extends string>({
  label,
  options,
  value,
  onChange,
  format = (o) => o,
  horizontal,
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
  format?: (option: T) => string;
  horizontal?: boolean;
}) {
  return (
    <fieldset className={styles.radioGroup}>
      <legend className={styles.fieldLabel}>{label}</legend>
      <div className={horizontal ? styles.radiosRow : styles.radios}>
        {options.map((o) => (
          <label key={o} className={styles.radio}>
            <input type="radio" checked={o === value} onChange={() => onChange(o)} />
            {format(o)}
          </label>
        ))}
      </div>
    </fieldset>
  );
}

export function Notice({ tone = "info", children }: { tone?: "info" | "warning" | "error"; children: ReactNode }) {
  return <div className={`${styles.notice} ${styles[tone]}`}>{children}</div>;
}

/** The message for a failed request: missing database, API not running, or anything else. */
export function ErrorState({ error }: { error: unknown }) {
  if (error instanceof ApiError && error.kind === "no_database")
    return (
      <Notice>
        No database yet. Run <code>uv run listening fetch</code> then <code>uv run listening build</code>.
      </Notice>
    );
  if (error instanceof ApiError && error.kind === "unreachable")
    return (
      <Notice tone="warning">
        The data service isn't running. Start it with <code>uv run listening serve</code> (add <code>--dev</code> when using <code>npm run dev</code>).
      </Notice>
    );
  return <Notice tone="error">{error instanceof Error ? error.message : String(error)}</Notice>;
}
