<script setup lang="ts">
// Bias² and variance of five learners on the sine toy, measured over 200 fresh 50-point datasets
// (data/biasvar.json). Each bar stacks bias² (orange) and variance (sky); noise is not included.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/biasvar.json'

const groups = [
  { label: 'start from stumps', rows: [
    { key: 'stump', label: 'one stump', color: '#fbbf24' },
    { key: 'bagStump', label: '50 bagged stumps', color: '#60a5fa' },
    { key: 'boostStump', label: '100 boosted stumps', color: '#a78bfa' },
  ] },
  { label: 'start from deep trees', rows: [
    { key: 'deep', label: 'one deep tree', color: '#fbbf24' },
    { key: 'bagDeep', label: '50 bagged deep trees', color: '#60a5fa' },
  ] },
]
const src = d as Record<string, any>
const W = 620
const L = 170
const R = 560
const rowH = 34
const gapH = 30
const max = 0.12
const sx = (v: number) => L + v / max * (R - L)
let y = 26
const rows: any[] = []
const heads: any[] = []
for (const g of groups) {
  heads.push({ label: g.label, y: y + 4 })
  y += 12
  for (const r of g.rows) {
    const b = src[r.key].bias2
    const v = src[r.key].var
    rows.push({ ...r, y, b, v, total: b + v })
    y += rowH
  }
  y += gapH - 12
}
const H = y + 10
const ticks = [0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12]
</script>

<template>
  <svg role="img" :aria-label="`Bias squared and variance: ${rows.map(r => `${r.label} ${r.b} and ${r.v}`).join('; ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <g transform="translate(0, 0)">
      <rect :x="L" y="2" width="14" height="12" rx="2" :style="{ fill: '#fb923c', fillOpacity: 0.85 }" />
      <text :x="L + 20" y="12" :style="{ fill: '#fdba74', fontSize: '13px', fontWeight: 700 }">bias²</text>
      <rect :x="L + 80" y="2" width="14" height="12" rx="2" :style="{ fill: '#38bdf8', fillOpacity: 0.85 }" />
      <text :x="L + 100" y="12" :style="{ fill: '#7dd3fc', fontSize: '13px', fontWeight: 700 }">variance</text>
    </g>
    <line v-for="t in ticks" :key="t" :x1="sx(t)" :x2="sx(t)" y1="24" :y2="H - 26" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <text v-for="h in heads" :key="h.label" x="0" :y="h.y" :style="{ fill: '#94a3b8', fontSize: '12px', fontWeight: 700, letterSpacing: '0.05em' }">{{ h.label.toUpperCase() }}</text>
    <g v-for="r in rows" :key="r.key">
      <text :x="L - 12" :y="r.y + rowH / 2 + 5" text-anchor="end" :style="{ fill: r.color, fontSize: '14px', fontWeight: 700 }">{{ r.label }}</text>
      <rect :x="L" :y="r.y + 6" :width="sx(r.b) - L" :height="rowH - 12" :style="{ fill: '#fb923c', fillOpacity: 0.85 }" />
      <rect :x="sx(r.b)" :y="r.y + 6" :width="sx(r.total) - sx(r.b)" :height="rowH - 12" :style="{ fill: '#38bdf8', fillOpacity: 0.85 }" />
      <text :x="sx(r.total) + 8" :y="r.y + rowH / 2 + 5" :style="{ fill: '#e2e8f0', fontSize: '13px' }">{{ r.b.toFixed(3) }} + {{ r.v.toFixed(3) }}</text>
    </g>
    <text v-for="t in ticks" :key="`x${t}`" :x="sx(t)" :y="H - 10" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t.toFixed(2) }}</text>
  </svg>
</template>
