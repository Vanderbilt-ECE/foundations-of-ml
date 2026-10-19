<script setup lang="ts">
// AdaBoost's stump weight α = ½ ln((1 − ε)/ε) against the weighted error ε.
// Violet dots are the three rounds from the 12-point example (data/ada.json).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/ada.json'

const W = 520
const H = 290
const L = 46
const R = 500
const T = 14
const Bot = 248
const eLo = 0
const eHi = 0.7
const aLo = -0.6
const aHi = 2.4
const alpha = (e: number) => 0.5 * Math.log((1 - e) / e)
const sx = (e: number) => L + (e - eLo) / (eHi - eLo) * (R - L)
const sy = (a: number) => Bot - (Math.max(aLo, Math.min(aHi, a)) - aLo) / (aHi - aLo) * (Bot - T)
const es = Array.from({ length: 140 }, (_, i) => 0.009 + i * (0.69 / 139))
const curve = es.map(e => `${sx(e).toFixed(1)},${sy(alpha(e)).toFixed(1)}`).join(' ')
const rounds = d.rounds.map((r, i) => ({ key: i, x: sx(r.e), y: sy(r.alpha), e: r.e.toFixed(2), a: r.alpha.toFixed(2) }))
const xt = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
const yt = [-0.5, 0, 0.5, 1, 1.5, 2]
</script>

<template>
  <svg role="img" aria-label="Stump weight alpha falls as weighted error rises: large near zero error, zero at 0.5, negative above 0.5" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <rect :x="sx(0.5)" :y="T" :width="R - sx(0.5)" :height="Bot - T" :style="{ fill: '#f87171', fillOpacity: 0.08 }" />
    <text :x="sx(0.6)" :y="T + 18" text-anchor="middle" :style="{ fill: '#fca5a5', fontSize: '12px' }">worse than</text>
    <text :x="sx(0.6)" :y="T + 33" text-anchor="middle" :style="{ fill: '#fca5a5', fontSize: '12px' }">a coin flip</text>
    <line v-for="t in xt" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <polyline :points="curve" :style="{ fill: 'none', stroke: '#e2e8f0', strokeWidth: 3 }" />
    <circle :cx="sx(0.5)" :cy="sy(0)" r="5" :style="{ fill: '#f87171', stroke: '#0f172a', strokeWidth: 2 }" />
    <text :x="sx(0.5) + 8" :y="sy(0) - 8" :style="{ fill: '#fca5a5', fontSize: '12px' }">ε = 0.5 → <tspan class="greek">α</tspan> = 0</text>
    <g v-for="(p, i) in rounds" :key="p.key">
      <circle :cx="p.x" :cy="p.y" r="5.5" :style="{ fill: '#a78bfa', stroke: '#0f172a', strokeWidth: 2 }" />
      <text :x="sx(0.27)" :y="sy(1.85) + i * 17" :style="{ fill: '#c4b5fd', fontSize: '12px' }">round {{ i + 1 }}: ε {{ p.e }} → <tspan class="greek">α</tspan> {{ p.a }}</text>
    </g>
    <text v-for="t in xt" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text v-for="t in yt" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">weighted error ε of the stump</text>
    <text x="13" :y="(T + Bot) / 2" text-anchor="middle" :transform="`rotate(-90 13 ${(T + Bot) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">stump weight <tspan class="greek">α</tspan></text>
  </svg>
</template>
