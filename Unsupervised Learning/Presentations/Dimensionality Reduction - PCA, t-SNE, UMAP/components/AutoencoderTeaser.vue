<script setup lang="ts">
// Teaser for the neural-networks module: an autoencoder. A digit goes in (64 numbers), is squeezed through a
// 2-number bottleneck, and is rebuilt on the other side. Pulses run left to right along the connections.
// The output shown is PCA's own 2-component rebuild of the digit: PCA is the linear version of this network.
import { computed } from 'vue'
import d from '../data/digits.json'
import { decode } from '../utils/plot'

const x = decode(d.img[d.picks[2]])
const out = computed(() => {
  const z = d.V.slice(0, 2).map(v => v.reduce((s, vi, i) => s + vi * (x[i] - d.mean[i]), 0))
  return d.mean.map((m, i) => m + z.reduce((s, zj, j) => s + zj * d.V[j][i], 0))
})
const W = 620; const H = 230
const layers = [9, 5, 2, 5, 9]
const lx = (l: number) => 120 + l * 95
const ly = (l: number, i: number) => H / 2 + (i - (layers[l] - 1) / 2) * 22
const edges = layers.slice(0, -1).flatMap((n, l) => Array.from({ length: n }, (_, i) => Array.from({ length: layers[l + 1] }, (__, j) => ({ l, i, j }))).flat())
</script>

<template>
  <div class="flex items-center justify-center gap-2">
    <div class="text-center"><DigitImg :v="x" :size="80" /><div class="text-xs mt-1">x ∈ ℝ⁶⁴</div></div>
    <svg :viewBox="`70 0 ${W - 140} ${H}`" style="width: 480px" role="img" aria-label="An autoencoder: layers narrowing to a 2-unit bottleneck and widening again">
      <line
        v-for="(e, k) in edges" :key="k" :x1="lx(e.l)" :y1="ly(e.l, e.i)" :x2="lx(e.l + 1)" :y2="ly(e.l + 1, e.j)"
        class="edge" :style="{ stroke: e.l < 2 ? '#2dd4bf' : '#a78bfa', animationDelay: `${e.l * 0.35}s` }"
      />
      <g v-for="(n, l) in layers" :key="l">
        <circle v-for="i in n" :key="i" :cx="lx(l)" :cy="ly(l, i - 1)" :r="l === 2 ? 8 : 5.5" :style="{ fill: l === 2 ? '#fbbf24' : '#1e293b', stroke: l < 2 ? '#2dd4bf' : l === 2 ? '#fbbf24' : '#a78bfa', strokeWidth: 2 }" />
      </g>
      <text :x="lx(1)" :y="H - 8" text-anchor="middle" :style="{ fill: '#5eead4', fontSize: '13px' }">encoder</text>
      <text :x="lx(2)" :y="ly(2, 0) - 18" text-anchor="middle" :style="{ fill: '#fcd34d', fontSize: '13px', fontWeight: 700 }">z ∈ ℝ²</text>
      <text :x="lx(3)" :y="H - 8" text-anchor="middle" :style="{ fill: '#c4b5fd', fontSize: '13px' }">decoder</text>
    </svg>
    <div class="text-center"><DigitImg :v="out" :size="80" /><div class="text-xs mt-1">x̂ (linear: PCA, k = 2)</div></div>
  </div>
</template>

<style scoped>
.edge { stroke-width: 0.8; stroke-opacity: 0.18; animation: pulse 2.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { stroke-opacity: 0.12; } 30% { stroke-opacity: 0.75; } 60% { stroke-opacity: 0.12; } }
</style>
