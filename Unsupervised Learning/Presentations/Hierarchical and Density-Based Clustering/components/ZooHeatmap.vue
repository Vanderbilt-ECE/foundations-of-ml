<script setup lang="ts">
// The zoo's trait table with rows in dendrogram order (data/zoo.json): one row per animal, one column per trait.
// Teal = has the trait; legs shaded amber by count (0-8). Left band: the K = 7 cut, colored by each group's
// most common class (as on the tree slide). Right band: true class. `hl` outlines the six traits whose
// averages differ most between the seven groups.
import d from '../data/zoo.json'
import { color } from '../utils/clusters'

withDefaults(defineProps<{ hl?: boolean }>(), { hl: false })
const lab = (d.labs as Record<string, number[]>)['7']
const groups = (d.groups as Record<string, { major: string }[]>)['7']
const n = d.names.length
const W = 470; const H = 420; const L = 26; const T = 74; const B = 414
const cw = 23
const rh = (B - T) / n
const label = (t: string) => t.replace('breathes', 'breathes air').replace('catsize', 'cat-size+')
const cell = (v: number, j: number) => (d.traits[j] === 'legs'
  ? { fill: '#fbbf24', fillOpacity: 0.08 + 0.85 * v / 8 }
  : { fill: v ? '#2dd4bf' : '#ffffff', fillOpacity: v ? 0.85 : 0.04 })
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Trait table of 101 animals ordered by the dendrogram; blocks of shared traits line up with the clusters">
    <g v-for="(t, j) in d.traits" :key="t">
      <text :x="L + 10 + j * cw + cw / 2" :y="T - 6" :transform="`rotate(-55 ${L + 10 + j * cw + cw / 2} ${T - 6})`" :style="{ fill: hl && d.keyTraits.includes(j) ? '#fbbf24' : '#cbd5e1', fontSize: '11px', fontWeight: hl && d.keyTraits.includes(j) ? 700 : 400 }">{{ label(t) }}</text>
    </g>
    <g v-for="(leaf, pos) in d.order" :key="leaf">
      <rect :x="L - 12" :y="T + pos * rh" width="16" :height="rh + 0.3" :style="{ fill: color(d.classes.indexOf(groups[lab[leaf]].major)) }" />
      <rect v-for="(v, j) in d.F[leaf]" :key="j" :x="L + 10 + j * cw" :y="T + pos * rh" :width="cw - 1.5" :height="rh + 0.3" :style="cell(v, j)" />
      <rect :x="L + 16 + 16 * cw" :y="T + pos * rh" width="14" :height="rh + 0.3" :style="{ fill: color(d.type[leaf]) }" />
    </g>
    <text :x="L - 4" :y="T - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">K=7</text>
    <text :x="L + 23 + 16 * cw" :y="T - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '10px' }">class</text>
    <g class="fade" :style="{ opacity: hl ? 1 : 0 }">
      <rect v-for="j in d.keyTraits" :key="`h${j}`" :x="L + 9 + j * cw" :y="T - 1" :width="cw" :height="B - T + 2" rx="3" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
    </g>
  </svg>
</template>

<style scoped>
.fade { transition: opacity 0.5s ease; }
</style>
