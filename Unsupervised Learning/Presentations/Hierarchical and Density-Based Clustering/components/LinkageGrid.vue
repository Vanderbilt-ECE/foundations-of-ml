<script setup lang="ts">
// Four linkages × three datasets (data/linkgrid.json), each cut at the true number of groups.
// Badge = ARI against the true groups (true outliers count as singletons).
// hl: cells to ring, as "dataset:linkage".
import d from '../data/linkgrid.json'

withDefaults(defineProps<{ hl?: string[] }>(), { hl: () => [] })
const rows = [['blobs3', 'three blobs'], ['moons', 'two moons'], ['outliers', 'blobs + 15 outliers']] as const
const links = ['single', 'complete', 'average', 'ward'] as const
const names: Record<string, string> = { single: 'Single', complete: 'Complete', average: 'Average', ward: 'Ward' }
const badge = (a: number) => (a >= 0.85 ? 'text-teal-300' : a >= 0.5 ? 'text-amber-300' : 'text-red-300')
</script>

<template>
  <div class="grid gap-x-2 gap-y-1 items-center" style="grid-template-columns: 5.2rem repeat(4, 1fr)">
    <div />
    <div v-for="l in links" :key="l" class="text-center text-sm font-bold opacity-85">{{ names[l] }}</div>
    <template v-for="[ds, label] in rows" :key="ds">
      <div class="text-xs opacity-80 text-right pr-1 leading-tight">{{ label }}<br><span class="opacity-60">K = {{ d[ds].k }}</span></div>
      <div v-for="l in links" :key="l" class="cell relative rounded-lg" :class="{ ring: hl.includes(`${ds}:${l}`) }">
        <ClusterPlot :pts="d[ds].pts" :lab="d[ds][l].lab" :w="200" :h="112" :r="1.7" :label="`${names[l]} linkage on ${label}`" />
        <div class="absolute right-1 bottom-0 text-xs font-mono font-bold" :class="badge(d[ds][l].ari)">ARI {{ d[ds][l].ari.toFixed(2) }}</div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.cell { border: 2px solid rgba(255, 255, 255, 0.05); background: rgba(255, 255, 255, 0.025); transition: border-color 0.4s ease, background 0.4s ease; }
.cell.ring { border-color: #fbbf24; background: rgba(251, 191, 36, 0.08); }
</style>
