<script setup lang="ts">
// Prediction at x0 = 0.3 over 400 fresh training sets (data/atx0.json):
// one deep tree vs a bagged ensemble of 50 trees. Same axis for both panels.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/atx0.json'

const props = withDefaults(defineProps<{ which: 'single' | 'bagged' }>(), {})

const vals: number[] = props.which === 'single' ? d.single : d.bagged
const mean = props.which === 'single' ? d.meanSingle : d.meanBagged
const variance = props.which === 'single' ? d.varSingle : d.varBagged
const color = props.which === 'single' ? '#fbbf24' : '#60a5fa'
const title = props.which === 'single' ? 'One deep tree' : `Bagged, B = ${d.B}`

const lo = 0
const hi = 1.8
const bw = 0.06
const nb = Math.round((hi - lo) / bw)
const bins = Array.from({ length: nb }, () => 0)
vals.forEach(v => { bins[Math.min(nb - 1, Math.max(0, Math.floor((v - lo) / bw)))]++ })
const maxCount = 55 // fixed so the two panels share a vertical scale

const W = 460
const H = 170
const L = 14
const R = 446
const T = 30
const Bot = 138
const sx = (v: number) => L + (v - lo) / (hi - lo) * (R - L)
const bh = (c: number) => Math.min(c, maxCount) / maxCount * (Bot - T)
const bars = bins.map((c, i) => ({ key: i, x: sx(lo + i * bw) + 1, w: sx(bw) - L - 2, h: bh(c) }))
const ticks = [0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8]
</script>

<template>
  <svg role="img" :aria-label="`${title}: predictions at x = ${d.x0} centered at ${mean}, variance ${variance}; true value ${d.truth}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text :x="L" y="18" :style="{ fill: color, fontSize: '15px', fontWeight: 700 }">{{ title }}</text>
    <text :x="R" y="18" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">variance {{ variance.toFixed(3) }}</text>
    <rect v-for="b in bars" :key="b.key" :x="b.x" :y="Bot - b.h" :width="b.w" :height="b.h" rx="1.5" :style="{ fill: color, fillOpacity: 0.7 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="sx(d.truth)" :x2="sx(d.truth)" :y1="T - 4" :y2="Bot" :style="{ stroke: '#e2e8f0', strokeWidth: 2, strokeDasharray: '5 4' }" />
    <text v-for="t in ticks" :key="t" :x="sx(t)" :y="Bot + 17" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="sx(d.truth) + 6" :y="T + 6" :style="{ fill: '#e2e8f0', fontSize: '12px' }">truth {{ d.truth.toFixed(2) }}</text>
    <text :x="(L + R) / 2" :y="H - 2" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">prediction at x = {{ d.x0 }}</text>
  </svg>
</template>
