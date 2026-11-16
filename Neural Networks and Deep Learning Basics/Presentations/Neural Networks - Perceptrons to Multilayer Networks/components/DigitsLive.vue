<script setup lang="ts">
// Multiclass classification, trained live: reading handwritten digits.
// Data: 1,797 real 8×8 digit scans (UCI optdigits), split 1,500 train / 297 test (scripts/make_data.py).
// Network: 64 pixels → 32 ReLU → 10 softmax, trained on mini-batches of 32 with cross-entropy.
// Left: 24 test digits with the network's current guess (teal = right, red = wrong).
// Right: test accuracy over training, and the softmax probabilities for one highlighted digit (cycles).
// Print mode shows the network after training.
import { computed, reactive, shallowRef } from 'vue'
import d from '../data/digits.json'
import { batchOf, MLP } from '../utils/mlp'
import { C, pathOf, rng, useActive, useLoop } from '../utils/plot'
import { decode } from '../utils/rng'

const prep = (s: string) => decode(s).map(v => v / 16)
const Xtr = d.train.img.map(prep)
const Ytr = d.train.y.map(y => Array.from({ length: 10 }, (_, k) => +(k === y)))
const Xte = d.test.img.map(prep); const yte = d.test.y
const SHOW = Array.from({ length: 24 }, (_, i) => i)
const STEPS = 400; const EVAL_EVERY = 5

let net: MLP; let R = rng(9)
const st = reactive({ step: 0, acc: 0, hist: [] as number[][], pred: [] as number[], pause: 0, focus: 0, focusT: 0 })
const probs = shallowRef<number[]>([])
const argmax = (p: number[]) => p.indexOf(Math.max(...p))
function evaluate() {
  let c = 0
  for (let i = 0; i < Xte.length; i++) c += +(argmax(net.predict(Xte[i])) === yte[i])
  st.acc = c / Xte.length
  st.hist.push([st.step, st.acc])
  st.pred = SHOW.map(i => argmax(net.predict(Xte[i])))
  probs.value = net.predict(Xte[SHOW[st.focus]])
}
function reset() {
  net = new MLP([64, 32, 10], 'relu', 'softmax', 1); R = rng(9)
  st.step = 0; st.hist = []; st.pause = 0.8
  evaluate()
}
function train(k: number) {
  for (let i = 0; i < k; i++) {
    const idx = batchOf(Xtr.length, 32, R)
    net.step(idx.map(j => Xtr[j]), idx.map(j => Ytr[j]), 0.003)
    st.step++
    if (st.step % EVAL_EVERY === 0) evaluate()
  }
}
reset()
const { isPrintMode } = useActive()
if (isPrintMode.value) { st.focus = 3; train(STEPS); evaluate() }
useLoop((dt) => {
  st.focusT += dt
  if (st.focusT > 1.6) { st.focusT = 0; st.focus = (st.focus + 1) % SHOW.length; probs.value = net.predict(Xte[SHOW[st.focus]]) }
  if (st.pause > 0) { st.pause -= dt; if (st.pause <= 0 && st.step >= STEPS) reset(); return }
  train(1)
  if (st.step >= STEPS) st.pause = 5
}, reset)

// digit thumbnails: each 8×8 image becomes one PNG data URL, built once (one <image> per digit keeps re-renders cheap)
const PX = 6; const CELL = 8 * PX + 14
function toUrl(v: number[]) {
  const cv = document.createElement('canvas'); cv.width = 8; cv.height = 8
  const ctx = cv.getContext('2d')!; const im = ctx.createImageData(8, 8)
  v.forEach((p, k) => { const g = Math.round(255 * p / 16); im.data.set([g, g, Math.min(255, g + 12), 255], 4 * k) })
  ctx.putImageData(im, 0, 0)
  return cv.toDataURL()
}
const thumbs = SHOW.map(i => toUrl(decode(d.test.img[i])))
// accuracy chart
const AW = 300; const AH = 130
const ax = (s: number) => 34 + s / STEPS * (AW - 44)
const ay = (a: number) => AH - 22 - a * (AH - 34)
const accPath = computed(() => pathOf(st.hist.map(h => [ax(h[0]), ay(h[1])])))
// probability bars
const BW = 300; const BH = 120
const bx = (k: number) => 10 + k * ((BW - 20) / 10)
</script>

