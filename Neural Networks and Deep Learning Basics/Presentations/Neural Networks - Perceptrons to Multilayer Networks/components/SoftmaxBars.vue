<script setup lang="ts">
// Softmax, one operation at a time, for a network looking at a handwritten "3".
// step 0: the 10 output scores z (logits) — any real numbers, some negative
// 1: exponentiate, eᶻ — all positive, and the largest scores pull far ahead
// 2: divide by the total — probabilities that sum to 1, shown also as one stacked bar
import { computed } from 'vue'
import { C, clamp, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const z = [-1.2, 0.3, 1.1, 4.0, -0.5, 2.2, -2.0, 0.6, 2.8, 0.1]
const e = z.map(Math.exp)
const sum = e.reduce((a, v) => a + v, 0)
const p = e.map(v => v / sum)
const eMax = Math.max(...e); const zMax = Math.max(...z.map(Math.abs))

const W = 640; const H = 260; const top = 52; const base = 210; const mid = 130
// each bar is [y_top, y_bottom] in SVG units
const target = computed(() => props.step === 0
  ? z.map(v => (v >= 0 ? [mid - v / zMax * (mid - top), mid] : [mid, mid - v / zMax * (mid - top) * 0.75]))
  : e.map(v => [base - v / eMax * (base - top), base]))
const bars = useTween(() => target.value, 1000)
const ph = useTween(() => props.step, 1000)
const bx = (k: number) => 50 + k * ((W - 70) / 10)
const bw = (W - 70) / 10 - 12
const label = (k: number) => (props.step === 0 ? z[k].toFixed(1) : props.step === 1 ? e[k].toFixed(1) : `${(100 * p[k]).toFixed(0)}%`)
const COLS = [C.dim, C.dim, C.dim, C.teal, C.dim, C.violet, C.dim, C.dim, C.amber, C.dim]
// stacked bar segments, largest first
const order = [...p.keys()].sort((a, b) => p[b] - p[a])
const segs = order.reduce((acc: { k: number, x: number, w: number }[], k) => {
  const x = acc.length ? acc.at(-1)!.x + acc.at(-1)!.w : 0
  acc.push({ k, x, w: p[k] }); return acc
}, [])
const stack = computed(() => clamp(ph.value - 1))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 270px" role="img" aria-label="Ten output scores turned into probabilities by softmax">
      <line :x1="40" :x2="W - 14" :y1="mid + (base - mid) * clamp(ph)" :y2="mid + (base - mid) * clamp(ph)" :style="{ stroke: C.grid }" />
      <g v-for="(b, k) in bars" :key="k">
        <rect :x="bx(k) + 6" :y="b[0]" :width="bw" :height="Math.max(1, b[1] - b[0])" rx="3" :style="{ fill: COLS[k], fillOpacity: COLS[k] === C.dim ? 0.6 : 0.9 }" />
        <text :x="bx(k) + 6 + bw / 2" :y="Math.min(b[0], b[1]) - 7" text-anchor="middle" :style="{ fill: C.text, fontSize: '12px', fontFamily: 'monospace' }">{{ label(k) }}</text>
        <text :x="bx(k) + 6 + bw / 2" :y="H - 28" text-anchor="middle" :style="{ fill: COLS[k] === C.dim ? C.muted : COLS[k], fontSize: '15px', fontWeight: 700 }">{{ k }}</text>
      </g>
      <text x="40" y="16" :style="{ fill: C.amber, fontSize: '15px' }" class="font-mono">{{ ['scores z (logits)', 'eᶻ: all positive', 'eᶻ / Σ eᶻ: probabilities'][step] ?? '' }}</text>
      <text :x="W - 14" y="16" text-anchor="end" :style="{ fill: C.muted, fontSize: '13px', opacity: clamp(ph - 1) }">Σ eᶻ = {{ sum.toFixed(1) }}</text>
    </svg>
    <!-- stacked 100% bar -->
    <svg :viewBox="`0 0 ${W} 40`" class="w-full" :style="{ opacity: stack }" role="img" aria-label="The probabilities stacked into one bar that adds up to 100 percent">
      <rect v-for="s in segs" :key="s.k" :x="40 + s.x * (W - 54) * stack" y="4" :width="Math.max(0, s.w * (W - 54) * stack - 1.5)" height="24" :style="{ fill: COLS[s.k], fillOpacity: COLS[s.k] === C.dim ? 0.6 : 0.9 }" />
      <text v-for="s in segs.slice(0, 3)" :key="`t${s.k}`" :x="40 + (s.x + s.w / 2) * (W - 54) * stack" y="21" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '12px', fontWeight: 700 }">“{{ s.k }}” {{ (100 * s.w).toFixed(0) }}%</text>
    </svg>
  </div>
</template>
