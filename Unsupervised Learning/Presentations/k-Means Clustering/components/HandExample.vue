<script setup lang="ts">
// One iteration by hand on six points, K = 2 (data/hand.json).
// clicks: 0 points + starting centroids A and D · 1 distances · 2 assignment
//         3 update centroids · 4 reassign: nothing changes
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/hand.json'
import { color, fmt } from '../utils/kmeans'

const { $clicks } = useSlideContext()
const s = computed(() => $clicks.value)
const names = ['A', 'B', 'C', 'D', 'E', 'F']
const cents = computed(() => (s.value >= 3 ? d.c1 : d.c0))
const lab = computed(() => (s.value >= 2 ? d.lab0 : null))
const dom = { x: [0, 6] as [number, number], y: [0, 8] as [number, number] }
const pt = (p: number[]) => `(${p[0]}, ${p[1]})`
</script>

<template>
  <div class="grid grid-cols-[0.8fr_1.2fr] gap-6 items-start">
    <div>
      <ClusterPlot :pts="d.pts" :lab="lab" :centroids="cents" :domain="dom" :w="300" :h="380" :r="7" :lines="s >= 2" frame label="Six points and two centroids">
        <template #default="{ sx, sy }">
          <text v-for="(p, i) in d.pts" :key="i" :x="sx(p[0]) + 10" :y="sy(p[1]) + 4" :style="{ fill: '#e2e8f0', fontSize: '14px', fontWeight: 700 }">{{ names[i] }}</text>
        </template>
      </ClusterPlot>
    </div>
    <div class="text-sm">
      <table class="hand">
        <thead>
          <tr>
            <th>pt</th><th>x</th>
            <th :class="{ hid: s < 1 }">‖x − μ₁‖</th>
            <th :class="{ hid: s < 1 }">‖x − μ₂‖</th>
            <th :class="{ hid: s < 2 }">cluster</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(p, i) in d.pts" :key="i">
            <td class="font-bold">{{ names[i] }}</td>
            <td class="font-mono">{{ pt(p) }}</td>
            <td class="font-mono" :class="{ hid: s < 1, win: s >= 2 && d.lab0[i] === 0 }">{{ d.d0[i][0].toFixed(2) }}</td>
            <td class="font-mono" :class="{ hid: s < 1, win: s >= 2 && d.lab0[i] === 1 }">{{ d.d0[i][1].toFixed(2) }}</td>
            <td :class="{ hid: s < 2 }"><span class="font-bold" :style="{ color: color(d.lab0[i]) }">{{ d.lab0[i] + 1 }}</span></td>
          </tr>
        </tbody>
      </table>
      <div class="grid grid-cols-2 gap-3 mt-3">
        <div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2>
          <div class="text-xs opacity-60">centroids</div>
          <div class="font-mono"><span class="text-teal-300">μ₁</span> = {{ s >= 3 ? `(${fmt(d.c1[0][0], 2)}, ${fmt(d.c1[0][1], 2)})` : pt(d.c0[0]) }}</div>
          <div class="font-mono"><span class="text-blue-300">μ₂</span> = {{ s >= 3 ? `(${fmt(d.c1[1][0], 2)}, ${fmt(d.c1[1][1], 2)})` : pt(d.c0[1]) }}</div>
        </div>
        <div border="2 solid white/5" bg="white/5" rounded-lg px-3 py-2 :class="{ hid: s < 2 }">
          <div class="text-xs opacity-60">objective J</div>
          <div class="font-mono text-amber-300">{{ s >= 3 ? `${d.J0.toFixed(2)} → ${d.J1.toFixed(2)}` : d.J0.toFixed(2) }}</div>
          <div class="text-xs mt-1" :class="s >= 4 ? 'text-green-300' : 'opacity-0'">reassign: no change → converged</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hand { width: 100%; border-collapse: collapse; }
.hand th, .hand td { padding: 4px 8px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.08); transition: opacity 0.5s ease, background-color 0.5s ease; }
.hand th { font-weight: 600; opacity: 0.7; font-size: 0.8rem; }
.hid { opacity: 0 !important; }
.win { background: rgba(45, 212, 191, 0.12); font-weight: 700; }
</style>
