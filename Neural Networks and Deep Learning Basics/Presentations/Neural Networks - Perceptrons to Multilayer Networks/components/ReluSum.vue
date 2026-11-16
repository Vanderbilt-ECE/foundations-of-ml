<script setup lang="ts">
// Universal approximation, by construction. A network with one hidden layer of n ReLU units computes
//   ŷ(x) = c + Σₖ aₖ · ReLU(x − xₖ)
// i.e. a sum of "hinges". Each hinge adds one bend, so n units make a curve with n bends.
// Here the hinge positions are evenly spaced and the aₖ are chosen to pass through the target at each hinge
// (a hand-built network, not a trained one). Steps 0-4: n = 1, 2, 4, 8, 20.
// Each dot marks one hidden unit's hinge: the point where it switches on and the output's slope changes.
// (The individual hinge terms aren't drawn: they're unbounded ramps whose sizes are slope *changes*,
// so plotted separately they don't visibly add up to the curve.)
import { computed } from 'vue'
import { C, pathOf, useTween } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const NS = [1, 2, 4, 8, 20]
const n = computed(() => NS[Math.max(0, Math.min(NS.length - 1, props.step))])

const g = (x: number) => 0.5 + 0.28 * Math.sin(2 * Math.PI * 1.25 * x + 0.3) + 0.12 * Math.cos(9 * x)
const XS = Array.from({ length: 201 }, (_, i) => i / 200)

function hinges(n: number) {
  const xk = Array.from({ length: n + 1 }, (_, k) => k / n)
  const yk = xk.map(g)
  const slope = Array.from({ length: n }, (_, k) => (yk[k + 1] - yk[k]) * n)
  const a = slope.map((s, k) => (k ? s - slope[k - 1] : s))
  return { c: yk[0], xk: xk.slice(0, n), a }
}
const approx = (n: number) => { const h = hinges(n); return XS.map(x => h.c + h.a.reduce((s, ak, k) => s + ak * Math.max(0, x - h.xk[k]), 0)) }
const yHat = useTween(() => approx(n.value), 900)
const knots = computed(() => hinges(n.value).xk)
const maxErr = computed(() => Math.max(...XS.map((x, i) => Math.abs(approx(n.value)[i] - g(x)))))

const W = 640; const H = 270
const sx = (x: number) => 40 + x * (W - 60)
const syT = (y: number) => H - 14 - y * (H - 44)
const target = pathOf(XS.map(x => [sx(x), syT(g(x))]))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 340px" role="img" :aria-label="`A curve approximated by the sum of ${n} ReLU units; each dot is one unit's bend`">
      <!-- target and the network's output -->
      <path :d="target" :style="{ fill: 'none', stroke: C.muted, strokeWidth: 2, strokeDasharray: '6 5' }" />
      <path :d="pathOf(XS.map((x, i) => [sx(x), syT(yHat[i])]))" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 3 }" />
      <circle v-for="xk in knots" :key="`k${xk}`" :cx="sx(xk)" :cy="syT(g(xk))" r="4.5" :style="{ fill: C.amber }" />
      <!-- legend -->
      <text x="44" y="16" :style="{ fill: C.amber, fontSize: '14px' }">network output ŷ(x)</text>
      <text x="210" y="16" :style="{ fill: C.muted, fontSize: '14px' }">- - target</text>
      <circle cx="312" cy="11" r="4.5" :style="{ fill: C.amber }" />
      <text x="322" y="16" :style="{ fill: C.text, fontSize: '14px' }">one hidden unit: the slope changes here</text>
    </svg>
    <div class="flex justify-center gap-10 font-mono text-lg mt-1">
      <span>hidden units: <span class="text-teal-300">{{ n }}</span></span>
      <span>worst error: <span class="text-amber-300">{{ maxErr.toFixed(3) }}</span></span>
    </div>
  </div>
</template>
