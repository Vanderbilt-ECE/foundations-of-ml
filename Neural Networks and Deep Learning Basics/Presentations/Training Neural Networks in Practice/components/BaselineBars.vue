<script setup lang="ts">
// Test RMSE on California Housing (measured, data/demo.json): two baselines and the MLP, as dollar errors.
import demo from '../data/demo.json'
import { C } from '../utils/plot'

withDefaults(defineProps<{ width?: number }>(), { width: 420 })
const ROWS = [
  { name: 'always predict the average', v: demo.test.mean, color: C.muted },
  { name: 'linear regression', v: demo.test.linear, color: C.blue },
  { name: 'MLP + early stopping', v: demo.test.mlp, color: C.teal },
]
const H = 150; const L = 8; const MAXV = 1.25
</script>

<template>
  <svg :viewBox="`0 0 ${width} ${H}`" class="w-full" role="img" aria-label="Test error: average baseline about 116 thousand dollars, linear regression about 73 thousand, MLP about 53 thousand">
    <g v-for="(r, i) in ROWS" :key="r.name">
      <text :x="L" :y="18 + i * 46" style="font-size: 13px" :style="{ fill: C.text }">{{ r.name }}</text>
      <rect :x="L" :y="24 + i * 46" :width="(width - 110) * r.v / MAXV" height="16" rx="3" :style="{ fill: r.color, fillOpacity: 0.85 }" />
      <text :x="L + (width - 110) * r.v / MAXV + 8" :y="37 + i * 46" style="font-size: 14px; font-weight: 700" :style="{ fill: r.color }">${{ Math.round(r.v * 100) }}k</text>
    </g>
  </svg>
</template>
