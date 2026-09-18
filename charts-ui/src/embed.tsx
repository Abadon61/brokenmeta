import { createRoot } from "react-dom/client";
import { Area } from "@/components/charts/area";
import { AreaChart } from "@/components/charts/area-chart";
import { Grid } from "@/components/charts/grid";
import { ChartTooltip } from "@/components/charts/tooltip";
import { XAxis } from "@/components/charts/x-axis";
import css from "./embed.css?inline";

type Series = { key: string; label: string; color: string };
type Row = Record<string, string | number>;
type Payload = { series: Series[]; data: Row[]; aspectRatio?: string };

function toDate(v: string | number): Date {
  const s = String(v);
  return new Date(/^\d{4}-\d{2}-\d{2}$/.test(s) ? `${s}T00:00:00Z` : /^\d+$/.test(s) ? Number(s) : s);
}

function mount(el: HTMLElement) {
  if (el.dataset.bmMounted) return;
  let payload: Payload;
  try {
    payload = JSON.parse(el.getAttribute("data-bm-area-chart") || "");
  } catch {
    return;
  }
  if (!payload.data || payload.data.length < 2) return;
  el.dataset.bmMounted = "true";

  const data = payload.data.map((row) => ({ ...row, date: toDate(row.date) }));
  const host = document.createElement("div");
  host.className = "bm-bk-chart";
  const shadow = host.attachShadow({ mode: "open" });
  const style = document.createElement("style");
  style.textContent = css;
  const root = document.createElement("div");
  shadow.append(style, root);

  createRoot(root).render(
    <AreaChart data={data} aspectRatio={payload.aspectRatio || "2.6 / 1"} margin={{ top: 24, right: 24, bottom: 36, left: 24 }}>
      <Grid horizontal />
      {payload.series.map((s) => (
        <Area key={s.key} dataKey={s.key} fill={s.color} stroke={s.color} fillOpacity={0.22} strokeWidth={2.5} />
      ))}
      <XAxis />
      <ChartTooltip
        rows={(point) =>
          payload.series.map((s) => ({
            color: s.color,
            label: s.label,
            value: (point.tip as string | undefined) ?? (point[s.key] as number),
          }))
        }
      />
    </AreaChart>,
  );

  el.replaceChildren(host);
}

export function mountAll() {
  document.querySelectorAll<HTMLElement>("[data-bm-area-chart]").forEach(mount);
}

mountAll();
