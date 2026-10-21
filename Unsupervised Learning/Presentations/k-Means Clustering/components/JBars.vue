<script setup lang="ts">
// J after every half-step of the Lloyd run on blobs3 (data/blobs3.json).
// Blue = after an assign step, teal = after an update step. Bars grow in on mount.
import { useNav } from '@slidev/client'
import { onMounted, ref } from 'vue'
import run from '../data/blobs3.json'

const steps = run.frames.map((f, i) => ({ i, J: f.J, phase: f.phase })).filter(s => s.J != null) as { i: number, J: number, phase: string }[]
const W = 560; const H = 250; const L = 20; const R = 550; const T = 24; const B = 200
const bw = (R - L) / steps.length
const jmax = Math.max(...steps.map(s => s.J))
const h = (v: number) => v / jmax * (B - T)
const { isPrintMode } = useNav()
const grown = ref(isPrintMode.value)
onMounted(() => { if (!grown.value) setTimeout(() => (grown.value = true), 250) })
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Objective after each step: ${steps.map(s => s.J).join(', ')}; it never increases`">
    <line :x1="L" :x2="R" :y1="B" :y2="B" :style="{ stroke: '#475569' }" />
    <g v-for="(s, n) in steps" :key="s.i">
      <rect
        :x="L + n * bw + 6" :width="bw - 12" :y="B - (grown ? h(s.J) : 0)" :height="grown ? h(s.J) : 0" rx="3" class="bar"
        :style="{ fill: s.phase === 'assign' ? '#60a5fa' : '#2dd4bf', fillOpacity: 0.85, transitionDelay: `${n * 120}ms` }"
      />
      <text :x="L + n * bw + bw / 2" :y="B - (grown ? h(s.J) : 0) - 6" text-anchor="middle" class="bar" :style="{ fill: '#e2e8f0', fontSize: '11px', fontWeight: 600, transitionDelay: `${n * 120}ms` }">{{ Math.round(s.J) }}</text>
      <text :x="L + n * bw + bw / 2" :y="B + 16" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">{{ s.phase === 'assign' ? 'A' : 'U' }}</text>
    </g>
    <text :x="L" :y="B + 38" :style="{ fill: '#94a3b8', fontSize: '11px' }">A = after assign · U = after update · the last A changes nothing: converged</text>
  </svg>
</template>

<style scoped>
.bar { transition: y 0.7s cubic-bezier(.2, .9, .3, 1), height 0.7s cubic-bezier(.2, .9, .3, 1); }
</style>
