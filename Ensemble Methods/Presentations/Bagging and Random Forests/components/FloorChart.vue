<script setup lang="ts">
// Var(f̄)/σ² = ρ + (1 − ρ)/B against B on a log axis, one curve per ρ, with dashed floor lines.
// Same chart as "Correlation Sets the Variance Floor" in Why Ensembles Work.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const props = withDefaults(defineProps<{ rhos?: number[], colors?: string[] }>(), {
  rhos: () => [0, 0.2, 0.5],
  colors: () => ['#2dd4bf', '#60a5fa', '#f59e0b'],
})

const W = 500
const H = 300
const L = 56
const R = 440
const T = 24
const Bot = 252
const maxB = 500
const sx = (B: number) => L + Math.log(B) / Math.log(maxB) * (R - L)
const sy = (v: number) => Bot - v * (Bot - T)
const ticks = [1, 2, 5, 10, 20, 50, 100, 200, 500]
const curves = props.rhos.map((rho, k) => {
  const pts = Array.from({ length: 121 }, (_, i) => {
    const B = Math.exp(i / 120 * Math.log(maxB))
    return `${sx(B).toFixed(1)},${sy(rho + (1 - rho) / B).toFixed(1)}`
  }).join(' ')
  return { rho, pts, color: props.colors[k % props.colors.length], y: sy(rho) }
})
</script>

<template>
  <svg role="img" :aria-label="`Ensemble variance over sigma squared against number of models, for correlations ${rhos.join(', ')}`" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <line v-for="t in ticks" :key="t" :x1="sx(t)" :x2="sx(t)" :y1="T" :y2="Bot" :style="{ stroke: '#334155', strokeWidth: 1 }" />
    <line :x1="L" :x2="R" :y1="Bot" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <line :x1="L" :x2="L" :y1="T" :y2="Bot" :style="{ stroke: '#64748b', strokeWidth: 2 }" />
    <template v-for="c in curves" :key="c.rho">
      <line v-if="c.rho > 0" :x1="L" :x2="R" :y1="c.y" :y2="c.y" :style="{ stroke: c.color, strokeWidth: 1.5, strokeDasharray: '6 5', opacity: 0.8 }" />
      <polyline :points="c.pts" :style="{ fill: 'none', stroke: c.color, strokeWidth: 4, strokeLinejoin: 'round' }" />
      <text :x="R + 6" :y="c.y + 4" :style="{ fill: c.color, fontSize: '13px', fontWeight: 700 }">ρ = {{ c.rho }}</text>
    </template>
    <text :x="L - 8" :y="sy(1) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">1</text>
    <text :x="L - 8" :y="sy(0.5) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">0.5</text>
    <text :x="L - 8" :y="sy(0) + 4" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '12px' }">0</text>
    <text v-for="t in ticks" :key="`l${t}`" :x="sx(t)" :y="Bot + 18" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '12px' }">{{ t }}</text>
    <text x="16" :y="(T + Bot) / 2" text-anchor="middle" :transform="`rotate(-90 16 ${(T + Bot) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">Var(f̄) / σ²</text>
    <text :x="(L + R) / 2" :y="H - 4" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">B (number of models, log scale)</text>
  </svg>
</template>
