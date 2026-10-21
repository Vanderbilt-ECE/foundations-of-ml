<script setup lang="ts">
// The objective J as literal lines: every point connected to its centroid (data/blobs3.json).
// clicks 0: a poor set of centroids (the random start of the Lloyd run, after assigning)
// clicks 1: the converged centroids. J tweens between the two values.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import run from '../data/blobs3.json'
import { domainOf, fmt, useTween } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const good = computed(() => $clicks.value >= 1)
const f = computed(() => (good.value ? run.frames[run.frames.length - 1] : run.frames[1]))
const J = useTween(() => [f.value.J as number], 800)
const dom = domainOf(run.pts as number[][], 0.08)
</script>

<template>
  <div class="relative">
    <ClusterPlot :pts="run.pts" :lab="f.lab" :centroids="f.c" :domain="dom" lines :w="520" :h="380" frame :label="`Each point linked to its centroid; total squared length J = ${f.J}`" />
    <div class="absolute top-3 left-3" border="2 solid white/10" bg="black/50" rounded-lg px-3 py-2>
      <div class="text-xs opacity-70">{{ good ? 'good centroids' : 'poor centroids' }}</div>
      <div class="font-mono text-2xl font-bold" :class="good ? 'text-teal-300' : 'text-red-300'">J = {{ fmt(J[0], 1) }}</div>
    </div>
  </div>
</template>
