<script setup lang="ts">
// All 1797 digits on one 2D map (data/digits.json), colored by their label. Hover a point to see the image;
// hover a digit in the legend to pick out that class. `by`: which map (pca, tsne or umap).
import { ref } from 'vue'
import d from '../data/digits.json'
import { color } from '../utils/plot'

withDefaults(defineProps<{ by?: 'pca' | 'tsne' | 'umap', w?: number, h?: number }>(), { by: 'pca', w: 470, h: 330 })
const focus = ref<number | null>(null)
</script>

<template>
  <div class="flex items-center gap-3">
    <EmbedPlot :pts="d.emb[by]" :lab="d.y" :imgs="d.img" :focus="focus" :w="w" :h="h" hover labels :label="`Digits mapped to 2D with ${by}`" />
    <div class="flex flex-col gap-1">
      <div
        v-for="c in 10" :key="c" class="w-7 h-6 rounded text-center text-sm font-bold cursor-pointer transition-all"
        :style="{ color: color(c - 1), background: focus === c - 1 ? 'rgba(255,255,255,0.12)' : 'transparent', border: `1.5px solid ${focus === c - 1 ? color(c - 1) : 'transparent'}` }"
        @pointerenter="focus = c - 1" @pointerleave="focus = null"
      >
        {{ c - 1 }}
      </div>
    </div>
  </div>
</template>
