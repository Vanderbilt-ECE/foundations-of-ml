<script setup lang="ts">
// Classification losses against the margin m = y·F(x): positive means correct with confidence,
// negative means wrong. 0–1 loss (gray), exponential loss e^(−m) (violet, AdaBoost),
// log loss log₂(1 + e^(−m)) (pink, gradient boosting's default for classifiers).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const W = 500
const H = 290
const L = 40
const R = 484
const T = 12
const Bot = 248
const mLo = -2.5
const mHi = 2.5
const yHi = 5
const sx = (m: number) => L + (m - mLo) / (mHi - mLo) * (R - L)
const sy = (v: number) => Bot - v / yHi * (Bot - T)
const ms = Array.from({ length: 160 }, (_, i) => mLo + i * (mHi - mLo) / 159)
const path = (f: (m: number) => number) => ms.map(m => `${sx(m).toFixed(1)},${sy(f(m)).toFixed(1)}`).join(' ')
const expL = (m: number) => Math.exp(-m)
const logL = (m: number) => Math.log2(1 + Math.exp(-m))
const zeroOne = `${sx(mLo)},${sy(1)} ${sx(0)},${sy(1)} ${sx(0)},${sy(0)} ${sx(mHi)},${sy(0)}`
const xt = [-2, -1, 0, 1, 2]
const yt = [0, 1, 2, 3, 4, 5]
</script>

<template>
  <svg role="img" aria-label="Loss against margin: exponential loss grows much faster than log loss for badly misclassified points" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <rect :x="sx(mLo)" :y="T" :width="sx(0) - sx(mLo)" :height="Bot - T" :style="{ fill: '#f87171', fillOpacity: 0.06 }" />
    <text :x="sx(-1.25)" :y="Bot - 8" text-anchor="middle" :style="{ fill: '#fca5a5', fontSize: '12px' }">wrong side</text>
    <text :x="sx(1.7)" :y="sy(0.8)" text-anchor="middle" :style="{ fill: '#5eead4', fontSize: '12px' }">right side</text>
    <line v-for="t in xt" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <polyline :points="zeroOne" :style="{ fill: 'none', stroke: '#94a3b8', strokeWidth: 2.5 }" />
    <defs>
      <clipPath id="ml-clip"><rect :x="L" :y="T" :width="R - L" :height="Bot - T + 2" /></clipPath>
    </defs>
    <polyline clip-path="url(#ml-clip)" :points="path(logL)" :style="{ fill: 'none', stroke: '#f472b6', strokeWidth: 3.5 }" />
    <polyline clip-path="url(#ml-clip)" :points="path(expL)" :style="{ fill: 'none', stroke: '#a78bfa', strokeWidth: 3.5 }" />
    <circle :cx="sx(-1.5)" :cy="sy(expL(-1.5))" r="5" :style="{ fill: '#a78bfa', stroke: '#0f172a', strokeWidth: 2 }" />
    <circle :cx="sx(-1.5)" :cy="sy(logL(-1.5))" r="5" :style="{ fill: '#f472b6', stroke: '#0f172a', strokeWidth: 2 }" />
    <text :x="sx(-1.5) + 9" :y="sy(expL(-1.5)) + 4" :style="{ fill: '#c4b5fd', fontSize: '12px' }">{{ expL(-1.5).toFixed(2) }}</text>
    <text :x="sx(-1.5) - 9" :y="sy(logL(-1.5)) + 18" text-anchor="end" :style="{ fill: '#f9a8d4', fontSize: '12px' }">{{ logL(-1.5).toFixed(2) }}</text>
    <text :x="sx(0.6)" :y="sy(4.4)" :style="{ fill: '#c4b5fd', fontSize: '13px', fontWeight: 700 }">exponential e⁻ᵐ  (AdaBoost)</text>
    <text :x="sx(0.6)" :y="sy(4.4) + 18" :style="{ fill: '#f9a8d4', fontSize: '13px', fontWeight: 700 }">log loss  (gradient boosting)</text>
    <text :x="sx(0.6)" :y="sy(4.4) + 36" :style="{ fill: '#94a3b8', fontSize: '13px', fontWeight: 700 }">0–1 loss  (what we count)</text>
    <text v-for="t in xt" :key="`x${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text v-for="t in yt" :key="`y${t}`" :x="L - 8" :y="sy(t) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">margin m = y·F(x)</text>
  </svg>
</template>
