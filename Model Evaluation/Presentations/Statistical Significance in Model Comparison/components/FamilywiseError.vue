<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Plotly from 'plotly.js-dist-min'
import { axis, baseLayout, config } from './plotTheme'

const props = defineProps<{ step: number }>()
const el = ref<HTMLDivElement | null>(null)
const a = 0.05
const ms = Array.from({ length: 50 }, (_, i) => i + 1)
const visibility = () => [true, props.step >= 1, props.step >= 2, props.step >= 2]

onMounted(() => {
  const raw = {
    type: 'scatter', mode: 'lines', x: ms, y: ms.map(m => 1 - (1 - a) ** m),
    line: { color: '#f87171', width: 4 }, fill: 'tozeroy', fillcolor: 'rgba(248,113,113,.10)',
    hovertemplate: '%{x} comparisons<br>P(≥1 false win) = %{y:.0%}<extra></extra>',
  }
  const pt = {
    type: 'scatter', mode: 'markers+text', x: [20], y: [1 - (1 - a) ** 20],
    marker: { color: '#fbbf24', size: 12, line: { color: '#0f172a', width: 2 } },
    text: ['64% at m = 20'], textposition: 'bottom right', textfont: { color: '#fbbf24', size: 14 }, hoverinfo: 'skip',
  }
  const bonf = {
    type: 'scatter', mode: 'lines', x: ms, y: ms.map(m => 1 - (1 - a / m) ** m),
    line: { color: '#2dd4bf', width: 4 },
    hovertemplate: '%{x} comparisons<br>with Bonferroni = %{y:.1%}<extra></extra>',
  }
  const line05 = {
    type: 'scatter', mode: 'lines', x: [1, 50], y: [0.05, 0.05],
    line: { color: 'rgba(226,232,240,.55)', width: 2, dash: 'dash' }, hoverinfo: 'skip',
  }
  const layout = {
    ...baseLayout,
    xaxis: axis('Number of comparisons m', { range: [1, 50] }),
    yaxis: axis('P(at least one false "win")', { range: [0, 1.02], tickformat: '.0%', dtick: 0.2 }),
    annotations: [
      { x: 50, y: 0.93, xref: 'x', yref: 'y', text: 'uncorrected α = 0.05 per test', showarrow: false, xanchor: 'right', font: { size: 13, color: '#fca5a5' } },
      { x: 50, y: 0.14, xref: 'x', yref: 'y', text: 'Bonferroni: α/m per test', showarrow: false, xanchor: 'right', font: { size: 13, color: '#5eead4' } },
    ],
  }
  Plotly.newPlot(el.value!, [raw, pt, bonf, line05] as any, layout as any, config as any).then(() => {
    Plotly.restyle(el.value!, { visible: visibility() } as any)
  })
})
watch(() => props.step, () => { if (el.value) Plotly.restyle(el.value, { visible: visibility() } as any) })
onBeforeUnmount(() => { if (el.value) Plotly.purge(el.value) })
</script>

<template>
  <div ref="el" role="img" aria-label="Line chart: the chance of at least one false positive grows from 5 percent at one comparison to 64 percent at twenty and over 90 percent at fifty, while a Bonferroni correction holds it near 5 percent" class="w-full h-full" />
</template>
