<script setup lang="ts">
// 2,500 pixels of china.jpg as points in RGB space (data/pixels.json), in an orbiting 3D Plotly scene.
// quantized=false: each point drawn in its own color.
// quantized=true:  each point drawn in the color of its k-means centroid (K = 8), centroids shown large.
import { computed } from 'vue'
import d from '../data/pixels.json'

const props = withDefaults(defineProps<{ quantized?: boolean, width?: number, height?: number }>(), { quantized: false, width: 520, height: 420 })
const rgb = (c: number[]) => `rgb(${c[0]},${c[1]},${c[2]})`
const axis = (title: string, col: string) => ({
  title: { text: title, font: { color: col } }, range: [0, 255], color: '#94a3b8',
  gridcolor: 'rgba(148,163,184,0.18)', zerolinecolor: 'rgba(148,163,184,0.3)', backgroundcolor: 'rgba(0,0,0,0)', showbackground: false,
  tickvals: [0, 128, 255],
})
const layout = {
  scene: {
    xaxis: axis('red', '#f87171'), yaxis: axis('green', '#4ade80'), zaxis: axis('blue', '#60a5fa'),
    camera: { eye: { x: 1.75, y: -1.75, z: 0.95 } },
    aspectmode: 'cube',
  },
}
const data = computed(() => {
  const pts = {
    type: 'scatter3d', mode: 'markers', hoverinfo: 'skip',
    x: d.rgb.map(c => c[0]), y: d.rgb.map(c => c[1]), z: d.rgb.map(c => c[2]),
    marker: { size: 2.6, opacity: 0.9, color: d.rgb.map((c, i) => rgb(props.quantized ? d.c8[d.lab8[i]] : c)) },
  }
  const cents = {
    type: 'scatter3d', mode: 'markers',
    x: d.c8.map(c => c[0]), y: d.c8.map(c => c[1]), z: d.c8.map(c => c[2]),
    marker: { size: 13, color: d.c8.map(rgb), line: { color: '#ffffff', width: 3 }, opacity: 1 },
    hovertemplate: 'centroid<br>R %{x:.0f} · G %{y:.0f} · B %{z:.0f}<extra></extra>',
    visible: props.quantized,
  }
  return [pts, cents]
})
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="width" :height="height" spin />
</template>
