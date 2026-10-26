<script setup lang="ts">
// The M-step seen from one component: every point counts, weighted by its responsibility gamma_ik.
// Point size and opacity = gamma_ik for the selected component k; the cross is the weighted mean and the
// ellipse the weighted covariance, both computed here from the drawn weights (they match em.json's next frame).
import { computed } from 'vue'
import d from '../data/em.json'
import { color, domainOf, equalScale } from '../utils/clusters'
import { ellipsePath, resp } from '../utils/gmm'

const props = withDefaults(defineProps<{ k?: number }>(), { k: 0 })
const W = 500; const H = 360
const S = equalScale(domainOf(d.pts, 0.06), W, H)
const F = d.frames[3] // early in the run, so the responsibilities are still visibly soft
const G = d.pts.map(p => resp(p, F))
const kk = computed(() => Math.max(0, Math.min(2, props.k)))
const stats = computed(() => {
  const k = kk.value
  let n = 0; let mx = 0; let my = 0
  d.pts.forEach((p, i) => { n += G[i][k]; mx += G[i][k] * p[0]; my += G[i][k] * p[1] })
  mx /= n; my /= n
  let a = 0; let b = 0; let c = 0
  d.pts.forEach((p, i) => { const dx = p[0] - mx; const dy = p[1] - my; a += G[i][k] * dx * dx; b += G[i][k] * dx * dy; c += G[i][k] * dy * dy })
  return { n, mu: [mx, my], cov: [[a / n, b / n], [b / n, c / n]] }
})
const old = computed(() => ({ mu: F.mu[kk.value], cov: F.cov[kk.value] }))
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-5 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Points sized by their responsibility for one component, with that component's weighted mean and covariance ellipse">
      <circle
        v-for="(p, i) in d.pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" class="pt"
        :r="1.2 + 3.6 * G[i][kk]" :style="{ fill: G[i][kk] > 0.02 ? color(kk) : '#64748b', fillOpacity: 0.3 + 0.65 * G[i][kk] }"
      />
      <path :d="ellipsePath(old.mu, old.cov, 1, S.sx, S.sy)" :style="{ fill: 'none', stroke: '#e2e8f0', strokeOpacity: 0.55, strokeWidth: 1.5, strokeDasharray: '4 4' }" />
      <path :d="ellipsePath(stats.mu, stats.cov, 1, S.sx, S.sy)" class="ell" :style="{ fill: color(kk), fillOpacity: 0.1, stroke: color(kk), strokeWidth: 2.6 }" />
      <path :d="ellipsePath(stats.mu, stats.cov, 2, S.sx, S.sy)" :style="{ fill: 'none', stroke: color(kk), strokeWidth: 1.3, strokeDasharray: '5 4' }" />
      <g :transform="`translate(${S.sx(stats.mu[0]).toFixed(1)},${S.sy(stats.mu[1]).toFixed(1)})`">
        <circle r="8" :style="{ fill: color(kk), stroke: '#0b1020', strokeWidth: 2.4 }" />
        <path d="M-3.6,0H3.6M0,-3.6V3.6" :style="{ stroke: '#0b1020', strokeWidth: 2.2 }" />
      </g>
    </svg>
    <div class="text-left space-y-2 font-mono text-sm">
      <div :style="{ color: color(kk) }" class="font-bold font-sans text-base">Component {{ kk + 1 }}</div>
      <div>N<sub>k</sub> = Σᵢ γᵢₖ = {{ stats.n.toFixed(1) }} <span class="opacity-60">of {{ d.pts.length }}</span></div>
      <div>π<sub>k</sub> = N<sub>k</sub>/n = {{ (stats.n / d.pts.length).toFixed(3) }}</div>
      <div>μ<sub>k</sub> = ({{ stats.mu[0].toFixed(2) }}, {{ stats.mu[1].toFixed(2) }})</div>
      <div class="font-sans text-xs opacity-75 pt-2">Big, bright dots pull hard on the new mean and shape; faint dots barely count. Dashed white: the ellipse before this M-step.</div>
    </div>
  </div>
</template>

<style scoped>
.pt { transition: r 0.6s ease, fill 0.6s ease, fill-opacity 0.6s ease; }
</style>
