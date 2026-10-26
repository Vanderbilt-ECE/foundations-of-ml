<script setup lang="ts">
// 5-fold cross-validated accuracy of StandardScaler -> PCA(k) -> LogisticRegression on digits (data/clf.json),
// against k. Hover for exact values. The dashed line is the accuracy with all 64 components.
import d from '../data/clf.json'

const full = d.acc[d.acc.length - 1]
const data = [
  {
    type: 'scatter', mode: 'lines+markers', x: d.k, y: d.acc, line: { color: '#2dd4bf', width: 3, shape: 'spline' },
    marker: { size: 8, color: '#2dd4bf', line: { color: '#0b1020', width: 1.5 } },
    hovertemplate: 'k = %{x}<br>accuracy %{y:.1%}<extra></extra>',
  },
]
const layout = {
  margin: { l: 56, r: 16, t: 10, b: 46 },
  xaxis: { title: { text: 'principal components kept (k)' }, type: 'log', tickvals: [1, 2, 5, 10, 20, 30, 64], gridcolor: 'rgba(148,163,184,0.12)', zeroline: false },
  yaxis: { title: { text: 'CV accuracy' }, tickformat: '.0%', range: [0.3, 1], gridcolor: 'rgba(148,163,184,0.12)', zeroline: false },
  shapes: [{ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: full, y1: full, line: { color: '#fbbf24', dash: 'dash', width: 1.5 } }],
  annotations: [{ xref: 'paper', x: 0.02, y: full, yshift: 10, text: `all 64: ${(100 * full).toFixed(1)}%`, showarrow: false, font: { color: '#fcd34d' }, xanchor: 'left' }],
  hoverlabel: { bgcolor: '#0b1020', bordercolor: '#2dd4bf', font: { color: '#e2e8f0' } },
}
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="500" :height="300" />
</template>
