<script setup lang="ts">
// EM on the running example (data/em.json, recorded by make_data.py's hand-written EM), as alternating moves:
// E-step = the points recolor (responsibilities under the current ellipses), M-step = the ellipses refit.
// Right: the log-likelihood after each iteration, drawn as it goes, and the current weights.
//   play = false: the starting guess (three data points as means, a broad shared covariance)
//   play = true:  run 15 iterations, then hold. The PDF export shows the final state.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import d from '../data/em.json'
import { color } from '../utils/clusters'
import { useActive } from '../utils/gmm'

const props = withDefaults(defineProps<{ play?: boolean }>(), { play: false })
const LAST = 15
const END = 2 * LAST + 1
const { active, isPrintMode } = useActive()
const s = ref(isPrintMode.value ? END : 0)
let timer: ReturnType<typeof setInterval> | undefined
function run() {
  clearInterval(timer)
  if (!props.play || !active.value) return
  s.value = 0
  timer = setInterval(() => { s.value < END ? s.value++ : clearInterval(timer) }, 650)
}
watch(() => [props.play, active.value], () => (props.play ? run() : (clearInterval(timer), s.value = isPrintMode.value ? END : 0)), { immediate: true })
onBeforeUnmount(() => clearInterval(timer))

// s = 0: start; s odd: E-step of iteration (s-1)/2 done; s even > 0: M-step done (ellipses at frame s/2)
const it = computed(() => Math.floor(s.value / 2))
const mix = computed(() => d.frames[it.value])
const colorMix = computed(() => (s.value === 0 ? null : d.frames[Math.floor((s.value - 1) / 2)]))
const phase = computed(() => (s.value === 0 ? 'start' : s.value % 2 ? 'E' : 'M'))

const lls = d.frames.slice(0, LAST + 1).map(f => f.ll)
const CW = 270; const CH = 150; const lo = lls[0]; const hi = lls[LAST]
const cx = (i: number) => 34 + i / LAST * (CW - 44)
const cy = (v: number) => CH - 22 - (v - lo) / (hi - lo) * (CH - 36)
// the log-likelihood of frame t is known once its E-step has run
const nLL = computed(() => (s.value === 0 ? 0 : Math.floor((s.value - 1) / 2) + 1))
const llPath = computed(() => lls.slice(0, nLL.value).map((v, i) => `${i ? 'L' : 'M'}${cx(i).toFixed(1)},${cy(v).toFixed(1)}`).join(''))
</script>

<template>
  <div class="grid grid-cols-[1.45fr_1fr] gap-5 items-center">
    <GmmPlot :pts="d.pts" :mix="mix" :color-mix="colorMix" :mode="s === 0 ? 'gray' : 'soft'" :w="520" :h="380" :r="2.8" :ms="520" frame label="EM iterations: points recolor, then ellipses refit" />
    <div class="text-left space-y-3">
      <div class="flex items-baseline gap-3">
        <span class="text-sm opacity-70">iteration</span>
        <span class="font-mono text-4xl font-bold">{{ it }}</span>
      </div>
      <div class="flex gap-2 text-sm font-bold">
        <div class="phase" :class="{ on: phase === 'E' }" style="--c: #2dd4bf">E-step · recolor points</div>
        <div class="phase" :class="{ on: phase === 'M' }" style="--c: #fbbf24">M-step · refit ellipses</div>
      </div>
      <svg :viewBox="`0 0 ${CW} ${CH}`" class="w-full" role="img" aria-label="Log-likelihood rising with each EM iteration and leveling off">
        <line :x1="cx(0)" :x2="cx(LAST)" :y1="CH - 22" :y2="CH - 22" :style="{ stroke: '#475569' }" />
        <text :x="cx(0)" :y="CH - 6" :style="{ fill: '#94a3b8', fontSize: '11px' }">0</text>
        <text :x="cx(LAST)" :y="CH - 6" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ LAST }}</text>
        <text x="2" y="12" :style="{ fill: '#94a3b8', fontSize: '11px' }">log-likelihood</text>
        <text :x="cx(LAST)" :y="cy(hi) - 6" text-anchor="end" :style="{ fill: '#5eead4', fontSize: '11px' }">{{ hi.toFixed(0) }}</text>
        <text :x="cx(0) + 4" :y="cy(lo) + 2" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ lo.toFixed(0) }}</text>
        <path :d="llPath" :style="{ fill: 'none', stroke: '#2dd4bf', strokeWidth: 2.5 }" />
        <circle v-for="(v, i) in lls.slice(0, nLL)" :key="i" :cx="cx(i)" :cy="cy(v)" r="3" :style="{ fill: '#2dd4bf' }" />
      </svg>
      <div class="flex gap-4 font-mono text-sm">
        <span v-for="(w, k) in mix.w" :key="k" :style="{ color: color(k) }">π{{ ['₁', '₂', '₃'][k] }}={{ w.toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.phase { padding: 4px 10px; border-radius: 6px; border: 2px solid rgba(255,255,255,0.08); opacity: 0.35; transition: all 0.25s; }
.phase.on { opacity: 1; border-color: var(--c); color: var(--c); background: color-mix(in srgb, var(--c) 15%, transparent); }
</style>
