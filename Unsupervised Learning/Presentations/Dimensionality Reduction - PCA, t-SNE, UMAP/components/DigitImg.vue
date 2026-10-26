<script setup lang="ts">
// An 8x8 image as 64 SVG squares. Grayscale (dark -> light) for pixel values 0-16, or diverging
// (violet negative, dark zero, teal positive) for principal components and other signed images.
import { computed } from 'vue'
import { decode } from '../utils/plot'

const props = withDefaults(defineProps<{
  v: string | number[]
  size?: number
  div?: boolean
  max?: number // value drawn at full intensity (default 16, or max |v| when diverging)
  frame?: boolean
}>(), { size: 64, div: false, frame: true })

const vals = computed(() => (typeof props.v === 'string' ? decode(props.v) : props.v))
const top = computed(() => props.max ?? (props.div ? Math.max(1e-9, ...vals.value.map(Math.abs)) : 16))
const DARK = [15, 23, 42]; const LIGHT = [226, 232, 240]; const POS = [45, 212, 191]; const NEG = [167, 139, 250]
const mix = (a: number[], b: number[], t: number) => `rgb(${a.map((v, i) => Math.round(v + (b[i] - v) * t)).join(',')})`
const fill = (x: number) => {
  const t = Math.max(-1, Math.min(1, x / top.value))
  if (!props.div) return mix(DARK, LIGHT, Math.max(0, t))
  return t >= 0 ? mix(DARK, POS, t) : mix(DARK, NEG, -t)
}
</script>

<template>
  <svg viewBox="0 0 8 8" :width="size" :height="size" shape-rendering="crispEdges" class="block" :style="{ outline: frame ? '1px solid rgba(148,163,184,0.35)' : 'none' }" role="img" aria-label="8 by 8 pixel image">
    <rect v-for="(x, i) in vals" :key="i" :x="i % 8" :y="Math.floor(i / 8)" width="1.02" height="1.02" :fill="fill(x)" />
  </svg>
</template>
