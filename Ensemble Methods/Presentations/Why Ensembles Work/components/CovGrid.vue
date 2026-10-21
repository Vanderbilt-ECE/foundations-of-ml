<script setup lang="ts">
// B×B grid of Cov(f_b, f_b'): diagonal cells are σ², off-diagonal cells are ρσ²
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const props = withDefaults(defineProps<{ B?: number }>(), { B: 5 })

const cell = 52
const left = 46
const top = 34
const idx = Array.from({ length: props.B }, (_, i) => i)
</script>

<template>
  <svg role="img" :aria-label="`${B} by ${B} covariance grid: ${B} diagonal cells equal sigma squared, the other ${B * (B - 1)} cells equal rho sigma squared`" :viewBox="`0 0 ${left + B * cell + 8} ${top + B * cell + 8}`" class="w-full">
    <text v-for="j in idx" :key="`c${j}`" :x="left + j * cell + cell / 2" :y="top - 12" text-anchor="middle" fill="#94a3b8" style="font-size: 15px">f{{ j + 1 }}</text>
    <text v-for="i in idx" :key="`r${i}`" :x="left - 12" :y="top + i * cell + cell / 2 + 5" text-anchor="end" fill="#94a3b8" style="font-size: 15px">f{{ i + 1 }}</text>
    <g v-for="i in idx" :key="i">
      <g v-for="j in idx" :key="j">
        <rect
          :x="left + j * cell + 2" :y="top + i * cell + 2" :width="cell - 4" :height="cell - 4" rx="6"
          :style="{ fill: i === j ? '#2dd4bf' : '#60a5fa', fillOpacity: i === j ? 0.55 : 0.18, stroke: i === j ? '#2dd4bf' : '#3b82f6', strokeWidth: 1.5 }"
        />
        <text :x="left + j * cell + cell / 2" :y="top + i * cell + cell / 2 + 6" text-anchor="middle" :style="{ fill: i === j ? '#ccfbf1' : '#bfdbfe', fontSize: '16px' }">{{ i === j ? 'σ²' : 'ρσ²' }}</text>
      </g>
    </g>
  </svg>
</template>
