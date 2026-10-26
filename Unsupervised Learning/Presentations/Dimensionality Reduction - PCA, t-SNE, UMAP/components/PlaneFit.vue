<script setup lang="ts">
// The Gaussian Mixture deck's closing teaser, continued (data/teaser.json): its 500 points lifted onto a tilted
// plane in 3D, plus a little noise off the plane.
// step 0: the cloud · 1: PCA's plane and its three axes (arrows = 2 standard deviations along each component)
// step 2: also the 2D map, each point's coordinates along PC1 and PC2 (the same points, the same colors).
import { computed } from 'vue'
import d from '../data/teaser.json'
import { color } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const C = ['#fbbf24', '#a78bfa', '#f87171']
const mu = d.mean
const tip = (j: number, s: number) => mu.map((m, k) => m + s * 2 * d.sd[j] * d.V[j][k])
const plane = (() => {
  const c = [[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([a, b]) => mu.map((m, k) => m + a * 2.6 * d.sd[0] * d.V[0][k] + b * 2.6 * d.sd[1] * d.V[1][k]))
  const g = (k: number) => [[c[0][k], c[1][k]], [c[2][k], c[3][k]]]
  return { type: 'surface', x: g(0), y: g(1), z: g(2), showscale: false, hoverinfo: 'skip', opacity: 0.22, colorscale: [[0, '#2dd4bf'], [1, '#2dd4bf']] }
})()
const axes = [0, 1, 2].map(j => ({
  type: 'scatter3d', mode: 'lines', hoverinfo: 'skip',
  x: [tip(j, -1)[0], tip(j, 1)[0]], y: [tip(j, -1)[1], tip(j, 1)[1]], z: [tip(j, -1)[2], tip(j, 1)[2]],
  line: { color: C[j], width: 7 },
}))
const cloud = {
  type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
  x: d.pts.map(p => p[0]), y: d.pts.map(p => p[1]), z: d.pts.map(p => p[2]),
  marker: { size: 2.4, color: d.truth.map(k => color(k)), opacity: 0.9 },
}
const data = computed(() => (props.step >= 1 ? [plane, ...axes, cloud] : [cloud]))
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: axis('x₃'), aspectmode: 'data', camera: { eye: { x: -1.1, y: -1.6, z: 1.15 } } } }

// 2D map of the scores
const W = 380; const H = 300; const U = 23
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
</script>

<template>
  <div class="grid grid-cols-2 gap-4 items-center">
    <PlotlyChart :data="data" :layout="layout" :width="440" :height="330" spin />
    <div class="reveal" :class="{ shown: step >= 2 }">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 300px" role="img" aria-label="The same points drawn by their first two principal component scores">
        <line :x1="sx(-7.5)" :x2="sx(7.5)" :y1="H / 2" :y2="H / 2" :style="{ stroke: C[0], strokeWidth: 2, strokeOpacity: 0.7 }" />
        <line :x1="W / 2" :x2="W / 2" :y1="sy(-5.8)" :y2="sy(5.8)" :style="{ stroke: C[1], strokeWidth: 2, strokeOpacity: 0.7 }" />
        <circle v-for="(p, i) in d.Z" :key="i" :cx="sx(p[0])" :cy="sy(p[1])" r="2.3" :style="{ fill: color(d.truth[i]), fillOpacity: 0.85 }" />
        <text :x="sx(7.5)" :y="H / 2 - 8" text-anchor="end" :style="{ fill: '#fcd34d', fontSize: '13px', fontWeight: 700 }">PC1</text>
        <text :x="W / 2 + 8" :y="sy(5.8) + 10" :style="{ fill: '#c4b5fd', fontSize: '13px', fontWeight: 700 }">PC2</text>
      </svg>
    </div>
  </div>
</template>
