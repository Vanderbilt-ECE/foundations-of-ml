<script setup lang="ts">
// Binary classification, trained live. Is the machine running OK, from (standardized) temperature and pressure?
// The OK readings sit in a disc around nominal, so the boundary has to curve all the way round.
// Two models train side by side with a sigmoid output and binary cross-entropy:
//   no hidden layer (= logistic regression): can only draw a straight boundary
//   one hidden layer of 8 tanh units: bends the boundary into a closed curve
// Background color = the model's P(OK). Click to restart. Print mode shows both models fully trained.
import { onMounted, reactive, ref, watch } from 'vue'
import { MLP } from '../utils/mlp'
import { C, useActive, useLoop } from '../utils/plot'
import { ring } from '../utils/rng'

const D = ring()
const X = D.map(d => d.x); const Y = D.map(d => [d.y])
const STEPS = 1200; const PER_FRAME = 4
const MODELS = [
  { title: 'No hidden layer', sub: '2 → 1, sigmoid (logistic regression)', sizes: [2, 1], cls: 'text-violet-300' },
  { title: 'One hidden layer', sub: '2 → 8 → 1, tanh hidden, sigmoid out', sizes: [2, 8, 1], cls: 'text-teal-300' },
]
let nets: MLP[] = []
const st = reactive({ step: 0, acc: [0, 0], pause: 0, frame: 0 })
function reset() {
  nets = MODELS.map(m => new MLP(m.sizes, 'tanh', 'sigmoid', 3))
  st.step = 0; st.pause = 0.6; measure()
}
function measure() {
  st.acc = nets.map(n => X.reduce((a, x, i) => a + +((n.predict(x)[0] > 0.5) === (Y[i][0] === 1)), 0) / X.length)
  st.frame++
}
const train = (k: number) => { for (let i = 0; i < k; i++) for (const n of nets) n.step(X, Y, 0.02); st.step += k }
reset()
const { isPrintMode } = useActive()
if (isPrintMode.value) { train(STEPS); measure() }
useLoop((dt) => {
  if (st.pause > 0) { st.pause -= dt; if (st.pause <= 0 && st.step >= STEPS) reset(); return }
  train(PER_FRAME); measure()
  if (st.step >= STEPS) st.pause = 4
}, reset)

// ---- drawing ----
const S = 300; const G = 50; const R = 1.1
const canvases = ref<HTMLCanvasElement[]>([])
const toPx = (v: number) => (v + R) / (2 * R) * S
const rgb = (h: string) => [1, 3, 5].map(i => Number.parseInt(h.slice(i, i + 2), 16))
const TEAL = rgb(C.teal); const VIOLET = rgb(C.violet)
function draw() {
  canvases.value.forEach((cv, m) => {
    const ctx = cv?.getContext('2d'); if (!ctx || !nets[m]) return
    ctx.clearRect(0, 0, S, S)
    const cell = S / G
    for (let i = 0; i < G; i++) {
      for (let j = 0; j < G; j++) {
        const x = [-R + (i + 0.5) * 2 * R / G, R - (j + 0.5) * 2 * R / G]
        const p = nets[m].predict(x)[0]
        const c = p > 0.5 ? TEAL : VIOLET
        ctx.fillStyle = `rgba(${c[0]},${c[1]},${c[2]},${0.08 + 0.3 * Math.abs(p - 0.5) * 2})`
        ctx.fillRect(i * cell, j * cell, cell, cell) // S / G is a whole number of pixels, so cells tile without overlap
      }
    }
    for (const d of D) {
      const px = toPx(d.x[0]); const py = S - toPx(d.x[1])
      ctx.fillStyle = d.y ? C.teal : C.violet
      ctx.beginPath()
      if (d.y) ctx.arc(px, py, 3.6, 0, 2 * Math.PI)
      else ctx.rect(px - 3, py - 3, 6, 6)
      ctx.fill()
    }
  })
}
onMounted(draw)
watch(() => st.frame, draw)
</script>

<template>
  <div class="grid grid-cols-2 gap-8 text-left">
    <div v-for="(m, k) in MODELS" :key="k">
      <div class="flex justify-between items-baseline">
        <span class="font-bold" :class="m.cls">{{ m.title }}</span>
        <span class="font-mono">accuracy <span class="text-xl" :class="m.cls">{{ (100 * st.acc[k]).toFixed(0) }}%</span></span>
      </div>
      <div class="text-xs opacity-70 mb-1">{{ m.sub }}</div>
      <canvas
        :ref="(el: any) => { if (el) canvases[k] = el }" :width="S" :height="S"
        class="w-full rounded-lg cursor-pointer" style="max-height: 290px; max-width: 290px; border: 1px solid #334155"
        role="img" :aria-label="`${m.title}: predicted probability that the machine is OK, over temperature and pressure`"
        @click="reset"
      />
    </div>
  </div>
  <div class="flex justify-between text-sm opacity-75 mt-2">
    <span>x: temperature · y: pressure (standardized)</span>
    <span><span class="inline-block w-3 h-3 rounded-full bg-teal-400 align-middle" /> OK &nbsp; <span class="inline-block w-3 h-3 bg-violet-400 align-middle" /> fault &nbsp; · step {{ st.step }}</span>
  </div>
</template>
