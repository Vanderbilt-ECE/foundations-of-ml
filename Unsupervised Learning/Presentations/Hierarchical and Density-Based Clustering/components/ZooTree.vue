<script setup lang="ts">
// All 101 UCI Zoo animals clustered on their 16 traits (data/zoo.json; average linkage, Manhattan distance,
// legs rescaled to 0-1). Sideways dendrogram: root on the left, leaves on the right, then a strip with each
// animal's true class (never shown to the algorithm). A vertical cut moves with clicks: Ks[i] clusters.
// Each cluster's branches take the color of its most common class, so matching colors = agreement.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/zoo.json'
import { color, linkPath, useTween } from '../utils/clusters'

const props = withDefaults(defineProps<{ Ks?: number[] }>(), { Ks: () => [2, 4, 7] })
const { $clicks } = useSlideContext()
const K = computed(() => props.Ks[Math.min($clicks.value, props.Ks.length - 1)])
const lab = computed(() => (d.labs as Record<string, number[]>)[K.value])
const groups = computed(() => (d.groups as Record<string, { n: number, major: string, purity: number, ex: string[] }[]>)[K.value])
const cut = computed(() => (d.cuts as Record<string, number>)[K.value])
const gcol = (c: number) => color(d.classes.indexOf(groups.value[c].major))
const n = d.names.length

const W = 400; const H = 405; const L = 12; const R = 368; const T = 18; const B = 399
const hmax = Math.max(...d.h) * 1.03
const at = (pos: number, h: number): [number, number] => [R - h / hmax * (R - L), T + (pos + 0.5) / n * (B - T)]
const cx = useTween(() => [at(0, cut.value)[0]], 650)
const links = Array.from({ length: n - 1 }, (_, i) => linkPath(d, i, at))
// groups listed top to bottom in the order they appear in the tree
const plural = (c: string) => (c === 'fish' ? 'fish' : `${c}s`)
const listed = computed(() => groups.value.map((g, c) => ({ ...g, c })))
</script>

<template>
  <div class="grid grid-cols-[1fr_1.15fr] gap-4 items-start">
    <div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="`Dendrogram of 101 animals cut into ${K} groups, next to a strip of their true classes`">
        <path
          v-for="(p, i) in links" :key="i" :d="p" class="lk"
          :style="{ stroke: d.h[n + i] < cut ? gcol(lab[d.rep[n + i]]) : '#94a3b8', strokeWidth: d.h[n + i] < cut ? 1.2 : 1.8, fill: 'none' }"
        />
        <rect v-for="(leaf, pos) in d.order" :key="leaf" :x="R + 8" :y="at(pos, 0)[1] - (B - T) / n / 2" width="14" :height="(B - T) / n + 0.3" :style="{ fill: color(d.type[leaf]) }" />
        <text :x="R + 15" :y="T - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">class</text>
        <line :x1="cx[0]" :x2="cx[0]" :y1="T" :y2="B" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '7 5' }" />
      </svg>
      <div class="flex flex-wrap gap-x-2 gap-y-0.5 text-xs mt-1 opacity-85" style="font-size: 0.68rem">
        <span v-for="(c, k) in d.classes" :key="c"><span class="inline-block w-2.5 h-2.5 rounded-sm mr-1" :style="{ background: color(k) }" />{{ c }}</span>
      </div>
    </div>
    <div class="text-left" style="min-height: 25.5rem">
      <div class="text-xs uppercase tracking-wider opacity-60 mb-2">Cut into K = {{ K }} · ARI vs. true class {{ (d.ari as Record<string, number>)[K].toFixed(2) }}</div>
      <TransitionGroup name="row" tag="div" class="space-y-1.5">
        <div v-for="g in listed" :key="`${K}-${g.c}`" class="rounded-md px-3 py-1" :style="{ background: 'rgba(255,255,255,0.05)', borderLeft: `4px solid ${gcol(g.c)}` }">
          <div class="text-sm"><b>{{ g.n }}</b> animal{{ g.n === 1 ? '' : 's' }} · {{ g.purity >= 0.75 ? 'mostly' : 'largest class:' }} <b :style="{ color: gcol(g.c) }">{{ plural(g.major) }}</b> <span class="opacity-60">({{ Math.round(g.purity * 100) }}%)</span></div>
          <div class="text-xs opacity-75 truncate">{{ g.ex.join(', ') }}</div>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<style scoped>
.lk { transition: stroke 0.5s ease; }
.row-enter-active { transition: opacity 0.5s ease, transform 0.5s ease; }
.row-enter-from { opacity: 0; transform: translateX(10px); }
.row-leave-active { display: none; }
</style>
