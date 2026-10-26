<script setup lang="ts">
// UMAP laying out the digits' graph (data/umapepochs.json): the embedding after 0 epochs (the spectral start)
// and after 5, 15, 40, 100, 200 epochs of stochastic gradient descent. Plays on a loop while the slide is
// showing; click an epoch to jump. PDF export: the final layout.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import dg from '../data/digits.json'
import d from '../data/umapepochs.json'
import { useActive } from '../utils/plot'

const { active, isPrintMode } = useActive()
const e = ref(isPrintMode.value ? d.epochs.length - 1 : 0)
let timer: ReturnType<typeof setInterval> | undefined
const run = () => {
  clearInterval(timer)
  timer = setInterval(() => (e.value = (e.value + 1) % d.epochs.length), 1900)
}
watch(active, v => (v ? (e.value = 0, run()) : clearInterval(timer)), { immediate: true })
onBeforeUnmount(() => clearInterval(timer))
const pts = computed(() => d.emb[e.value])
function pick(i: number) { e.value = i; run() }
</script>

<template>
  <div class="text-center">
    <EmbedPlot :pts="pts" :lab="dg.y" :imgs="dg.img" :w="480" :h="300" :r="1.9" :ms="1300" hover labels label="UMAP layout of the digits as optimization proceeds" />
    <div class="flex justify-center gap-1.5 mt-2">
      <button
        v-for="(ep, i) in d.epochs" :key="ep" class="px-2 py-0.5 rounded font-mono text-sm transition-all"
        :style="{ border: `2px solid ${e === i ? '#2dd4bf' : 'rgba(255,255,255,0.08)'}`, background: e === i ? 'rgba(45,212,191,0.15)' : 'rgba(255,255,255,0.03)' }"
        @click="pick(i)"
      >
        {{ i === 0 ? 'start' : `epoch ${ep}` }}
      </button>
    </div>
  </div>
</template>
