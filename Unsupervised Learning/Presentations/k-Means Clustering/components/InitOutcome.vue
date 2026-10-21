<script setup lang="ts">
// Outcome of 50 single runs (n_init=1) on blobs6: random init vs k-means++ (data/blobs6.json).
// Each bar is split into runs that found the best solution and runs that got stuck in a local minimum.
// `pp=false` hides the k-means++ bar.
import { computed } from 'vue'
import d from '../data/blobs6.json'

const props = withDefaults(defineProps<{ pp?: boolean }>(), { pp: true })
const mean = (a: number[]) => a.reduce((s, x) => s + x, 0) / a.length
const N = d.random.J.length
const rows = computed(() => [
  { name: 'Random init', stuck: d.stuckRandom, iters: mean(d.random.iter), show: true, color: '#f87171' },
  { name: 'k-means++', stuck: d.stuckPP, iters: mean(d.pp.iter), show: props.pp, color: '#2dd4bf' },
].map(r => ({ ...r, good: N - r.stuck })))
const W = 560; const BW = 520; const bh = 54
</script>

<template>
  <svg :viewBox="`0 0 ${W} 300`" class="w-full" role="img" :aria-label="`Of ${N} runs, random initialization got stuck ${d.stuckRandom} times and k-means++ ${d.stuckPP} times`">
    <g v-for="(r, i) in rows" :key="r.name" :transform="`translate(20,${i * 140 + 10})`" :style="{ opacity: r.show ? 1 : 0, transition: 'opacity .6s' }">
      <text y="16" :style="{ fill: r.color, fontSize: '18px', fontWeight: 700 }">{{ r.name }}</text>
      <text :x="BW" y="16" text-anchor="end" :style="{ fill: '#cbd5e1', fontSize: '13px' }">{{ r.iters.toFixed(1) }} iterations on average</text>
      <rect y="28" :width="BW" :height="bh" rx="6" :style="{ fill: 'rgba(255,255,255,0.04)' }" />
      <rect y="28" :width="BW * r.good / N" :height="bh" rx="6" :style="{ fill: '#2dd4bf', fillOpacity: 0.75 }" />
      <rect v-if="r.stuck" :x="BW * r.good / N" y="28" :width="BW * r.stuck / N" :height="bh" rx="6" :style="{ fill: '#f87171', fillOpacity: 0.75 }" />
      <text :x="BW * r.good / N / 2" y="62" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '15px', fontWeight: 700 }">{{ r.good }} found the best J</text>
      <text v-if="r.stuck" :x="BW * r.good / N + BW * r.stuck / N / 2" y="62" text-anchor="middle" :style="{ fill: '#0b1020', fontSize: '15px', fontWeight: 700 }">{{ r.stuck }} stuck</text>
      <text y="108" :style="{ fill: '#94a3b8', fontSize: '12px' }">{{ N }} single runs · "stuck" = ended in a local minimum with a higher J than the best ({{ Math.round(d.best).toLocaleString() }})</text>
    </g>
  </svg>
</template>
