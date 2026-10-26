<script setup lang="ts">
// The Swiss roll (data/swiss.json): 900 points on a rolled-up 2D sheet in 3D, colored by position along the roll.
// Right panel, by `view`: 'pca' (the best flat projection: the roll's layers land on top of each other)
// or 'truth' (the sheet unrolled: position along the roll x height). Switching morphs the points.
import { computed } from 'vue'
import d from '../data/swiss.json'
import { ramp } from '../utils/plot'

const props = withDefaults(defineProps<{ view?: 'pca' | 'truth' | null }>(), { view: null })
const t0 = Math.min(...d.t); const t1 = Math.max(...d.t)
const u = d.t.map(t => (t - t0) / (t1 - t0))
const cols = u.map(ramp)
const data = [{
  type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
  x: d.pts.map(p => p[0]), y: d.pts.map(p => p[1]), z: d.pts.map(p => p[2]),
  marker: { size: 2.6, color: cols, opacity: 0.95 },
}]
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: axis('x₃'), aspectmode: 'data', camera: { eye: { x: 0.3, y: -1.9, z: 0.6 }, up: { x: 0, y: 0, z: 1 } } } }
const pts = computed(() => d.emb[props.view ?? 'pca'])
</script>

<template>
  <div class="grid grid-cols-2 gap-4 items-center">
    <PlotlyChart :data="data" :layout="layout" :width="440" :height="330" spin />
    <div class="reveal text-center" :class="{ shown: view != null }">
      <EmbedPlot :pts="pts" :lab="u.map(() => 0)" :cols="cols" :w="400" :h="280" :r="2.4" :ms="1600" label="The Swiss roll in 2D" />
      <div class="text-sm font-mono mt-1">{{ view === 'truth' ? 'unrolled: the 2D sheet it really is' : 'PCA: the best flat shadow' }}</div>
    </div>
  </div>
</template>
