<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Plotly from 'plotly.js-dist-min'
import { axis, baseLayout, config, normCdf } from './plotTheme'

const props = defineProps<{ step: number }>()
const el = ref<HTMLDivElement | null>(null)
const q = 0.1
const gaps = [
  { d: 0.05, c: '#2dd4bf' },
  { d: 0.03, c: '#60a5fa' },
  { d: 0.02, c: '#a78bfa' },
  { d: 0.01, c: '#fbbf24' },
]
const power = (n: number, d: number) => normCdf(d * Math.sqrt(n / q) - 1.96)

const visibility = () => [true, ...gaps.map((_, i) => i < props.step)]

onMounted(() => {
  const ns = Array.from({ length: 140 }, (_, i) => Math.round(Math.pow(10, 2 + (i / 139) * 2.5)))
  const ref80 = {
    type: 'scatter', mode: 'lines', x: [100, 31623], y: [0.8, 0.8],
    line: { color: 'rgba(226,232,240,.6)', width: 2, dash: 'dash' }, hoverinfo: 'skip',
  }
  const curves = gaps.map(g => ({
    type: 'scatter', mode: 'lines', x: ns, y: ns.map(n => power(n, g.d)),
    line: { color: g.c, width: 4 }, name: `${g.d * 100} pts`,
    hovertemplate: `gap ${g.d * 100} pts<br>n = %{x}<br>power = %{y:.0%}<extra></extra>`,
    visible: false,
  }))
  const layout = {
    ...baseLayout,
    xaxis: axis('Test-set size n (log scale)', { type: 'log', range: [2, 4.5], tickvals: [100, 300, 1000, 3000, 10000, 30000], ticktext: ['100', '300', '1k', '3k', '10k', '30k'] }),
    yaxis: axis('Power', { range: [0, 1.02], tickformat: '.0%', dtick: 0.2 }),
    annotations: [{ x: 4.45, y: 0.8, xref: 'x', yref: 'y', text: '80% power', showarrow: false, xanchor: 'right', yanchor: 'top', font: { size: 13, color: '#e2e8f0' } }],
  }
  Plotly.newPlot(el.value!, [ref80, ...curves] as any, layout as any, config as any).then(() => {
    Plotly.restyle(el.value!, { visible: visibility() } as any)
  })
})
watch(() => props.step, () => { if (el.value) Plotly.restyle(el.value, { visible: visibility() } as any) })
onBeforeUnmount(() => { if (el.value) Plotly.purge(el.value) })
</script>

<template>
  <div ref="el" role="img" aria-label="Power curves: the probability of detecting a real accuracy gap rises with test-set size, and smaller gaps need far more data to reach 80 percent power" class="w-full h-full" />
</template>
