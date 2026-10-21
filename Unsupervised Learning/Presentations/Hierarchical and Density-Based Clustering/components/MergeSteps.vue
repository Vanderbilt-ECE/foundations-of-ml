<script setup lang="ts">
// Agglomerative clustering of 8 points with single linkage (data/merge8.json), one merge per click.
// Left: each merge draws the closest pair of points between the two clusters (together these
// edges form a minimum spanning tree). Right: the dendrogram gains one link per merge, drawn at
// the merge distance. Points still on their own are gray.
import { useNav, useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/merge8.json'
import { color, domainOf, equalScale, linkPath } from '../utils/clusters'

const { $clicks } = useSlideContext()
const { isPrintMode } = useNav()
const n = d.pts.length
const t = computed(() => Math.min($clicks.value, n - 1))
const f = computed(() => d.frames[t.value])
const col = (k: number) => (k < 0 ? '#94a3b8' : color(k))

const S = equalScale(domainOf(d.pts, 0.14), 400, 290)
const edges = computed(() => d.frames.slice(1, t.value + 1).map(fr => fr.edge as number[]))

const DW = 380; const DH = 290; const L = 44; const R = 372; const T = 12; const B = 252
const hmax = Math.max(...d.tree.h) * 1.08
const at = (pos: number, h: number): [number, number] => [L + (pos + 0.5) / n * (R - L), B - h / hmax * (B - T)]
const ticks = [0, 1, 2, 3, 4].filter(v => v <= hmax)
</script>

<template>
  <div>
    <div class="grid grid-cols-2 gap-4 items-end">
      <svg :viewBox="`0 0 400 290`" class="w-full" role="img" aria-label="Eight labeled points; lines join the closest pair at each merge">
        <line
          v-for="(e, k) in edges" :key="`e${k}`"
          :x1="S.sx(d.pts[e[0]][0])" :y1="S.sy(d.pts[e[0]][1])" :x2="S.sx(d.pts[e[1]][0])" :y2="S.sy(d.pts[e[1]][1])"
          :class="{ draw: !isPrintMode && k === t - 1 }" pathLength="1"
          :style="{ stroke: col(f.lab[e[0]]), strokeWidth: k === t - 1 ? 3.5 : 2.2, strokeLinecap: 'round' }"
        />
        <g v-for="(p, i) in d.pts" :key="i">
          <circle :cx="S.sx(p[0])" :cy="S.sy(p[1])" r="9" class="pt" :style="{ fill: col(f.lab[i]), stroke: '#0b1020', strokeWidth: 2 }" />
          <text :x="S.sx(p[0])" :y="S.sy(p[1]) - 14" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '14px', fontWeight: 700 }">{{ d.names[i] }}</text>
        </g>
      </svg>
      <svg :viewBox="`0 0 ${DW} ${DH}`" class="w-full" role="img" aria-label="Dendrogram growing one merge at a time">
        <line :x1="L" :x2="L" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
        <g v-for="v in ticks" :key="v">
          <line :x1="L - 4" :x2="L" :y1="at(0, v)[1]" :y2="at(0, v)[1]" :style="{ stroke: '#475569' }" />
          <text :x="L - 8" :y="at(0, v)[1] + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
        </g>
        <text :x="12" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 12 ${(T + B) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">merge distance</text>
        <path
          v-for="i in t" :key="`l${i}`" :d="linkPath(d.tree, i - 1, at)" pathLength="1"
          :class="{ draw: !isPrintMode && i === t }"
          :style="{ stroke: col(f.lab[d.tree.rep[n + i - 1]]), strokeWidth: i === t ? 3.2 : 2.2, fill: 'none' }"
        />
        <text v-for="(leaf, pos) in d.tree.order" :key="`n${leaf}`" :x="at(pos, 0)[0]" :y="B + 22" text-anchor="middle" :style="{ fill: col(f.lab[leaf]), fontSize: '14px', fontWeight: 700 }">{{ d.names[leaf] }}</text>
      </svg>
    </div>
    <div class="mt-2 text-center text-sm" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="height: 2.6em; line-height: 1.6em">
      <template v-if="t === 0">Start: <b>8 clusters</b>, one point each. Find the two closest clusters.</template>
      <template v-else>
        Merge <b class="text-amber-300">{{ f.pair![0] }}</b> + <b class="text-amber-300">{{ f.pair![1] }}</b> at distance <b class="font-mono">{{ f.h.toFixed(2) }}</b>
        <span class="opacity-70"> · {{ n - t }} cluster{{ n - t === 1 ? '' : 's' }} left</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.pt { transition: fill 0.5s ease; }
.draw { stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw 0.7s ease forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
</style>
