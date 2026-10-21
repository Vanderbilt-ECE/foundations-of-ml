<script setup lang="ts">
// Scatter of model A error vs model B error at one input x0, one dot per training draw.
// Points are built so the sample correlation is exactly rho; the same draws are used for every rho.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const props = withDefaults(defineProps<{ rho: number, color?: string, n?: number }>(), { color: '#2dd4bf', n: 60 })

function rng(seed: number) {
  return () => {
    seed = (seed + 0x6D2B79F5) | 0
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
const rand = rng(670)
const normal = () => Math.sqrt(-2 * Math.log(1 - rand())) * Math.cos(2 * Math.PI * rand())
const mean = (v: number[]) => v.reduce((s, x) => s + x, 0) / v.length
const dot = (u: number[], v: number[]) => u.reduce((s, x, i) => s + x * v[i], 0)
const center = (v: number[]) => { const m = mean(v); return v.map(x => x - m) }
const unit = (v: number[]) => { const s = Math.sqrt(dot(v, v) / v.length); return v.map(x => x / s) }

const z1 = unit(center(Array.from({ length: props.n }, normal)))
let z2 = center(Array.from({ length: props.n }, normal))
const proj = dot(z2, z1) / dot(z1, z1)
z2 = unit(z2.map((x, i) => x - proj * z1[i]))

const a = z1
const b = z1.map((x, i) => props.rho * x + Math.sqrt(1 - props.rho ** 2) * z2[i])
// highlight the draw where model A overshoots the most
const hi = a.indexOf(Math.max(...a))

const size = 220
const pad = 30
// same scale for every rho, with room so no dot sits on the frame
const lim = 1.1 * Math.max(...z1.map(Math.abs), ...z2.map(Math.abs))
const sx = (v: number) => pad + (Math.max(-lim, Math.min(lim, v)) + lim) / (2 * lim) * size
const sy = (v: number) => pad + (lim - Math.max(-lim, Math.min(lim, v))) / (2 * lim) * size
const pts = a.map((x, i) => ({ key: i, cx: sx(x), cy: sy(b[i]) })).filter(p => p.key !== hi)
const hp = { cx: sx(a[hi]), cy: sy(b[hi]) }
const rhoLabel = props.rho < 0 ? `−${-props.rho}` : `${props.rho}`
const W = pad + size + 10
const H = pad + size + 26
</script>

<template>
  <svg role="img" :aria-label="`Scatter of model A error against model B error, correlation ${rho}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <rect :x="pad" :y="pad" :width="size" :height="size" rx="6" :style="{ fill: '#ffffff', fillOpacity: 0.03, stroke: '#475569', strokeWidth: 1 }" />
    <line :x1="pad" :x2="pad + size" :y1="sy(0)" :y2="sy(0)" stroke="#64748b" stroke-width="1" stroke-dasharray="4 4" />
    <line :x1="sx(0)" :x2="sx(0)" :y1="pad" :y2="pad + size" stroke="#64748b" stroke-width="1" stroke-dasharray="4 4" />
    <circle v-for="p in pts" :key="p.key" :cx="p.cx" :cy="p.cy" r="4.5" :style="{ fill: color, fillOpacity: 0.6 }" />
    <circle :cx="hp.cx" :cy="hp.cy" r="7" :style="{ fill: '#fbbf24', stroke: '#0f172a', strokeWidth: 1.5 }" />
    <text :x="sx(0)" :y="pad + size + 18" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '13px' }">model A error →</text>
    <text :x="14" :y="sy(0)" text-anchor="middle" :transform="`rotate(-90 14 ${sy(0)})`" :style="{ fill: '#94a3b8', fontSize: '13px' }">model B error →</text>
    <text :x="pad + size / 2" :y="pad - 10" text-anchor="middle" :style="{ fill: color, fontSize: '17px', fontWeight: 700 }">ρ = {{ rhoLabel }}</text>
  </svg>
</template>
