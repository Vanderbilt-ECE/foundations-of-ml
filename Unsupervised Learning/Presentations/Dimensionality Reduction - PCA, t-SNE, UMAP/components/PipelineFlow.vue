<script setup lang="ts">
// The practical pipeline as a flow diagram, with data packets moving along it: raw features -> PCA to 95% ->
// either a 2D map for looking (t-SNE / UMAP) or clustering on the PCA scores (k-means / GMM).
// Bottom: how well 10-cluster k-means (or a GMM) recovers the true digits on each representation
// (adjusted Rand index, data/digits.json). Hover a bar for the representation's name.
import { ref } from 'vue'
import d from '../data/digits.json'
import { useActive } from '../utils/plot'

const W = 760; const H = 190
const boxes = [
  { x: 10, y: 70, w: 130, label: 'digits', sub: '1797 × 64', c: '#94a3b8' },
  { x: 200, y: 70, w: 150, label: 'PCA (95%)', sub: `1797 × ${d.ari.k95}`, c: '#fbbf24' },
  { x: 430, y: 14, w: 150, label: 't-SNE / UMAP', sub: '2D: for looking', c: '#a78bfa' },
  { x: 430, y: 126, w: 150, label: 'k-means / GMM', sub: 'on the PCA scores', c: '#2dd4bf' },
  { x: 630, y: 70, w: 120, label: 'check', sub: 'color the map', c: '#60a5fa' },
]
const paths = ['M140,95 L200,95', 'M350,95 C390,95 390,39 430,39', 'M350,95 C390,95 390,151 430,151', 'M580,39 C605,39 605,95 630,95', 'M580,151 C605,151 605,95 630,95']
const BARS = [
  ['k-means · raw 64-D', d.ari.raw, '#94a3b8'],
  ['k-means · PCA 2', d.ari.pca2, '#fbbf24'],
  [`k-means · PCA ${d.ari.k95}`, d.ari.pca95, '#fbbf24'],
  [`GMM · PCA ${d.ari.k95}`, d.ari.gmm_pca95, '#2dd4bf'],
  ['k-means · UMAP 2D', d.ari.umap, '#a78bfa'],
  ['k-means · t-SNE 2D', d.ari.tsne, '#a78bfa'],
] as const
const hot = ref<number | null>(null)
const { isPrintMode } = useActive()
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 190px" role="img" aria-label="Pipeline: digits to PCA, then to a 2D map for viewing or to clustering, then checking">
      <path v-for="(p, i) in paths" :id="`pf${i}`" :key="i" :d="p" :style="{ fill: 'none', stroke: '#475569', strokeWidth: 2 }" />
      <circle v-for="(p, i) in paths" :key="`dot${i}`" r="4.5" :style="{ fill: i === 0 ? '#e2e8f0' : i % 2 ? '#a78bfa' : '#2dd4bf' }">
        <animateMotion :dur="`${1.6 + 0.2 * i}s`" repeatCount="indefinite" :begin="`-${0.3 * i}s`"><mpath :href="`#pf${i}`" /></animateMotion>
      </circle>
      <g v-for="b in boxes" :key="b.label">
        <rect :x="b.x" :y="b.y" :width="b.w" height="50" rx="8" :style="{ fill: `${b.c}22`, stroke: b.c, strokeWidth: 2 }" />
        <text :x="b.x + b.w / 2" :y="b.y + 22" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '15px', fontWeight: 700 }">{{ b.label }}</text>
        <text :x="b.x + b.w / 2" :y="b.y + 40" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ b.sub }}</text>
      </g>
    </svg>
    <div class="grid grid-cols-6 gap-2 mt-3 items-end" style="height: 120px">
      <div v-for="([name, v, c], i) in BARS" :key="name" class="flex flex-col items-center justify-end h-full" @pointerenter="hot = i" @pointerleave="hot = null">
        <div class="font-mono text-sm mb-1" :style="{ color: c }">{{ v.toFixed(2) }}</div>
        <div class="w-12 rounded-t bar" :class="{ grow: !isPrintMode }" :style="{ height: `${80 * v}px`, background: c, opacity: hot == null || hot === i ? 0.9 : 0.35 }" />
        <div class="text-xs mt-1 text-center leading-tight opacity-80" style="min-height: 2.2em">{{ name }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bar { transition: opacity 0.2s; transform-origin: bottom; }
.grow { animation: grow 0.9s ease both; }
@keyframes grow { from { transform: scaleY(0); } to { transform: none; } }
</style>
