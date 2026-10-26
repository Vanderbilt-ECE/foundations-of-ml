<script setup lang="ts">
// One digit (a "3" from data/digits.json) as an 8x8 grid of pixels; step 1 unrolls the grid, row by row,
// into a single row of 64 numbers: the feature vector. Each pixel flies to its slot with a small stagger.
// Hover any pixel (in either layout) to see its row, column, feature index and value.
import { computed, ref } from 'vue'
import d from '../data/digits.json'
import { decode } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const v = decode(d.img[d.picks[2]])
const W = 800; const H = 250
const G = 24; const gx = W / 2 - 4 * G; const gy = 12 // grid: 24px cells, centered
const R = 12; const rx = (W - 64 * R) / 2; const ry = 150 // row: 12px cells
const pos = (i: number) => (props.step >= 1
  ? { x: rx + i * R, y: ry, s: R }
  : { x: gx + (i % 8) * G, y: gy + Math.floor(i / 8) * G, s: G })
const hot = ref<number | null>(null)
const shade = (x: number) => `rgb(${[15, 23, 42].map((a, k) => Math.round(a + ([226, 232, 240][k] - a) * x / 16)).join(',')})`
const info = computed(() => (hot.value == null ? null : { r: Math.floor(hot.value / 8), c: hot.value % 8, j: hot.value, x: v[hot.value] }))
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 260px" role="img" aria-label="An 8 by 8 image of a handwritten 3 unrolled into a row of 64 pixel values">
    <g
      v-for="(x, i) in v" :key="i" class="px" :style="{ transform: `translate(${pos(i).x}px, ${pos(i).y}px)`, transitionDelay: `${(step ? i : 63 - i) * 14}ms` }"
      @pointerenter="hot = i" @pointerleave="hot = null"
    >
      <rect :width="pos(i).s" :height="step ? R * 2.4 : pos(i).s" class="cell" :style="{ fill: shade(x), stroke: hot === i ? '#fbbf24' : 'rgba(148,163,184,0.25)', strokeWidth: hot === i ? 2 : 0.6 }" />
    </g>
    <g class="reveal" :class="{ shown: step >= 1 }">
      <text :x="rx" :y="ry - 8" :style="{ fill: '#94a3b8', fontSize: '12px' }">x₁</text>
      <text :x="rx + 64 * R" :y="ry - 8" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">x₆₄</text>
      <text :x="W / 2" :y="ry + R * 2.4 + 26" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '15px' }" class="font-mono">x = ( {{ v.slice(0, 12).join(', ') }}, … , {{ v.slice(-4).join(', ') }} ) ∈ ℝ⁶⁴</text>
    </g>
    <text v-if="info" :x="W - 8" :y="22" text-anchor="end" :style="{ fill: '#fcd34d', fontSize: '14px' }" class="font-mono">row {{ info.r + 1 }}, col {{ info.c + 1 }} → feature x{{ info.j + 1 }} = {{ info.x }}</text>
  </svg>
</template>

<style scoped>
.px { transition: transform 0.9s cubic-bezier(0.65, 0, 0.35, 1); cursor: crosshair; }
.cell { transition: width 0.9s ease, height 0.9s ease; }
</style>
