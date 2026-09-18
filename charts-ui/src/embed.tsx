import { createRoot } from "react-dom/client";
import { Area } from "@/components/charts/area";
import { AreaChart } from "@/components/charts/area-chart";
import { Bar } from "@/components/charts/bar";
import { BarChart } from "@/components/charts/bar-chart";
import { BarXAxis } from "@/components/charts/bar-x-axis";
import { Gauge } from "@/components/charts/gauge";
import { Grid } from "@/components/charts/grid";
import { ChartTooltip } from "@/components/charts/tooltip";
import { XAxis } from "@/components/charts/x-axis";
import css from "./embed.css?inline";

type Series = { key: string; label: string; color: string };
type Row = Record<string, string | number>;
type Payload = {
  type?: "area" | "bar" | "gauge";
  series?: Series[];
  data?: Row[];
  aspectRatio?: string;
  value?: number;
  suffix?: string;
  label?: string;
  color?: string;
  size?: number;
};

const ATTR = "data-bm-chart";

function toDate(v: string | number): Date {
  const s = String(v);
  return new Date(/^\d{4}-\d{2}-\d{2}$/.test(s) ? `${s}T00:00:00Z` : /^\d+$/.test(s) ? Number(s) : s);
}

function tipRows(series: Series[]) {
  return (point: Record<string, unknown>) => {
    const active = series.filter((s) => Number(point[s.key]) > 0);
    const shown = typeof point.tip === "string" ? (active.length ? active.slice(0, 1) : series.slice(0, 1)) : series;
    return shown.map((s) => ({ color: s.color, label: s.label, value: (point.tip as string | undefined) ?? (point[s.key] as number) }));
  };
}

function areaChart(p: Payload) {
  const series = p.series ?? [];
  const data = (p.data ?? []).map((row) => ({ ...row, date: toDate(row.date) }));
  return (
    <AreaChart data={data} aspectRatio={p.aspectRatio || "2.6 / 1"} margin={{ top: 24, right: 24, bottom: 36, left: 24 }}>
      <Grid horizontal />
      {series.map((s) => (
        <Area key={s.key} dataKey={s.key} fill={s.color} stroke={s.color} fillOpacity={0.22} strokeWidth={2.5} />
      ))}
      <XAxis />
      <ChartTooltip rows={tipRows(series)} />
    </AreaChart>
  );
}

function barChart(p: Payload) {
  const series = p.series ?? [];
  return (
    <BarChart data={p.data ?? []} xDataKey="name" stacked aspectRatio={p.aspectRatio || "2.4 / 1"} margin={{ top: 16, right: 12, bottom: 32, left: 12 }}>
      <Grid horizontal />
      {series.map((s) => (
        <Bar key={s.key} dataKey={s.key} fill={s.color} stroke={s.color} lineCap={3} />
      ))}
      <BarXAxis showAllLabels />
      <ChartTooltip rows={tipRows(series)} />
    </BarChart>
  );
}

function gauge(p: Payload) {
  const size = p.size ?? 112;
  return (
    <Gauge
      value={p.value ?? 0}
      centerValue={p.value ?? 0}
      suffix={p.suffix}
      defaultLabel={p.label}
      activeFill={p.color}
      inactiveFill="rgba(240,231,216,0.12)"
      totalNotches={30}
      width={size}
      height={Math.round(size * 0.86)}
      minWidth={0}
    />
  );
}

function mount(el: HTMLElement) {
  if (el.dataset.bmMounted) return;
  let p: Payload;
  try {
    p = JSON.parse(el.getAttribute(ATTR) || "");
  } catch {
    return;
  }
  const type = p.type ?? "area";
  if (type !== "gauge" && (!p.data || p.data.length < (type === "area" ? 2 : 1))) return;
  el.dataset.bmMounted = "true";

  const host = document.createElement("div");
  host.className = "bm-bk-chart";
  const shadow = host.attachShadow({ mode: "open" });
  const style = document.createElement("style");
  style.textContent = css;
  const root = document.createElement("div");
  shadow.append(style, root);
  createRoot(root).render(type === "gauge" ? gauge(p) : type === "bar" ? barChart(p) : areaChart(p));
  el.replaceChildren(host);
}

export function mountAll() {
  document.querySelectorAll<HTMLElement>(`[${ATTR}]`).forEach(mount);
}

mountAll();
