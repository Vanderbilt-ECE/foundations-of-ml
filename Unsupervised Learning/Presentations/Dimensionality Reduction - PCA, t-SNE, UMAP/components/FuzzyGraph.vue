<script setup lang="ts">
// UMAP's graph on the spiral. For each point i: ρᵢ = distance to its nearest neighbor, and σᵢ chosen so that
// Σⱼ exp(−(dᵢⱼ − ρᵢ)/σᵢ) = log₂(k) over its k nearest neighbors. Directed weights wᵢⱼ = exp(−(dᵢⱼ − ρᵢ)/σᵢ),
// then the fuzzy union w = a + b − ab. Edge opacity = weight. Hover a point: its own k edges and its ρ ring.
// Every point is connected at weight 1 to its nearest neighbor, however sparse its region ("local connectivity").
import { computed, ref } from 'vue'
import { ramp, spiral, toLocal } from '../utils/plot'

const S = spiral(160, 9, 0.035)
const n = S.pts.length
const W = 330; const H = 320; const U = 68
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const k = ref(8)
const dist = (i: number, j: number) => Math.hypot(S.pts[i][0] - S.pts[j][0], S.pts[i][1] - S.pts[j][1])
const order = S.pts.map((_, i) => S.pts.map((__, j) => j).filter(j => j !== i).sort((a, b) => dist(i, a) - dist(i, b)))

const graph = computed(() => {
  const target = Math.log2(k.value)
  const w = new Map<string, number>()
  const dir: { j: number, w: number }[][] = []
  const rho: number[] = []
  for (let i = 0; i < n; i++) {
    const nb = order[i].slice(0, k.value)
    const r = dist(i, nb[0])
    let lo = 1e-6; let hi = 10; let s = 1
    for (let t = 0; t < 50; t++) {
      s = (lo + hi) / 2
      const sum = nb.reduce((a, j) => a + Math.exp(-Math.max(0, dist(i, j) - r) / s), 0)
      if (sum > target) hi = s; else lo = s
    }
    rho.push(r)
    dir.push(nb.map(j => ({ j, w: Math.exp(-Math.max(0, dist(i, j) - r) / s) })))
  }
  dir.forEach((row, i) => row.forEach(({ j, w: a }) => {
    const key = i < j ? `${i}-${j}` : `${j}-${i}`
    const b = w.get(key) ?? 0
    w.set(key, a + b - a * b) // fuzzy union of the two directions
  }))
  return { edges: [...w.entries()].map(([key, v]) => ({ i: +key.split('-')[0], j: +key.split('-')[1], w: v })), dir, rho }
})
const hot = ref<number | null>(null)
function move(e: PointerEvent) {
  const [x, y] = toLocal(e, e.currentTarget as Element, W, H)
  let best = -1; let bd = 15 ** 2
  S.pts.forEach((p, j) => {
    const dd = (sx(p[0]) - x) ** 2 + (sy(p[1]) - y) ** 2
    if (dd < bd) { bd = dd; best = j }
  })
  hot.value = best < 0 ? null : best
}
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 330px" role="img" aria-label="A weighted neighbor graph on a spiral" @pointermove="move" @pointerleave="hot = null">
      <line
        v-for="e in graph.edges" :key="`${e.i}-${e.j}`" :x1="sx(S.pts[e.i][0])" :y1="sy(S.pts[e.i][1])" :x2="sx(S.pts[e.j][0])" :y2="sy(S.pts[e.j][1])"
        :style="{ stroke: '#2dd4bf', strokeOpacity: hot == null ? 0.25 + 0.7 * e.w : 0.08, strokeWidth: 1 + 2.5 * e.w }"
      />
      <g v-if="hot != null">
        <circle :cx="sx(S.pts[hot][0])" :cy="sy(S.pts[hot][1])" :r="graph.rho[hot] * U" :style="{ fill: 'none', stroke: '#fbbf24', strokeDasharray: '3 3' }" />
        <line
          v-for="o in graph.dir[hot]" :key="o.j" :x1="sx(S.pts[hot][0])" :y1="sy(S.pts[hot][1])" :x2="sx(S.pts[o.j][0])" :y2="sy(S.pts[o.j][1])"
          :style="{ stroke: '#fbbf24', strokeOpacity: 0.2 + 0.8 * o.w, strokeWidth: 0.8 + 3 * o.w }"
        />
      </g>
      <circle v-for="(p, i) in S.pts" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" :r="hot === i ? 6 : 3" :style="{ fill: ramp(S.s[i] / S.total), stroke: '#0b1020', strokeWidth: 1 }" />
    </svg>
    <div class="text-left space-y-3">
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="w-32">n_neighbors {{ k }}</span>
        <input v-model.number="k" type="range" min="3" max="30" class="flex-1" style="accent-color: #2dd4bf">
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1">
        <template v-if="hot != null">
          <div class="text-amber-300">ρ = {{ graph.rho[hot].toFixed(3) }} <span class="opacity-60">nearest neighbor</span></div>
          <div>weights: {{ graph.dir[hot].slice(0, 5).map(o => o.w.toFixed(2)).join(', ') }}, …</div>
        </template>
        <div v-else class="opacity-60">hover a point</div>
      </div>
      <div class="text-xs opacity-75">Edge opacity = fuzzy weight w = a + b − ab of the two directed weights.</div>
    </div>
  </div>
</template>
