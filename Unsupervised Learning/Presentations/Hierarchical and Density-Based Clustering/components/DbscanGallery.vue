<script setup lang="ts">
// k-means (top) vs DBSCAN (bottom) on three of k-means' failure cases (data/gallery.json).
// `show` = how many DBSCAN panels are revealed. Gray points are DBSCAN noise.
// For blobs + outliers, k-means gets K = 4 (as in the k-Means deck) and DBSCAN gets minPts = 10.
import d from '../data/gallery.json'

withDefaults(defineProps<{ show?: number }>(), { show: 3 })
const cols = [['moons', 'Two moons'], ['circles', 'Two rings'], ['outliers', 'Blobs + 15 outliers']] as const
const badge = (a: number) => (a >= 0.85 ? 'text-teal-300' : a >= 0.5 ? 'text-amber-300' : 'text-red-300')
</script>

<template>
  <div class="grid gap-x-3 gap-y-1 items-center" style="grid-template-columns: 4.5rem repeat(3, 1fr)">
    <div />
    <div v-for="[k, t] in cols" :key="k" class="text-center text-sm font-bold opacity-85">{{ t }}</div>
    <div class="text-sm font-bold text-right pr-1 opacity-80">k-means</div>
    <div v-for="[k] in cols" :key="`k${k}`" class="relative">
      <ClusterPlot :pts="d[k].pts" :lab="d[k].km" :centroids="d[k].kmC" cells frame :w="280" :h="170" :r="2" :c-r="6" :label="`k-means on ${k}`" />
      <div class="absolute right-2 bottom-1 text-xs font-mono font-bold" :class="badge(d[k].kmAri)">ARI {{ d[k].kmAri.toFixed(2) }}</div>
    </div>
    <div class="text-sm font-bold text-right pr-1 text-teal-300">DBSCAN</div>
    <div v-for="([k], i) in cols" :key="`d${k}`" class="relative panel" :class="{ off: i >= show }">
      <ClusterPlot :pts="d[k].pts" :lab="d[k].db" frame :w="280" :h="170" :r="2" :label="`DBSCAN on ${k}; gray points are noise`" />
      <div class="absolute right-2 bottom-1 text-xs font-mono font-bold" :class="badge(d[k].dbAri)">ARI {{ d[k].dbAri.toFixed(2) }}</div>
    </div>
    <div />
    <div v-for="([k], i) in cols" :key="`c${k}`" class="text-xs text-center opacity-80 panel" :class="{ off: i >= show }" style="min-height: 2.6em">
      <div class="font-mono opacity-75">ε = {{ d[k].eps }}, minPts = {{ d[k].minPts }}</div>
      <template v-if="k === 'outliers'">{{ d.outliers.flagged }} of 15 outliers are noise, plus {{ d.outliers.edge }} blob-edge points</template>
      <template v-else>{{ d[k].noise }} noise points; both shapes followed exactly</template>
    </div>
  </div>
</template>

<style scoped>
.panel { transition: opacity 0.6s ease, transform 0.6s ease; }
.panel.off { opacity: 0; transform: translateY(8px); }
</style>
