<script setup lang="ts">
// The right order (left) and the wrong order (right) for splitting and scaling.
//   step 0: rows split into train / validation / test
//   step 1: the scaler is fit on train only, then transforms all three
//   step ≥ 2: the wrong order appears on the right: fit on all rows, test statistics leak in
import { C } from '../utils/plot'

defineProps<{ step: number }>()
const W = 900; const H = 345
const BAR = { y: 46, h: 38 }
const SEG = [
  { x0: 20, x1: 332, name: 'train · 60%', color: C.blue },
  { x0: 332, x1: 436, name: 'val · 20%', color: C.amber },
  { x0: 436, x1: 540, name: 'test · 20%', color: C.violet },
]
const BOX = { x: 106, y: 140, w: 140, h: 44 }
const OUT_Y = 262
const head = (x: number, y: number, dir: 'down' | 'right' = 'down') =>
  dir === 'down' ? `M${x - 6},${y - 10} L${x},${y} L${x + 6},${y - 10} Z` : `M${x - 10},${y - 6} L${x},${y} L${x - 10},${y + 6} Z`
const fade = (on: boolean, delay = 0) => ({ opacity: on ? 1 : 0, transition: `opacity .5s ${delay}s` })
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Split the rows into train, validation and test first, fit the scaler on the training rows only, then transform all three. The wrong order fits on all rows and leaks test information.">
    <!-- the right order -->
    <text x="20" y="30" style="font-size: 15px; font-weight: 700" :style="{ fill: C.teal }">✓ Right order</text>
    <g v-for="s in SEG" :key="s.name">
      <rect :x="s.x0 + 1" :y="BAR.y" :width="s.x1 - s.x0 - 2" :height="BAR.h" rx="6" :style="{ fill: s.color, fillOpacity: 0.25, stroke: s.color, strokeWidth: 2 }" />
      <text :x="(s.x0 + s.x1) / 2" :y="BAR.y + 24" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.text }">{{ s.name }}</text>
    </g>
    <text x="548" :y="BAR.y + 24" style="font-size: 13px" :style="{ fill: C.muted }">1 · split</text>

    <g :style="fade(step >= 1)">
      <!-- fit: train only -->
      <line :x1="176" :y1="BAR.y + BAR.h + 2" :x2="176" :y2="BOX.y - 2" :style="{ stroke: C.blue, strokeWidth: 2.5 }" />
      <path :d="head(176, BOX.y - 1)" :style="{ fill: C.blue }" />
      <text x="186" :y="BOX.y - 26" style="font-size: 13px" :style="{ fill: C.blue }">fit: μ and σ of the training rows</text>
      <rect :x="BOX.x" :y="BOX.y" :width="BOX.w" :height="BOX.h" rx="8" :style="{ fill: 'rgba(45,212,191,0.18)', stroke: C.teal, strokeWidth: 2 }" />
      <text :x="BOX.x + BOX.w / 2" :y="BOX.y + 27" text-anchor="middle" style="font-size: 14px; font-weight: 700" :style="{ fill: C.teal }">StandardScaler</text>
      <!-- transform: all three -->
      <g v-for="s in SEG" :key="`o${s.name}`">
        <path :d="`M176,${BOX.y + BOX.h} C176,${BOX.y + BOX.h + 40} ${(s.x0 + s.x1) / 2},${OUT_Y - 40} ${(s.x0 + s.x1) / 2},${OUT_Y - 3}`" :style="{ fill: 'none', stroke: C.teal, strokeWidth: 2 }" />
        <path :d="head((s.x0 + s.x1) / 2, OUT_Y - 1)" :style="{ fill: C.teal }" />
        <rect :x="s.x0 + 1" :y="OUT_Y" :width="s.x1 - s.x0 - 2" :height="BAR.h" rx="6" :style="{ fill: s.color, fillOpacity: 0.45, stroke: s.color, strokeWidth: 2 }" />
        <text :x="(s.x0 + s.x1) / 2" :y="OUT_Y + 24" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.text }">scaled</text>
      </g>
      <text x="300" :y="BOX.y + 28" style="font-size: 13px" :style="{ fill: C.teal }">transform all three with the same μ, σ</text>
      <text x="548" :y="OUT_Y + 24" style="font-size: 13px" :style="{ fill: C.muted }">2 · fit, 3 · transform</text>
    </g>

    <!-- the wrong order -->
    <g :style="fade(step >= 2)">
      <line x1="690" x2="690" y1="10" :y2="H - 10" :style="{ stroke: C.grid, strokeDasharray: '4 6' }" />
      <text x="712" y="30" style="font-size: 15px; font-weight: 700" :style="{ fill: C.red }">✗ Wrong order</text>
      <rect x="712" :y="BAR.y" width="176" :height="BAR.h" rx="6" :style="{ fill: C.dim, fillOpacity: 0.3, stroke: C.muted, strokeWidth: 2 }" />
      <text x="800" :y="BAR.y + 24" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.text }">all rows</text>
      <line x1="800" :y1="BAR.y + BAR.h + 2" x2="800" :y2="BOX.y - 2" :style="{ stroke: C.red, strokeWidth: 2.5 }" />
      <path :d="head(800, BOX.y - 1)" :style="{ fill: C.red }" />
      <rect x="730" :y="BOX.y" width="140" :height="BOX.h" rx="8" :style="{ fill: 'rgba(248,113,113,0.15)', stroke: C.red, strokeWidth: 2 }" />
      <text x="800" :y="BOX.y + 27" text-anchor="middle" style="font-size: 14px; font-weight: 700" :style="{ fill: C.red }">fit on everything</text>
      <line x1="800" :y1="BOX.y + BOX.h" x2="800" :y2="OUT_Y - 3" :style="{ stroke: C.red, strokeWidth: 2 }" />
      <path :d="head(800, OUT_Y - 1)" :style="{ fill: C.red }" />
      <rect x="712" :y="OUT_Y" width="104" :height="BAR.h" rx="6" :style="{ fill: C.blue, fillOpacity: 0.3, stroke: C.blue, strokeWidth: 2 }" />
      <rect x="818" :y="OUT_Y" width="70" :height="BAR.h" rx="6" :style="{ fill: C.red, fillOpacity: 0.3, stroke: C.red, strokeWidth: 2.5 }" />
      <text x="853" :y="OUT_Y + 24" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.text }">test</text>
      <text x="800" :y="OUT_Y + BAR.h + 22" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.red }">test rows shaped the scaling:</text>
      <text x="800" :y="OUT_Y + BAR.h + 40" text-anchor="middle" style="font-size: 13px; font-weight: 700" :style="{ fill: C.red }">leakage</text>
    </g>
  </svg>
</template>
