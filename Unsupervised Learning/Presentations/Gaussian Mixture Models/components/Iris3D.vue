<script setup lang="ts">
// Iris in 3D (data/iris.json): petal length, petal width, sepal length (cm) for 150 flowers.
// by = 'species' (the truth, never shown to the algorithms) · 'km' (k-means, K = 3) · 'gmm' (GMM, K = 3, full),
// which also draws each component's ellipsoid at Mahalanobis distance 2.
// The PDF export falls back to PlotlyChart's static projection of the points.
import { computed } from 'vue'
import d from '../data/iris.json'
import { color } from '../utils/clusters'
import { ellipsoid } from '../utils/gmm'

const props = withDefaults(defineProps<{ by?: 'species' | 'km' | 'gmm' }>(), { by: 'species' })
const lab = computed(() => (props.by === 'species' ? d.species : props.by === 'km' ? d.km : d.lab))
const shells = d.gmm.mu.map((mu, k) => ({
  type: 'surface', ...ellipsoid(mu, d.gmm.cov[k], 2), showscale: false, hoverinfo: 'skip', opacity: 0.16,
  colorscale: [[0, color(k)], [1, color(k)]], contours: { x: { highlight: false }, y: { highlight: false }, z: { highlight: false } },
}))
const data = computed(() => [
  ...(props.by === 'gmm' ? shells : []),
  {
    type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
    x: d.pts.map(p => p[0]), y: d.pts.map(p => p[1]), z: d.pts.map(p => p[2]),
    marker: { size: 3.6, color: lab.value.map(k => color(k)), opacity: 0.95, line: { color: '#0b1020', width: 0.5 } },
  },
])
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.18)', zeroline: false })
const layout = { scene: { xaxis: axis(d.features[0]), yaxis: axis(d.features[1]), zaxis: axis(d.features[2]), aspectmode: 'cube', camera: { eye: { x: 1.55, y: -1.35, z: 0.75 } } } }
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="500" :height="410" spin />
</template>
