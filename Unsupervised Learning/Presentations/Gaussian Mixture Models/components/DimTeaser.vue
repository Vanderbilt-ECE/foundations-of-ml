<script setup lang="ts">
// Teaser for the next deck: 3D points that really live near a tilted plane (the running example's 2D points,
// embedded in 3D plus a little noise). Three numbers per point, but two directions carry all the structure.
import d from '../data/em.json'
import { color } from '../utils/clusters'
import { rng } from '../utils/gmm'

const R = rng(3)
const e1 = [0.8, 0.2, 0.55]; const e2 = [-0.3, 0.9, 0.3]; const nrm = [0.52, 0.38, -0.76] // plane axes and normal (approx.)
const P = d.pts.map((p) => {
  const z = 0.12 * R.n()
  return [0, 1, 2].map(j => p[0] * e1[j] + p[1] * e2[j] + z * nrm[j])
})
const corners = [[-5, -5.5], [7.5, -5.5], [-5, 4.5], [7.5, 4.5]].map(([a, b]) => [0, 1, 2].map(j => a * e1[j] + b * e2[j]))
const data = [
  {
    type: 'surface', showscale: false, hoverinfo: 'skip', opacity: 0.18, colorscale: [[0, '#94a3b8'], [1, '#94a3b8']],
    x: [[corners[0][0], corners[1][0]], [corners[2][0], corners[3][0]]],
    y: [[corners[0][1], corners[1][1]], [corners[2][1], corners[3][1]]],
    z: [[corners[0][2], corners[1][2]], [corners[2][2], corners[3][2]]],
  },
  { type: 'scatter3d', mode: 'markers', hoverinfo: 'skip', x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]), marker: { size: 2.4, color: d.truth.map(k => color(k)), opacity: 0.9 } },
]
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: axis('x₃'), aspectmode: 'data', camera: { eye: { x: 1.4, y: -1.5, z: 0.7 } } } }
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="460" :height="340" spin />
</template>
