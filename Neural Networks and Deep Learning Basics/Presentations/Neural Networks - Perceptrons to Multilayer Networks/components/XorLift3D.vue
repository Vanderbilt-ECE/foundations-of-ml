<script setup lang="ts">
// XOR lifted into 3D by one hidden neuron, h = AND(x₁, x₂), drawn with Plotly for real perspective.
//   step 0: the four XOR points on the floor (h = 0 for all)
//   step 1: (1,1) rises to h = 1 (its old spot stays as a hollow marker)
//   step 2: the plane x₁ + x₂ − 2h = 0.5 fades in, with dotted gaps from each point to it:
//           teal points sit under the plane, violet points over it
// Plotly doesn't tween 3D traces, so the lift height and the plane's opacity are tweened here and
// PlotlyChart redraws on every change. The camera sways gently so the depth reads; drag to rotate.
// PDF export has no WebGL: the #print slot falls back to the hand-projected SVG in XorLift.vue.
import { computed } from 'vue'
import { C, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const lift = useTween(() => (props.step >= 1 ? 1 : 0), 1100)
const fade = useTween(() => (props.step >= 2 ? 1 : 0), 700)

const planeH = (x: number, y: number) => (x + y - 0.5) / 2
const PTS = [
  { x: 0, y: 0, cls: 0, pos: 'bottom left' },
  { x: 0, y: 1, cls: 1, pos: 'top left' },
  { x: 1, y: 0, cls: 1, pos: 'bottom right' },
  { x: 1, y: 1, cls: 0, pos: 'top right' },
]
const hOf = (p: typeof PTS[number]) => (p.x === 1 && p.y === 1 ? lift.value : 0)
const label = (p: typeof PTS[number]) => (p.x === 1 && p.y === 1 && lift.value > 0.5 ? '(1,1)  h = 1' : `(${p.x},${p.y})`)

const line = (P: number[][], color: string, width = 4, dash = 'solid', opacity = 1) => ({
  type: 'scatter3d', mode: 'lines', hoverinfo: 'skip', opacity,
  x: P.map(p => p[0]), y: P.map(p => p[1]), z: P.map(p => p[2]),
  line: { color, width, dash },
})
const markers = (cls: number) => {
  const P = PTS.filter(p => p.cls === cls)
  return {
    type: 'scatter3d', mode: 'markers+text', hoverinfo: 'skip',
    x: P.map(p => p.x), y: P.map(p => p.y), z: P.map(hOf),
    text: P.map(label), textposition: P.map(p => p.pos),
    textfont: { color: C.text, size: 14 },
    marker: { size: 11, symbol: cls ? 'circle' : 'square', color: cls ? C.teal : C.violet, line: { color: C.bg, width: 1 } },
  }
}

const E = [-0.12, 1.12] // the plane's extent over the floor
const F = [-0.2, 1.2] // the floor's extent
const data = computed(() => {
  const f = fade.value
  const T: any[] = [
    // a faint floor at h = 0, then the XOR square on it
    { type: 'surface', hoverinfo: 'skip', showscale: false, opacity: 0.35, x: [F, F], y: [[F[0], F[0]], [F[1], F[1]]], z: [[0, 0], [0, 0]],
      colorscale: [[0, C.grid], [1, C.grid]], lighting: { ambient: 1, diffuse: 0, specular: 0 } },
    line([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 0]], C.dim, 3),
  ]
  if (lift.value > 0.02) {
    T.push(line([[1, 1, 0], [1, 1, lift.value]], C.amber, 4, 'dash'))
    T.push({ type: 'scatter3d', mode: 'markers', hoverinfo: 'skip', x: [1], y: [1], z: [0], marker: { size: 9, symbol: 'square-open', color: C.violet, opacity: 0.6 } })
  }
  if (f > 0.01) {
    T.push({
      type: 'surface', hoverinfo: 'skip', showscale: false, opacity: 0.42 * f,
      x: [E, E], y: [[E[0], E[0]], [E[1], E[1]]], z: [[planeH(E[0], E[0]), planeH(E[1], E[0])], [planeH(E[0], E[1]), planeH(E[1], E[1])]],
      colorscale: [[0, C.amber], [1, C.amber]], lighting: { ambient: 0.9, diffuse: 0.3, specular: 0.05 },
    })
    T.push(line([[E[0], E[0]], [E[1], E[0]], [E[1], E[1]], [E[0], E[1]], [E[0], E[0]]].map(([x, y]) => [x, y, planeH(x, y)]), C.amber, 3, 'solid', f))
    for (const p of PTS) T.push(line([[p.x, p.y, hOf(p)], [p.x, p.y, planeH(p.x, p.y)]], p.cls ? C.teal : C.violet, 5, 'dot', f))
  }
  T.push(markers(1), markers(0))
  return T
})

const axis = (title: string, color: string, range: number[]) => ({
  title: { text: title, font: { color, size: 14 } }, range, tickvals: [0, 0.5, 1], ticktext: ['0', '', '1'],
  tickfont: { color: C.muted, size: 11 }, color: C.dim, gridcolor: 'rgba(148,163,184,0.22)',
  showbackground: false, zeroline: false, showspikes: false,
})
const eye = { x: 1.2, y: -1.5, z: 0.72 }
const layout = computed(() => ({
  scene: {
    xaxis: axis('x₁', C.muted, [-0.2, 1.2]),
    yaxis: axis('x₂', C.muted, [-0.2, 1.2]),
    zaxis: axis('h = AND(x₁, x₂)', C.amber, [-0.45, 1.15]),
    aspectmode: 'manual', aspectratio: { x: 1, y: 1, z: 0.85 },
    camera: { eye, center: { x: 0, y: 0, z: -0.1 } },
    annotations: fade.value > 0.5
      ? [{ x: E[0], y: E[0], z: planeH(E[0], E[0]), text: 'x₁ + x₂ − 2h = 0.5', showarrow: false, yanchor: 'top', yshift: -8, font: { color: C.amber, size: 14 } }]
      : [],
  },
}))
</script>

<template>
  <PlotlyChart :data="data" :layout="layout" :width="500" :height="350" :sway="0.22">
    <template #print>
      <XorLift :step="step" />
    </template>
  </PlotlyChart>
</template>
