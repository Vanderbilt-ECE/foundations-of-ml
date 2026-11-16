<script setup lang="ts">
// A small, reusable SVG line chart: several series, optional log axes, reference lines,
// shaded bands, labelled points, and text. Used by most of the measured-data slides.
//   series[i].y may contain null (a gap, e.g. a run that turned into NaN).
//   draw (0–1) reveals the series from left to right, for "drawing in" animations.
//   visible[i] fades a series in or out, for click reveals.
// All font sizes are inline styles (Slidev overrides SVG font-size attributes).
import { computed, useId } from 'vue'
import { C, pathOf } from '../utils/plot'

export interface Series {
  y: (number | null)[]
  x?: number[]
  color: string
  name?: string
  dash?: string
  width?: number
  opacity?: number
  label?: string           // drawn at the end of the line
  labelDy?: number
}
export interface Mark { x: number, y?: number, color?: string, label?: string, dash?: string, r?: number, anchor?: 'start' | 'middle' | 'end', dy?: number }
export interface Band { x0: number, x1: number, color: string, opacity?: number, label?: string }
export type Tick = number | { v: number, t: string }

const props = withDefaults(defineProps<{
  series: Series[]
  width?: number
  height?: number
  xRange?: [number, number]
  yRange?: [number, number]
  xLog?: boolean
  yLog?: boolean
  xTicks?: Tick[]
  yTicks?: Tick[]
  xLabel?: string
  yLabel?: string
  title?: string
  vlines?: Mark[]
  hlines?: { y: number, color?: string, label?: string, dash?: string }[]
  bands?: Band[]
  points?: Mark[]
  texts?: { x: number, y: number, text: string, color?: string, anchor?: 'start' | 'middle' | 'end', size?: number, weight?: number }[]
  visible?: boolean[]
  draw?: number
  font?: number
  legend?: { color: string, text: string, dash?: string, show?: boolean }[]
  legendAt?: 'tl' | 'tr' | 'bl' | 'br'
}>(), { width: 520, height: 300, draw: 1, font: 12, legendAt: 'tr' })

const uid = useId()
const M = computed(() => ({ l: props.yLabel ? 52 : 40, r: 14, t: props.title ? 26 : 10, b: props.xLabel ? 40 : 24 }))
const xs = (s: Series) => s.x ?? s.y.map((_, i) => i + 1)

const ext = computed(() => {
  const allX = props.series.flatMap(xs)
  const allY = props.series.flatMap(s => s.y.filter((v): v is number => v != null && Number.isFinite(v)))
  return {
    x: props.xRange ?? [Math.min(...allX), Math.max(...allX)] as [number, number],
    y: props.yRange ?? [Math.min(...allY), Math.max(...allY)] as [number, number],
  }
})
const tx = (v: number, log?: boolean) => (log ? Math.log10(v) : v)
const sx = (v: number) => {
  const [a, b] = ext.value.x
  return M.value.l + (tx(v, props.xLog) - tx(a, props.xLog)) / (tx(b, props.xLog) - tx(a, props.xLog)) * (props.width - M.value.l - M.value.r)
}
const sy = (v: number) => {
  const [a, b] = ext.value.y
  return props.height - M.value.b - (tx(v, props.yLog) - tx(a, props.yLog)) / (tx(b, props.yLog) - tx(a, props.yLog)) * (props.height - M.value.t - M.value.b)
}
const xMax = computed(() => {
  const [a, b] = ext.value.x
  return props.xLog ? 10 ** (tx(a, true) + (tx(b, true) - tx(a, true)) * props.draw) : a + (b - a) * props.draw
})

function linePath(s: Series) {
  const X = xs(s); const segs: number[][][] = [[]]
  s.y.forEach((v, i) => {
    if (X[i] > xMax.value + 1e-9) return
    if (v == null || !Number.isFinite(v) || (props.yLog && v <= 0)) { if (segs.at(-1)!.length) segs.push([]); return }
    segs.at(-1)!.push([sx(X[i]), sy(v)])
  })
  return segs.filter(g => g.length > 1).map(pathOf).join(' ')
}
function lastPoint(s: Series) {
  const X = xs(s)
  for (let i = s.y.length - 1; i >= 0; i--) {
    const v = s.y[i]
    if (X[i] <= xMax.value + 1e-9 && v != null && Number.isFinite(v)) return [sx(X[i]), sy(v)]
  }
  return null
}

