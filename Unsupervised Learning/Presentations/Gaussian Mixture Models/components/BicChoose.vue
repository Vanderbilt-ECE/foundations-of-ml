<script setup lang="ts">
// Choosing K on the running example (data/bic.json, full covariance, K = 1..8).
// Left: -2 log L keeps falling; AIC and BIC add a penalty and turn back up. Right: the fit at the selected K.
import { computed } from 'vue'
import d from '../data/em.json'
import b from '../data/bic.json'

const props = withDefaults(defineProps<{ k?: number }>(), { k: 1 })
const S = b.sweep.full
const series = [
  { key: '−2 log L', c: '#94a3b8', v: S.map(s => -2 * s.ll), dash: '5 4' },
  { key: 'AIC', c: '#fbbf24', v: S.map(s => s.aic), dash: 'none' },
  { key: 'BIC', c: '#2dd4bf', v: S.map(s => s.bic), dash: 'none' },
]
const W = 420; const H = 300; const Y0 = 3300; const Y1 = 4200
const sx = (k: number) => 50 + (k - 1) / 7 * (W - 110)
const sy = (v: number) => 16 + (Y1 - v) / (Y1 - Y0) * (H - 50)
const kk = computed(() => Math.max(1, Math.min(8, props.k)))
const sel = computed(() => S[kk.value - 1])
</script>

<template>
  <div class="grid grid-cols-[1.15fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Minus two log-likelihood falls with K while AIC and BIC reach a minimum at K = 3">
      <line :x1="sx(1)" :x2="sx(8)" :y1="sy(Y0)" :y2="sy(Y0)" :style="{ stroke: '#475569' }" />
      <g v-for="k in 8" :key="k">
        <text :x="sx(k)" :y="sy(Y0) + 16" text-anchor="middle" :style="{ fill: k === kk ? '#f8fafc' : '#64748b', fontSize: '12px', fontWeight: k === kk ? 700 : 400 }">{{ k }}</text>
      </g>
      <text :x="sx(8)" :y="sy(Y0) + 32" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">components K</text>
      <rect :x="sx(kk) - 14" :y="sy(Y1)" width="28" :height="sy(Y0) - sy(Y1)" rx="6" class="sel" :style="{ fill: '#f8fafc', fillOpacity: 0.07 }" />
      <g v-for="s in series" :key="s.key">
        <path :d="s.v.map((v, i) => `${i ? 'L' : 'M'}${sx(i + 1).toFixed(1)},${sy(v).toFixed(1)}`).join('')" :style="{ fill: 'none', stroke: s.c, strokeWidth: 2.6, strokeDasharray: s.dash }" />
        <circle v-for="(v, i) in s.v" :key="i" :cx="sx(i + 1)" :cy="sy(v)" :r="i + 1 === kk ? 5.5 : 3" :style="{ fill: s.c }" />
        <text :x="sx(8) + 8" :y="sy(s.v[7]) + 4" :style="{ fill: s.c, fontSize: '12px', fontWeight: 700 }">{{ s.key }}</text>
      </g>
      <text :x="sx(b.best.full)" :y="sy(S[b.best.full - 1].bic) - 12" text-anchor="middle" :style="{ fill: '#5eead4', fontSize: '12px', fontWeight: 700 }">min</text>
    </svg>
    <div>
      <GmmPlot :pts="d.pts" :mix="b.fits[kk - 1]" mode="soft" :levels="[1, 2]" :w="380" :h="280" :r="2.2" frame :label="`Fit with K = ${kk}`" />
      <div class="font-mono text-sm text-center mt-1">
        K = {{ kk }} · p = {{ sel.p }} · <span class="text-teal-300">BIC {{ sel.bic.toFixed(0) }}</span> · <span class="text-amber-300">AIC {{ sel.aic.toFixed(0) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sel { transition: x 0.5s ease; }
</style>
