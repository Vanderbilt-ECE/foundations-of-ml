<script setup lang="ts">
// DBSCAN on data with two densities (data/varied.json: two tight blobs close together + one wide sparse disk).
// Left: ARI against the true groups for every ε from 0.05 to 1.6 (noise points scored as singletons).
// Right: the clustering at the marked ε. Clicks: ε = 0.15 → 0.3 → 0.6 → HDBSCAN.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/varied.json'
import { useTween } from '../utils/clusters'

const { $clicks } = useSlideContext()
const s = computed(() => Math.min($clicks.value, 3))
const run = computed(() => (s.value < 3 ? d.dil[s.value] : null))
const lab = computed(() => (run.value ? run.value.lab : d.hdb))
const W = 400; const H = 300; const L = 44; const R = 390; const T = 14; const B = 258
const X = (e: number) => L + (e - 0.05) / (1.6 - 0.05) * (R - L)
const Y = (a: number) => B - Math.max(0, a) * (B - T)
const curve = d.sweep.map((p, i) => `${i ? 'L' : 'M'}${X(p.eps).toFixed(1)},${Y(p.ari).toFixed(1)}`).join('')
const mx = useTween(() => [X(run.value ? run.value.eps : d.dil[2].eps)], 600)
const caption = computed(() => [
  'Small ε: the tight blobs are found, but the whole sparse disk is noise.',
  'Medium ε: the disk shatters into fragments; the rest is noise.',
  'Large ε: the disk is one cluster, but the two tight blobs have merged.',
  `HDBSCAN: all three groups, ${d.hdbNoise} noise points. ARI ${d.hdbAri.toFixed(2)}.`,
][s.value])
</script>

<template>
  <div>
    <div class="grid grid-cols-[1fr_1fr] gap-5 items-center">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="ARI of DBSCAN against epsilon; it never gets close to 1">
        <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
        <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
        <g v-for="v in [0, 0.25, 0.5, 0.75, 1]" :key="v">
          <text :x="L - 7" :y="Y(v) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
          <line :x1="L" :x2="R" :y1="Y(v)" :y2="Y(v)" :style="{ stroke: '#1e293b' }" />
        </g>
        <g v-for="v in [0.2, 0.6, 1.0, 1.4]" :key="`x${v}`">
          <text :x="X(v)" :y="B + 16" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
        </g>
        <text :x="(L + R) / 2" :y="H - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">ε</text>
        <text x="12" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 12 ${(T + B) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">ARI vs. true groups</text>
        <path :d="curve" :style="{ stroke: '#e2e8f0', strokeWidth: 2, fill: 'none' }" />
        <circle :cx="X(d.best.eps)" :cy="Y(d.best.ari)" r="4" :style="{ fill: '#fbbf24' }" />
        <text :x="X(d.best.eps) + 8" :y="Y(d.best.ari) - 8" :style="{ fill: '#fbbf24', fontSize: '12px' }">best ε: ARI {{ d.best.ari.toFixed(2) }}</text>
        <line class="fade" :style="{ opacity: s < 3 ? 1 : 0, stroke: '#2dd4bf', strokeWidth: 2, strokeDasharray: '5 4' }" :x1="mx[0]" :x2="mx[0]" :y1="T" :y2="B" />
        <g class="fade" :style="{ opacity: s >= 3 ? 1 : 0 }">
          <line :x1="L" :x2="R" :y1="Y(d.hdbAri)" :y2="Y(d.hdbAri)" :style="{ stroke: '#2dd4bf', strokeWidth: 2.5, strokeDasharray: '8 5' }" />
          <text :x="R - 4" :y="Y(d.hdbAri) - 7" text-anchor="end" :style="{ fill: '#2dd4bf', fontSize: '13px', fontWeight: 700 }">HDBSCAN {{ d.hdbAri.toFixed(2) }}</text>
        </g>
      </svg>
      <div>
        <ClusterPlot :pts="d.pts" :lab="lab" frame :w="400" :h="300" :r="2.6" :label="s < 3 ? `DBSCAN with epsilon ${run!.eps}` : 'HDBSCAN result'" />
        <div class="text-center font-mono text-sm mt-1">{{ s < 3 ? `ε = ${run!.eps} · ${run!.k} clusters · ${run!.noise} noise · ARI ${run!.ari.toFixed(2)}` : `HDBSCAN · min_cluster_size = ${d.mcs}` }}</div>
      </div>
    </div>
    <div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.6em">{{ caption }}</div>
  </div>
</template>

<style scoped>
.fade { transition: opacity 0.5s ease; }
</style>
