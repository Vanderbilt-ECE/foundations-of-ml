<script setup lang="ts">
// t-SNE maps of all 1797 digits (data/perplexity.json) at six perplexities, and at perplexity 30 from three
// other random starts. Each map was rotated/reflected onto the perplexity-30 map (Procrustes), so switching
// morphs points instead of spinning the picture. Hover a point to see the digit.
import { computed, ref } from 'vue'
import dg from '../data/digits.json'
import d from '../data/perplexity.json'

const key = ref<string>('30')
const pts = computed(() => (key.value.startsWith('s') ? d.seeds[+key.value.slice(1)] : d.emb[key.value as keyof typeof d.emb]))
const btn = (on: boolean) => ({ border: `2px solid ${on ? '#2dd4bf' : 'rgba(255,255,255,0.08)'}`, background: on ? 'rgba(45,212,191,0.15)' : 'rgba(255,255,255,0.03)' })
</script>

<template>
  <div class="grid grid-cols-[auto_1fr] gap-6 items-center">
    <EmbedPlot :pts="pts" :lab="dg.y" :imgs="dg.img" :w="460" :h="340" :r="1.9" :ms="1400" hover labels label="t-SNE map of the digits, for the chosen perplexity" />
    <div class="text-left space-y-4">
      <div>
        <div class="text-xs uppercase tracking-wide opacity-60 mb-1">perplexity</div>
        <div class="flex flex-wrap gap-1.5">
          <button v-for="p in d.perps" :key="p" class="px-2 py-1 rounded font-mono text-sm transition-all" :style="btn(key === String(p))" @click="key = String(p)">{{ p }}</button>
        </div>
      </div>
      <div>
        <div class="text-xs uppercase tracking-wide opacity-60 mb-1">perplexity 30, other random seeds</div>
        <div class="flex gap-1.5">
          <button v-for="(_, i) in d.seeds" :key="i" class="px-2 py-1 rounded font-mono text-sm transition-all" :style="btn(key === `s${i}`)" @click="key = `s${i}`">seed {{ i + 1 }}</button>
        </div>
      </div>
      <div class="text-sm opacity-85 space-y-1">
        <div><b class="text-amber-300">Low</b>: many tiny fragments; only the closest neighbors count.</div>
        <div><b class="text-teal-300">High</b>: rounder, more global, clusters start to touch.</div>
        <div><b class="text-violet-300">Seeds</b>: same clusters, different arrangement.</div>
      </div>
    </div>
  </div>
</template>
