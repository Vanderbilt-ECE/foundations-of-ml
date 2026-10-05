<script setup lang="ts">
import { normCdf } from './plotTheme'

defineProps<{ step: number }>()

const W = 520, base = 230, scale = 400, lo = -3.5, hi = 7
const crit = 1.96, shift = 2.8
const X = (z: number) => ((z - lo) / (hi - lo)) * W
const pdf = (z: number, m: number) => Math.exp(-((z - m) ** 2) / 2) / Math.sqrt(2 * Math.PI)
const Y = (z: number, m: number) => base - pdf(z, m) * scale
const xs = (a: number, b: number, n = 60) => Array.from({ length: n + 1 }, (_, i) => a + ((b - a) * i) / n)

const line = (m: number) => 'M' + xs(lo, hi, 120).map(z => `${X(z).toFixed(1)} ${Y(z, m).toFixed(1)}`).join(' L')
const area = (m: number, a: number, b: number) =>
  `M${X(a).toFixed(1)} ${base} L` + xs(a, b).map(z => `${X(z).toFixed(1)} ${Y(z, m).toFixed(1)}`).join(' L') + ` L${X(b).toFixed(1)} ${base} Z`

const h0 = line(0)
const h1 = line(shift)
const alpha = area(0, crit, 3.6)
const beta = area(shift, -0.6, crit)
const power = area(shift, crit, hi)
const betaPct = Math.round(normCdf(crit - shift) * 100)
</script>

<template>
  <svg role="img" aria-label="Two overlapping bell curves: the null distribution centered at zero and an alternative distribution shifted right. A critical line splits them: the small null tail beyond it is the false-positive rate alpha, the alternative's area left of it is the false-negative rate beta, and the area right of it is power." viewBox="0 0 520 300" class="w-full max-w-xl mx-auto">
    <line x1="0" :y1="base" :x2="W" :y2="base" stroke="#64748b" stroke-width="2" />
    <!-- shaded regions -->
    <path v-show="step >= 3" :d="power" fill="#2dd4bf" fill-opacity=".22" />
    <path v-show="step >= 2" :d="beta" fill="#60a5fa" fill-opacity=".45" />
    <path v-show="step >= 1" :d="alpha" fill="#f87171" fill-opacity=".8" />
    <!-- curves -->
    <path :d="h0" fill="none" stroke="#94a3b8" stroke-width="3.5" />
    <path :d="h1" fill="none" stroke="#2dd4bf" stroke-width="3.5" />
    <!-- critical value -->
    <line :x1="X(crit)" y1="52" :x2="X(crit)" :y2="base + 8" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5" />
    <text :x="X(crit)" y="44" fill="#fbbf24" text-anchor="middle" style="font-size:15px">critical value</text>
    <g fill="#cbd5e1" style="font-size:15px" text-anchor="middle">
      <text :x="X(0)" y="258">0</text>
      <text :x="X(shift)" y="258" fill="#5eead4">true gap</text>
    </g>
    <g style="font-size:16px" text-anchor="middle">
      <text :x="X(-1.35)" y="108" fill="#cbd5e1">H₀: no real gap</text>
      <text :x="X(5.2)" y="108" fill="#5eead4">H₁: real gap</text>
    </g>
    <g style="font-size:16px; font-weight:700" text-anchor="middle">
      <text v-show="step >= 1" :x="X(3.9)" y="206" fill="#f87171">α</text>
      <text v-show="step >= 2" :x="X(0.85)" y="223" fill="#bfdbfe" style="font-size:14px">β ≈ {{ betaPct }}%</text>
      <text v-show="step >= 3" :x="X(5.4)" y="170" fill="#5eead4">power = 1 − β</text>
    </g>
    <line v-show="step >= 1" :x1="X(3.75)" y1="206" :x2="X(2.6)" y2="224" stroke="#f87171" stroke-width="1.5" />
  </svg>
</template>
