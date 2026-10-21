<script setup lang="ts">
// Density as a landscape (data/varied.json: kernel density estimate of the varied-density data, scaled to peak 1).
// Left: the surface in 3D (Plotly) with a translucent "sea level" plane. Right: the view from above;
// land above sea level is shaded by island, and each island is a cluster at that level.
// level = index into levels (0.6, 0.15, 0.025), from high water to low water.
import { computed } from 'vue'
import d from '../data/varied.json'
import { PALETTE } from '../utils/clusters'

const props = withDefaults(defineProps<{ level?: number }>(), { level: 0 })
const lv = computed(() => d.levels[Math.max(0, Math.min(props.level, d.levels.length - 1))].level)
const nx = d.grid.x.length; const ny = d.grid.y.length
const z = d.grid.z as number[][]

// islands: 4-connected components of the cells above sea level, numbered by size
const islands = computed(() => {
  const id = z.map(row => row.map(() => -1))
  const comps: number[][][] = []
  for (let j = 0; j < ny; j++) {
    for (let i = 0; i < nx; i++) {
      if (z[j][i] <= lv.value || id[j][i] >= 0) continue
      const cells: number[][] = []
      const stack = [[j, i]]
      id[j][i] = comps.length
      while (stack.length) {
        const [b, a] = stack.pop()!
        cells.push([b, a])
        for (const [db, da] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
          const bb = b + db; const aa = a + da
          if (bb >= 0 && bb < ny && aa >= 0 && aa < nx && z[bb][aa] > lv.value && id[bb][aa] < 0) {
            id[bb][aa] = comps.length
            stack.push([bb, aa])
          }
        }
      }
      comps.push(cells)
    }
  }
  // the island holding the disk's peak is blue (cluster 1); the others take teal, then amber, left to right
  const order = comps.map((c, k) => ({ k, x: c.reduce((s, q) => s + q[1], 0) / c.length, y: c.reduce((s, q) => s + q[0], 0) / c.length }))
  const colorOf: Record<number, string> = {}
  const low = order.filter(o => o.y < ny * 0.45).sort((a, b) => a.x - b.x)
  low.forEach((o, i) => { colorOf[o.k] = [PALETTE[0], PALETTE[2]][i] ?? PALETTE[3] })
  order.filter(o => o.y >= ny * 0.45).forEach((o) => { colorOf[o.k] = PALETTE[1] })
  return { id, n: comps.length, colorOf }
})

const TW = 300; const TH = TW * (d.grid.y[ny - 1] - d.grid.y[0]) / (d.grid.x[nx - 1] - d.grid.x[0])
const cw = TW / nx; const ch = TH / ny
const px = (x: number) => (x - d.grid.x[0]) / (d.grid.x[nx - 1] - d.grid.x[0]) * TW
const py = (y: number) => TH - (y - d.grid.y[0]) / (d.grid.y[ny - 1] - d.grid.y[0]) * TH

const data = computed(() => [
  {
    type: 'surface', x: d.grid.x, y: d.grid.y, z, showscale: false, hoverinfo: 'skip',
    colorscale: [[0, '#0f172a'], [0.15, '#155e75'], [0.5, '#14b8a6'], [1, '#ccfbf1']],
    contours: { z: { show: true, start: 0.05, end: 1, size: 0.1, color: 'rgba(255,255,255,0.25)' } },
  },
  {
    type: 'surface', x: [d.grid.x[0], d.grid.x[nx - 1]], y: [d.grid.y[0], d.grid.y[ny - 1]],
    z: [[lv.value, lv.value], [lv.value, lv.value]], showscale: false, opacity: 0.55, hoverinfo: 'skip',
    colorscale: [[0, '#2563eb'], [1, '#2563eb']],
  },
])
const axis = (t: string) => ({ title: { text: t }, color: '#94a3b8', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', showticklabels: false })
const layout = { scene: { xaxis: axis(''), yaxis: axis(''), zaxis: { ...axis('density'), range: [0, 1] }, aspectmode: 'manual', aspectratio: { x: 0.85, y: 1.4, z: 0.7 }, camera: { eye: { x: 1.55, y: -1.25, z: 0.95 } } } }
</script>

<template>
  <div class="grid grid-cols-[1.25fr_1fr] gap-4 items-center">
    <PlotlyChart :data="data" :layout="layout" :width="470" :height="380" spin>
      <template #print>
        <svg :viewBox="`0 0 ${TW} ${TH}`" :style="{ height: '360px' }" class="mx-auto block" role="img" aria-label="Estimated density seen from above, brighter is denser">
          <template v-for="(row, j) in z" :key="j">
            <rect v-for="(v, i) in row" :key="i" :x="i * cw" :y="TH - (j + 1) * ch" :width="cw + 0.4" :height="ch + 0.4" :style="{ fill: '#14b8a6', fillOpacity: 0.05 + 0.95 * v }" />
          </template>
        </svg>
      </template>
    </PlotlyChart>
    <div class="flex flex-col items-center">
      <svg :viewBox="`0 0 ${TW} ${TH}`" :style="{ height: '300px' }" role="img" :aria-label="`View from above: ${islands.n} islands above sea level`">
        <template v-for="(row, j) in z" :key="j">
          <rect
            v-for="(v, i) in row" :key="i" :x="i * cw" :y="TH - (j + 1) * ch" :width="cw + 0.4" :height="ch + 0.4"
            :style="{ fill: v > lv ? islands.colorOf[islands.id[j][i]] : '#1e3a8a', fillOpacity: v > lv ? 0.35 + 0.6 * v : 0.12 + 0.5 * v }"
          />
        </template>
        <circle v-for="(p, k) in d.pts" :key="`p${k}`" :cx="px(p[0])" :cy="py(p[1])" r="1.3" :style="{ fill: '#fff', fillOpacity: 0.55 }" />
      </svg>
      <div class="mt-2 text-center">
        <span class="font-mono text-3xl font-bold text-teal-300">{{ islands.n }}</span>
        <span class="text-sm opacity-80"> island{{ islands.n === 1 ? '' : 's' }} at sea level {{ lv }}</span>
      </div>
    </div>
  </div>
</template>
