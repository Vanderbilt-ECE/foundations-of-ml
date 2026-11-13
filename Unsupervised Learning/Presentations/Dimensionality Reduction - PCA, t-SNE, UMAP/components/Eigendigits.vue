<script setup lang="ts">
// The first 10 principal components of digits (data/digits.json), each drawn as an 8x8 image
// (teal = positive weight, violet = negative), with the share of variance it explains.
// The PDF export skips the entrance animation.
import d from '../data/digits.json'
import { useActive } from '../utils/plot'

const J = 10
const { isPrintMode } = useActive()
</script>

<template>
  <div>
    <div class="grid grid-cols-5 gap-x-6 gap-y-5 w-max mx-auto mt-2">
      <div v-for="i in J" :key="i" class="text-center" :class="{ eig: !isPrintMode }" :style="{ animationDelay: `${i * 90}ms` }">
        <DigitImg :v="d.V[i - 1]" :size="132" div class="mx-auto" />
        <div class="text-sm font-mono mt-1.5">PC{{ i }} · {{ (100 * d.evr[i - 1]).toFixed(1) }}%</div>
      </div>
    </div>
    <div class="text-xs opacity-70 text-center mt-4">
      Each component is a weight per pixel: <span class="text-teal-300">teal = positive</span>, <span class="text-violet-300">violet = negative</span>
    </div>
  </div>
</template>

<style scoped>
.eig { animation: rise 0.6s ease both; }
@keyframes rise { from { opacity: 0; transform: translateY(12px) scale(0.9); } to { opacity: 1; transform: none; } }
</style>
