import { useMemo, useState, type ReactNode } from "react";
import styles from "./DataTable.module.css";

export type ColumnKind = "text" | "number" | "percent" | "progress" | "image" | "year";

export interface Column<T> {
  key: keyof T & string;
  label: string;
  kind?: ColumnKind;
  /** Fixed width, e.g. "56px" for thumbnails. */
  width?: string;
  /** Right-align a column whose kind isn't numeric (e.g. numbers drawn with `render`). */
  align?: "right";
  render?: (row: T) => ReactNode;
}

interface Props<T> {
  rows: T[];
  columns: Column<T>[];
  maxHeight?: number;
  /** Clicking anywhere on a row calls this (constitution VI: the whole row is the target). */
  onRowClick?: (row: T, index: number) => void;
  selectedIndex?: number | null;
  sortable?: boolean;
}

const numberFormat = new Intl.NumberFormat("en-GB");
const percentFormat = new Intl.NumberFormat("en-GB", { style: "percent", maximumFractionDigits: 0 });

function cell<T>(row: T, column: Column<T>): ReactNode {
  if (column.render) return column.render(row);
  const value = row[column.key] as unknown;
  if (value === null || value === undefined) return "";
  switch (column.kind) {
    case "number":
      return numberFormat.format(value as number);
    case "year":
      return String(value);
    case "percent":
      return percentFormat.format(value as number);
    case "progress":
      return (
        <span className={styles.progress}>
          <span className={styles.bar}>
            <span style={{ width: `${Math.max(0, Math.min(1, value as number)) * 100}%` }} />
          </span>
          <span className={styles.progressLabel}>{percentFormat.format(value as number)}</span>
        </span>
      );
    case "image":
      return <img className={styles.thumb} src={value as string} alt="" loading="lazy" />;
    default:
      return String(value);
  }
}

export function DataTable<T>({ rows, columns, maxHeight, onRowClick, selectedIndex, sortable }: Props<T>) {
  const [sort, setSort] = useState<{ key: string; desc: boolean } | null>(null);
  const shown = useMemo(() => {
    if (!sort) return rows.map((row, index) => ({ row, index }));
    const key = sort.key as keyof T;
    return rows
      .map((row, index) => ({ row, index }))
      .sort((a, b) => {
        const x = a.row[key] as unknown as number | string;
        const y = b.row[key] as unknown as number | string;
        const order = x < y ? -1 : x > y ? 1 : 0;
        return sort.desc ? -order : order;
      });
  }, [rows, sort]);

  const toggleSort = (key: string) =>
    setSort((s) => (s?.key === key ? (s.desc ? { key, desc: false } : null) : { key, desc: true }));

  return (
    <div className={styles.wrap} style={{ maxHeight }}>
      <table className={styles.table}>
        <thead>
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                style={{ width: c.width }}
                className={[isNumeric(c) ? styles.num : "", sortable ? styles.sortable : ""].join(" ")}
                onClick={sortable ? () => toggleSort(c.key) : undefined}
              >
                {c.label}
                {sort?.key === c.key ? (sort.desc ? " ↓" : " ↑") : ""}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shown.map(({ row, index }) => (
            <tr
              key={index}
              className={[onRowClick ? styles.clickable : "", selectedIndex === index ? styles.selected : ""].join(" ")}
              onClick={onRowClick ? () => onRowClick(row, index) : undefined}
            >
              {columns.map((c) => (
                <td key={c.key} className={isNumeric(c) ? styles.num : ""}>
                  {cell(row, c)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const isNumeric = <T,>(c: Column<T>) => c.align === "right" || c.kind === "number" || c.kind === "percent";
