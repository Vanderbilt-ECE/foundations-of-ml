<script setup lang="ts">
// k-means with K = 8 on the locations of California's 20,640 census block groups
// (data/california.json; 3,000 shown). Coordinates are km east/north of the state's mean.
// Each click advances Lloyd's algorithm to frames[steps[clicks]]; points take the color of
// their nearest current centroid, so the Voronoi "service areas" redraw as depots move.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/california.json'
import { domainOf, fmt } from '../utils/kmeans'

const props = withDefaults(defineProps<{ steps?: number[] }>(), { steps: () => [0, 1, 2, 3, 5, 8, 20] })
const { $clicks } = useSlideContext()
const fi = computed(() => Math.min(props.steps[Math.min($clicks.value, props.steps.length - 1)], d.frames.length - 1))
const f = computed(() => d.frames[fi.value])
const done = computed(() => fi.value === d.frames.length - 1)
const pts = d.pts as number[][]
const lab = computed(() => pts.map(p => {
  let best = 0; let bd = Infinity
  f.value.c.forEach((c, k) => {
    const v = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2
    if (v < bd) { bd = v; best = k }
  })
  return best
}))
const trails = computed(() => f.value.c.map((_, k) => d.frames.slice(0, fi.value + 1).map(fr => fr.c[k])))
const dom = domainOf(pts, 0.04)
// nearest city to each final depot, from centersLatLon in the JSON (checked by hand)
const cities = ['Los Angeles', 'Fresno', 'Santa Barbara / Bakersfield', 'San Diego', 'SF Bay Area', 'Redding', 'San Jose', 'Sacramento']
</script>

<template>
  <div class="grid grid-cols-[1fr_1fr] gap-6 items-center">
    <ClusterPlot :pts="pts" :lab="lab" :centroids="f.c" :trails="trails" :domain="dom" :w="420" :h="400" :r="1.8" :c-r="8" cells label="California block groups clustered into eight regions">
      <template #default="{ sx, sy }">
        <g v-if="done">
          <text v-for="(c, k) in f.c" :key="k" :x="sx(c[0]) + 12" :y="sy(c[1]) + 4" class="city" :style="{ fill: '#fff', fontSize: '11px', fontWeight: 700, paintOrder: 'stroke', stroke: '#000', strokeWidth: 3 }">{{ cities[k] }}</text>
        </g>
      </template>
    </ClusterPlot>
    <div class="space-y-3 text-left">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
        <div class="text-xs uppercase tracking-wider opacity-60">{{ fi === 0 ? 'Random start' : done ? 'Converged' : `Iteration ${fi}` }}</div>
        <div class="text-sm opacity-80 mt-1">mean squared distance to the nearest depot</div>
        <div class="font-mono text-3xl text-amber-300 mt-1">{{ f.J == null ? '—' : `${fmt(f.J, 0)} km²` }}</div>
      </div>
      <div class="reveal" :class="{ shown: done }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
        <div class="text-sm">On average a block group is <b class="text-teal-300">{{ d.meanDistKm }} km</b> from its depot. The busiest depot serves <b>{{ Math.max(...d.sizes).toLocaleString() }}</b> of {{ d.n.toLocaleString() }} block groups.</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reveal { opacity: 0; transform: translateY(8px); transition: opacity 0.6s ease, transform 0.6s ease; }
.reveal.shown { opacity: 1; transform: none; }
</style>
