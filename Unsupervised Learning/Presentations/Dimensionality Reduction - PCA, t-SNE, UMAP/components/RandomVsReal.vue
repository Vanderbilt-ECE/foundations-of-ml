<script setup lang="ts">
// Twelve real digits next to twelve random points of the same 64-dimensional cube (each pixel uniform on 0-16).
// "Draw again" resamples both sets. Random vectors essentially never look like digits:
// the digits occupy a thin, structured sliver of the space.
import { ref } from 'vue'
import d from '../data/digits.json'
import { rng, useActive } from '../utils/plot'

const { isPrintMode } = useActive()
const seed = ref(11)
const real = ref<string[]>([]); const noise = ref<number[][]>([])
function draw() {
  const R = rng(seed.value++)
  real.value = Array.from({ length: 12 }, () => d.img[Math.floor(R.u() * d.img.length)])
  noise.value = Array.from({ length: 12 }, () => Array.from({ length: 64 }, () => Math.floor(R.u() * 17)))
}
draw()
</script>

<template>
  <div class="flex items-center justify-center gap-8">
    <div>
      <div class="text-sm font-bold text-teal-300 mb-2">12 real digits</div>
      <div class="grid grid-cols-4 gap-2"><DigitImg v-for="(s, i) in real" :key="`r${i}${s}`" :v="s" :size="54" :class="{ pop: !isPrintMode }" /></div>
    </div>
    <button class="px-3 py-2 rounded-md text-sm border-2 border-white/10 bg-white/5 hover:bg-white/10" @click="draw">
      ↻ Draw again
    </button>
    <div>
      <div class="text-sm font-bold text-red-300 mb-2">12 random points of ℝ⁶⁴</div>
      <div class="grid grid-cols-4 gap-2"><DigitImg v-for="(s, i) in noise" :key="`n${i}${seed}`" :v="s" :size="54" :class="{ pop: !isPrintMode }" /></div>
    </div>
  </div>
</template>

<style scoped>
.pop { animation: pop 0.45s ease both; }
@keyframes pop { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: none; } }
</style>
