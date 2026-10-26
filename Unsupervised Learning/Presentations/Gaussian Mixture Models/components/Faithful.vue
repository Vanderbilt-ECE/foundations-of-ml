<script setup lang="ts">
// Old Faithful (data/faithful.json): 272 eruptions, duration vs. waiting time before it, both in minutes.
//   step 0: raw points · step 1: the BIC-chosen GMM (soft colors) and the BIC sweep
//   step 2: anomalies = the 2% of eruptions with the lowest log-density under the model (ringed)
// Axes are not equal-aspect (minutes on both, but very different ranges), so ellipses are drawn in data space.
import { computed } from 'vue'
import f from '../data/faithful.json'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const dom = { x: [1.3, 5.4] as [number, number], y: [40, 100] as [number, number] }
const flagged = f.flag.map((v, i) => (v ? i : -1)).filter(i => i >= 0)
const W = 230; const H = 150; const lo = Math.min(...f.sweep.map(s => s.bic)); const hi = Math.max(...f.sweep.map(s => s.bic))
const bx = (k: number) => 30 + (k - 1) / 5 * (W - 45)
const by = (v: number) => 26 + (hi - v) / (hi - lo) * (H - 54)
const mode = computed(() => (props.step === 0 ? 'gray' : 'soft'))
</script>

<template>
  <div class="grid grid-cols-[1.6fr_1fr] gap-5 items-center">
    <GmmPlot
      :pts="f.pts" :mix="step >= 1 ? f.gmm : null" :mode="mode" :domain="dom" :equal="false" :levels="[1, 2]"
      :focus="step >= 2 ? flagged : null" :w="520" :h="360" :r="3.2" frame label="Old Faithful eruptions: duration against waiting time"
    >
      <template #default="{ sx, sy }">
        <g v-for="t in [2, 3, 4, 5]" :key="`x${t}`"><text :x="sx(t)" :y="352" text-anchor="middle" :style="{ fill: '#64748b', fontSize: '11px' }">{{ t }}</text></g>
        <g v-for="t in [50, 60, 70, 80, 90]" :key="`y${t}`"><text x="8" :y="sy(t) + 4" :style="{ fill: '#64748b', fontSize: '11px' }">{{ t }}</text></g>
        <text :x="sx(5.35)" y="338" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '12px' }">eruption length (min)</text>
        <text x="30" y="20" :style="{ fill: '#94a3b8', fontSize: '12px' }">wait before it (min)</text>
        <g v-if="step >= 2">
          <circle v-for="i in flagged" :key="`r${i}`" :cx="sx(f.pts[i][0])" :cy="sy(f.pts[i][1])" r="9" :style="{ fill: 'none', stroke: '#f87171', strokeWidth: 2.2 }" />
        </g>
      </template>
    </GmmPlot>
    <div class="text-left space-y-3">
      <div class="reveal" :class="{ shown: step >= 1 }">
        <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="BIC against number of components, lowest at K = 2">
          <path :d="f.sweep.map((s, i) => `${i ? 'L' : 'M'}${bx(s.k).toFixed(1)},${by(s.bic).toFixed(1)}`).join('')" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2.4 }" />
          <circle v-for="s in f.sweep" :key="s.k" :cx="bx(s.k)" :cy="by(s.bic)" :r="s.k === f.k ? 6 : 3" :style="{ fill: '#2dd4bf' }" />
          <text v-for="s in f.sweep" :key="`k${s.k}`" :x="bx(s.k)" :y="H - 8" text-anchor="middle" :style="{ fill: s.k === f.k ? '#f8fafc' : '#64748b', fontSize: '11px' }">{{ s.k }}</text>
          <text x="4" y="10" :style="{ fill: '#94a3b8', fontSize: '11px' }">BIC by K</text>
        </svg>
        <div class="text-sm font-mono">K = {{ f.k }} · π = {{ f.gmm.w.map(w => w.toFixed(2)).join(' / ') }}</div>
        <div class="text-xs opacity-75">short eruptions ≈ {{ f.gmm.mu[0][0].toFixed(1) }} min after a {{ f.gmm.mu[0][1].toFixed(0) }} min wait; long ≈ {{ f.gmm.mu[1][0].toFixed(1) }} min after {{ f.gmm.mu[1][1].toFixed(0) }} min</div>
      </div>
      <div class="reveal text-sm" :class="{ shown: step >= 2 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
        <b class="text-red-300">{{ flagged.length }} unusual eruptions</b>: log p(x) &lt; {{ f.thr }}, the lowest 2%. Mostly mid-length eruptions, between the two types.
      </div>
    </div>
  </div>
</template>
