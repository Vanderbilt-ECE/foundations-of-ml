<script setup lang="ts">
// All 1797 digits placed by their first three PCA scores, z_j = (x - mean) · V_j, computed from data/digits.json
// (same mean and directions as the 2D map, so PC1/PC2 match it). One Plotly trace per digit class, so clicking
// the legend hides or shows a class. The scene orbits slowly until the pointer enters it; drag to rotate.
// The PDF export draws a static projection (PlotlyChart's fallback).
import d from '../data/digits.json'
import { color, decode } from '../utils/plot'

const props = withDefaults(defineProps<{ width?: number, height?: number }>(), { width: 600, height: 420 })

const Z = d.img.map((s) => {
  const x = decode(s)
  return [0, 1, 2].map(j => x.reduce((acc, v, i) => acc + (v - d.mean[i]) * d.V[j][i], 0))
})

const data = Array.from({ length: 10 }, (_, k) => {
  const idx = d.y.map((y, i) => (y === k ? i : -1)).filter(i => i >= 0)
  return {
    type: 'scatter3d', mode: 'markers', name: String(k),
    x: idx.map(i => Z[i][0]), y: idx.map(i => Z[i][1]), z: idx.map(i => Z[i][2]),
    marker: { size: 2.6, color: color(k), opacity: 0.85 },
    hovertemplate: `digit ${k}<extra></extra>`,
  }
})

const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = {
  showlegend: true,
  legend: { x: 1, y: 0.5, xanchor: 'right', font: { size: 14 }, itemsizing: 'constant', bgcolor: 'rgba(0,0,0,0)' },
  scene: {
    xaxis: axis('PC1'), yaxis: axis('PC2'), zaxis: axis('PC3'), aspectmode: 'cube',
    camera: { eye: { x: 1.5, y: -1.5, z: 0.8 } },
  },
}
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="props.width" :height="props.height" spin />
</template>
