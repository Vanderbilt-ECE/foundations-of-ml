<script setup lang="ts">
// A 3D cloud near a tilted plane. Reveal the geometry across the opening slides:
// 0: cloud · 1: covariance eigenvectors · 2: the plane spanned by PC1 and PC2 · 3: 2D scores.
// Axes extend two standard deviations either side of the mean; eigenvectors themselves are unit length.
import { computed } from 'vue'
import d from '../data/teaser.json'
import { color } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const C = ['#fbbf24', '#a78bfa', '#f87171']
const mu = d.mean
const tip = (j: number, s: number) => mu.map((m, k) => m + s * 2 * d.sd[j] * d.V[j][k])
const corners = [[-1, -1], [1, -1], [-1, 1], [1, 1]].map(([a, b]) => mu.map((m, k) => m + a * 2.6 * d.sd[0] * d.V[0][k] + b * 2.6 * d.sd[1] * d.V[1][k]))
const plane = (() => {
  const c = corners
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
const data = computed(() => [...(props.step >= 2 ? [plane] : []), ...(props.step >= 1 ? axes : []), cloud])
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const eye = { x: -1.1, y: -1.6, z: 1.15 }
const layout = computed(() => ({ scene: {
  xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: axis('x₃'), aspectmode: 'data', camera: { eye },
  annotations: props.step >= 1 ? [0, 1, 2].map(j => {
    const p = tip(j, 1)
    return { x: p[0], y: p[1], z: p[2], text: `PC${j + 1}`, showarrow: false, font: { color: C[j], size: 13 }, yshift: 12 }
  }) : [],
} }))

// Preserve the plane, axis colors, and equal spatial scale in the PDF's static view.
const az = Math.atan2(eye.y, eye.x)
const el = Math.atan2(eye.z, Math.hypot(eye.x, eye.y))
const project = (p: number[]) => {
  const [x, y, z] = p.map((v, k) => v - mu[k])
  return [220 + 22 * (-Math.sin(az) * x + Math.cos(az) * y),
    165 - 22 * (-Math.cos(az) * Math.sin(el) * x - Math.sin(az) * Math.sin(el) * y + Math.cos(el) * z)]
}
const planePolygon = [0, 1, 3, 2].map(i => project(corners[i]).join(',')).join(' ')
const printAxes = [0, 1, 2].map(j => ({ a: project(tip(j, -1)), b: project(tip(j, 1)) }))
const printPoints = d.pts.map(project)

// 2D map of the scores
const W = 380; const H = 300; const U = 23
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
</script>

<template>
  <div class="grid grid-cols-2 gap-4 items-center">
    <PlotlyChart :data="data" :layout="layout" :width="440" :height="330" spin>
      <template #print>
        <svg viewBox="0 0 440 330" class="w-full" role="img" aria-label="3D data cloud with covariance axes and the principal plane revealed in sequence">
          <polygon v-if="step >= 2" :points="planePolygon" fill="#2dd4bf" fill-opacity="0.16" stroke="#2dd4bf" stroke-opacity="0.5" />
          <circle v-for="(p, i) in printPoints" :key="i" :cx="p[0]" :cy="p[1]" r="2" :fill="color(d.truth[i])" fill-opacity="0.85" />
          <g v-if="step >= 1">
            <g v-for="(a, j) in printAxes" :key="j">
              <line :x1="a.a[0]" :y1="a.a[1]" :x2="a.b[0]" :y2="a.b[1]" :stroke="C[j]" stroke-width="3" />
              <text :x="a.b[0] + 5" :y="a.b[1] - 8" :fill="C[j]" font-size="13" font-weight="700">PC{{ j + 1 }}</text>
            </g>
          </g>
          <text x="16" y="316" fill="#94a3b8" font-size="12">Three measured coordinates: x₁, x₂, x₃</text>
        </svg>
      </template>
    </PlotlyChart>
    <div v-if="step < 3"><slot /></div>
    <div v-else>
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
