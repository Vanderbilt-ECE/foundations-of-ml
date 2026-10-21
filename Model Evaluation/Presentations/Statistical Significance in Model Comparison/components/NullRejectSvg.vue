<script setup lang="ts">
const W = 640, L = 20, R = 620, base = 190, scale = 380, lo = -3.6, hi = 3.6, crit = 1.96
const X = (z: number) => L + ((z - lo) / (hi - lo)) * (R - L)
const pdf = (z: number) => Math.exp(-(z * z) / 2) / Math.sqrt(2 * Math.PI)
const Y = (z: number) => base - pdf(z) * scale
const xs = (a: number, b: number, n = 80) => Array.from({ length: n + 1 }, (_, i) => a + ((b - a) * i) / n)
const pts = (a: number, b: number) => xs(a, b).map(z => `${X(z).toFixed(1)} ${Y(z).toFixed(1)}`).join(' L')
const fill = (a: number, b: number) => `M${X(a).toFixed(1)} ${base} L${pts(a, b)} L${X(b).toFixed(1)} ${base} Z`

const curve = 'M' + pts(lo, hi)
const left = fill(lo, -crit)
const right = fill(crit, hi)
</script>

<template>
  <svg role="img" aria-label="Bell curve of the gap in standard errors if the models were equal. The tails beyond minus and plus 1.96 are shaded red and together hold 5 percent of the area: a gap landing there leads us to reject the null hypothesis." :viewBox="`0 0 ${W} 250`" class="w-full max-w-xl mx-auto -mt-4">
    <line :x1="L" :y1="base" :x2="R" :y2="base" stroke="#64748b" stroke-width="2" />
    <path :d="left" fill="#f87171" style="fill-opacity: .85" />
    <path :d="right" fill="#f87171" style="fill-opacity: .85" />
    <path :d="curve" fill="none" stroke="#94a3b8" stroke-width="3.5" />
    <text :x="X(0)" y="30" fill="#e2e8f0" text-anchor="middle" style="font-size:17px;font-weight:700">H₀: models equal</text>
    <line :x1="X(-crit)" y1="110" :x2="X(-crit)" :y2="base + 5" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5" />
    <line :x1="X(crit)" y1="110" :x2="X(crit)" :y2="base + 5" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5" />
    <g fill="#fbbf24" style="font-size:15px" text-anchor="middle">
      <text :x="X(-crit)" :y="base + 22">−1.96</text>
      <text :x="X(crit)" :y="base + 22">+1.96</text>
    </g>
    <text :x="X(0)" :y="base + 22" fill="#cbd5e1" text-anchor="middle" style="font-size:15px">0</text>
    <g fill="#f87171" style="font-size:15px;font-weight:700" text-anchor="middle">
      <text :x="X(-2.8)" y="160">2.5%</text>
      <text :x="X(2.8)" y="160">2.5%</text>
    </g>
    <g fill="#fca5a5" style="font-size:14px" text-anchor="middle">
      <text :x="X(-2.8)" y="138">reject H₀</text>
      <text :x="X(2.8)" y="138">reject H₀</text>
    </g>
    <text :x="X(0)" :y="base + 50" fill="#e2e8f0" text-anchor="middle" style="font-size:15px">gap in standard errors (z)</text>
  </svg>
</template>
