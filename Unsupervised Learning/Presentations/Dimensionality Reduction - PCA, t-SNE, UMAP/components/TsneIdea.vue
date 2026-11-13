<script setup lang="ts">
// t-SNE in one picture. Left: 18 points in 3 clusters in the original space, drawn in 3D (standing in for
// high dimensions) with their neighbor links p_ij (thicker = closer). It orbits slowly; drag to rotate.
// Right: the 2D map. The map points start scrambled and slide into place; each link is drawn in the map too,
// red while it is stretched, teal once matched. The finished map keeps every cluster's neighbors together but
// places the clusters in a different arrangement than the original: t-SNE keeps neighborhoods, not positions.
// The map loops while the slide is showing; the PDF export shows the finished map and a static 3D view.
import { computed, ref } from 'vue'
import { rng, useActive, useLoop } from '../utils/plot'

const R = rng(21)
const COLS = ['#2dd4bf', '#fbbf24', '#a78bfa']
const centers3 = [[-1.2, 0.5, 0.9], [1.1, 1.0, -0.8], [0.2, -1.2, 0.1]]
const lab = Array.from({ length: 18 }, (_, i) => i % 3)
const offs = lab.map(() => [0.32 * R.n(), 0.32 * R.n(), 0.32 * R.n()])
const hi = lab.map((c, i) => centers3[c].map((v, k) => v + offs[i][k]))

// neighbor links in the original space
const links: { i: number, j: number, w: number }[] = []
hi.forEach((p, i) => hi.forEach((q, j) => {
  const d = Math.hypot(p[0] - q[0], p[1] - q[1], p[2] - q[2])
  if (i < j && d < 0.95) links.push({ i, j, w: Math.exp(-d * d / 0.3) })
}))

// --- left: 3D view (Plotly). Links in two weight bins, since a Plotly line trace has one width. ---
const linkTrace = (keep: (w: number) => boolean, width: number, opacity: number) => {
  const x: (number | null)[] = []; const y: (number | null)[] = []; const z: (number | null)[] = []
  for (const l of links.filter(l => keep(l.w))) {
    x.push(hi[l.i][0], hi[l.j][0], null); y.push(hi[l.i][1], hi[l.j][1], null); z.push(hi[l.i][2], hi[l.j][2], null)
  }
  return { type: 'scatter3d', mode: 'lines', hoverinfo: 'skip', x, y, z, line: { color: `rgba(203,213,225,${opacity})`, width } }
}
const data3 = [
  linkTrace(w => w < 0.5, 2, 0.35),
  linkTrace(w => w >= 0.5, 5, 0.75),
  {
    type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
    x: hi.map(p => p[0]), y: hi.map(p => p[1]), z: hi.map(p => p[2]),
    marker: { size: 6, color: lab.map(c => COLS[c]), line: { color: '#0b1020', width: 1 } },
  },
]
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout3 = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: axis('x₃'), aspectmode: 'cube', camera: { eye: { x: 1.5, y: 1.5, z: 0.9 } } } }

// --- right: 2D map. Clusters land in a different arrangement; within a cluster, neighbors stay close. ---
const mapCenters = [[0.9, -0.8], [-1.0, -0.3], [0.5, 0.95]]
const target = lab.map((c, i) => [mapCenters[c][0] + 0.9 * offs[i][0], mapCenters[c][1] + 0.9 * offs[i][1]])
const start = hi.map(() => [1.8 * (R.u() - 0.5), 1.8 * (R.u() - 0.5)])

const { isPrintMode } = useActive()
const u = ref(isPrintMode.value ? 1 : 0)
useLoop((_, t) => {
  const c = t % 8 // 1 s scrambled, 4.5 s settling, 2.5 s hold
  u.value = Math.min(1, Math.max(0, (c - 1) / 4.5))
}, () => { u.value = 0 })
const e = computed(() => 1 - (1 - u.value) ** 3)
const map = computed(() => start.map((s, i) => [s[0] + (target[i][0] - s[0]) * e.value, s[1] + (target[i][1] - s[1]) * e.value]))

const W = 300; const H = 270; const U = 82
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const stretch = (l: { i: number, j: number }) => {
  const a = map.value[l.i]; const b = map.value[l.j]
  const dm = Math.hypot(a[0] - b[0], a[1] - b[1])
  const dt = Math.hypot(target[l.i][0] - target[l.j][0], target[l.i][1] - target[l.j][1])
  return Math.min(1, Math.abs(dm - dt) / 0.6)
}
const mixC = (s: number) => `rgb(${Math.round(45 + (248 - 45) * s)},${Math.round(212 + (113 - 212) * s)},${Math.round(191 + (113 - 191) * s)})`
</script>

<template>
  <div class="grid grid-cols-[1fr_auto_1fr] gap-2 items-center">
    <div class="text-center">
      <div class="text-sm font-bold text-teal-300">original space: pᵢⱼ</div>
      <div class="text-xs opacity-60 mb-1">high-dimensional (drawn in 3D)</div>
      <div class="rounded-[10px] overflow-hidden mx-auto" style="width: 300px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08)">
        <PlotlyChart :data="data3" :layout="layout3" :width="300" :height="270" spin />
      </div>
    </div>
    <div class="text-3xl opacity-60 px-1">⟶</div>
    <div class="text-center">
      <div class="text-sm font-bold text-amber-300">2D map: qᵢⱼ</div>
      <div class="text-xs opacity-60 mb-1">same neighbors, new layout</div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="mx-auto block" style="width: 300px; height: 270px" role="img" aria-label="Points in the 2D map moving until their links match">
        <rect x="1" y="1" :width="W - 2" :height="H - 2" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: 'rgba(255,255,255,0.08)' }" />
        <line v-for="(l, k) in links" :key="k" :x1="sx(map[l.i][0])" :y1="sy(map[l.i][1])" :x2="sx(map[l.j][0])" :y2="sy(map[l.j][1])" :style="{ stroke: mixC(stretch(l)), strokeOpacity: 0.3 + 0.5 * l.w, strokeWidth: 0.5 + 3 * l.w }" />
        <circle v-for="(p, i) in map" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="6" :style="{ fill: COLS[lab[i]], stroke: '#0b1020', strokeWidth: 1.5 }" />
      </svg>
    </div>
  </div>
</template>
