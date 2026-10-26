<script setup lang="ts">
// One of three t-SNE pitfalls (data/pitfalls.json), morphing from the original data to its t-SNE map:
//   size  — a tight and a 10x more diffuse cluster come out the same size
//   gap   — clusters at gaps 10 and 50 come out roughly evenly spaced
//   noise — 300 points of pure 30-D Gaussian noise (shown: first two coordinates) break into small clumps at perplexity 3
import { computed } from 'vue'
import d from '../data/pitfalls.json'

const props = withDefaults(defineProps<{ which: 'size' | 'gap' | 'noise', emb?: boolean }>(), { emb: false })
const set = computed(() => d[props.which])
const pts = computed(() => (props.emb ? set.value.emb : set.value.raw))
</script>

<template>
  <EmbedPlot :pts="pts" :lab="set.lab" :w="270" :h="200" :r="2.3" :ms="1400" :label="`t-SNE pitfall: ${which}`" />
</template>
