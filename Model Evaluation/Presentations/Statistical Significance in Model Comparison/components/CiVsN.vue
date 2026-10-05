<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Plotly from 'plotly.js-dist-min'
import { axis, baseLayout, config } from './plotTheme'

const el = ref<HTMLDivElement | null>(null)
const p = 0.9
const half = (n: number) => 196 * Math.sqrt(p * (1 - p) / n)

onMounted(() => {
  const ns = Array.from({ length: 120 }, (_, i) => Math.round(Math.pow(10, 1.7 + (i / 119) * 2.6)))
  const marks = [100, 200, 1000, 10000]
  const curve = {
    type: 'scatter', mode: 'lines', x: ns, y: ns.map(half),
    line: { color: '#2dd4bf', width: 4 }, fill: 'tozeroy', fillcolor: 'rgba(45,212,191,.12)',
    hovertemplate: 'n = %{x}<br>±%{y:.1f} pts<extra></extra>',
  }
  const pts = {
    type: 'scatter', mode: 'markers+text', x: marks, y: marks.map(half),
    marker: { color: '#fbbf24', size: 11, line: { color: '#0f172a', width: 2 } },
    text: marks.map(n => `±${half(n).toFixed(1)}`),
    textposition: ['top right', 'bottom left', 'top right', 'top right'],
    textfont: { color: '#fbbf24', size: 14 }, hoverinfo: 'skip',
  }
  const layout = {
    ...baseLayout,
    xaxis: axis('Test-set size n (log scale)', { type: 'log', range: [1.7, 4.3], tickvals: [100, 300, 1000, 3000, 10000], ticktext: ['100', '300', '1k', '3k', '10k'] }),
    yaxis: axis('95% CI half-width (accuracy pts)', { range: [0, 10], ticksuffix: '' }),
    annotations: [{
      xref: 'paper', yref: 'paper', x: 0.98, y: 0.98, xanchor: 'right', yanchor: 'top', showarrow: false,
      text: 'curve drawn for p̂ = 90%', font: { size: 14, color: '#5eead4' },
    }, {
      x: Math.log10(200), y: half(200), ax: 80, ay: -55, showarrow: true, arrowcolor: '#94a3b8',
      text: '91% vs 89% at n = 200:<br>each score is ±4 pts', font: { size: 13, color: '#e2e8f0' }, align: 'left',
    }],
  }
  Plotly.newPlot(el.value!, [curve, pts] as any, layout as any, config as any)
})
onBeforeUnmount(() => { if (el.value) Plotly.purge(el.value) })
</script>

<template>
  <div ref="el" role="img" aria-label="Line chart: the 95 percent confidence interval half-width for an accuracy of 90 percent shrinks as test set size grows, from about 6 points at n=100 to under 1 point at n=10000" class="w-full h-full" />
</template>
