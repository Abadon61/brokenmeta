import { createRoot } from "react-dom/client";
import { Area } from "@/components/charts/area";
import { AreaChart } from "@/components/charts/area-chart";
import { Bar } from "@/components/charts/bar";
import { BarChart } from "@/components/charts/bar-chart";
import { BarXAxis } from "@/components/charts/bar-x-axis";
import { Gauge } from "@/components/charts/gauge";
import { Grid } from "@/components/charts/grid";
import { RadarArea } from "@/components/charts/radar-area";
import { RadarAxis } from "@/components/charts/radar-axis";
import { RadarChart } from "@/components/charts/radar-chart";
import { RadarGrid } from "@/components/charts/radar-grid";
import { RadarLabels } from "@/components/charts/radar-labels";
import { Ring } from "@/components/charts/ring";
import { RingChart } from "@/components/charts/ring-chart";
import { ChartTooltip } from "@/components/charts/tooltip";
import { XAxis } from "@/components/charts/x-axis";
import css from "./embed.css?inline";

type Series = { key: string; label: string; color: string };
type Row = Record<string, string | number>;
type Payload = {
  type?: "area" | "bar" | "gauge" | "gauge-linear" | "ring" | "radar";
  rings?: { label: string; value: number; maxValue: number; color?: string }[];
  metrics?: { key: string; label: string }[];
  radar?: { label: string; color?: string; values: Record<string, number> }[];
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

function linearGauge(p: Payload) {
  return (
    <Gauge
      orientation="linear"
      value={p.value ?? 0}
      centerValue={p.value ?? 0}
      suffix={p.suffix}
      defaultLabel={p.label}
      activeFill={p.color}
      inactiveFill="rgba(240,231,216,0.12)"
      totalNotches={40}
      minWidth={0}
      linearHeight={22}
    />
  );
}

function ringChart(p: Payload) {
  const rings = p.rings ?? [];
  const size = p.size ?? 150;
  const first = rings[0];
  return (
    <div style={{ position: "relative", width: size, height: size, margin: "0 auto" }}>
      <RingChart data={rings} size={size} strokeWidth={9} ringGap={5} baseInnerRadius={34}>
        {rings.map((r, i) => (
          <Ring key={r.label} index={i} color={r.color} />
        ))}
      </RingChart>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", pointerEvents: "none", lineHeight: 1.15 }}>
        <div style={{ fontSize: 22, fontWeight: 700, color: "var(--chart-tooltip-foreground)" }}>{first?.value}%</div>
        <div style={{ fontSize: 10, color: "var(--chart-tooltip-muted)" }}>{first?.label}</div>
      </div>
    </div>
  );
}

function radarChart(p: Payload) {
  return (
    <RadarChart data={p.radar ?? []} metrics={p.metrics ?? []} size={p.size ?? 230} margin={76}>
      <RadarGrid />
      <RadarAxis />
      <RadarLabels />
      {(p.radar ?? []).map((r, i) => (
        <RadarArea key={r.label} index={i} color={r.color} />
      ))}
    </RadarChart>
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
  if (!["gauge", "gauge-linear", "ring", "radar"].includes(type) && (!p.data || p.data.length < (type === "area" ? 2 : 1))) return;
  el.dataset.bmMounted = "true";

  const host = document.createElement("div");
  host.className = "bm-bk-chart";
  const shadow = host.attachShadow({ mode: "open" });
  const style = document.createElement("style");
  style.textContent = css;
  const root = document.createElement("div");
  shadow.append(style, root);
  const views: Record<string, (q: Payload) => React.ReactElement> = {
    gauge, "gauge-linear": linearGauge, ring: ringChart, radar: radarChart, bar: barChart, area: areaChart,
  };
  createRoot(root).render(views[type](p));
  el.replaceChildren(host);
}

export function mountAll() {
  document.querySelectorAll<HTMLElement>(`[${ATTR}]`).forEach(mount);
}

mountAll();
