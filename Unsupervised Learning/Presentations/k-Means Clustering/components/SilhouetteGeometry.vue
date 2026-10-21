<script setup lang="ts">
// Silhouette of one boundary point on blobs3 (data/blobs3.json → probe).
// clicks: 0 the point · 1 a = mean distance to its own cluster · 2 b = mean distance
//         to the nearest other cluster · 3 the score s = (b − a) / max(a, b)
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import run from '../data/blobs3.json'
import { color, domainOf, equalScale } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const s = computed(() => $clicks.value)
const fin = run.frames[run.frames.length - 1]
const lab = fin.lab as number[]
const pts = run.pts as number[][]
const i0 = run.probe
const p0 = pts[i0]
const own = lab[i0]
const dist = (q: number[]) => Math.hypot(q[0] - p0[0], q[1] - p0[1])
const meanTo = (k: number) => {
  const m = pts.filter((_, j) => lab[j] === k && j !== i0)
  return m.reduce((acc, q) => acc + dist(q), 0) / m.length
}
const a = meanTo(own)
const others = [0, 1, 2].filter(k => k !== own).map(k => ({ k, v: meanTo(k) })).sort((x, y) => x.v - y.v)
const nb = others[0].k
const b = others[0].v
const sil = (b - a) / Math.max(a, b)

const W = 520; const H = 380
const S = equalScale(domainOf(pts, 0.06), W, H)
const linesTo = (k: number) => pts.map((q, j) => (lab[j] === k && j !== i0 ? `M${S.sx(p0[0])},${S.sy(p0[1])}L${S.sx(q[0])},${S.sy(q[1])}` : '')).join('')
const dOwn = linesTo(own)
const dNb = linesTo(nb)
</script>

<template>
  <div class="grid grid-cols-[1.4fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Silhouette of one point: a = ${a.toFixed(2)}, b = ${b.toFixed(2)}, s = ${sil.toFixed(2)}`">
      <path :d="dOwn" class="ln" :style="{ stroke: color(own), strokeOpacity: s >= 1 ? 0.35 : 0, strokeWidth: 1 }" />
      <path :d="dNb" class="ln" :style="{ stroke: color(nb), strokeOpacity: s >= 2 ? 0.3 : 0, strokeWidth: 1 }" />
      <circle
        v-for="(q, j) in pts" :key="j" :cx="S.sx(q[0])" :cy="S.sy(q[1])" r="3.4" class="pt"
        :style="{ fill: color(lab[j]), fillOpacity: (lab[j] === own && s >= 1) || (lab[j] === nb && s >= 2) || s === 0 ? 0.9 : 0.25 }"
      />
      <circle :cx="S.sx(p0[0])" :cy="S.sy(p0[1])" r="9" :style="{ fill: color(own), stroke: '#fff', strokeWidth: 3 }" />
    </svg>
    <div class="space-y-3 text-left">
      <div class="card" :class="{ off: s < 1 }" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>
        <div class="text-sm opacity-80"><b :style="{ color: color(own) }">a(x)</b>: average distance to the other points <b>in its own cluster</b></div>
        <div class="font-mono text-xl mt-1">a = {{ a.toFixed(2) }}</div>
      </div>
      <div class="card" :class="{ off: s < 2 }" border="2 solid white/10" bg="white/5" rounded-lg px-4 py-2>
        <div class="text-sm opacity-80"><b :style="{ color: color(nb) }">b(x)</b>: average distance to the points of the <b>nearest other</b> cluster</div>
        <div class="font-mono text-xl mt-1">b = {{ b.toFixed(2) }}</div>
      </div>
      <div class="card" :class="{ off: s < 3 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
        <div class="text-sm opacity-80">s(x) = (b − a) / max(a, b)</div>
        <div class="font-mono text-xl mt-1 text-amber-300">s = {{ sil.toFixed(2) }}</div>
        <div class="text-xs opacity-70 mt-1">+1 deep inside its cluster · 0 on the border · negative: probably in the wrong cluster</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ln { transition: stroke-opacity 0.6s ease; }
.pt { transition: fill-opacity 0.6s ease; }
.card { transition: opacity 0.5s ease, transform 0.5s ease; }
.off { opacity: 0; transform: translateX(14px); }
</style>