function autoTicks(range: [number, number], log?: boolean): Tick[] {
  const [a, b] = range
  if (log) {
    const out: Tick[] = []
    for (let e = Math.ceil(Math.log10(a) - 1e-9); e <= Math.floor(Math.log10(b) + 1e-9); e++) out.push({ v: 10 ** e, t: e === 0 ? '1' : e === 1 ? '10' : e === 2 ? '100' : `10${sup(e)}` })
    return out
  }
  const span = b - a; const raw = span / 5; const p = 10 ** Math.floor(Math.log10(raw))
  const step = [1, 2, 2.5, 5, 10].map(m => m * p).find(s => span / s <= 6)!
  const out: Tick[] = []
  for (let v = Math.ceil(a / step - 1e-9) * step; v <= b + 1e-9; v += step) out.push(Number(v.toFixed(10)))
  return out
}
const sup = (e: number) => String(e).split('').map(c => '⁰¹²³⁴⁵⁶⁷⁸⁹⁻'['0123456789-'.indexOf(c)]).join('')
const tickList = (t: Tick[] | undefined, r: [number, number], log?: boolean) =>
  (t ?? autoTicks(r, log)).map(k => (typeof k === 'number' ? { v: k, t: String(k) } : k)).filter(k => k.v >= r[0] - 1e-9 && k.v <= r[1] + 1e-9)
const XT = computed(() => tickList(props.xTicks, ext.value.x, props.xLog))
const YT = computed(() => tickList(props.yTicks, ext.value.y, props.yLog))
const vis = (i: number) => props.visible?.[i] ?? true
const f = (k = 1) => ({ fontSize: `${props.font * k}px` })
// legend box: width from the longest entry (≈ 0.55 em per character)
const LG = computed(() => {
  const items = props.legend ?? []
  const w = 34 + Math.max(0, ...items.map(i => i.text.length)) * props.font * 0.55
  const h = items.length * props.font * 1.5 + 8
  const right = props.legendAt.endsWith('r'); const top = props.legendAt.startsWith('t')
  return { items, w, h, x: right ? props.width - M.value.r - w - 6 : M.value.l + 6, y: top ? M.value.t + 6 : props.height - M.value.b - h - 6 }
})
</script>

