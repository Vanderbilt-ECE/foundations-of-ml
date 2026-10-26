<script setup lang="ts">
// The running example's true mixture density p(x) as a landscape (Plotly surface): one hill per component,
// height set by weight and spread. The 500 sampled points sit on the floor, colored by their component.
// The PDF export shows the density from above instead.
import d from '../data/em.json'
import { color } from '../utils/clusters'
import { mixPdf } from '../utils/gmm'

const gx = Array.from({ length: 60 }, (_, i) => -4.5 + 11 * i / 59)
const gy = Array.from({ length: 50 }, (_, i) => -5 + 8.5 * i / 49)
const z = gy.map(y => gx.map(x => mixPdf([x, y], d.true)))
const data = [
  {
    type: 'surface', x: gx, y: gy, z, showscale: false, hoverinfo: 'skip', opacity: 0.92,
    colorscale: [[0, '#0f172a'], [0.15, '#1e3a5f'], [0.5, '#14b8a6'], [1, '#ccfbf1']],
    contours: { z: { show: true, start: 0.005, end: 0.2, size: 0.012, color: 'rgba(255,255,255,0.3)' } },
    lighting: { ambient: 0.75, diffuse: 0.5, specular: 0.1 },
  },
  {
    type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
    x: d.pts.map(p => p[0]), y: d.pts.map(p => p[1]), z: d.pts.map(() => 0),
    marker: { size: 2.4, color: d.truth.map(k => color(k)), opacity: 0.9 },
  },
]
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: { ...axis('p(x)') }, aspectmode: 'manual', aspectratio: { x: 1.25, y: 1, z: 0.6 }, camera: { eye: { x: 1.2, y: -1.55, z: 0.95 } } } }
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="560" :height="390" spin>
    <template #print>
      <GmmPlot :pts="d.pts" :mix="d.true" mode="lab" :lab="d.truth" field="density" :levels="[]" :means="false" :w="520" :h="380" :r="2" />
    </template>
  </PlotlyChart>
</template>
