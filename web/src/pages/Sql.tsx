// SQL: the TypeScript twin of dashboard/views/sql.py. Queries run read-only through /api/sql
// (rain_in_my_head.sql_examples); examples and the schema list are the ones Streamlit shows.
import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { fetchSqlMeta, runSql, type SqlCell } from "../api";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState, Notice } from "../components/ui";
import styles from "./Sql.module.css";

const count = new Intl.NumberFormat("en-GB");

/** A cell as pandas prints it: floats keep their ".0" (JSON drops it). */
const show = (value: SqlCell, isFloat: boolean) =>
  value === null ? "" : isFloat && typeof value === "number" && Number.isInteger(value) ? value.toFixed(1) : String(value);

/** The CSV pandas `to_csv(index=False)` writes: fields quoted only when they hold a comma, quote or newline. */
export function toCsv(columns: string[], rows: SqlCell[][], floats: Set<number>): string {
  const field = (text: string) => (/[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text);
  const lines = [columns.map(field), ...rows.map((row) => row.map((v, i) => field(show(v, floats.has(i)))))];
  return lines.map((line) => line.join(",")).join("\n") + "\n";
}

function download(name: string, text: string) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  a.click();
  URL.revokeObjectURL(url);
}

export default function Sql() {
  const meta = useQuery({ queryKey: ["sql-meta"], queryFn: fetchSqlMeta });
  const [sql, setSql] = useState("");
  const [example, setExample] = useState("");
  const run = useMutation({ mutationFn: runSql });

  const submit = () => {
    if (sql.trim()) run.mutate(sql);
  };

  return (
    <>
      <h1>SQL</h1>
      {meta.error ? (
        <div className={styles.section}>
          <ErrorState error={meta.error} />
        </div>
      ) : !meta.data ? (
        <p className="caption">Loading…</p>
      ) : (
        <div className={styles.stack}>
          <details className={styles.expander}>
            <summary>
              Tables and columns — start with <code>v_plays</code> (one row per play, everything joined)
            </summary>
            <div className={styles.expanderBody}>
              <DataTable
                rows={meta.data.schema}
                columns={[
                  { key: "object", label: "object" },
                  { key: "column", label: "column" },
                  { key: "type", label: "type" },
                ]}
                maxHeight={350}
              />
            </div>
          </details>

          <label className={styles.label}>
            Examples
            <select
              className={styles.field}
              value={example}
              onChange={(e) => {
                setExample(e.target.value);
                setSql(meta.data.examples[e.target.value]);
              }}
            >
              <option value="" disabled>
                Load an example query…
              </option>
              {Object.keys(meta.data.examples).map((title) => (
                <option key={title}>{title}</option>
              ))}
            </select>
          </label>

          <label className={styles.label}>
            Query
            <textarea
              className={`${styles.field} ${styles.editor}`}
              value={sql}
              spellCheck={false}
              placeholder="SELECT * FROM v_plays ORDER BY played_at DESC LIMIT 20"
              onChange={(e) => setSql(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                  e.preventDefault();
                  submit();
                }
              }}
            />
          </label>

          <div>
            <button className={styles.primary} onClick={submit} disabled={run.isPending}>
              Run
            </button>
            <span className={`caption ${styles.shortcut}`}>or ⌘/Ctrl + Enter</span>
          </div>

          {run.error ? (
            <ErrorState error={run.error} />
          ) : run.data && "error" in run.data ? (
            <Notice tone="error">{run.data.error}</Notice>
          ) : run.data ? (
            <Result columns={run.data.columns} floatColumns={run.data.float_columns} rows={run.data.rows} rowCount={run.data.row_count} />
          ) : null}
        </div>
      )}
    </>
  );
}

function Result({ columns, floatColumns, rows, rowCount }: { columns: string[]; floatColumns: number[]; rows: SqlCell[][]; rowCount: number }) {
  const floats = new Set(floatColumns);
  // Keyed by position, so duplicate column names (SELECT a, a) still show.
  const records = useMemo(() => rows.map((row) => Object.fromEntries(row.map((v, i) => [String(i), v]))), [rows]);
  const tableColumns: Column<Record<string, SqlCell>>[] = columns.map((label, i) => {
    const numeric = rows.length > 0 && rows.every((r) => r[i] === null || typeof r[i] === "number");
    return { key: String(i), label, render: (r) => (r[i] === null ? <span className={styles.null}>None</span> : show(r[i], floats.has(i))), align: numeric ? "right" : undefined };
  });

  return (
    <div className={styles.stack}>
      <p className="caption">{count.format(rowCount)} rows</p>
      <DataTable rows={records} columns={tableColumns} maxHeight={480} sortable />
      <div>
        <button className={styles.secondary} onClick={() => download("query.csv", toCsv(columns, rows, floats))}>
          Download CSV
        </button>
      </div>
    </div>
  );
}
