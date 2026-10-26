<script setup lang="ts">
// Title animation (data/digits.json): all 1797 digits, 64 numbers each, morphing between three 2D maps:
// PCA -> t-SNE -> UMAP, on a loop while the slide is showing. Click a method to jump to it.
// The PDF export shows the UMAP map.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import d from '../data/digits.json'
import { useActive } from '../utils/plot'

const METHODS = [['pca', 'PCA'], ['tsne', 't-SNE'], ['umap', 'UMAP']] as const
const { active, isPrintMode } = useActive()
const m = ref(isPrintMode.value ? 2 : 0)
let timer: ReturnType<typeof setInterval> | undefined
const run = () => {
  clearInterval(timer)
  timer = setInterval(() => (m.value = (m.value + 1) % 3), 3600)
}
watch(active, v => (v ? (m.value = 0, setTimeout(run, 400)) : clearInterval(timer)), { immediate: true })
onBeforeUnmount(() => clearInterval(timer))
const pts = computed(() => d.emb[METHODS[m.value][0]])
function pick(i: number) {
  m.value = i
  run()
}
</script>

<template>
  <div class="flex items-center justify-center gap-6">
    <EmbedPlot :pts="pts" :lab="d.y" :w="640" :h="270" :r="1.9" :ms="1500" labels label="1797 handwritten digits, each a point, morphing between PCA, t-SNE and UMAP maps" />
    <div class="flex flex-col gap-2 text-left">
      <button
        v-for="([, name], i) in METHODS" :key="name" class="px-3 py-1 rounded-md text-sm font-mono transition-all duration-500"
        :style="{ background: m === i ? 'rgba(45,212,191,0.18)' : 'rgba(255,255,255,0.04)', border: `2px solid ${m === i ? '#2dd4bf' : 'rgba(255,255,255,0.08)'}`, opacity: m === i ? 1 : 0.55 }"
        @click="pick(i)"
      >
        {{ name }}
      </button>
      <div class="text-xs opacity-60 mt-1 w-24">64 pixels per digit → 2 coordinates</div>
    </div>
  </div>
</template>
