<script setup lang="ts">
// t-SNE running live in the browser on 400 digits (data/tsnelive.json picks them), exact gradient
// (utils/tsne.ts, the same algorithm as scripts/make_data.py, whose KL is checked against sklearn).
// Starts when the slide is shown; "restart" reseeds the random start, the buttons change the perplexity.
// The map is rescaled every frame to fit. Hover a point to see the digit. PDF export: the finished Python run.
import { computed, ref, shallowRef } from 'vue'
import dg from '../data/digits.json'
import tl from '../data/tsnelive.json'
import { decode, rng, useActive, useLoop } from '../utils/plot'
import { EXAGGERATION_ITERS, jointP, sqdist, tsneInit, tsneStep } from '../utils/tsne'

const ITERS = 1000
const lab = tl.idx.map(i => dg.y[i])
const imgs = tl.idx.map(i => dg.img[i])
const X = tl.idx.map(i => decode(dg.img[i]))
const D = sqdist(X)
const perp = ref(30)
let P = jointP(D, perp.value)
let seed = 1
const { isPrintMode } = useActive()
const st = shallowRef(tsneInit(X.length, rng(seed).n))
const pts = ref<number[][]>(isPrintMode.value ? tl.final : st.value.Y.map(() => [0, 0]))
const it = ref(0); const kl = ref(Number.NaN)
let scale = 1e-4

function frame() {
  const Y = st.value.Y
  let m = 1e-9
  for (const p of Y) m = Math.max(m, Math.abs(p[0]), Math.abs(p[1]))
  scale = Math.max(m, scale * 0.97) // ease the zoom out, so the map doesn't jitter
  const cx = Y.reduce((s, p) => s + p[0], 0) / Y.length; const cy = Y.reduce((s, p) => s + p[1], 0) / Y.length
  pts.value = Y.map(p => [(p[0] - cx) / scale, (p[1] - cy) / scale])
  it.value = st.value.it; kl.value = st.value.kl
}
function restart(newSeed = true) {
  if (newSeed) seed++
  st.value = tsneInit(X.length, rng(seed).n)
  scale = 1e-4
  frame()
}
function setPerp(p: number) {
  perp.value = p
  P = jointP(D, p)
  restart(false)
}
useLoop(() => {
  if (st.value.it >= ITERS) return
  for (let s = 0; s < 4; s++) tsneStep(st.value, P)
  frame()
}, () => { if (st.value.it >= ITERS || st.value.it === 0) restart(false) })
const phase = computed(() => (it.value < EXAGGERATION_ITERS ? 'early exaggeration (×12 attraction)' : it.value >= ITERS ? 'done' : 'refining'))
</script>

<template>
  <div class="grid grid-cols-[auto_1fr] gap-6 items-center">
    <EmbedPlot :pts="pts" :lab="lab" :imgs="imgs" :w="440" :h="340" :r="2.8" :ms="0" hover labels label="t-SNE map of 400 digits, computed live" />
    <div class="text-left space-y-3">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1">
        <div>iteration <span class="text-amber-300">{{ isPrintMode ? ITERS : it }}</span> / {{ ITERS }}</div>
        <div class="h-1.5 rounded-full overflow-hidden" style="background: rgba(148,163,184,0.18)">
          <div class="h-full" :style="{ width: `${100 * (isPrintMode ? 1 : it / ITERS)}%`, background: it < EXAGGERATION_ITERS ? '#fbbf24' : '#2dd4bf' }" />
        </div>
        <div class="text-xs opacity-75">{{ isPrintMode ? 'done' : phase }}</div>
        <div>KL(P‖Q) = <span class="text-teal-300">{{ isPrintMode ? tl.kl.toFixed(3) : (Number.isNaN(kl) ? '—' : kl.toFixed(3)) }}</span></div>
      </div>
      <div class="flex flex-wrap gap-2 text-sm">
        <button class="px-2 py-1 rounded border-2 border-white/10 bg-white/5 hover:bg-white/10" @click="restart()">↻ restart</button>
        <button
          v-for="p in [5, 30, 100]" :key="p" class="px-2 py-1 rounded font-mono transition-all"
          :style="{ border: `2px solid ${perp === p ? '#2dd4bf' : 'rgba(255,255,255,0.08)'}`, background: perp === p ? 'rgba(45,212,191,0.15)' : 'rgba(255,255,255,0.03)' }"
          @click="setPerp(p)"
        >
          perp {{ p }}
        </button>
      </div>
      <div class="text-xs opacity-70">Same algorithm in Python ends at KL {{ tl.kl }}; sklearn's exact t-SNE on these points: {{ tl.klSk }}.</div>
    </div>
  </div>
</template>
