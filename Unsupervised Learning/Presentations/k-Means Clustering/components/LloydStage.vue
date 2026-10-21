<script setup lang="ts">
// Lloyd's algorithm on blobs3, driven by the slide's click count (data/blobs3.json).
//   steps[i] = which recorded frame to show after i clicks
//   (frames: init, assign, update, assign, ..., final assign with no change)
// Side panel: phase, iteration, and a J curve that grows as the run proceeds.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import run from '../data/blobs3.json'
import { domainOf, fmt, useTween } from '../utils/kmeans'

const props = withDefaults(defineProps<{
  steps?: number[]
  cells?: boolean
  lines?: boolean
  trails?: boolean
  panel?: boolean
  w?: number
  h?: number
}>(), { steps: () => run.frames.map((_, i) => i), cells: true, lines: false, trails: true, panel: true, w: 520, h: 400 })

const { $clicks } = useSlideContext()
const fi = computed(() => props.steps[Math.min($clicks.value, props.steps.length - 1)])
const f = computed(() => run.frames[fi.value])
const last = run.frames.length - 1
const dom = domainOf(run.pts as number[][], 0.08)

// centroid path so far: positions after each update
const trails = computed(() => {
  if (!props.trails) return null
  const hist: number[][][] = run.frames[0].c.map(() => [])
  run.frames.slice(0, fi.value + 1).forEach((fr, i) => {
    if (i === 0 || fr.phase === 'update') fr.c.forEach((c, k) => hist[k].push(c))
  })
  return hist
})
const iter = computed(() => run.frames.slice(1, fi.value + 1).filter(x => x.phase === 'update').length)
const phase = computed(() => (fi.value === last ? 'converged' : f.value.phase))
const phaseText: Record<string, string> = {
  init: 'K = 3 centroids on random data points',
  assign: 'Each point joins its nearest centroid',
  update: 'Each centroid moves to the mean of its points',
  converged: 'No point changed cluster. Done.',
}
const J = useTween(() => [f.value.J ?? 0], 600)

// J chart: one dot per frame that has a J
const Js = run.frames.map((x, i) => ({ i, J: x.J, phase: x.phase })).filter(x => x.J != null) as { i: number, J: number, phase: string }[]
const CW = 250; const CH = 150; const cl = 40; const cr = 240; const ct = 10; const cb = 122
const jmax = Math.max(...Js.map(x => x.J))
const cx = (i: number) => cl + (i - 1) / (last - 1) * (cr - cl)
const cy = (v: number) => cb - v / jmax * (cb - ct)
const shown = computed(() => Js.filter(x => x.i <= fi.value))
</script>

<template>
  <div class="grid gap-5 items-center" :class="panel ? 'grid-cols-[1.45fr_1fr]' : 'grid-cols-1'">
    <ClusterPlot
      :pts="run.pts" :lab="f.lab" :centroids="f.c" :trails="trails" :domain="dom"
      :cells="cells && f.lab !== null" :lines="lines" :w="w" :h="h"
      label="Lloyd's algorithm on three blobs: points colored by nearest centroid"
    />
    <div v-if="panel" class="text-left space-y-3">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
        <div class="text-xs uppercase tracking-wider opacity-60">Iteration {{ iter }}</div>
        <div class="text-lg font-bold mt-1 phase" :class="{ 'text-blue-300': phase === 'assign', 'text-teal-300': phase === 'update', 'text-amber-300': phase === 'init', 'text-green-300': phase === 'converged' }">
          {{ phase === 'converged' ? 'Converged' : phase[0].toUpperCase() + phase.slice(1) }}
        </div>
        <div class="text-sm opacity-80 mt-1 leading-snug" style="min-height: 2.6em">{{ phaseText[phase] }}</div>
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
        <div class="flex items-baseline justify-between">
          <span class="text-sm opacity-70">Objective J</span>
          <span class="text-2xl font-bold font-mono text-amber-300">{{ f.J == null ? '—' : fmt(J[0], 1) }}</span>
        </div>
        <svg :viewBox="`0 0 ${CW} ${CH}`" class="w-full mt-1" role="img" aria-label="Objective J after each step; it only goes down">
          <line :x1="cl" :x2="cr" :y1="cb" :y2="cb" :style="{ stroke: '#475569' }" />
          <line :x1="cl" :x2="cl" :y1="ct" :y2="cb" :style="{ stroke: '#475569' }" />
          <text :x="cl - 6" :y="cy(jmax) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ Math.round(jmax) }}</text>
          <text :x="cl - 6" :y="cb + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '10px' }">0</text>
          <text :x="(cl + cr) / 2" :y="CH - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">step →</text>
          <polyline :points="shown.map(x => `${cx(x.i)},${cy(x.J)}`).join(' ')" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
          <circle v-for="x in shown" :key="x.i" :cx="cx(x.i)" :cy="cy(x.J)" r="3.5" :style="{ fill: x.phase === 'assign' ? '#60a5fa' : '#2dd4bf' }" />
        </svg>
        <div class="flex gap-4 text-xs opacity-70 mt-1">
          <span><span class="inline-block w-2 h-2 rounded-full bg-blue-400 mr-1" />after assign</span>
          <span><span class="inline-block w-2 h-2 rounded-full bg-teal-400 mr-1" />after update</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.phase { transition: color 0.4s ease; }
</style>
