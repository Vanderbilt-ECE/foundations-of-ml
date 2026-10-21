<script setup lang="ts">
// HDBSCAN's condensed tree for the varied-density data (data/varied.json → tree, min_cluster_size = 25).
// Vertical axis: λ = 1 / distance, so going down means "denser". Each branch narrows as points fall out of
// it; it ends when it splits in two or runs out of points.
// stage 0 tree · 1 one horizontal cut at ε = 1.25 (= DBSCAN* with that ε) · 2 a cut at ε = 0.25
// stage 3 HDBSCAN's choice: the long-lived branches, picked at different heights.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/varied.json'
import { color, useTween } from '../utils/clusters'

const { $clicks } = useSlideContext()
const s = computed(() => Math.min($clicks.value, 3))
const n = d.pts.length
type Node = { birth: number, size: number, fell: number[], kids: number[], death: number }
const nodes: Record<number, Node> = {}
const get = (c: number) => (nodes[c] ??= { birth: 0, size: n, fell: [], kids: [], death: 0 })
for (const [p, c, lam, sz] of d.tree as number[][]) {
  if (c >= n) {
    const k = get(c); k.birth = lam; k.size = sz
    get(p).kids.push(c)
  }
  else { get(p).fell.push(lam) }
}
const root = Math.min(...Object.keys(nodes).map(Number))
for (const c of Object.keys(nodes).map(Number)) {
  const k = nodes[c]
  k.fell.sort((a, b) => a - b)
  k.death = k.kids.length ? nodes[k.kids[0]].birth : (k.fell.at(-1) ?? k.birth)
}
const W = 430; const H = 360; const T = 16; const B = 340; const LM = 40
const lmax = 6.5
const Y = (lam: number) => T + Math.min(lam, lmax) / lmax * (B - T)
const unit = (W - LM - 20) / n

// polygon for each node: width = points still in the branch, shrinking as points fall out
const shapes: { c: number, d: string }[] = []
function place(c: number, cx: number) {
  const k = nodes[c]
  const steps = [k.birth, ...k.fell.filter(l => l < k.death), k.death]
  let w = k.size
  const left: string[] = []; const right: string[] = []
  steps.forEach((lam, i) => {
    if (i > 0) {
      left.push(`${(cx - w * unit / 2).toFixed(1)},${Y(lam).toFixed(1)}`)
      right.push(`${(cx + w * unit / 2).toFixed(1)},${Y(lam).toFixed(1)}`)
      if (i < steps.length - 1) w -= 1
    }
    left.push(`${(cx - w * unit / 2).toFixed(1)},${Y(lam).toFixed(1)}`)
    right.push(`${(cx + w * unit / 2).toFixed(1)},${Y(lam).toFixed(1)}`)
  })
  shapes.push({ c, d: `M${left.join('L')}L${right.reverse().join('L')}Z` })
  const total = k.kids.reduce((t, q) => t + nodes[q].size, 0)
  let x0 = cx - total * unit / 2
  for (const q of k.kids) {
    place(q, x0 + nodes[q].size * unit / 2)
    x0 += nodes[q].size * unit
  }
}
place(root, LM + (W - LM - 20) / 2 + 10)
const sel = d.selected as Record<string, number>
const cutY = useTween(() => [Y(s.value === 1 ? d.cuts[0].lam : s.value === 2 ? d.cuts[1].lam : s.value === 0 ? 0 : d.cuts[1].lam)], 650)
const lab = computed(() => (s.value === 1 ? d.cuts[0].lab : s.value === 2 ? d.cuts[1].lab : s.value === 3 ? d.hdb : null))
const caption = computed(() => [
  'The whole hierarchy over every density level.',
  `One cut at ε = ${d.cuts[0].eps}: ${d.cuts[0].k} clusters, the tight pair merged.`,
  `One cut at ε = ${d.cuts[1].eps}: the pair splits, the disk is all noise (${d.cuts[1].noise} points).`,
  'HDBSCAN keeps the branches that last longest, each at its own level.',
][s.value])
const ticks = [0, 1, 2, 3, 4, 5, 6]
</script>

<template>
  <div>
    <div class="grid grid-cols-[1.05fr_1fr] gap-5 items-center">
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Condensed cluster tree: one root splitting into the disk and the tight pair, and the pair splitting in two further down">
        <line :x1="LM" :x2="LM" :y1="T" :y2="B" :style="{ stroke: '#475569' }" />
        <g v-for="v in ticks" :key="v">
          <text :x="LM - 6" :y="Y(v) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
        </g>
        <text x="11" :y="(T + B) / 2" text-anchor="middle" :transform="`rotate(-90 11 ${(T + B) / 2})`" :style="{ fill: '#94a3b8', fontSize: '12px' }">λ = 1 / distance (denser ↓)</text>
        <path
          v-for="sh in shapes" :key="sh.c" :d="sh.d" class="br"
          :style="{
            fill: s >= 3 && sel[sh.c] !== undefined ? color(sel[sh.c]) : '#94a3b8',
            fillOpacity: s >= 3 && sel[sh.c] !== undefined ? 0.75 : 0.28,
            stroke: s >= 3 && sel[sh.c] !== undefined ? '#fff' : 'rgba(148,163,184,0.6)', strokeWidth: 1,
          }"
        />
        <g class="fade" :style="{ opacity: s === 1 || s === 2 ? 1 : 0 }">
          <line :x1="LM" :x2="W - 6" :y1="cutY[0]" :y2="cutY[0]" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '7 5' }" />
          <text :x="W - 8" :y="cutY[0] - 7" text-anchor="end" :style="{ fill: '#fbbf24', fontSize: '12px', fontWeight: 700 }">one ε for every cluster</text>
        </g>
      </svg>
      <ClusterPlot :pts="d.pts" :lab="lab" frame :w="400" :h="340" :r="2.6" label="The varied-density data colored by the current cut or by HDBSCAN" />
    </div>
    <div class="text-sm text-center mt-2" border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2 style="min-height: 2.6em">{{ caption }}</div>
  </div>
</template>

<style scoped>
.br { transition: fill 0.5s ease, fill-opacity 0.5s ease, stroke 0.5s ease; }
.fade { transition: opacity 0.5s ease; }
</style>
