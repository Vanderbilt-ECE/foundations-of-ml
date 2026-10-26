<script setup lang="ts">
// The fitted Old Faithful density p(x) as a surface (data/faithful.json; height scaled to peak 1).
// Each eruption is lifted to its own density; the six flagged as anomalies (lowest 2%) are red,
// and the translucent plane is the density threshold that flags them. The PDF export shows it from above.
import f from '../data/faithful.json'

const flagged = f.flag.map((v, i) => (v ? i : -1)).filter(i => i >= 0)
const height = (i: number) => Math.exp(f.logd[i]) / f.grid.peak
const thr = Math.exp(f.thr) / f.grid.peak
const pick = (idx: number[]) => ({ x: idx.map(i => f.pts[i][0]), y: idx.map(i => f.pts[i][1]), z: idx.map(height) })
const normal = f.pts.map((_, i) => i).filter(i => !f.flag[i])
const [x0, x1] = [f.grid.x[0], f.grid.x[f.grid.x.length - 1]]
const [y0, y1] = [f.grid.y[0], f.grid.y[f.grid.y.length - 1]]
const data = [
  {
    type: 'surface', x: f.grid.x, y: f.grid.y, z: f.grid.z, showscale: false, hoverinfo: 'skip', opacity: 0.85,
    colorscale: [[0, '#0f172a'], [0.15, '#1e3a5f'], [0.5, '#14b8a6'], [1, '#ccfbf1']],
    contours: { z: { show: true, start: 0.05, end: 1, size: 0.1, color: 'rgba(255,255,255,0.3)' } },
  },
  { type: 'surface', x: [x0, x1], y: [y0, y1], z: [[thr, thr], [thr, thr]], showscale: false, opacity: 0.35, hoverinfo: 'skip', colorscale: [[0, '#f87171'], [1, '#f87171']] },
  { type: 'scatter3d', mode: 'markers', hoverinfo: 'skip', ...pick(normal), marker: { size: 2.6, color: '#e2e8f0', opacity: 0.9 } },
  { type: 'scatter3d', mode: 'markers', hoverinfo: 'skip', ...pick(flagged), marker: { size: 6, color: '#f87171', line: { color: '#fff', width: 1 } } },
]
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false })
const layout = { scene: { xaxis: axis('eruption (min)'), yaxis: axis('wait (min)'), zaxis: { ...axis('density'), showticklabels: false, range: [0, 1.05] }, aspectmode: 'manual', aspectratio: { x: 1, y: 1.15, z: 0.65 }, camera: { eye: { x: 1.65, y: -1.25, z: 0.85 } } } }
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="560" :height="400" spin>
    <template #print>
      <GmmPlot :pts="f.pts" :mix="f.gmm" mode="gray" field="density" :domain="{ x: [1.3, 5.4], y: [40, 100] }" :equal="false" :focus="flagged" :levels="[]" :means="false" :w="520" :h="380" :r="3" />
    </template>
  </PlotlyChart>
</template>
