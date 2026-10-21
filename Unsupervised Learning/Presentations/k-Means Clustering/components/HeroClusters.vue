<script setup lang="ts">
// Title animation: the unlabeled blobs3 points light up cluster by cluster,
// rippling outward from each final centroid. Skipped in print/export (final state shown).
import { useNav } from '@slidev/client'
import { computed, onMounted, ref } from 'vue'
import run from '../data/blobs3.json'
import { color, domainOf, equalScale } from '../utils/kmeans'

const W = 760
const H = 300
const fin = run.frames[run.frames.length - 1]
const S = equalScale(domainOf(run.pts as number[][], 0.04), W, H)
const { isPrintMode } = useNav()
const on = ref(isPrintMode.value)
onMounted(() => { if (!on.value) setTimeout(() => (on.value = true), 500) })
const delay = computed(() => run.pts.map((p, i) => {
  const c = fin.c[fin.lab![i]]
  return Math.hypot(p[0] - c[0], p[1] - c[1]) * 260
}))
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Unlabeled points light up in three colored groups around three centers">
    <circle
      v-for="(p, i) in run.pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" r="3.4" class="hp"
      :style="{ fill: on ? color(fin.lab![i]) : '#64748b', fillOpacity: on ? 0.9 : 0.5, transitionDelay: `${700 + delay[i]}ms` }"
    />
    <g v-for="(c, k) in fin.c" :key="k" class="hc" :style="{ opacity: on ? 1 : 0, transform: `translate(${S.sx(c[0])}px, ${S.sy(c[1])}px) scale(${on ? 1 : 2.4})` }">
      <circle r="14" :style="{ fill: color(k), fillOpacity: 0.2 }" />
      <circle r="8" :style="{ fill: color(k), stroke: '#0b1020', strokeWidth: 2.5 }" />
    </g>
  </svg>
</template>

<style scoped>
.hp { transition: fill 0.6s ease, fill-opacity 0.6s ease; }
.hc { transition: opacity 0.6s ease, transform 0.9s cubic-bezier(.2, 1.4, .4, 1); }
</style>
