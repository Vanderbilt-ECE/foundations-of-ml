<script setup lang="ts">
// Three random starts on blobs6, each run to convergence (data/blobs6.json → showcase).
// `show` = how many panels are visible (driven by v-click count on the slide).
import d from '../data/blobs6.json'
import { domainOf } from '../utils/kmeans'

withDefaults(defineProps<{ show?: number }>(), { show: 3 })
const dom = domainOf(d.pts as number[][], 0.05)
const tags = ['Found the six groups', 'Stuck: 1 centroid, 2 blobs', 'Stuck: 3 centroids, 1 blob']
</script>

<template>
  <div class="grid grid-cols-3 gap-4">
    <div v-for="(f, i) in d.showcase" :key="i" class="panel" :class="{ off: i >= show }">
      <ClusterPlot :pts="d.pts" :lab="f.lab" :centroids="f.c" :domain="dom" :w="300" :h="230" :r="2.4" :c-r="7" cells frame :label="`Random start ${i + 1}, final objective ${f.J}`" />
      <div class="flex justify-between items-baseline px-1 mt-1">
        <span class="text-sm" :class="i === 0 ? 'text-teal-300' : 'text-red-300'">{{ tags[i] }}</span>
        <span class="font-mono text-sm text-amber-300">J = {{ Math.round(f.J!).toLocaleString() }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel { transition: opacity 0.5s ease, transform 0.5s ease; }
.off { opacity: 0; transform: translateY(12px); }
</style>