<template>
  <div class="grid grid-cols-[1.15fr_1fr] gap-6 items-start text-left">
    <svg :viewBox="`0 0 ${6 * CELL} ${4 * (CELL + 18)}`" class="w-full" style="max-height: 340px" role="img" aria-label="Twenty-four handwritten test digits with the network's current prediction under each">
      <g v-for="(img, n) in thumbs" :key="n" :transform="`translate(${(n % 6) * CELL + 7}, ${Math.floor(n / 6) * (CELL + 18) + 4})`">
        <rect x="-4" y="-4" :width="8 * PX + 8" :height="8 * PX + 8" rx="5" :style="{ fill: 'none', stroke: n === st.focus ? C.amber : (st.pred[n] === yte[n] ? C.teal : C.red), strokeWidth: n === st.focus ? 2.5 : 1.2, strokeOpacity: n === st.focus ? 1 : 0.6 }" />
        <image :href="img" x="0" y="0" :width="8 * PX" :height="8 * PX" style="image-rendering: pixelated" />
        <text :x="4 * PX" :y="8 * PX + 20" text-anchor="middle" :style="{ fill: st.pred[n] === yte[n] ? C.teal : C.red, fontSize: '15px', fontWeight: 700, fontFamily: 'monospace' }">{{ st.pred[n] }}</text>
      </g>
    </svg>
    <div>
      <div class="flex justify-between items-baseline">
        <span class="opacity-80">test accuracy</span>
        <span class="font-mono text-3xl text-teal-300">{{ (100 * st.acc).toFixed(1) }}%</span>
      </div>
      <svg :viewBox="`0 0 ${AW} ${AH}`" class="w-full" role="img" aria-label="Test accuracy rising during training">
        <line v-for="a in [0, 0.5, 1]" :key="a" x1="34" :x2="AW - 10" :y1="ay(a)" :y2="ay(a)" :style="{ stroke: C.grid, strokeDasharray: a ? '3 4' : '' }" />
        <text v-for="a in [0, 0.5, 1]" :key="`t${a}`" x="28" :y="ay(a) + 4" text-anchor="end" :style="{ fill: C.muted, fontSize: '10px' }">{{ a * 100 }}%</text>
        <path :d="accPath" :style="{ fill: 'none', stroke: C.teal, strokeWidth: 2.5 }" />
        <text :x="AW - 10" :y="AH - 6" text-anchor="end" :style="{ fill: C.muted, fontSize: '11px' }">training step {{ st.step }}</text>
      </svg>
      <div class="text-sm opacity-80 mt-2">softmax output for the <span class="text-amber-300">highlighted</span> digit</div>
      <svg :viewBox="`0 0 ${BW} ${BH}`" class="w-full" role="img" aria-label="Probability the network assigns to each digit 0 to 9">
        <rect v-for="(p, k) in probs" :key="k" :x="bx(k) + 3" :y="BH - 22 - p * (BH - 34)" :width="(BW - 20) / 10 - 6" :height="Math.max(1, p * (BH - 34))" :style="{ fill: k === yte[SHOW[st.focus]] ? C.teal : C.dim, transition: 'all 0.3s' }" />
        <text v-for="k in 10" :key="`l${k}`" :x="bx(k - 1) + (BW - 20) / 20" :y="BH - 6" text-anchor="middle" :style="{ fill: k - 1 === yte[SHOW[st.focus]] ? C.teal : C.muted, fontSize: '13px', fontFamily: 'monospace' }">{{ k - 1 }}</text>
      </svg>
    </div>
  </div>
</template>
