<script setup lang="ts">
// blobs3 grouped two ways (data/blobs3.json): raw points (clicks 0), then k-means with K = 2 (click 1), then K = 3 (clicks ≥ 2).
// Centroids are the group means; the morph between them is tweened by ClusterPlot.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import run from '../data/blobs3.json'
import { domainOf } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const K = computed(() => ($clicks.value >= 2 ? 3 : $clicks.value >= 1 ? 2 : 0))
const lab = computed(() => (K.value === 0 ? null : K.value === 3 ? run.frames[run.frames.length - 1].lab! : run.k2))
const cents = computed(() => K.value === 0 ? null : Array.from({ length: K.value }, (_, k) => {
  const m = run.pts.filter((_, i) => lab.value![i] === k)
  return [m.reduce((s, p) => s + p[0], 0) / m.length, m.reduce((s, p) => s + p[1], 0) / m.length]
}))
const dom = domainOf(run.pts as number[][], 0.08)
</script>

<template>
  <div class="relative">
    <ClusterPlot :pts="run.pts" :lab="lab" :centroids="cents" :domain="dom" cells frame :w="520" :h="380" :label="K ? `The same points grouped into ${K} clusters` : 'The same points, ungrouped'" />
    <div v-if="K" class="absolute top-2 left-3 text-2xl font-bold">K = <span class="text-amber-300">{{ K }}</span></div>
  </div>
</template>
