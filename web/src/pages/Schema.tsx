// Schema: the "Database schema" card on the Analyst page, the TypeScript twin of dashboard/views/schema.py. The map itself is pages/schema/map.ts,
// a port of the Streamlit component; the layout is saved through the API to the same
// schema_layout.json, so both dashboards show cards in the same places.
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { ApiError, fetchSchema, resetSchemaLayout, saveSchemaLayout } from "../api";
import { ErrorState, Loading, Notice } from "../components/ui";
import { createMap } from "./schema/map";
import "./schema/map.css";

const saveError = (e: unknown) =>
  new Error(e instanceof ApiError && (e.kind === "http" || e.kind === "refused") ? e.message : "Couldn't save the layout: the data service isn't responding");

export default function Schema() {
  // Read once per visit: refetching would redraw the map under a drag.
  const query = useQuery({ queryKey: ["schema"], queryFn: fetchSchema, staleTime: 0, gcTime: 0 });
  const root = useRef<HTMLDivElement>(null);
  const data = query.data;

  useEffect(() => {
    if (!data || !data.objects.length || !root.current) return;
    return createMap(root.current, data, {
      onLayout: (positions) =>
        saveSchemaLayout(positions).then(
          () => "Layout saved",
          (e) => Promise.reject(saveError(e)),
        ),
      onReset: () =>
        resetSchemaLayout().then(
          (r) => r.positions,
          (e) => Promise.reject(saveError(e)),
        ),
    });
  }, [data]);

  return query.error ? (
    <ErrorState error={query.error} />
  ) : !data ? (
    <Loading />
  ) : !data.objects.length ? (
    <Notice>
      The database has no tables yet. Run <code>uv run rain-in-my-head build</code> first.
    </Notice>
  ) : (
    <>
      <p className="caption" style={{ margin: "0 0 16px" }}>
            Every table and view in <code>listening.db</code>. Drag a card by its header to move it; the layout is saved for next time. Hover over a card to see
        what it links to.
      </p>
      <div ref={root} />
    </>
  );
}
