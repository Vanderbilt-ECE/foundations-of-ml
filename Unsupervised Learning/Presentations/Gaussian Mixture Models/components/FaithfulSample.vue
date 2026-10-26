<script setup lang="ts">
// A GMM is generative: gmm.sample(272) draws brand-new eruptions from the fitted Old Faithful model
// (data/faithful.json, synth). Left: the real data. Right: the samples appearing a few at a time, colored by the
// component that generated each. Restarts when the slide is shown; the PDF export shows all of them.
import { computed, ref } from 'vue'
import f from '../data/faithful.json'
import { useLoop } from '../utils/gmm'

const n = ref(f.synth.length)
useLoop((_, t) => { n.value = Math.min(f.synth.length, Math.floor(t * 40)) }, () => { n.value = 0 })
const dom = { x: [1.3, 5.4] as [number, number], y: [40, 100] as [number, number] }
const pts = computed(() => f.synth.slice(0, n.value))
const lab = computed(() => f.synthZ.slice(0, n.value))
</script>

<template>
  <div class="grid grid-cols-2 gap-5">
    <div>
      <div class="text-sm font-bold text-center mb-1">Real: 272 eruptions</div>
      <GmmPlot :pts="f.pts" mode="gray" :domain="dom" :equal="false" :w="380" :h="270" :r="2.8" frame label="The real Old Faithful eruptions" />
    </div>
    <div>
      <div class="text-sm font-bold text-center mb-1 text-teal-300">Sampled from the GMM: {{ n }}</div>
      <GmmPlot :pts="pts" mode="lab" :lab="lab" :mix="f.gmm" :levels="[2]" :means="false" :domain="dom" :equal="false" :w="380" :h="270" :r="2.8" frame label="New eruptions sampled from the fitted mixture" />
    </div>
  </div>
</template>
