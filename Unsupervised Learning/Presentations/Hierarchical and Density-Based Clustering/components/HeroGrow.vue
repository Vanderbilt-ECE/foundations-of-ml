<script setup lang="ts">
// Title animation (data/hero.json): DBSCAN grows every cluster outward from its first core point,
// one breadth-first "wave" at a time. Points it never reaches stay gray: noise.
// Replays each time the slide becomes active; the PDF export shows the finished state.
import { useNav, useSlideContext } from '@slidev/client'
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import d from '../data/hero.json'
import { color, domainOf, equalScale } from '../utils/clusters'

const { $page } = useSlideContext()
const { currentSlideNo, isPrintMode } = useNav()
const active = computed(() => currentSlideNo.value === $page.value)
const W = 760; const H = 250
const S = equalScale(domainOf(d.pts, 0.03), W, H)
const last = Math.max(...d.wave) + 1
const w = ref(isPrintMode.value ? last : -1)
let timer: ReturnType<typeof setInterval> | undefined

function play() {
  clearInterval(timer)
  if (isPrintMode.value) return
  w.value = -1
  timer = setInterval(() => {
    w.value += 1
    if (w.value >= last) clearInterval(timer)
  }, 85)
}
watch(active, v => (v ? setTimeout(play, 350) : clearInterval(timer)), { immediate: true })
onBeforeUnmount(() => clearInterval(timer))

const reached = (i: number) => d.lab[i] >= 0 && d.wave[i] <= w.value
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Two moons, two rings and scattered noise; clusters spread outward point by point, and isolated points stay gray">
    <circle
      v-for="(p, i) in d.pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" class="pt"
      :r="reached(i) ? 3.3 : 2.3"
      :style="{
        fill: reached(i) ? color(d.lab[i]) : (w >= last && d.lab[i] < 0 ? '#94a3b8' : '#334155'),
        fillOpacity: reached(i) ? 0.95 : 0.8,
        stroke: w >= last && d.lab[i] < 0 ? '#e2e8f0' : 'none',
        strokeWidth: 1,
      }"
    />
  </svg>
</template>

<style scoped>
.pt { transition: fill 0.35s ease, r 0.35s ease, stroke 0.6s ease; }
</style>
