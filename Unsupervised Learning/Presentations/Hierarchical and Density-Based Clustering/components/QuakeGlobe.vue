<script setup lang="ts">
// Every M4.5+ earthquake of 2024 (USGS; data/quakes.json) on an orbiting globe, colored by DBSCAN cluster
// (haversine distance, ε = 150 km, minPts = 10). Gray = noise. Coastlines from Natural Earth.
// A dark sphere hides the far side; drag to rotate, hover a point for magnitude and depth.
import d from '../data/quakes.json'
import { GRAY, PALETTE } from '../utils/clusters'

const props = withDefaults(defineProps<{ width?: number, height?: number }>(), { width: 470, height: 430 })
const rad = Math.PI / 180
const xyz = (lat: number, lon: number, r = 1) => [r * Math.cos(lat * rad) * Math.cos(lon * rad), r * Math.cos(lat * rad) * Math.sin(lon * rad), r * Math.sin(lat * rad)]
const P = d.lat.map((la, i) => xyz(la, d.lon[i], 1.008))
const coast = { x: [] as (number | null)[], y: [] as (number | null)[], z: [] as (number | null)[] }
for (const line of d.coast) {
  for (const [lo, la] of line) {
    const [x, y, z] = xyz(la, lo, 1.002)
    coast.x.push(x); coast.y.push(y); coast.z.push(z)
  }
  coast.x.push(null); coast.y.push(null); coast.z.push(null)
}
// sphere surface
const N = 40
const sph = { x: [] as number[][], y: [] as number[][], z: [] as number[][] }
for (let a = 0; a <= N; a++) {
  const rx: number[] = []; const ry: number[] = []; const rz: number[] = []
  for (let b = 0; b <= N; b++) {
    const [x, y, z] = xyz(-90 + 180 * a / N, -180 + 360 * b / N, 0.995)
    rx.push(x); ry.push(y); rz.push(z)
  }
  sph.x.push(rx); sph.y.push(ry); sph.z.push(rz)
}
const isNoise = d.db.map(l => l < 0)
const pick = (keep: boolean) => d.db.map((_, i) => i).filter(i => isNoise[i] !== keep)
const clus = pick(true); const noise = pick(false)
const trace = (idx: number[], col: (i: number) => string, size: number) => ({
  type: 'scatter3d', mode: 'markers',
  x: idx.map(i => P[i][0]), y: idx.map(i => P[i][1]), z: idx.map(i => P[i][2]),
  customdata: idx.map(i => [d.mag[i], d.depth[i]]),
  hovertemplate: 'M%{customdata[0]} · depth %{customdata[1]} km<extra></extra>',
  marker: { size, color: idx.map(col), opacity: 0.9, line: { width: 0 } },
})
const data = [
  { type: 'surface', ...sph, showscale: false, hoverinfo: 'skip', colorscale: [[0, '#0b1730'], [1, '#0b1730']], opacity: 1, lighting: { ambient: 1, diffuse: 0, specular: 0 } },
  { type: 'scatter3d', mode: 'lines', ...coast, hoverinfo: 'skip', line: { color: '#64748b', width: 1.5 } },
  trace(noise, () => GRAY, 2),
  trace(clus, i => PALETTE[d.dbCol[d.db[i]]], 2.6),
]
const hidden = { visible: false, range: [-1.05, 1.05] }
const layout = { scene: { xaxis: hidden, yaxis: hidden, zaxis: hidden, aspectmode: 'cube', camera: { eye: { x: -1.45, y: 0.62, z: 0.42 } } } }
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="props.width" :height="props.height" spin globe />
</template>
