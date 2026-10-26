<script setup lang="ts">
// Title animation (data/em.json): EM fitting three Gaussians, on a loop. Points start gray, take the blended
// colors of their responsibilities (E-step), then the ellipses move to fit them (M-step), and so on.
// Replays each time the slide becomes active; the PDF export shows the finished fit.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import d from '../data/em.json'
import { useActive } from '../utils/gmm'

const LAST = 12 // iterations shown; the fit has converged by then
const { active, isPrintMode } = useActive()
const s = ref(isPrintMode.value ? 2 * LAST + 1 : 0)
let timer: ReturnType<typeof setInterval> | undefined

function play() {
  clearInterval(timer)
  s.value = 0
  timer = setInterval(() => {
    s.value = s.value >= 2 * LAST + 6 ? 0 : s.value + 1 // hold the converged fit for a few beats, then restart
  }, 520)
}
watch(active, v => (v ? setTimeout(play, 300) : clearInterval(timer)), { immediate: true })
onBeforeUnmount(() => clearInterval(timer))

const step = computed(() => Math.min(s.value, 2 * LAST + 1))
const mix = computed(() => d.frames[Math.floor(step.value / 2)])
const colorMix = computed(() => (step.value === 0 ? null : d.frames[Math.floor((step.value - 1) / 2)]))
</script>

<template>
  <GmmPlot
    :pts="d.pts" :mix="mix" :color-mix="colorMix" :mode="step === 0 ? 'gray' : 'soft'" :levels="[1, 2]"
    :w="760" :h="280" :r="2.6" :ms="480" label="EM fitting three Gaussian ellipses to unlabeled points"
  />
</template>
