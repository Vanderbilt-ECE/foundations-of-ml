<script setup lang="ts">
// Why maximum likelihood can blow up: a 4th component sits on a single data point and shrinks.
// Its density at that point, 1 / (2 pi sigma^2), grows without bound, so log L does too, while the fit gets worse.
// floor = true: a variance floor (what reg_covar does, exaggerated here so it is visible) stops the collapse.
// Loops while the slide is showing; the PDF export shows sigma = 0.05 (the initial value of sig).
import { computed, ref } from 'vue'
import d from '../data/em.json'
import type { Mix } from '../utils/gmm'
import { logLik, mixPdf, useLoop } from '../utils/gmm'

const props = withDefaults(defineProps<{ floor?: boolean }>(), { floor: false })
const F = d.frames[d.frames.length - 1]
// the point with the lowest density under the converged fit: the most isolated one
const iso = d.pts.reduce((b, p, i) => (mixPdf(p, F) < mixPdf(d.pts[b], F) ? i : b), 0)
const X = d.pts[iso]
const FLOOR = 0.18
const sig = ref(0.05)
useLoop((_, t) => {
  const u = t % 7.5
  const s = 0.9 * 10 ** (-1.6 * Math.max(0, u - 0.6)) // a factor of 10 every 0.6 s
  sig.value = props.floor ? Math.max(FLOOR, s) : Math.max(1e-12, s)
}, () => { sig.value = 0.9 })
const mix = computed<Mix>(() => {
  const w = [...F.w.map(v => v * (1 - 1 / d.pts.length)), 1 / d.pts.length]
  return { w, mu: [...F.mu, X], cov: [...F.cov, [[sig.value ** 2, 0], [0, sig.value ** 2]]] }
})
const base = logLik(d.pts, F)
const ll = computed(() => logLik(d.pts, mix.value))
const gain = computed(() => ll.value - base)
const BAR = 240
</script>

<template>
  <div class="grid grid-cols-[1.5fr_1fr] gap-5 items-center">
    <GmmPlot :pts="d.pts" :mix="mix" mode="hard" :levels="[1, 2]" :w="500" :h="360" :r="2.4" :ms="0" frame label="A fourth Gaussian shrinking onto a single point">
      <template #default="{ sx, sy }">
        <circle :cx="sx(X[0])" :cy="sy(X[1])" r="14" :style="{ fill: 'none', stroke: '#f8fafc', strokeWidth: 1.5, strokeDasharray: '3 3' }" />
      </template>
    </GmmPlot>
    <div class="text-left space-y-3 font-mono text-sm">
      <div>σ of component 4 = <span class="text-blue-300 font-bold">{{ sig < 0.01 ? sig.toExponential(1) : sig.toFixed(3) }}</span></div>
      <div>density at its point = {{ (1 / (2 * Math.PI * sig ** 2)).toExponential(1) }}</div>
      <div class="font-sans text-xs opacity-70 mt-2">log L gained over the 3-component fit</div>
      <div class="flex items-end gap-3" :style="{ height: `${BAR}px` }">
        <div class="w-10 rounded-t-md" :style="{ height: `${Math.min(BAR, Math.max(2, 6 * gain))}px`, background: gain * 6 > BAR ? '#f87171' : '#60a5fa' }" />
        <div class="pb-1" :class="gain * 6 > BAR ? 'text-red-300' : ''">{{ gain >= 0 ? '+' : '−' }}{{ Math.abs(gain).toFixed(1) }}{{ gain * 6 > BAR ? ' ↑ off the chart' : '' }}</div>
      </div>
    </div>
  </div>
</template>
