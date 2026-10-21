<script setup lang="ts">
defineProps<{ step: number }>()

const L = 20, R = 500, crit = 1.96, chiCrit = crit * crit

// Top panel: the gap in standard errors (z) under H₀
const zBase = 125, zScale = 250, zLo = -3.5, zHi = 3.5
const zX = (z: number) => L + ((z - zLo) / (zHi - zLo)) * (R - L)
const zPdf = (z: number) => Math.exp(-(z * z) / 2) / Math.sqrt(2 * Math.PI)
const zY = (z: number) => zBase - zPdf(z) * zScale

// Bottom panel: McNemar's χ² (1 degree of freedom) under H₀; the spike at 0 is clipped
const cBase = 290, cScale = 400, cCap = 130, cLo = 0, cHi = 9
const cX = (x: number) => L + ((x - cLo) / (cHi - cLo)) * (R - L)
const cPdf = (x: number) => Math.exp(-x / 2) / Math.sqrt(2 * Math.PI * x)
const cY = (x: number) => cBase - Math.min(cPdf(x) * cScale, cCap)

const xs = (a: number, b: number, n = 80) => Array.from({ length: n + 1 }, (_, i) => a + ((b - a) * i) / n)
const pts = (fx: (v: number) => number, fy: (v: number) => number, a: number, b: number) =>
  xs(a, b).map(v => `${fx(v).toFixed(1)} ${fy(v).toFixed(1)}`).join(' L')
const fill = (fx: (v: number) => number, fy: (v: number) => number, base: number, a: number, b: number) =>
  `M${fx(a).toFixed(1)} ${base} L${pts(fx, fy, a, b)} L${fx(b).toFixed(1)} ${base} Z`

const zCurve = 'M' + pts(zX, zY, zLo, zHi)
const zLeft = fill(zX, zY, zBase, zLo, -crit)
const zRight = fill(zX, zY, zBase, crit, zHi)
// start where the curve enters the panel, so the clipped spike runs off the top
const cStart = xs(0.01, 2, 400).find(x => cPdf(x) * cScale <= cCap)!
const cCurve = 'M' + pts(cX, cY, cStart, cHi)
const cTail = fill(cX, cY, cBase, chiCrit, cHi)
</script>

<template>
  <svg role="img" aria-label="Two linked distributions under the null hypothesis. Top: the gap in standard errors, a bell curve with 2.5 percent tails shaded beyond minus and plus 1.96. Bottom: McNemar's chi-squared statistic, which is the gap squared; both tails fold into one 5 percent tail beyond 3.84, which equals 1.96 squared. Below 3.84 there is no verdict; above it we reject the null hypothesis." viewBox="0 0 520 335" class="w-full max-w-xl mx-auto">
    <!-- top: z scale -->
    <line :x1="L" :y1="zBase" :x2="R" :y2="zBase" stroke="#64748b" stroke-width="2" />
    <g v-show="step >= 1">
      <path :d="zLeft" fill="#f87171" style="fill-opacity: .8" />
      <path :d="zRight" fill="#f87171" style="fill-opacity: .8" />
    </g>
    <path :d="zCurve" fill="none" stroke="#94a3b8" stroke-width="3" />
    <text :x="zX(0)" y="14" fill="#cbd5e1" text-anchor="middle" style="font-size:13px;font-weight:700">gap in standard errors (z)</text>
    <g v-show="step >= 1">
      <line :x1="zX(-crit)" y1="62" :x2="zX(-crit)" :y2="zBase + 4" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 4" />
      <line :x1="zX(crit)" y1="62" :x2="zX(crit)" :y2="zBase + 4" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 4" />
      <g fill="#fbbf24" style="font-size:13px" text-anchor="middle">
        <text :x="zX(-crit)" :y="zBase + 18">−1.96</text>
        <text :x="zX(crit)" :y="zBase + 18">+1.96</text>
      </g>
      <g fill="#f87171" style="font-size:13px;font-weight:700" text-anchor="middle">
        <text :x="zX(-2.75)" y="100">2.5%</text>
        <text :x="zX(2.75)" y="100">2.5%</text>
      </g>
    </g>
    <text :x="zX(0)" :y="zBase + 18" fill="#cbd5e1" text-anchor="middle" style="font-size:13px">0</text>

    <!-- bottom: χ² scale -->
    <g v-show="step >= 2">
      <text :x="R" y="168" fill="#e2e8f0" text-anchor="end" style="font-size:14px;font-weight:700">square it: χ² ≈ z²</text>
      <text :x="R" y="186" fill="#cbd5e1" text-anchor="end" style="font-size:12px">both 2.5% tails fold into one 5% tail</text>
      <line :x1="L" :y1="cBase" :x2="R" :y2="cBase" stroke="#64748b" stroke-width="2" />
      <path :d="cTail" fill="#f87171" style="fill-opacity: .8" />
      <path :d="cCurve" fill="none" stroke="#94a3b8" stroke-width="3" />
      <line :x1="cX(chiCrit)" y1="214" :x2="cX(chiCrit)" :y2="cBase + 4" stroke="#f59e0b" stroke-width="2" stroke-dasharray="5 4" />
      <text :x="cX(chiCrit) + 6" y="222" fill="#fbbf24" style="font-size:13px">3.84 = 1.96²</text>
      <text :x="cX(5.4)" y="270" fill="#f87171" style="font-size:13px;font-weight:700">5%</text>
      <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle">
        <text :x="cX(0)" :y="cBase + 18">0</text>
        <text :x="cX(9)" :y="cBase + 18" text-anchor="end">χ²</text>
      </g>
    </g>
    <g v-show="step >= 3" style="font-size:13px;font-weight:700" text-anchor="middle">
      <rect :x="cX(0)" :y="cBase + 26" :width="cX(chiCrit) - cX(0) - 3" height="22" rx="5" fill="#64748b" style="fill-opacity: .25" />
      <text :x="(cX(0) + cX(chiCrit)) / 2" :y="cBase + 42" fill="#cbd5e1">don't reject H₀</text>
      <rect :x="cX(chiCrit) + 3" :y="cBase + 26" :width="R - cX(chiCrit) - 3" height="22" rx="5" fill="#f87171" style="fill-opacity: .25" />
      <text :x="(cX(chiCrit) + R) / 2" :y="cBase + 42" fill="#fca5a5">reject H₀</text>
    </g>
  </svg>
</template>