<template>
  <svg :viewBox="`0 0 ${width} ${height}`" class="w-full" role="img" :aria-label="title ?? 'line chart'">
    <defs>
      <clipPath :id="`clip-${uid}`">
        <rect :x="M.l" :y="M.t - 2" :width="width - M.l - M.r" :height="height - M.t - M.b + 4" />
      </clipPath>
    </defs>
    <text v-if="title" :x="M.l" y="16" :style="{ ...f(1.1), fill: C.text, fontWeight: 700 }">{{ title }}</text>

    <!-- grid and axes -->
    <g>
      <line v-for="t in YT" :key="`gy${t.v}`" :x1="M.l" :x2="width - M.r" :y1="sy(t.v)" :y2="sy(t.v)" :style="{ stroke: C.grid, strokeOpacity: 0.6 }" />
      <text v-for="t in YT" :key="`ty${t.v}`" :x="M.l - 6" :y="sy(t.v) + 4" text-anchor="end" :style="{ ...f(0.95), fill: C.muted }">{{ t.t }}</text>
      <text v-for="t in XT" :key="`tx${t.v}`" :x="sx(t.v)" :y="height - M.b + 15" text-anchor="middle" :style="{ ...f(0.95), fill: C.muted }">{{ t.t }}</text>
      <line :x1="M.l" :x2="M.l" :y1="M.t" :y2="height - M.b" :style="{ stroke: C.dim }" />
      <line :x1="M.l" :x2="width - M.r" :y1="height - M.b" :y2="height - M.b" :style="{ stroke: C.dim }" />
      <text v-if="xLabel" :x="(M.l + width - M.r) / 2" :y="height - 6" text-anchor="middle" :style="{ ...f(), fill: C.muted }">{{ xLabel }}</text>
      <text v-if="yLabel" :transform="`translate(14 ${(M.t + height - M.b) / 2}) rotate(-90)`" text-anchor="middle" :style="{ ...f(), fill: C.muted }">{{ yLabel }}</text>
    </g>

    <g :clip-path="`url(#clip-${uid})`">
      <rect v-for="(b, i) in bands" :key="`b${i}`" :x="sx(b.x0)" :y="M.t" :width="Math.max(0, sx(Math.min(b.x1, xMax)) - sx(b.x0))" :height="height - M.t - M.b" :style="{ fill: b.color, fillOpacity: b.opacity ?? 0.15 }" />
      <line v-for="(h, i) in hlines" :key="`h${i}`" :x1="M.l" :x2="width - M.r" :y1="sy(h.y)" :y2="sy(h.y)" :style="{ stroke: h.color ?? C.muted, strokeDasharray: h.dash ?? '5 4', strokeWidth: 1.5 }" />
      <line v-for="(v, i) in vlines" :key="`v${i}`" :x1="sx(v.x)" :x2="sx(v.x)" :y1="M.t" :y2="height - M.b" :style="{ stroke: v.color ?? C.muted, strokeDasharray: v.dash ?? '4 4', strokeWidth: 1.5 }" />
      <path
        v-for="(s, i) in series" :key="`s${i}`" :d="linePath(s)"
        :style="{ fill: 'none', stroke: s.color, strokeWidth: s.width ?? 2.5, strokeDasharray: s.dash, strokeLinejoin: 'round', strokeLinecap: 'round', opacity: vis(i) ? (s.opacity ?? 1) : 0, transition: 'opacity .5s' }"
      />
      <circle v-for="(p, i) in points" :key="`p${i}`" :cx="sx(p.x)" :cy="sy(p.y!)" :r="p.r ?? 5" :style="{ fill: p.color ?? C.amber }" />
    </g>

    <!-- labels outside the clip -->
    <text v-for="(b, i) in (bands ?? []).filter(b => b.label)" :key="`bl${i}`" :x="(sx(b.x0) + sx(b.x1)) / 2" :y="M.t + 14" text-anchor="middle" :style="{ ...f(0.95), fill: b.color }">{{ b.label }}</text>
    <text v-for="(h, i) in (hlines ?? []).filter(h => h.label)" :key="`hl${i}`" :x="width - M.r - 4" :y="sy(h.y) - 5" text-anchor="end" :style="{ ...f(0.95), fill: h.color ?? C.muted }">{{ h.label }}</text>
    <text v-for="(v, i) in (vlines ?? []).filter(v => v.label)" :key="`vl${i}`" :x="sx(v.x) + (v.dy ?? 4)" :y="M.t + 12" :text-anchor="v.anchor ?? 'start'" :style="{ ...f(0.95), fill: v.color ?? C.muted }">{{ v.label }}</text>
    <text v-for="(p, i) in (points ?? []).filter(p => p.label)" :key="`pl${i}`" :x="sx(p.x)" :y="sy(p.y!) + (p.dy ?? -10)" :text-anchor="p.anchor ?? 'middle'" :style="{ ...f(0.95), fill: p.color ?? C.amber, fontWeight: 700 }">{{ p.label }}</text>
    <text v-for="(t, i) in texts" :key="`t${i}`" :x="sx(t.x)" :y="sy(t.y)" :text-anchor="t.anchor ?? 'start'" :style="{ ...f(t.size ?? 1), fill: t.color ?? C.text, fontWeight: t.weight ?? 400 }">{{ t.text }}</text>
    <g v-if="LG.items.length">
      <rect :x="LG.x" :y="LG.y" :width="LG.w" :height="LG.h" rx="6" :style="{ fill: C.bg, fillOpacity: 0.92, stroke: C.grid }" />
      <g v-for="(it, i) in LG.items" :key="`lg${i}`" :style="{ opacity: it.show === false ? 0 : 1, transition: 'opacity .5s' }">
        <line :x1="LG.x + 8" :x2="LG.x + 26" :y1="LG.y + 4 + font * (1.5 * i + 0.95)" :y2="LG.y + 4 + font * (1.5 * i + 0.95)" :style="{ stroke: it.color, strokeWidth: 3, strokeDasharray: it.dash }" />
        <text :x="LG.x + 32" :y="LG.y + 4 + font * (1.5 * i + 1.3)" :style="{ ...f(), fill: it.color }">{{ it.text }}</text>
      </g>
    </g>
    <template v-for="(s, i) in series" :key="`l${i}`">
      <text v-if="s.label && lastPoint(s)" :x="lastPoint(s)![0] + 6" :y="lastPoint(s)![1] + 4 + (s.labelDy ?? 0)" :style="{ ...f(), fill: s.color, fontWeight: 700, opacity: vis(i) ? 1 : 0, transition: 'opacity .5s' }">{{ s.label }}</text>
    </template>
  </svg>
</template>
