<script setup lang="ts">
// Silhouette plots for K = 4, 6, 8 on blobs6 (data/blobs6.json → knife, sweep).
// Each cluster's per-point scores are sorted into a horizontal "knife"; the dashed
// line is the mean. `show` = number of panels visible.
import d from '../data/blobs6.json'
import { color, domainOf } from '../utils/kmeans'

withDefaults(defineProps<{ show?: number }>(), { show: 3 })
const ks = [4, 6, 8] as const
const dom = domainOf(d.pts as number[][], 0.05)
const W = 260; const H = 200; const L = 30; const R = 250
const sx = (v: number) => L + (v + 0.2) / 1.2 * (R - L)
const knife = (k: 4 | 6 | 8) => {
  const g = (d.knife as any)[k].groups as number[][]
  const total = g.reduce((s, x) => s + x.length, 0) + (g.length - 1) * 14
  const per = (H - 30) / total
  let y = 8
  return g.map((vals, c) => {
    const top = y
    const path = vals.map((v, j) => `M${sx(0)},${(top + j * per).toFixed(2)}H${sx(v).toFixed(2)}`).join('')
    y += vals.length * per + 14 * per
    return { c, path, mid: top + vals.length * per / 2, w: Math.max(per, 0.6) }
  })
}
</script>

<template>
  <div class="grid grid-cols-3 gap-5">
    <div v-for="(k, n) in ks" :key="k" class="panel" :class="{ off: n >= show }">
      <div class="flex justify-between items-baseline">
        <span class="text-lg font-bold">K = {{ k }}</span>
        <span class="text-sm font-mono" :class="k === 6 ? 'text-teal-300' : 'text-amber-300'">mean {{ (d.knife as any)[k].mean.toFixed(3) }}</span>
      </div>
      <ClusterPlot :pts="d.pts" :lab="d.sweep[k - 1].lab" :centroids="d.sweep[k - 1].c" :domain="dom" :w="260" :h="125" :r="1.7" :c-r="5" frame :label="`k-means with K = ${k}`" />
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full mt-1" role="img" :aria-label="`Silhouette plot for K = ${k}, mean ${(d.knife as any)[k].mean}`">
        <g v-for="kn in knife(k)" :key="kn.c">
          <path :d="kn.path" :style="{ stroke: color(kn.c), strokeWidth: kn.w, strokeOpacity: 0.85 }" />
        </g>
        <line :x1="sx(0)" :x2="sx(0)" y1="4" :y2="H - 20" :style="{ stroke: '#94a3b8' }" />
        <line :x1="sx((d.knife as any)[k].mean)" :x2="sx((d.knife as any)[k].mean)" y1="4" :y2="H - 20" :style="{ stroke: '#f87171', strokeDasharray: '5 4', strokeWidth: 1.5 }" />
        <text v-for="t in [0, 0.5, 1]" :key="t" :x="sx(t)" :y="H - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ t }}</text>
      </svg>
    </div>
  </div>
</template>

<style scoped>
.panel { transition: opacity 0.5s ease, transform 0.5s ease; }
.off { opacity: 0; transform: translateY(12px); }
</style>
