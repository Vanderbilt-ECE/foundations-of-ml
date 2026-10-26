<script setup lang="ts">
// Wine (data/wine.json): 178 wines, 13 measurements in wildly different units, 3 cultivars (colors, never
// shown to PCA). std = false: PCA on the raw numbers · true: after StandardScaler.
// Left: the wines on PC1/PC2. Right: PC1's weight on each feature. Both morph when the switch flips.
import { computed } from 'vue'
import d from '../data/wine.json'
import { color, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ std?: boolean }>(), { std: false })
const cur = computed(() => (props.std ? d.std : d.raw))
const Z = useTween(() => cur.value.Z, 1100)
const L = useTween(() => cur.value.load[0], 1100)
const W = 300; const H = 260
const sx = (x: number) => W / 2 + x * 130
const sy = (y: number) => H / 2 - y * 115
const BW = 340; const row = 19
const bx = (v: number) => 250 + v * 82
</script>

<template>
  <div class="grid grid-cols-[1fr_1.15fr] gap-4 items-center">
    <div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 270px" role="img" aria-label="Wines plotted on their first two principal components, colored by cultivar">
        <line :x1="0" :x2="W" :y1="H / 2" :y2="H / 2" :style="{ stroke: '#1e293b' }" />
        <line :x1="W / 2" :x2="W / 2" :y1="0" :y2="H" :style="{ stroke: '#1e293b' }" />
        <circle v-for="(p, i) in Z" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="3.3" :style="{ fill: color(d.y[i]), fillOpacity: 0.85 }" />
        <text :x="W - 6" :y="H / 2 - 6" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">PC1</text>
      </svg>
      <div class="text-center text-sm font-mono">PC1 explains <span class="text-amber-300">{{ (100 * cur.evr[0]).toFixed(1) }}%</span></div>
    </div>
    <svg :viewBox="`0 0 ${BW} ${13 * row + 26}`" class="w-full" style="max-height: 290px" role="img" aria-label="Weight of each feature in the first principal component">
      <text x="250" y="12" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">PC1 weights</text>
      <line x1="250" x2="250" y1="18" :y2="18 + 13 * row" :style="{ stroke: '#475569' }" />
      <g v-for="(f, i) in d.features" :key="f">
        <text x="128" :y="18 + i * row + 13" text-anchor="end" :style="{ fill: f === 'proline' ? '#fcd34d' : '#cbd5e1', fontSize: '11.5px' }">{{ f }}</text>
        <text x="133" :y="18 + i * row + 13" :style="{ fill: '#64748b', fontSize: '10px' }" class="font-mono">sd {{ d.sd[i] }}</text>
        <rect :x="Math.min(bx(0), bx(L[i]))" :y="18 + i * row + 3" :width="Math.abs(bx(L[i]) - bx(0))" :height="row - 6" rx="2" :style="{ fill: L[i] >= 0 ? '#2dd4bf' : '#a78bfa', fillOpacity: 0.85 }" />
      </g>
    </svg>
  </div>
</template>
