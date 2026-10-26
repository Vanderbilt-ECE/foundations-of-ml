<script setup lang="ts">
// The same 1797 digits through PCA, t-SNE and UMAP (data/digits.json), with linked hover: point at a digit in
// any map and it is ringed in all three, with its image. Below each: trustworthiness (k = 10) and fit time
// on a laptop (make_data.py's run).
import { ref } from 'vue'
import d from '../data/digits.json'

const hot = ref<number | null>(null)
const M = [['pca', 'PCA', `${d.time.pca < 1 ? '<1' : d.time.pca.toFixed(0)} ms`], ['tsne', 't-SNE', `${d.time.tsne.toFixed(1)} s`], ['umap', 'UMAP', `${d.time.umap.toFixed(1)} s`]] as const
</script>

<template>
  <div class="grid grid-cols-3 gap-3">
    <div v-for="[k, name, time] in M" :key="k" class="text-center">
      <div class="font-bold mb-1">{{ name }}</div>
      <EmbedPlot :pts="d.emb[k]" :lab="d.y" :imgs="d.img" :mark="hot" :w="270" :h="240" :r="1.6" hover labels :label="`Digits mapped by ${name}`" @hover="hot = $event" />
      <div class="text-sm font-mono mt-1">trust <span class="text-amber-300">{{ d.trust[k].toFixed(3) }}</span> · {{ time }}</div>
    </div>
  </div>
</template>
