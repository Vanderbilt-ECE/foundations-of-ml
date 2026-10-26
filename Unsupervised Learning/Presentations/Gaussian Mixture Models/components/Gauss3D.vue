<script setup lang="ts">
// A 2D Gaussian density as a 3D hill (Plotly surface), with its contour lines projected onto the floor.
// mode 0: spherical (Sigma = I) · 1: diagonal (different variances, no tilt) · 2: full (correlated, tilted).
// Changing mode morphs the covariance smoothly. The PDF export draws the floor contours as an SVG instead.
import { computed } from 'vue'
import { useTween } from '../utils/clusters'
import { ellipsePath, logpdf } from '../utils/gmm'

const props = withDefaults(defineProps<{ mode?: number }>(), { mode: 0 })
const COVS = [[1, 0, 1], [2.4, 0, 0.45], [1.8, 1.1, 1.2]] // [s_xx, s_xy, s_yy]; determinants near 1 keep the peak heights comparable
const c = useTween(() => COVS[Math.max(0, Math.min(2, props.mode))], 900)
const S = computed(() => [[c.value[0], c.value[1]], [c.value[1], c.value[2]]])

const G = Array.from({ length: 45 }, (_, i) => -4 + 8 * i / 44)
const data = computed(() => [{
  type: 'surface', x: G, y: G, showscale: false, hoverinfo: 'skip',
  z: G.map(y => G.map(x => Math.exp(logpdf([x, y], [0, 0], S.value)))),
  cmin: 0, cmax: 0.16,
  colorscale: [[0, '#0f172a'], [0.2, '#134e4a'], [0.55, '#14b8a6'], [1, '#ccfbf1']],
  contours: { z: { show: true, start: 0.01, end: 0.16, size: 0.02, color: 'rgba(255,255,255,0.35)', project: { z: true }, usecolormap: true } },
  lighting: { ambient: 0.75, diffuse: 0.5, specular: 0.15 },
}])
const axis = (t: string) => ({ title: { text: t, font: { color: '#94a3b8' } }, color: '#64748b', showbackground: false, gridcolor: 'rgba(148,163,184,0.15)', zeroline: false, showticklabels: false })
const layout = { scene: { xaxis: axis('x₁'), yaxis: axis('x₂'), zaxis: { ...axis('density'), range: [0, 0.17] }, aspectmode: 'manual', aspectratio: { x: 1, y: 1, z: 0.6 }, camera: { eye: { x: 1.5, y: -1.45, z: 0.95 } } } }

const PW = 300
const px = (x: number) => PW / 2 + x * PW / 8
const py = (y: number) => PW / 2 - y * PW / 8
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="500" :height="380" spin>
    <template #print>
      <svg :viewBox="`0 0 ${PW} ${PW}`" :style="{ height: '340px' }" class="mx-auto block" role="img" aria-label="Contour ellipses of the Gaussian, seen from above">
        <path v-for="s in [0.5, 1, 1.5, 2, 2.5]" :key="s" :d="ellipsePath([0, 0], S, s, px, py)" :style="{ fill: '#14b8a6', fillOpacity: 0.12, stroke: '#5eead4', strokeWidth: 1.5 }" />
      </svg>
    </template>
  </PlotlyChart>
</template>
