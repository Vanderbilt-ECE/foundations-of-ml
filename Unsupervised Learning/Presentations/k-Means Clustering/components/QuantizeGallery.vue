<script setup lang="ts">
// china.jpg redrawn with only K colors, the K k-means centroids in RGB space (data/pixels.json, data/img).
// Click count picks the version: original, then K = 2, 4, 8, 16, 32.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/pixels.json'

const imgs = import.meta.glob('../data/img/*.png', { eager: true, import: 'default' }) as Record<string, string>
const src = (name: string) => imgs[`../data/img/${name}.png`]
const seq = [0, 2, 4, 8, 16, 32]
const { $clicks } = useSlideContext()
const K = computed(() => seq[Math.min($clicks.value, seq.length - 1)])
const q = computed(() => (K.value ? (d.quant as any)[K.value] : null))
const rgb = (c: number[]) => `rgb(${c[0]},${c[1]},${c[2]})`
// palette swatches ordered by how many pixels use each color
const swatches = computed(() => {
  if (!q.value) return []
  const idx = q.value.counts.map((_: number, i: number) => i).sort((a: number, b: number) => q.value.counts[b] - q.value.counts[a])
  const tot = q.value.counts.reduce((s: number, x: number) => s + x, 0)
  return idx.map((i: number) => ({ c: rgb(q.value.palette[i]), share: q.value.counts[i] / tot }))
})
</script>

<template>
  <div class="grid grid-cols-[1fr_1fr] gap-6 items-center">
    <div class="relative rounded-lg overflow-hidden" style="aspect-ratio: 480 / 320">
      <img v-for="k in seq" :key="k" :src="src(k ? `china_k${k}` : 'china_orig')" class="layer" :class="{ on: k === K }" :alt="k ? `Photo redrawn with ${k} colors` : 'Original photo'">
    </div>
    <div class="space-y-3 text-left">
      <div class="text-4xl font-bold">{{ K ? `K = ${K}` : 'Original' }}</div>
      <div class="text-sm opacity-80">{{ K ? `${K} colors, each one a centroid in RGB space` : `${d.nPixels.toLocaleString()} pixels, up to 16.7 million possible colors` }}</div>
      <div v-if="K" class="flex h-7 rounded overflow-hidden" border="1 solid white/10">
        <div v-for="(s, i) in swatches" :key="i" class="sw" :style="{ background: s.c, flexGrow: s.share }" />
      </div>
      <div v-else class="h-7 text-xs opacity-60 flex items-center">palette: every color the camera recorded</div>
      <div class="grid grid-cols-2 gap-3">
        <div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
          <div class="text-xs opacity-60">bits per pixel</div>
          <div class="font-mono text-xl text-teal-300">{{ K ? Math.log2(K) : 24 }}</div>
        </div>
        <div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
          <div class="text-xs opacity-60">avg squared color error (×10⁻⁴)</div>
          <div class="font-mono text-xl text-amber-300">{{ q ? q.mse.toFixed(1) : '0' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.layer { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 0.6s ease; }
.layer.on { opacity: 1; }
.sw { transition: flex-grow 0.6s ease; }
</style>
