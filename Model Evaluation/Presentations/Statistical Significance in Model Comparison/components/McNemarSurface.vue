<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Plotly from 'plotly.js-dist-min'

const el = ref<HTMLDivElement | null>(null)
const N = 30

const chi2 = (a: number, b: number) =>
  a + b === 0 ? 0 : Math.max(Math.abs(a - b) - 1, 0) ** 2 / (a + b)

onMounted(() => {
  const axis = Array.from({ length: N + 1 }, (_, i) => i)
  // z[row = n10][col = n01]
  const z = axis.map(b => axis.map(a => chi2(a, b)))
  const zMax = chi2(N, 0)

  const text = '#e2e8f0'
  const grid = 'rgba(148,163,184,.25)'
  const axisStyle = (title: string, color: string) => ({
    title: { text: title, font: { size: 22, color } },
    range: [0, N],
    dtick: 10,
    tickfont: { size: 14, color: text },
    gridcolor: grid,
    zerolinecolor: grid,
    backgroundcolor: 'rgba(0,0,0,0)',
    showbackground: false,
  })

  const surface = {
    type: 'surface',
    x: axis,
    y: axis,
    z,
    cmin: 0,
    cmax: zMax,
    colorscale: [
      [0, '#2dd4bf'],
      [0.35, '#38bdf8'],
      [0.7, '#a78bfa'],
      [1, '#fbbf24'],
    ],
    contours: { z: { show: true, usecolormap: true, project: { z: false }, width: 1 } },
    colorbar: {
      title: { text: 'χ²', font: { size: 20, color: '#fbbf24' } },
      tickfont: { size: 13, color: text },
      len: 0.75, x: 0.88,
      thickness: 14,
      outlinewidth: 0,
    },
    hovertemplate: 'n₀₁ = %{x}<br>n₁₀ = %{y}<br>χ² = %{z:.2f}<extra></extra>',
  }

  // Equal-wins diagonal: the valley where χ² is 0
  const diag = {
    type: 'scatter3d',
    mode: 'lines',
    x: axis,
    y: axis,
    z: axis.map(() => 0),
    line: { color: '#ffffff', width: 6 },
    hoverinfo: 'skip',
    showlegend: false,
  }

  const layout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 0, r: 0, t: 0, b: 0 },
    font: { color: text },
    scene: {
      xaxis: axisStyle('n₀₁', '#5eead4'),
      yaxis: axisStyle('n₁₀', '#60a5fa'),
      zaxis: { ...axisStyle('χ²', '#fbbf24'), range: [0, zMax], dtick: 10 },
      aspectratio: { x: 1, y: 1, z: 0.7 },
      camera: { eye: { x: 1.45, y: -1.45, z: 0.7 } },
    },
  }

  // Critical value for alpha = 0.05 (1.96^2): the surface above this plane is "reject H0"
  const plane = {
    type: 'surface',
    x: [0, N],
    y: [0, N],
    z: [[3.84, 3.84], [3.84, 3.84]],
    showscale: false,
    opacity: 0.45,
    colorscale: [[0, '#fbbf24'], [1, '#fbbf24']],
    hoverinfo: 'skip',
  }

  Plotly.newPlot(el.value!, [surface, diag, plane] as any, layout as any, {
    responsive: true,
    displayModeBar: false,
  })
})

onBeforeUnmount(() => {
  if (el.value) Plotly.purge(el.value)
})
</script>

<template>
  <div
    ref="el"
    role="img"
    aria-label="Interactive 3D surface of McNemar chi-squared over n01 and n10 counts; the valley along equal counts is zero and the surface rises as the split becomes imbalanced"
    class="w-full h-full"
  />
</template>
