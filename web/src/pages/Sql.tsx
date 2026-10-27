// SQL: the "Write SQL" part of the Analyst page, the TypeScript twin of dashboard/views/sql.py. Queries
// run read-only through /api/sql (rain_in_my_head.sql_examples); the examples are the ones Streamlit shows.
// The table list Streamlit shows is replaced here by the schema map above it on the Analyst page.
import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router";
import { fetchSqlMeta, runSql, type SqlCell } from "../api";
import { DataTable, type Column } from "../components/DataTable";
import { Button, ErrorState, Loading, Notice } from "../components/ui";
import { formatCount } from "../format";
import styles from "./Sql.module.css";

/** A cell as pandas prints it: floats keep their ".0" (JSON drops it). */
const show = (value: SqlCell, isFloat: boolean) =>
  value === null ? "" : isFloat && typeof value === "number" && Number.isInteger(value) ? value.toFixed(1) : String(value);

/** The CSV pandas `to_csv(index=False)` writes: fields quoted only when they hold a comma, quote or newline. */
function toCsv(columns: string[], rows: SqlCell[][], floats: Set<number>): string {
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

  const navigate = useNavigate();
  return (
    <section>
      <h2>Write SQL</h2>
      {meta.error ? (
        <div className={styles.section}>
          <ErrorState error={meta.error} />
        </div>
      ) : !meta.data ? (
        <Loading />
      ) : (
        <div className={styles.stack}>
          <label className={styles.label}>
            Examples
            <select
              className={`${styles.field} ${styles.select}`}
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
            <span className="caption">Run with the button or ⌘/Ctrl + Enter.</span>
          </label>

          <div className={styles.actions}>
            <Button variant="primary" onClick={submit} disabled={run.isPending}>
              Run query
            </Button>
            <Button
              onClick={() => {
                setSql("");
                setExample("");
                run.reset();
              }}
            >
              Clear
            </Button>
            {/* The SQL playlist type is issue #31; its tab explains what's coming. */}
            <Button onClick={() => navigate("/playlists?type=sql")}>Use in Playlist Generator</Button>
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
    </section>
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
      <div>
        <h2>Results</h2>
        <p className="caption">{formatCount(rowCount)} rows · click a column header to sort</p>
      </div>
      <DataTable rows={records} columns={tableColumns} maxHeight={480} sortable />
      <div>
        <Button onClick={() => download("query.csv", toCsv(columns, rows, floats))}>Download CSV</Button>
      </div>
    </div>
  );
}
