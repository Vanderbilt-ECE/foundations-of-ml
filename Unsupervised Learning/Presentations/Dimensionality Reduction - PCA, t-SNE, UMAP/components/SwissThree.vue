<script setup lang="ts">
// The Swiss roll (data/swiss.json) through PCA, t-SNE and UMAP, colored by position along the roll.
// Under each: trustworthiness (k = 10), the share of each point's 10 map neighbors that were also near it
// in 3D (1 = perfect, roughly). Hover a point in any map to ring the same point in the other two.
import { ref } from 'vue'
import d from '../data/swiss.json'
import { ramp } from '../utils/plot'

const t0 = Math.min(...d.t); const t1 = Math.max(...d.t)
const cols = d.t.map(t => ramp((t - t0) / (t1 - t0)))
const lab = d.t.map(() => 0)
const hot = ref<number | null>(null)
const M = [['pca', 'PCA'], ['tsne', 't-SNE'], ['umap', 'UMAP']] as const
</script>

<template>
  <div class="grid grid-cols-3 gap-3">
    <div v-for="[k, name] in M" :key="k" class="text-center">
      <div class="font-bold mb-1">{{ name }}</div>
      <EmbedPlot :pts="d.emb[k]" :lab="lab" :cols="cols" :mark="hot" :w="270" :h="230" :r="2" hover :label="`Swiss roll mapped by ${name}`" @hover="hot = $event" />
      <div class="text-sm font-mono mt-1">trustworthiness <span class="text-amber-300">{{ d.trust[k].toFixed(3) }}</span></div>
    </div>
  </div>
</template>
