<script setup lang="ts">
// Method × dataset ARI table (data/compare.json), every method at its best-case settings:
// the true K for k-means / Ward / single, and the ε, minPts, min_cluster_size that score best.
// Cell color: red (ARI 0) → teal (ARI 1). The panel on the right shows one cell's clustering:
// pick[clicks] chooses it, and hovering any cell shows that one instead.
import { useSlideContext } from '@slidev/client'
import { computed, ref } from 'vue'
import d from '../data/compare.json'

const props = withDefaults(defineProps<{ pick?: [number, number][] }>(), { pick: () => [[1, 0], [1, 2], [0, 2], [4, 4]] })
const { $clicks } = useSlideContext()
const t = d.table
const hover = ref<[number, number] | null>(null)
const cur = computed(() => hover.value ?? props.pick[Math.min($clicks.value, props.pick.length - 1)])
const labs = t.labs as Record<string, Record<string, number[]> & { pts: number[][] }>
const ds = computed(() => t.datasets[cur.value[0]])
const m = computed(() => t.methods[cur.value[1]])
const bg = (a: number) => {
  const u = Math.max(0, Math.min(1, a))
  const mix = (x: number, y: number) => Math.round(x + (y - x) * u)
  return `rgba(${mix(248, 45)}, ${mix(113, 212)}, ${mix(113, 191)}, 0.55)`
}
const names: Record<string, string> = { blobs3: 'three blobs', moons: 'two moons', circles: 'two rings', outliers: 'blobs + outliers', varied: 'two densities' }
</script>

<template>
  <div class="grid grid-cols-[1.35fr_1fr] gap-5 items-center">
    <table class="ct" @mouseleave="hover = null">
      <thead>
        <tr>
          <th />
          <th v-for="mm in t.methods" :key="mm">{{ mm }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in t.ari" :key="i">
          <th class="text-left">
            <div class="flex items-center gap-2">
              <ClusterPlot :pts="labs[t.datasets[i]].pts" :lab="labs[t.datasets[i]].truth" :w="56" :h="38" :r="0.9" :label="`${t.datasets[i]} true groups`" style="width: 56px" />
              <span class="text-xs">{{ names[t.datasets[i]] }}</span>
            </div>
          </th>
          <td
            v-for="(a, j) in row" :key="j" :style="{ background: bg(a) }"
            :class="{ sel: cur[0] === i && cur[1] === j }"
            @mouseenter="hover = [i, j]"
          >{{ a.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <div>
      <ClusterPlot :pts="labs[ds].pts" :lab="labs[ds][m]" frame :w="380" :h="290" :r="2.4" :label="`${m} on ${ds}`" />
      <div class="text-center text-sm mt-1"><b>{{ m }}</b> on {{ names[ds] }} · ARI <span class="font-mono">{{ t.ari[cur[0]][cur[1]].toFixed(2) }}</span></div>
    </div>
  </div>
</template>

<style scoped>
.ct { border-collapse: separate; border-spacing: 3px; width: 100%; }
.ct th { font-size: 0.8rem; font-weight: 600; opacity: 0.85; padding: 2px 4px; }
.ct td { font-family: ui-monospace, monospace; font-size: 0.95rem; text-align: center; border-radius: 6px; padding: 8px 4px; cursor: default; border: 2px solid transparent; transition: border-color 0.3s ease; }
.ct td.sel { border-color: #fff; }
</style>
