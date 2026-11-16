<script setup lang="ts">
// A layered network drawn as nodes and edges, with signal flowing through it.
// Edge color/opacity come from a real (randomly initialized) MLP: teal = positive weight, violet = negative.
//   mode 'forward'  : teal pulses sweep left -> right, layer by layer, and nodes light up as the wave arrives
//   mode 'backward' : amber pulses sweep right -> left; edge width = |dLoss/dw| for one example (real gradients)
//   mode 'loss'     : forward pass done, the output shows its error
//   mode 'update'   : after one gradient step, edges re-draw with the new weights
//   mode 'none'     : static
// In print mode the wave is frozen mid-network.
import { computed, ref } from 'vue'
import { MLP } from '../utils/mlp'
import { C, clamp, rng, useActive, useLoop } from '../utils/plot'

const props = withDefaults(defineProps<{
  layers?: number[]
  mode?: 'forward' | 'backward' | 'loss' | 'update' | 'none'
  labels?: string[]
  height?: number
  seed?: number
}>(), { layers: () => [3, 5, 5, 2], mode: 'forward', labels: () => [], height: 300, seed: 7 })

const W = 640
const H = computed(() => props.height)
const padX = 60
const top = 24
const bottom = computed(() => (props.labels.length ? 38 : 18))

const net = new MLP(props.layers, 'tanh', 'sigmoid', props.seed, 1.3)
// one example and its gradients, for the backward view
const R = rng(props.seed + 1)
const x0 = Array.from({ length: props.layers[0] }, () => R.n())
const y0 = Array.from({ length: props.layers.at(-1)! }, (_, k) => +(k === 0))
const g = net.grads([x0], [y0]).gW
const gMax = Math.max(...g.flat(2).map(Math.abs))
// weights after a (deliberately large, for visibility) gradient step
const W1 = net.W.map((M, l) => M.map((r, j) => r.map((w, i) => w - 6 * g[l][j][i])))
const wMax = Math.max(...net.W.flat(2).map(Math.abs), ...W1.flat(2).map(Math.abs))

const nodeX = (l: number) => padX + l * (W - 2 * padX) / (props.layers.length - 1)
const nodeY = (l: number, i: number) => {
  const n = props.layers[l]
  const span = H.value - top - bottom.value
  const gap = Math.min(52, span / Math.max(1, n - 1))
  return top + span / 2 + (i - (n - 1) / 2) * gap
}
const nodes = computed(() => props.layers.flatMap((n, l) => Array.from({ length: n }, (_, i) => ({ l, i, x: nodeX(l), y: nodeY(l, i) }))))
const edges = computed(() => {
  const out: { l: number, i: number, j: number, x1: number, y1: number, x2: number, y2: number, w: number, w1: number, gr: number }[] = []
  for (let l = 0; l < props.layers.length - 1; l++) {
    for (let j = 0; j < props.layers[l + 1]; j++) {
      for (let i = 0; i < props.layers[l]; i++)
        out.push({ l, i, j, x1: nodeX(l), y1: nodeY(l, i), x2: nodeX(l + 1), y2: nodeY(l + 1, j), w: net.W[l][j][i], w1: W1[l][j][i], gr: g[l][j][i] })
    }
  }
  return out
})

// wave position s in [0, nGaps]: s = 1.5 means halfway between layer 1 and layer 2
const gaps = props.layers.length - 1
const { isPrintMode } = useActive()
const s = ref(gaps * 0.55)
const PERIOD = 1.1 // seconds per layer gap
useLoop((_, t) => {
  const cyc = (t / PERIOD) % (gaps + 1.2)
  const f = Math.min(cyc, gaps)
  s.value = props.mode === 'backward' ? gaps - f : f
})

const isWave = computed(() => props.mode === 'forward' || props.mode === 'backward')
const waveColor = computed(() => (props.mode === 'backward' ? C.amber : C.teal))
const glow = (l: number) => (isWave.value ? Math.exp(-((s.value - l) ** 2) / 0.08) : 0)

function edgeStyle(e: (typeof edges.value)[number]) {
  const w = props.mode === 'update' ? e.w1 : e.w
  if (props.mode === 'backward') {
    const m = Math.abs(e.gr) / gMax
    return { stroke: C.amber, strokeOpacity: 0.15 + 0.75 * m, strokeWidth: 0.6 + 5 * m, transition: 'all 0.6s' }
  }
  const m = Math.abs(w) / wMax
  return { stroke: w >= 0 ? C.teal : C.violet, strokeOpacity: 0.12 + 0.6 * m, strokeWidth: 0.6 + 3.2 * m, transition: 'all 0.8s' }
}
// pulses: one dot per edge currently inside the wave front
const pulses = computed(() => {
  if (!isWave.value) return []
  const l = Math.floor(clamp(s.value, 0, gaps - 1e-6))
  const u = s.value - l
  return edges.value.filter(e => e.l === l).map(e => ({ x: e.x1 + (e.x2 - e.x1) * u, y: e.y1 + (e.y2 - e.y1) * u, o: 0.35 + 0.65 * Math.abs(props.mode === 'backward' ? e.gr / gMax : e.w / wMax) }))
})
const outLayer = props.layers.length - 1
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" :style="{ maxHeight: `${H}px` }" role="img" :aria-label="`A neural network with layers of ${layers.join(', ')} units`">
    <line v-for="(e, k) in edges" :key="k" :x1="e.x1" :y1="e.y1" :x2="e.x2" :y2="e.y2" :style="edgeStyle(e)" />
    <circle v-for="(p, k) in pulses" :key="`p${k}`" :cx="p.x" :cy="p.y" r="3.6" :style="{ fill: waveColor, fillOpacity: p.o }" />
    <g v-for="(n, k) in nodes" :key="`n${k}`">
      <circle :cx="n.x" :cy="n.y" :r="11 + 5 * glow(n.l)" :style="{ fill: waveColor, fillOpacity: 0.25 * glow(n.l) }" />
      <circle
        :cx="n.x" :cy="n.y" r="11"
        :style="{
          fill: '#0f172a',
          stroke: mode === 'loss' && n.l === outLayer ? C.red : (n.l === 0 ? C.blue : n.l === outLayer ? C.amber : C.teal),
          strokeWidth: mode === 'loss' && n.l === outLayer ? 3.5 : 2.2,
          transition: 'stroke 0.5s',
        }"
      />
    </g>
    <g v-if="mode === 'loss'">
      <text :x="nodeX(outLayer) + 20" :y="nodeY(outLayer, 0) - 18" :style="{ fill: C.red, fontSize: '14px', fontWeight: 700 }">error</text>
    </g>
    <text v-for="(lab, l) in labels" :key="`l${l}`" :x="nodeX(l)" :y="H - 10" text-anchor="middle" :style="{ fill: C.muted, fontSize: '13px' }">{{ lab }}</text>
    <text v-if="isPrintMode && isWave" :x="W - 4" y="14" text-anchor="end" :style="{ fill: waveColor, fontSize: '11px' }">{{ mode === 'backward' ? '← gradients' : 'signal →' }}</text>
  </svg>
</template>
