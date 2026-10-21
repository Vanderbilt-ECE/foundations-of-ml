<script setup lang="ts">
// California's 20,640 census block groups (data/calmetro.json; the same 3,000 shown as in the k-Means deck),
// in km east/north of the state's mean. stage 0: k-means with K = 8, the depot regions from the k-Means deck;
// every block group is assigned somewhere. stage 1: HDBSCAN (min_cluster_size = 300, min_samples = 30):
// the dense metro areas, whatever their shape; rural block groups are noise (gray).
import { computed } from 'vue'
import d from '../data/calmetro.json'
import { color, domainOf } from '../utils/clusters'

const props = withDefaults(defineProps<{ stage?: number }>(), { stage: 0 })
const dom = domainOf(d.pts, 0.04)
const lab = computed(() => (props.stage >= 1 ? d.hdb : d.km))
</script>

<template>
  <div class="grid grid-cols-[1fr_1fr] gap-6 items-center">
    <ClusterPlot :pts="d.pts" :lab="lab" :centroids="stage >= 1 ? null : d.kmC" :cells="stage < 1" :domain="dom" :w="420" :h="400" :r="1.9" :c-r="7" label="California block groups clustered by location">
      <template #default="{ sx, sy }">
        <g v-if="stage >= 1">
          <text v-for="(c, k) in d.centers" :key="k" :x="sx(c[0])" :y="sy(c[1])" text-anchor="middle" :style="{ fill: '#fff', fontSize: '12px', fontWeight: 700, paintOrder: 'stroke', stroke: '#000', strokeWidth: 3 }">{{ k + 1 }}</text>
        </g>
      </template>
    </ClusterPlot>
    <div class="text-left" style="min-height: 22rem">
      <div v-if="stage < 1" class="space-y-3">
        <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="text-sm">
          <b class="text-blue-300">k-means, K = 8</b> (the depot problem from last deck): straight borders, and <b>every</b> block group belongs to some region, including empty desert and forest.
        </div>
        <div class="text-sm opacity-80">Good for <i>serving</i> everyone. But what if the question is <b>"where are the cities?"</b></div>
      </div>
      <div v-else>
        <div class="text-xs uppercase tracking-wider opacity-60 mb-2">HDBSCAN · {{ d.names.length }} metro areas</div>
        <div class="grid grid-cols-[auto_1fr_auto] gap-x-3 gap-y-1 text-sm items-center">
          <template v-for="(nm, k) in d.names" :key="nm">
            <span class="font-mono font-bold text-xs rounded px-1.5" :style="{ background: color(k), color: '#0b1020' }">{{ k + 1 }}</span>
            <span>{{ nm }}</span>
            <span class="font-mono opacity-80 text-right">{{ d.sizes[k].toLocaleString() }}</span>
          </template>
          <span class="font-mono font-bold text-xs rounded px-1.5" style="background: #64748b; color: #0b1020">–</span>
          <span>noise (rural, sparse)</span>
          <span class="font-mono opacity-80 text-right">{{ d.noise.toLocaleString() }}</span>
        </div>
        <div class="text-xs opacity-70 mt-2">block groups of {{ d.n.toLocaleString() }}</div>
      </div>
    </div>
  </div>
</template>
