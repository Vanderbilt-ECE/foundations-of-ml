<script setup lang="ts">
// t-SNE's first step: Gaussian neighbor probabilities p_{j|i}, with a bandwidth σᵢ per point chosen so the
// perplexity (2 to the entropy, an "effective number of neighbors") hits the target.
// A tight cluster (left) and a diffuse one (right). Click a point to make it i; the slider sets the perplexity.
// Each other point is drawn bigger and brighter the larger its p_{j|i}; the rings are σᵢ and 2σᵢ.
import { computed, ref } from 'vue'
import { rng, toLocal } from '../utils/plot'
import { condRow } from '../utils/tsne'

const R = rng(5)
const P = [
  ...Array.from({ length: 40 }, () => [-1.6 + 0.28 * R.n(), 0.2 + 0.28 * R.n()]),
  ...Array.from({ length: 30 }, () => [1.4 + 0.95 * R.n(), -0.1 + 0.95 * R.n()]),
]
const n = P.length
const D2 = P.map(p => P.map(q => (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2))
const i = ref(3)
const perp = ref(10)
const row = computed(() => condRow(D2[i.value], i.value, perp.value))
const pmax = computed(() => Math.max(...row.value.p))
const H2 = computed(() => -row.value.p.reduce((s, v) => s + (v > 1e-12 ? v * Math.log2(v) : 0), 0))

const W = 440; const H = 300; const U = 70
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
function pick(e: PointerEvent) {
  const [x, y] = toLocal(e, e.currentTarget as Element, W, H)
  let best = 0; let bd = Infinity
  P.forEach((p, j) => {
    const dd = (sx(p[0]) - x) ** 2 + (sy(p[1]) - y) ** 2
    if (dd < bd) { bd = dd; best = j }
  })
  i.value = best
}
</script>

<template>
  <div class="grid grid-cols-[1.45fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 320px; cursor: pointer" role="img" aria-label="Two clusters of different density; around the chosen point, rings show its Gaussian bandwidth" @pointerdown="pick">
      <circle v-for="s in [2, 1]" :key="s" :cx="sx(P[i][0])" :cy="sy(P[i][1])" :r="s * row.sigma * U" class="ring" :style="{ fill: 'rgba(251,191,36,0.06)', stroke: '#fbbf24', strokeOpacity: s === 1 ? 0.9 : 0.4, strokeDasharray: s === 2 ? '4 4' : 'none' }" />
      <circle
        v-for="(p, j) in P" :key="j" :cx="sx(p[0])" :cy="sy(p[1])" :r="j === i ? 7 : 2.5 + 7 * Math.sqrt(row.p[j] / pmax)"
        :style="{ fill: j === i ? '#fbbf24' : '#2dd4bf', fillOpacity: j === i ? 1 : 0.18 + 0.82 * Math.sqrt(row.p[j] / pmax), stroke: j === i ? '#0b1020' : 'none', strokeWidth: 2, transition: 'r 0.3s, fill-opacity 0.3s' }"
      />
    </svg>
    <div class="text-left space-y-3">
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="w-28">perplexity {{ perp }}</span>
        <input v-model.number="perp" type="range" min="2" max="40" class="flex-1" style="accent-color: #fbbf24">
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1">
        <div class="text-amber-300">σᵢ = {{ row.sigma.toFixed(3) }}</div>
        <div>2^H(Pᵢ) = {{ (2 ** H2).toFixed(1) }} <span class="opacity-60">≈ effective neighbors</span></div>
        <div class="opacity-80">largest p_j|i = {{ pmax.toFixed(3) }}</div>
      </div>
      <div class="text-xs opacity-70">Click a point in the tight cluster, then one in the diffuse cluster: same perplexity, very different σ.</div>
    </div>
  </div>
</template>

<style scoped>
.ring { transition: r 0.35s ease; }
</style>
