<script setup lang="ts">
// The mean digit and the first 10 principal components of digits (data/digits.json), as 8x8 images
// (teal = positive weight, violet = negative). Hover a component: the big panel walks along it,
// showing mean + c · PC_j for c sweeping between -2 and +2 standard deviations. The PDF export shows c = +2
// and skips the entrance animation.
import { computed, ref } from 'vue'
import d from '../data/digits.json'
import { useActive, useLoop } from '../utils/plot'

const J = 10
const j = ref(0)
const { isPrintMode } = useActive()
const c = ref(isPrintMode.value ? 2 : 0)
useLoop((_, t) => { c.value = 2 * Math.sin(1.6 * t) })
const sd = computed(() => Math.sqrt(d.lam[j.value]))
const walk = computed(() => d.mean.map((m, i) => m + c.value * sd.value * d.V[j.value][i]))
</script>

<template>
  <div class="grid grid-cols-[1fr_auto] gap-8 items-center">
    <div>
      <div class="flex items-end gap-4 mb-3">
        <div class="text-center">
          <DigitImg :v="d.mean" :size="78" />
          <div class="text-xs mt-1 font-bold">mean μ</div>
        </div>
        <div class="text-xs opacity-60 pb-6">+ weights on…</div>
      </div>
      <div class="grid grid-cols-5 gap-3">
        <div
          v-for="i in J" :key="i" class="text-center cursor-pointer rounded-md p-1 transition-all" :class="{ eig: !isPrintMode }" :style="{ animationDelay: `${i * 90}ms`, background: j === i - 1 ? 'rgba(251,191,36,0.15)' : 'transparent', outline: j === i - 1 ? '2px solid #fbbf24' : 'none' }"
          @pointerenter="j = i - 1"
        >
          <DigitImg :v="d.V[i - 1]" :size="62" div class="mx-auto" />
          <div class="text-xs font-mono mt-1">PC{{ i }} · {{ (100 * d.evr[i - 1]).toFixed(1) }}%</div>
        </div>
      </div>
    </div>
    <div class="text-center">
      <DigitImg :v="walk" :size="190" :max="16" />
      <div class="font-mono text-sm mt-2">μ <span :class="c >= 0 ? 'text-teal-300' : 'text-violet-300'">{{ c >= 0 ? '+' : '−' }} {{ Math.abs(c).toFixed(1) }}σ</span> · <span class="text-amber-300">PC{{ j + 1 }}</span></div>
      <div class="text-xs opacity-60 mt-1">hover a component</div>
    </div>
  </div>
</template>

<style scoped>
.eig { animation: rise 0.6s ease both; }
@keyframes rise { from { opacity: 0; transform: translateY(12px) scale(0.9); } to { opacity: 1; transform: none; } }
</style>
