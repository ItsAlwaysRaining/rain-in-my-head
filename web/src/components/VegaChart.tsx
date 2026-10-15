import { useEffect, useRef } from "react";
import embed, { type Result } from "vega-embed";
import type { TopLevelSpec } from "vega-lite";
import { chartConfig } from "../charts/config";

interface Props {
  spec: TopLevelSpec;
  /** Called with the selected datum fields for point param `param` (null when cleared). */
  onSelect?: (value: Record<string, unknown> | null) => void;
  /** Name of the point selection param to listen to. */
  param?: string;
  className?: string;
}

/** A Vega-Lite chart that fills its container's width, themed with chartConfig. */
export function VegaChart({ spec, onSelect, param = "pick", className }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const onSelectRef = useRef(onSelect);
  onSelectRef.current = onSelect;

  useEffect(() => {
    if (!ref.current) return;
    let result: Result | undefined;
    let cancelled = false;
    const full = { width: "container", ...spec, config: { ...chartConfig, ...(spec as { config?: object }).config } } as TopLevelSpec;
    embed(ref.current, full, { actions: false, renderer: "svg", tooltip: { theme: "dark" } }).then((r) => {
      if (cancelled) return r.finalize();
      result = r;
      if (onSelectRef.current) {
        r.view.addSignalListener(param, (_name, value: Record<string, unknown>) => {
          // A point param's signal is {} (or has no fields) when the selection is cleared.
          const fields = value && Object.keys(value).length ? value : null;
          onSelectRef.current?.(fields);
        });
      }
    });
    return () => {
      cancelled = true;
      result?.finalize();
    };
  }, [spec, param]);

  return <div ref={ref} className={className} style={{ width: "100%" }} />;
}
