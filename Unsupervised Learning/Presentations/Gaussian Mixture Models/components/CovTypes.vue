<script setup lang="ts">
// The four covariance_type options, each fit with K = 3 on the running example (data/covtypes.json).
// Badges: free parameters p, BIC (lower is better), and ARI against the true components.
// hl = index of the panel to emphasize (-1: none).
import d from '../data/em.json'
import ct from '../data/covtypes.json'

withDefaults(defineProps<{ hl?: number }>(), { hl: -1 })
const TYPES = [
  { key: 'spherical', what: 'one variance per component: circles' },
  { key: 'diag', what: 'one variance per axis: axis-aligned ellipses' },
  { key: 'tied', what: 'one shared full Σ: same shape everywhere' },
  { key: 'full', what: 'own full Σ each: any ellipse' },
] as const
const bestBic = Math.min(...TYPES.map(t => ct[t.key].bic))
</script>

<template>
  <div class="grid grid-cols-4 gap-3">
    <div
      v-for="(t, i) in TYPES" :key="t.key" class="panel text-left" :class="{ dim: hl >= 0 && hl !== i, on: hl === i }"
      border="2 solid white/5" bg="white/5" rounded-lg px-2 py-2
    >
      <div class="font-mono font-bold text-sm px-1" :class="t.key === 'full' ? 'text-teal-300' : ''">"{{ t.key }}"</div>
      <div class="text-xs opacity-70 px-1 h-8 leading-tight">{{ t.what }}</div>
      <GmmPlot :pts="d.pts" :mix="ct[t.key]" mode="soft" :levels="[1, 2]" :w="220" :h="190" :r="1.6" :label="`GMM with ${t.key} covariance`" />
      <div class="grid grid-cols-3 text-center font-mono text-xs mt-1">
        <div><div class="opacity-60">p</div>{{ ct[t.key].p }}</div>
        <div :class="ct[t.key].bic === bestBic ? 'text-teal-300 font-bold' : ''"><div class="opacity-60">BIC</div>{{ ct[t.key].bic.toFixed(0) }}</div>
        <div><div class="opacity-60">ARI</div>{{ ct[t.key].ari.toFixed(2) }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel { transition: opacity 0.4s ease, border-color 0.4s ease; }
.panel.dim { opacity: 0.4; }
.panel.on { border-color: rgba(251, 191, 36, 0.7) !important; }
</style>
