// Small building blocks: cards, KPI, tabs, chips, segmented control, radios, notices, breadcrumbs,
// the back link, and the page-level loading and error states. Looks follow the Figma prototype.
import { useState, type ButtonHTMLAttributes, type ReactNode } from "react";
import { Link } from "react-router";
import { ApiError } from "../api";
import { formatCount } from "../format";
import type { Crumb } from "../routes";
import styles from "./ui.module.css";

/** A raised card, optionally with a chart-title heading and controls on the right of it. */
export function Card({ title, actions, className, children }: { title?: string; actions?: ReactNode; className?: string; children: ReactNode }) {
  return (
    <section className={`${styles.card} ${className ?? ""}`}>
      {(title || actions) && (
        <header className={styles.cardHeader}>
          {title && <h3>{title}</h3>}
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

/** Page title and the line under it. */
export function PageHeader({ title, children }: { title: ReactNode; children?: ReactNode }) {
  return (
    <header className={styles.pageHeader}>
      <h1>{title}</h1>
      {children && <p className={styles.lede}>{children}</p>}
    </header>
  );
}

export function Kpi({ label, value, delta, help }: { label: string; value: number; delta: number | null; help?: string }) {
  const rounded = delta === null ? null : Math.round(delta * 100);
  return (
    <div className={styles.kpi} title={help}>
      <div className={styles.kpiLabel}>{label}</div>
      <div className={styles.kpiValue}>{formatCount(value)}</div>
      {rounded !== null && (
        <div className={`${styles.delta} ${delta! < 0 ? styles.down : styles.up}`}>
          {delta! < 0 ? "↓" : "↑"} {rounded > 0 ? "+" : ""}
          {rounded}%
        </div>
      )}
    </div>
  );
}

/** Underlined tabs. Pass `active` and `onChange` to keep the tab in the URL; otherwise it's local state. */
export function Tabs<K extends string>({
  tabs,
  active,
  onChange,
}: {
  tabs: { key: K; label: string; content: ReactNode }[];
  active?: K;
  onChange?: (key: K) => void;
}) {
  const [local, setLocal] = useState<K>(tabs[0].key);
  const current = active ?? local;
  const panel = tabs.find((t) => t.key === current) ?? tabs[0];
  return (
    <div>
      <div className={styles.tabList} role="tablist">
        {tabs.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={t.key === panel.key}
            className={t.key === panel.key ? styles.tabActive : styles.tab}
            onClick={() => (onChange ? onChange(t.key) : setLocal(t.key))}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div role="tabpanel" className={styles.tabPanel}>
        {panel.content}
      </div>
    </div>
  );
}

/** Pick one of a few options, shown as pill chips (Date range, Grain, Listening from). */
export function ChipGroup<T extends string>({
  label,
  options,
  value,
  onChange,
  format = (o) => o,
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
  format?: (option: T) => string;
}) {
  return (
    <div className={styles.field}>
      <div className={styles.fieldLabel} id={`chips-${label}`}>
        {label}
      </div>
      <div className={styles.chips} role="radiogroup" aria-labelledby={`chips-${label}`}>
        {options.map((o) => (
          <button key={o} type="button" role="radio" aria-checked={o === value} className={o === value ? styles.chipOn : styles.chip} onClick={() => onChange(o)}>
            {format(o)}
          </button>
        ))}
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
    <div className={styles.segmented} role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button key={o} type="button" role="radio" aria-checked={o === value} className={o === value ? styles.segmentActive : styles.segment} onClick={() => onChange(o)}>
          {format(o)}
        </button>
      ))}
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

export function Button({ variant = "secondary", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" }) {
  return <button type="button" {...props} className={`${variant === "primary" ? styles.primary : styles.secondary} ${props.className ?? ""}`} />;
}

export function Notice({ tone = "info", children }: { tone?: "info" | "success" | "warning" | "error"; children: ReactNode }) {
  return <div className={`${styles.notice} ${styles[tone]}`}>{children}</div>;
}

export function Breadcrumbs({ crumbs }: { crumbs: Crumb[] }) {
  if (crumbs.length === 0) return null;
  return (
    <nav aria-label="Breadcrumb" className={styles.breadcrumbs}>
      <ol>
        {crumbs.map((c, i) => (
          <li key={i}>{c.to ? <Link to={c.to}>{c.label}</Link> : <span aria-current="page">{c.label}</span>}</li>
        ))}
      </ol>
    </nav>
  );
}

// The Overview's filters, so "Back to Dashboards" returns to the same range, grain and period.
let dashboardsSearch = "";
export const rememberDashboardsSearch = (search: string) => {
  dashboardsSearch = search;
};

/** "← Back to Dashboards" at the top of the pages opened from the Overview. */
export function BackLink() {
  return (
    <Link to={`/dashboards${dashboardsSearch}`} className={styles.back}>
      <span aria-hidden>←</span> Back to Dashboards
    </Link>
  );
}

/** The raining cloud from the prototype's loading screen. */
export function Loading({ text = "Loading…" }: { text?: string }) {
  return (
    <div className={styles.loader} role="status">
      <svg viewBox="0 0 48 40" width="40" height="34" aria-hidden>
        <path
          d="M14 26h22a8 8 0 0 0 .6-16A11 11 0 0 0 15.4 12 7 7 0 0 0 14 26Z"
          fill="none"
          stroke="var(--rain)"
          strokeWidth="2"
          strokeLinejoin="round"
        />
        <rect className={styles.drop} x="23" y="30" width="2.5" height="6" rx="1.25" fill="var(--rain-strong)" />
      </svg>
      <span className="caption">{text}</span>
    </div>
  );
}

/** The message for a failed request: missing database, API not running, or anything else. */
export function ErrorState({ error }: { error: unknown }) {
  if (error instanceof ApiError && error.kind === "no_database")
    return (
      <Notice>
        No database yet. Run <code>uv run rain-in-my-head fetch</code> then <code>uv run rain-in-my-head build</code>.
      </Notice>
    );
  if (error instanceof ApiError && error.kind === "unreachable")
    return (
      <Notice tone="warning">
        The data service isn't running. Start it with <code>uv run rain-in-my-head serve</code> (add <code>--dev</code> when using <code>npm run dev</code>).
      </Notice>
    );
  return <Notice tone="error">{error instanceof Error ? error.message : String(error)}</Notice>;
}
