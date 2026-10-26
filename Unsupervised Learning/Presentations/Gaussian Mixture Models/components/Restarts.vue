<script setup lang="ts">
// Local optima (data/restarts.json): EM with K = 5 on five blobs, from 12 random starts (5 data points as means).
// Left: log-likelihood by iteration for each start. Every curve rises, but they level off at different heights.
// Right (show = true): the best and the worst final fits.
import { computed } from 'vue'
import d from '../data/restarts.json'
import { useActive } from '../utils/gmm'

withDefaults(defineProps<{ show?: boolean }>(), { show: false })
const { active, isPrintMode } = useActive()
const drawn = computed(() => active.value || isPrintMode.value)
const fin = d.runs.map(r => r.ll[r.ll.length - 1])
const best = fin[d.best]
const lo = Math.min(...d.runs.map(r => r.ll[1])) - 20; const hi = best + 15 // the random start itself (iteration 0) is far below
const W = 400; const H = 300; const T = d.runs[0].ll.length - 1
const sx = (i: number) => 46 + i / T * (W - 60)
const sy = (v: number) => 14 + (hi - Math.max(v, lo)) / (hi - lo) * (H - 50)
const tone = (i: number) => (fin[i] > best - 1 ? '#2dd4bf' : fin[i] < best - 150 ? '#f87171' : '#fbbf24')
const nBest = fin.filter(v => v > best - 1).length
</script>

<template>
  <div class="grid grid-cols-[1.25fr_1fr] gap-5 items-center">
    <div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Twelve log-likelihood curves rising and leveling off at different heights">
        <line :x1="sx(0)" :x2="sx(T)" :y1="H - 36" :y2="H - 36" :style="{ stroke: '#475569' }" />
        <text :x="sx(0)" :y="H - 20" :style="{ fill: '#94a3b8', fontSize: '11px' }">0</text>
        <text :x="sx(T)" :y="H - 20" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ T }} iterations</text>
        <text x="4" y="10" :style="{ fill: '#94a3b8', fontSize: '11px' }">log-likelihood</text>
        <path
          v-for="(r, i) in d.runs" :key="i" pathLength="1" class="run" :class="{ on: drawn }"
          :d="r.ll.map((v, j) => `${j ? 'L' : 'M'}${sx(j).toFixed(1)},${sy(v).toFixed(1)}`).join('')"
          :style="{ fill: 'none', stroke: tone(i), strokeWidth: 2, strokeOpacity: 0.85, transitionDelay: `${i * 120}ms` }"
        />
        <text :x="sx(T) - 2" :y="sy(best) - 6" text-anchor="end" :style="{ fill: '#5eead4', fontSize: '12px', fontWeight: 700 }">{{ best.toFixed(0) }} · {{ nBest }} of {{ d.runs.length }} starts</text>
      </svg>
    </div>
    <div class="grid grid-cols-1 gap-2 reveal" :class="{ shown: show }">
      <div v-for="(which, j) in [d.best, d.worst]" :key="j" border="2 solid white/5" bg="white/5" rounded-lg px-2 py-1>
        <GmmPlot :pts="d.pts" :mix="d.runs[which].final" mode="hard" :levels="[1.5]" :w="300" :h="120" :r="1.6" label="Final EM fit from one start" />
        <div class="text-xs font-mono text-center" :class="j ? 'text-red-300' : 'text-teal-300'">
          {{ j ? 'worst' : 'best' }} · log L {{ fin[which].toFixed(0) }} · ARI {{ d.runs[which].ari.toFixed(2) }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.run { stroke-dasharray: 1; stroke-dashoffset: 1; transition: stroke-dashoffset 1.6s ease; }
.run.on { stroke-dashoffset: 0; }
</style>
