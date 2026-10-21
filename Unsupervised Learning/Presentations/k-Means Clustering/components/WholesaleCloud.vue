<script setup lang="ts">
// Wholesale customers in 3 of their 6 dimensions (log spend), colored by the K = 4 clusters
// (data/wholesale.json). Orbiting 3D Plotly scene; drag to rotate, hover for the raw numbers.
// by="channel" colors by Hotel/Restaurant/Café vs Retail instead (a column k-means never saw).
import { computed } from 'vue'
import d from '../data/wholesale.json'
import { color } from '../utils/kmeans'

const props = withDefaults(defineProps<{ by?: 'cluster' | 'channel', width?: number, height?: number }>(), { by: 'cluster', width: 480, height: 400 })
const F = d.cols.indexOf('Fresh'); const G = d.cols.indexOf('Grocery'); const P = d.cols.indexOf('Detergents_Paper')
const axis = (t: string) => ({ title: { text: t }, color: '#94a3b8', gridcolor: 'rgba(148,163,184,0.18)', zerolinecolor: 'rgba(148,163,184,0.25)', showbackground: false })
const layout = {
  scene: {
    xaxis: axis('log Fresh'), yaxis: axis('log Grocery'), zaxis: axis('log Detergent/Paper'),
    camera: { eye: { x: 1.8, y: -1.5, z: 0.8 } }, aspectmode: 'cube',
  },
}
const data = computed(() => [{
  type: 'scatter3d', mode: 'markers',
  x: d.log.map(r => r[F]), y: d.log.map(r => r[G]), z: d.log.map(r => r[P]),
  customdata: d.raw.map(r => [r[F], r[G], r[P]]),
  hovertemplate: 'Fresh %{customdata[0]:,}<br>Grocery %{customdata[1]:,}<br>Detergent/Paper %{customdata[2]:,}<extra></extra>',
  marker: {
    size: 3.6, opacity: 0.9,
    color: props.by === 'cluster' ? d.lab4.map(k => color(k)) : d.channel.map(c => (c === 1 ? '#fbbf24' : '#60a5fa')),
  },
}])
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="width" :height="height" spin />
</template>
