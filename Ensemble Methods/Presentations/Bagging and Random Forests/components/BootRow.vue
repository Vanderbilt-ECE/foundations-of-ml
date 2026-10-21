<script setup lang="ts">
// One row of numbered tokens. With `sample`, shows a bootstrap draw of rows 1..10 from data/tokens.json:
// each drawn row appears once per draw, and the rows never drawn are listed as out-of-bag.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/tokens.json'

const props = withDefaults(defineProps<{ sample?: number, label: string }>(), { sample: -1 })

const palette = ['#2dd4bf', '#60a5fa', '#a78bfa', '#f59e0b', '#f87171', '#34d399', '#38bdf8', '#c084fc', '#fbbf24', '#fb7185']
const drawn = props.sample >= 0 ? d.samples[props.sample] : Array.from({ length: 10 }, (_, i) => i + 1)
const oob = Array.from({ length: 10 }, (_, i) => i + 1).filter(v => !drawn.includes(v))
const repeats = drawn.length - new Set(drawn).size
const cell = 34
const gap = 6
const left = 96
const W = left + 10 * (cell + gap) + 158
const toks = drawn.map((v, i) => ({ key: i, v, x: left + i * (cell + gap), dup: drawn.indexOf(v) !== i }))
</script>

<template>
  <svg role="img" :aria-label="`${label}: rows ${drawn.join(', ')}${oob.length ? `; out-of-bag rows ${oob.join(', ')}` : ''}`" :viewBox="`0 0 ${W} 44`" class="w-full">
    <text x="0" y="27" :style="{ fill: '#94a3b8', fontSize: '14px' }">{{ label }}</text>
    <g v-for="t in toks" :key="t.key">
      <rect :x="t.x" y="4" :width="cell" :height="cell" rx="8"
        :style="{ fill: palette[t.v - 1], fillOpacity: 0.28, stroke: palette[t.v - 1], strokeWidth: t.dup ? 2.5 : 1.5, strokeDasharray: t.dup ? '4 3' : 'none' }" />
      <text :x="t.x + cell / 2" y="27" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '15px', fontWeight: 700 }">{{ t.v }}</text>
    </g>
    <text v-if="sample >= 0" :x="left + 10 * (cell + gap) + 10" y="20" :style="{ fill: '#fca5a5', fontSize: '13px' }">OOB: {{ oob.join(', ') }}</text>
    <text v-if="sample >= 0" :x="left + 10 * (cell + gap) + 10" y="38" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ repeats }} repeat{{ repeats === 1 ? '' : 's' }}</text>
  </svg>
</template>
