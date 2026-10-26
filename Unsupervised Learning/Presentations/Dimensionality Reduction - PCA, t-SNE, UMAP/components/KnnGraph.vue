<script setup lang="ts">
// The k-nearest-neighbor graph of the spiral: an edge from every point to its k nearest (straight-line) neighbors.
// Small k: the graph follows the curve, so paths through the graph measure distance along the manifold.
// Large k: edges jump between arms (red "short circuits") and the graph no longer knows the shape.
// Press play to sweep k. This graph is the first step of Isomap, t-SNE (perplexity) and UMAP (n_neighbors).
import { computed, onBeforeUnmount, ref } from 'vue'
import { spiral } from '../utils/plot'

const S = spiral()
const n = S.pts.length
const W = 330; const H = 320; const U = 68
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const k = ref(6)
const KMAX = 40
const order = S.pts.map((p, i) => S.pts.map((q, j) => [Math.hypot(p[0] - q[0], p[1] - q[1]), j]).filter(([, j]) => j !== i).sort((a, b) => a[0] - b[0]).slice(0, KMAX).map(([, j]) => j))
const edges = computed(() => {
  const seen = new Set<string>()
  const out: { i: number, j: number, bad: boolean }[] = []
  for (let i = 0; i < n; i++) {
    for (const j of order[i].slice(0, k.value)) {
      const key = i < j ? `${i}-${j}` : `${j}-${i}`
      if (seen.has(key)) continue
      seen.add(key)
      const eu = Math.hypot(S.pts[i][0] - S.pts[j][0], S.pts[i][1] - S.pts[j][1])
      out.push({ i, j, bad: Math.abs(S.s[i] - S.s[j]) > 2.5 * eu + 0.3 })
    }
  }
  return out
})
const nBad = computed(() => edges.value.filter(e => e.bad).length)
let timer: ReturnType<typeof setInterval> | undefined
function play() {
  clearInterval(timer)
  k.value = 1
  timer = setInterval(() => (k.value >= KMAX ? clearInterval(timer) : k.value++), 220)
}
onBeforeUnmount(() => clearInterval(timer))
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 330px" role="img" aria-label="k-nearest-neighbor graph of a spiral; with large k, edges jump between arms">
      <line
        v-for="e in edges" :key="`${e.i}-${e.j}`" :x1="sx(S.pts[e.i][0])" :y1="sy(S.pts[e.i][1])" :x2="sx(S.pts[e.j][0])" :y2="sy(S.pts[e.j][1])"
        :style="{ stroke: e.bad ? '#f87171' : '#2dd4bf', strokeOpacity: e.bad ? 0.75 : 0.35, strokeWidth: e.bad ? 1.4 : 1 }"
      />
      <circle v-for="(p, i) in S.pts" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="2.6" :style="{ fill: '#e2e8f0' }" />
    </svg>
    <div class="text-left space-y-3">
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="w-14 text-lg text-amber-300">k = {{ k }}</span>
        <input v-model.number="k" type="range" min="1" :max="KMAX" class="flex-1" style="accent-color: #fbbf24">
        <button class="px-2 py-0.5 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10" @click="play">▶</button>
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1">
        <div>edges: {{ edges.length }}</div>
        <div :class="nBad ? 'text-red-300' : 'text-teal-300'">short circuits: {{ nBad }}</div>
      </div>
      <div class="text-sm opacity-85">
        <span class="text-teal-300 font-bold">Too small</span>: the graph falls apart into pieces.
        <span class="text-red-300 font-bold">Too large</span>: it bridges arms that are far apart on the curve.
      </div>
    </div>
  </div>
</template>
