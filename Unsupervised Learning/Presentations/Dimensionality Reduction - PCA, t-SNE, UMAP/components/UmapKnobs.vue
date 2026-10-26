<script setup lang="ts">
// UMAP's two main knobs on the digits (data/umapgrid.json, 900 of the 1797 digits shown): n_neighbors (how big a
// neighborhood each point trusts) x min_dist (how tightly points may pack in the map). All 16 maps were aligned
// to the default map, so switching morphs. Hover a point to see the digit.
import { computed, ref } from 'vue'
import dg from '../data/digits.json'
import d from '../data/umapgrid.json'

const nn = ref(15); const md = ref(0.1)
const pts = computed(() => d.emb[`${nn.value}_${md.value}` as keyof typeof d.emb])
const lab = d.idx.map(i => dg.y[i]); const imgs = d.idx.map(i => dg.img[i])
const btn = (on: boolean, c: string) => ({ border: `2px solid ${on ? c : 'rgba(255,255,255,0.08)'}`, background: on ? `${c}26` : 'rgba(255,255,255,0.03)' })
</script>

<template>
  <div class="grid grid-cols-[auto_1fr] gap-6 items-center">
    <EmbedPlot :pts="pts" :lab="lab" :imgs="imgs" :w="460" :h="340" :r="2.1" :ms="1300" hover labels label="UMAP map of digits for the chosen settings" />
    <div class="text-left space-y-4">
      <div>
        <div class="text-xs uppercase tracking-wide opacity-60 mb-1">n_neighbors <span class="normal-case">· local ↔ global</span></div>
        <div class="flex gap-1.5"><button v-for="v in d.nn" :key="v" class="px-2 py-1 rounded font-mono text-sm transition-all" :style="btn(nn === v, '#2dd4bf')" @click="nn = v">{{ v }}</button></div>
      </div>
      <div>
        <div class="text-xs uppercase tracking-wide opacity-60 mb-1">min_dist <span class="normal-case">· tight clumps ↔ even spread</span></div>
        <div class="flex gap-1.5"><button v-for="v in d.md" :key="v" class="px-2 py-1 rounded font-mono text-sm transition-all" :style="btn(md === v, '#fbbf24')" @click="md = v">{{ v }}</button></div>
      </div>
      <div class="text-sm opacity-85 font-mono">UMAP(n_neighbors={{ nn }}, min_dist={{ md }})</div>
    </div>
  </div>
</template>
