<script setup lang="ts">
// 8 training rows × 10 trees (data/oobgrid.json). A number is how many times the row was drawn
// into that tree's bootstrap sample; an empty red cell means the row is out-of-bag for that tree.
// With `row`, that row is highlighted and its out-of-bag trees are marked as its voters.
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
import d from '../data/oobgrid.json'

const props = withDefaults(defineProps<{ row?: number }>(), { row: -1 })

const nTrees = d.counts.length
const nRows = d.counts[0].length
const cell = 34
const gap = 4
const L = 70
const T = 34
const W = L + nTrees * (cell + gap) + 4
const H = T + nRows * (cell + gap) + 30
const cells = d.counts.flatMap((tree, t) => tree.map((c, i) => {
  const lit = props.row === i
  return {
    key: `${t}-${i}`,
    x: L + t * (cell + gap),
    y: T + i * (cell + gap),
    c,
    style: c === 0
      ? { fill: '#f87171', fillOpacity: lit ? 0.45 : 0.12, stroke: '#f87171', strokeWidth: lit ? 2.5 : 1 }
      : { fill: '#2dd4bf', fillOpacity: lit ? 0.12 : 0.08 + 0.12 * c, stroke: 'none' },
    dim: props.row >= 0 && !lit,
  }
}))
const voters = props.row >= 0 ? d.counts.map((tree, t) => (tree[props.row] === 0 ? t + 1 : 0)).filter(Boolean) : []
</script>

<template>
  <svg role="img" :aria-label="row >= 0 ? `Row ${row + 1} is out-of-bag for trees ${voters.join(', ')}, which vote on it` : 'Grid of 8 rows by 10 trees showing in-bag counts and out-of-bag cells'" :viewBox="`0 0 ${W} ${H}`" class="w-full">
    <text v-for="t in nTrees" :key="`h${t}`" :x="L + (t - 1) * (cell + gap) + cell / 2" :y="T - 10" text-anchor="middle"
      :style="{ fill: voters.includes(t) ? '#fca5a5' : '#94a3b8', fontSize: '12px', fontWeight: voters.includes(t) ? 700 : 400 }">T{{ t }}</text>
    <text v-for="i in nRows" :key="`r${i}`" :x="L - 10" :y="T + (i - 1) * (cell + gap) + cell / 2 + 5" text-anchor="end"
      :style="{ fill: row === i - 1 ? '#e2e8f0' : '#94a3b8', fontSize: '13px', fontWeight: row === i - 1 ? 700 : 400 }">row {{ i }}</text>
    <g v-for="c in cells" :key="c.key" :style="{ opacity: c.dim ? 0.45 : 1 }">
      <rect :x="c.x" :y="c.y" :width="cell" :height="cell" rx="5" :style="c.style" />
      <text v-if="c.c" :x="c.x + cell / 2" :y="c.y + cell / 2 + 5" text-anchor="middle" :style="{ fill: '#ccfbf1', fontSize: '13px' }">{{ c.c }}</text>
    </g>
    <text v-if="row >= 0" :x="L" :y="H - 8" :style="{ fill: '#fca5a5', fontSize: '13px' }">row {{ row + 1 }} is out-of-bag for {{ voters.length }} of {{ nTrees }} trees → T{{ voters.join(', T') }} vote</text>
    <text v-else :x="L" :y="H - 8" :style="{ fill: '#94a3b8', fontSize: '13px' }">number = times drawn into that tree's sample · red = out-of-bag</text>
  </svg>
</template>
