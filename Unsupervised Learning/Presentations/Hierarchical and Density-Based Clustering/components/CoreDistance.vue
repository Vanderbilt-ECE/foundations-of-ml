<script setup lang="ts">
// Core distances on the varied-density data (data/varied.json), computed here: the distance from each
// point to its k-th nearest neighbor. Small circles = dense neighborhood, big circles = sparse.
// k defaults to HDBSCAN's min_samples on the next slides (= min_cluster_size = 25).
// stage 0 points · 1 a circle for every 5th point · 2 one pair from each region, raw vs. mutual reachability distance.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/varied.json'
import { domainOf, equalScale } from '../utils/clusters'

const props = withDefaults(defineProps<{ k?: number, every?: number }>(), { k: 25, every: 5 })
const { $clicks } = useSlideContext()
const s = computed(() => Math.min($clicks.value, 2))
const pts = d.pts as number[][]
const n = pts.length
const dist = (i: number, j: number) => Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
const core = pts.map((_, i) => {
  const ds = pts.map((_, j) => dist(i, j)).sort((a, b) => a - b)
  return ds[props.k] // ds[0] is the point itself
})
const W = 420; const H = 360
const S = equalScale(domainOf(pts, 0.06), W, H)
// two example pairs: the point nearest a group's center and its nearest neighbor, in a tight blob and in the disk
function pairIn(label: number) {
  const idx = pts.map((_, i) => i).filter(i => d.truth[i] === label)
  const mx = idx.reduce((t, i) => t + pts[i][0], 0) / idx.length
  const my = idx.reduce((t, i) => t + pts[i][1], 0) / idx.length
  const a = idx.reduce((m, i) => (Math.hypot(pts[i][0] - mx, pts[i][1] - my) < Math.hypot(pts[m][0] - mx, pts[m][1] - my) ? i : m), idx[0])
  const b = idx.filter(i => i !== a).reduce((m, i) => (dist(a, i) < dist(a, m) ? i : m), idx.find(i => i !== a)!)
  return { a, b, d: dist(a, b), m: Math.max(core[a], core[b], dist(a, b)) }
}
const pairs = [pairIn(0), pairIn(2)]
const fmt = (v: number) => v.toFixed(2)
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Points with circles whose radius is the core distance; circles are tiny in dense blobs and large in the sparse disk">
      <g class="fade" :style="{ opacity: s >= 1 ? 1 : 0 }">
        <circle v-for="i in Array.from({ length: n }, (_, j) => j).filter(j => j % every === 0)" :key="`c${i}`" :cx="S.sx(pts[i][0])" :cy="S.sy(pts[i][1])" :r="core[i] * S.kx" :style="{ fill: 'none', stroke: d.truth[i] < 2 ? '#2dd4bf' : '#60a5fa', strokeOpacity: 0.45, strokeWidth: 1 }" />
      </g>
      <circle v-for="(p, i) in pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" r="2.4" :style="{ fill: '#e2e8f0', fillOpacity: 0.75 }" />
      <g class="fade" :style="{ opacity: s >= 2 ? 1 : 0 }">
        <g v-for="(pr, k) in pairs" :key="`p${k}`">
          <circle :cx="S.sx(pts[pr.a][0])" :cy="S.sy(pts[pr.a][1])" :r="core[pr.a] * S.kx" :style="{ fill: 'rgba(251,191,36,0.12)', stroke: '#fbbf24', strokeWidth: 2 }" />
          <circle :cx="S.sx(pts[pr.b][0])" :cy="S.sy(pts[pr.b][1])" :r="core[pr.b] * S.kx" :style="{ fill: 'rgba(251,191,36,0.12)', stroke: '#fbbf24', strokeWidth: 2 }" />
          <line :x1="S.sx(pts[pr.a][0])" :y1="S.sy(pts[pr.a][1])" :x2="S.sx(pts[pr.b][0])" :y2="S.sy(pts[pr.b][1])" :style="{ stroke: '#fbbf24', strokeWidth: 3 }" />
        </g>
      </g>
    </svg>
    <div class="space-y-3 text-left">
      <slot />
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
        <b>Core distance</b> of a point: how far to its {{ k }}th-nearest neighbor.
        <span class="text-teal-300">Small in dense blobs</span>, <span class="text-blue-300">large in the sparse disk</span>.
      </div>
      <div class="fade" :style="{ opacity: s >= 2 ? 1 : 0 }">
        <table class="pt">
          <thead><tr><th /><th>distance</th><th>mutual reach.</th></tr></thead>
          <tbody>
            <tr v-for="(pr, k) in pairs" :key="k">
              <td class="text-left">{{ k === 0 ? 'tight-blob pair' : 'disk pair' }}</td>
              <td class="font-mono">{{ fmt(pr.d) }}</td>
              <td class="font-mono text-amber-300 font-bold">{{ fmt(pr.m) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="text-xs opacity-80 mt-2">Inside a dense blob the two numbers are close. In the sparse disk, distances are stretched up to the core distance, so sparse points look farther apart than they are.</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade { transition: opacity 0.5s ease; }
.pt { border-collapse: separate; border-spacing: 6px 3px; font-size: 0.9rem; }
.pt th { font-size: 0.75rem; opacity: 0.7; font-weight: 600; }
.pt td { text-align: center; }
</style>
