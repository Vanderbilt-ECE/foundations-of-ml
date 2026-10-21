<script setup lang="ts">
// HDBSCAN on the varied-density data (data/varied.json), each point's opacity from probabilities_,
// HDBSCAN's strength of membership. Members score 0.4-1 here, so that range is stretched to faint-to-solid. soft=false draws every member at full strength (a hard label).
import d from '../data/varied.json'
import { color, domainOf, equalScale } from '../utils/clusters'

withDefaults(defineProps<{ soft?: boolean }>(), { soft: true })
const W = 420; const H = 330
const S = equalScale(domainOf(d.pts, 0.06), W, H)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Clustered points; points near the edge of a cluster are drawn faint">
    <rect x="1" y="1" :width="W - 2" :height="H - 2" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)', stroke: 'rgba(255,255,255,0.08)' }" />
    <circle
      v-for="(p, i) in d.pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" r="3" class="pt"
      :style="{ fill: color(d.hdb[i]), fillOpacity: d.hdb[i] < 0 ? 0.5 : (soft ? 0.06 + 0.94 * Math.max(0, (d.prob[i] - 0.4) / 0.6) ** 1.5 : 0.9) }"
    />
  </svg>
</template>

<style scoped>
.pt { transition: fill-opacity 0.8s ease; }
</style>
