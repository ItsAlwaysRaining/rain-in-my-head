// Visitors: who used what, for the owner (specs/012-usage-tracking). It reads /api/visitors, which only works on your
// Mac: on the hosted site no tier opens this page and the route is refused for everyone. `viewer usage` shows the
// same numbers. Times are estimates sent by the visitor's browser, and days and months run on UTC.
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchVisitors, type VisitorEvent, type VisitorPerson, type VisitorsEnv, type VisitorsRange } from "../api";
import { Card, ErrorState, Loading, Notice, PageHeader, SegmentedControl } from "../components/ui";
import { DataTable, type Column } from "../components/DataTable";
import { formatDateTime, formatDuration } from "../format";
import styles from "./Visitors.module.css";

const RANGES = ["7d", "30d", "12m"] as const;
const RANGE_LABELS: Record<VisitorsRange, string> = { "7d": "Last 7 days", "30d": "Last 30 days", "12m": "Last 12 months" };

interface Row {
  name: string;
  tier: string;
  last_login: string;
  visits: number;
  time: number;
  top_pages: string;
  features: string;
  limit_hits: number;
}

const toRow = (p: VisitorPerson): Row => {
  const byFeature = new Map<string, number>();
  for (const f of p.features) byFeature.set(f.feature, (byFeature.get(f.feature) ?? 0) + f.uses);
  return {
    name: p.status === "active" ? p.name : `${p.name} (revoked)`,
    tier: p.tier,
    last_login: p.last_login_at ? formatDateTime(p.last_login_at) : "never",
    visits: p.visits,
    time: p.seconds,
    top_pages: p.pages.slice(0, 3).map((r) => `${r.page} ${r.views}`).join(", ") || "–",
    features: [...byFeature].map(([k, v]) => `${k} ${v}`).join(", ") || "–",
    limit_hits: p.limit_hits,
  };
};

const COLUMNS: Column<Row>[] = [
  { key: "name", label: "Name" },
  { key: "tier", label: "Tier" },
  { key: "last_login", label: "Last login" },
  { key: "visits", label: "Visits", kind: "number" },
  { key: "time", label: "Time on site", align: "right", render: (r) => formatDuration(r.time), help: "An estimate from the visitor's browser" },
  { key: "top_pages", label: "Top pages (views)" },
  { key: "features", label: "Features used" },
  { key: "limit_hits", label: "Limit hits", kind: "number" },
];

const EVENT_COLUMNS: Column<VisitorEvent & { when: string }>[] = [
  { key: "when", label: "When (UTC)" },
  { key: "kind", label: "Kind" },
  { key: "page", label: "Page" },
  { key: "feature", label: "Feature" },
  { key: "detail", label: "Detail" },
  { key: "seconds", label: "Seconds", kind: "number" },
];

export default function Visitors() {
  const [env, setEnv] = useState<VisitorsEnv>("prod");
  const [range, setRange] = useState<VisitorsRange>("30d");
  const [person, setPerson] = useState<string | undefined>();
  const { data, error, isFetching } = useQuery({
    queryKey: ["visitors", env, range, person],
    queryFn: () => fetchVisitors({ env, range, person }),
    staleTime: 15_000,
  });

  const rows = (data?.people ?? []).map(toRow);
  const free = data?.free_plan;
  return (
    <>
      <PageHeader title="Visitors">
        Who used the hosted site and how. This page only opens on your Mac. Times are estimates from the visitor's browser, and days and months run on UTC.
      </PageHeader>
      <div className={styles.controls}>
        <SegmentedControl label="Database" options={["prod", "dev"] as const} value={env} onChange={(v) => { setEnv(v); setPerson(undefined); }} format={(o) => (o === "prod" ? "Live site (prod)" : "Test (dev)")} />
        <SegmentedControl label="Range" options={RANGES} value={range} onChange={setRange} format={(o) => RANGE_LABELS[o]} />
        {isFetching && <span className="caption">Updating…</span>}
      </div>

      {error ? (
        <ErrorState error={error} />
      ) : !data ? (
        <Loading />
      ) : (
        <div className={styles.stack}>
          <Card title={`People (${RANGE_LABELS[range].toLowerCase()})`}>
            {rows.length === 0 ? (
              <Notice>Nobody has been invited on {env} yet. Add someone with <code>viewer add</code>.</Notice>
            ) : (
              <DataTable
                rows={rows}
                columns={COLUMNS}
                onRowClick={(row) => setPerson(data.people.find((p) => toRow(p).name === row.name)?.name)}
                selectedIndex={person ? data.people.findIndex((p) => p.name === person) : null}
                sortable
              />
            )}
          </Card>

          {person && data.person && (
            <Card title={`${data.person.name}: latest records`} actions={<button type="button" className={styles.link} onClick={() => setPerson(undefined)}>Close</button>}>
              {data.person.events.length === 0 ? (
                <Notice>No records yet.</Notice>
              ) : (
                <DataTable rows={data.person.events.map((e) => ({ ...e, when: formatDateTime(e.at) }))} columns={EVENT_COLUMNS} maxHeight={360} />
              )}
            </Card>
          )}

          {free && (
            <Card title={`Free plan, ${free.month} (UTC)`}>
              <dl className={styles.facts}>
                <div><dt>Recorded requests</dt><dd>
                    {free.requests.toLocaleString("en-GB")}
                    {free.requests_limit ? ` of ${free.requests_limit.toLocaleString("en-GB")}` : ""}
                  </dd></div>
                <div><dt>Time on heavy pages</dt><dd>{formatDuration(free.heavy_page_seconds)}</dd></div>
                <div>
                  <dt>Visitor database</dt>
                  <dd>
                    {(free.database_bytes / 1048576).toFixed(1)} MB
                    {free.database_limit_bytes ? ` of ${(free.database_limit_bytes / 1048576).toFixed(0)} MB` : " (limit not set)"}
                  </dd>
                </div>
              </dl>
              {free.notes.map((n) => (
                <p key={n} className="caption">{n}</p>
              ))}
            </Card>
          )}
        </div>
      )}
    </>
  );
}
