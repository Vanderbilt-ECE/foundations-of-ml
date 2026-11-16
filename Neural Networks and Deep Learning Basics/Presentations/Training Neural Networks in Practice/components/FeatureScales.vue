<script setup lang="ts">
// The 8 California Housing features (training rows): middle 90% as a thick bar, min–max as a thin line.
//   step 0: raw values on a signed-log axis (longitude is negative, population reaches 35,682)
//   step 1: after standardizing, on a linear axis; the bars morph into place.
//           Whiskers past the right edge are clipped and labelled (outliers stay outliers).
import { computed } from 'vue'
import F from '../data/features.json'
import { C, useTween } from '../utils/plot'

const props = defineProps<{ step: number }>()
const W = 880; const ROW = 27; const TOP = 26; const H = TOP + F.names.length * ROW + 30
const L = 150; const R = 150
const symlog = (v: number) => Math.sign(v) * Math.log10(1 + Math.abs(v))
const RAW = { lo: symlog(-200), hi: symlog(1e5) }
const Z = { lo: -3, hi: 6 }
const px = (u: number, lo: number, hi: number) => L + (u - lo) / (hi - lo) * (W - L - R)
const rawX = (v: number) => px(symlog(v), RAW.lo, RAW.hi)
const zX = (v: number) => px(Math.min(Math.max(v, Z.lo), Z.hi), Z.lo, Z.hi)

const rawPos = F.raw.map(r => [rawX(r.min), rawX(r.q05), rawX(r.q95), rawX(r.max)])
const zPos = F.z.map(r => [zX(r.min), zX(r.q05), zX(r.q95), zX(r.max)])
const pos = useTween(() => (props.step >= 1 ? zPos : rawPos), 1000)

const rawTicks = [-100, -10, 0, 10, 100, 1000, 10000, 100000].map(v => ({ x: rawX(v), t: v >= 1000 ? `${v / 1000}k` : String(v) }))
const zTicks = [-2, 0, 2, 4, 6].map(v => ({ x: zX(v), t: String(v) }))
const showZ = computed(() => props.step >= 1)
const fmtN = (v: number) => (Math.abs(v) >= 1000 ? v.toLocaleString('en-US', { maximumFractionDigits: 0 }) : String(Number(v.toFixed(1))))
const COLORS = [C.teal, C.blue, C.violet, C.violet, C.amber, C.orange, C.blue, C.blue]
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="California Housing feature ranges, raw (from about −124 to 35,682) and after standardizing (mostly between −2 and 2, with outliers up to 80 standard deviations)">
    <text :x="L" y="14" style="font-size: 13px" :style="{ fill: C.muted }">{{ showZ ? 'standardized: z = (x − μ) / σ, linear axis' : 'raw values, log axis (both signs)' }}</text>
    <!-- axis ticks -->
    <g :style="{ opacity: showZ ? 0 : 1, transition: 'opacity .5s' }">
      <g v-for="t in rawTicks" :key="`r${t.t}`">
        <line :x1="t.x" :x2="t.x" :y1="TOP - 4" :y2="H - 26" :style="{ stroke: C.grid, strokeOpacity: 0.7 }" />
        <text :x="t.x" :y="H - 10" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.muted }">{{ t.t }}</text>
      </g>
    </g>
    <g :style="{ opacity: showZ ? 1 : 0, transition: 'opacity .5s' }">
      <g v-for="t in zTicks" :key="`z${t.t}`">
        <line :x1="t.x" :x2="t.x" :y1="TOP - 4" :y2="H - 26" :style="{ stroke: t.t === '0' ? C.dim : C.grid, strokeOpacity: 0.7 }" />
        <text :x="t.x" :y="H - 10" text-anchor="middle" style="font-size: 12px" :style="{ fill: C.muted }">{{ t.t }}</text>
      </g>
      <text :x="W - R + 22" :y="H - 10" style="font-size: 12px" :style="{ fill: C.muted }">std devs</text>
    </g>

    <g v-for="(name, i) in F.names" :key="name">
      <text :x="L - 10" :y="TOP + i * ROW + 16" text-anchor="end" style="font-size: 14px" :style="{ fill: C.text }">{{ name }}</text>
      <line :x1="pos[i][0]" :x2="pos[i][3]" :y1="TOP + i * ROW + 11" :y2="TOP + i * ROW + 11" :style="{ stroke: COLORS[i], strokeWidth: 1.5, strokeOpacity: 0.8 }" />
      <rect :x="pos[i][1]" :y="TOP + i * ROW + 4" :width="Math.max(3, pos[i][2] - pos[i][1])" height="14" rx="3" :style="{ fill: COLORS[i], fillOpacity: 0.75 }" />
      <text :x="W - R + 10" :y="TOP + i * ROW + 16" style="font-size: 12.5px" :style="{ fill: F.z[i].max > Z.hi && showZ ? C.red : C.muted }">
        {{ showZ ? `${fmtN(F.z[i].min)} … ${fmtN(F.z[i].max)}` : `${fmtN(F.raw[i].min)} … ${fmtN(F.raw[i].max)}` }}{{ showZ && F.z[i].max > Z.hi ? ' ▸' : '' }}
      </text>
    </g>
  </svg>
</template>
