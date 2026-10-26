<script setup lang="ts">
// The thin SVD of the centered data matrix as blocks: X_c (n x d) = U (n x d) · D (d x d, diagonal) · Vᵀ (d x d).
// Drawn for d = 8 with the digits' first 8 singular values (d_j = sqrt((n-1) λ_j)) as the diagonal.
// The slider keeps the first k columns of U, values of D and rows of Vᵀ: the rank-k approximation.
import { computed, ref } from 'vue'
import dg from '../data/digits.json'

const k = ref(3)
const D = 8
const sv = dg.lam.slice(0, D).map(l => Math.sqrt(l))
const top = sv[0]
const C = 26 // cell size
const nH = 9 * C // the tall n dimension, drawn shorter than it really is
const X0 = 20; const U0 = X0 + D * C + 60; const D0 = U0 + D * C + 34; const V0 = D0 + D * C + 34
const W = V0 + D * C + 16; const H = nH + 60
const kept = (j: number) => j < k.value
const pct = computed(() => (100 * dg.cum[k.value - 1]).toFixed(1))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 280px" role="img" aria-label="Block diagram of the singular value decomposition with the first k components highlighted">
      <!-- X_c -->
      <rect :x="X0" y="24" :width="D * C" :height="nH" rx="4" :style="{ fill: 'rgba(45,212,191,0.12)', stroke: '#2dd4bf', strokeWidth: 2 }" />
      <text :x="X0 + D * C / 2" y="16" text-anchor="middle" :style="{ fill: '#5eead4', fontSize: '15px', fontWeight: 700 }">X_c</text>
      <text :x="X0 + D * C / 2" :y="24 + nH + 20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">n × d</text>
      <text :x="U0 - 30" :y="24 + nH / 2 + 8" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '24px' }">=</text>
      <!-- U -->
      <rect v-for="j in D" :key="`u${j}`" :x="U0 + (j - 1) * C" y="24" :width="C - 3" :height="nH" rx="3" class="blk" :style="{ fill: kept(j - 1) ? 'rgba(251,191,36,0.35)' : 'rgba(148,163,184,0.08)', stroke: kept(j - 1) ? '#fbbf24' : '#334155' }" />
      <text :x="U0 + D * C / 2" y="16" text-anchor="middle" :style="{ fill: '#fcd34d', fontSize: '15px', fontWeight: 700 }">U</text>
      <!-- D -->
      <rect :x="D0" y="24" :width="D * C" :height="D * C" rx="3" :style="{ fill: 'none', stroke: '#334155' }" />
      <circle v-for="j in D" :key="`d${j}`" :cx="D0 + (j - 0.5) * C" :cy="24 + (j - 0.5) * C" :r="3 + 9 * sv[j - 1] / top" class="blk" :style="{ fill: kept(j - 1) ? '#fbbf24' : '#334155' }" />
      <text :x="D0 + D * C / 2" y="16" text-anchor="middle" :style="{ fill: '#fcd34d', fontSize: '15px', fontWeight: 700 }">D</text>
      <!-- V^T -->
      <rect v-for="j in D" :key="`v${j}`" :x="V0" :y="24 + (j - 1) * C" :width="D * C" :height="C - 3" rx="3" class="blk" :style="{ fill: kept(j - 1) ? 'rgba(167,139,250,0.35)' : 'rgba(148,163,184,0.08)', stroke: kept(j - 1) ? '#a78bfa' : '#334155' }" />
      <text :x="V0 + D * C / 2" y="16" text-anchor="middle" :style="{ fill: '#c4b5fd', fontSize: '15px', fontWeight: 700 }">Vᵀ</text>
      <text :x="V0 + D * C / 2" :y="24 + D * C + 20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">rows = principal directions</text>
      <text :x="D0 + D * C / 2" :y="24 + D * C + 20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">d₁ ≥ d₂ ≥ … ≥ 0</text>
    </svg>
    <div class="flex items-center gap-3 text-sm font-mono mt-1">
      <span class="text-amber-300 w-14">k = {{ k }}</span>
      <input v-model.number="k" type="range" min="1" :max="D" class="flex-1" style="accent-color: #fbbf24">
      <span class="opacity-80">digits: first {{ k }} keep {{ pct }}% of the variance</span>
    </div>
  </div>
</template>

<style scoped>
.blk { transition: fill 0.35s ease, stroke 0.35s ease; }
</style>
