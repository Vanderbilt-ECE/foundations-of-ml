<script setup lang="ts">
// Soft vs hard membership on the running example, under the converged EM fit (last frame of data/em.json).
//   step 0: soft (colors blended by responsibility) · step 1: hard (predict = argmax)
//   step 2: soft again, ringing the points whose largest responsibility is below 0.9
import { computed } from 'vue'
import d from '../data/em.json'
import { resp } from '../utils/gmm'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const F = d.frames[d.frames.length - 1]
const unsure = d.pts.map((p, i) => (Math.max(...resp(p, F)) < 0.9 ? i : -1)).filter(i => i >= 0)
const mode = computed(() => (props.step === 1 ? 'hard' : 'soft'))
</script>

<template>
  <GmmPlot :pts="d.pts" :mix="F" :mode="mode" :focus="step >= 2 ? unsure : null" :levels="[1, 2]" :w="540" :h="380" :r="3.2" frame label="Points colored by responsibility; boundary points show blended colors" />
</template>
