<script setup lang="ts">
// Universal approximation, by construction. A network with one hidden layer of n ReLU units computes
//   ŷ(x) = c + Σₖ aₖ · ReLU(x − xₖ)
// i.e. a sum of "hinges". Each hinge adds one bend, so n units make a curve with n bends.
// Here the hinge positions are evenly spaced and the aₖ are chosen to pass through the target at each hinge
// (a hand-built network, not a trained one). Steps 0-4: n = 1, 2, 4, 8, 20.
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
const terms = computed(() => { const h = hinges(n.value); return h.a.map((ak, k) => ({ ak, P: XS.map(x => ak * Math.max(0, x - h.xk[k])) , xk: h.xk[k] })) })
const maxErr = computed(() => Math.max(...XS.map((x, i) => Math.abs(approx(n.value)[i] - g(x)))))

const W = 640; const HT = 210; const HB = 110
const sx = (x: number) => 40 + x * (W - 60)
const syT = (y: number) => HT - 14 - y * (HT - 30)
const tMax = computed(() => Math.max(0.5, ...terms.value.flatMap(t => t.P.map(Math.abs))))
const syB = (y: number) => HT + HB / 2 + 6 - y / tMax.value * (HB / 2 - 8)
const target = pathOf(XS.map(x => [sx(x), syT(g(x))]))
</script>

<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${HT + HB + 14}`" class="w-full" style="max-height: 340px" role="img" :aria-label="`A curve approximated by the sum of ${n} ReLU units`">
      <!-- top: target and the network's output -->
      <path :d="target" :style="{ fill: 'none', stroke: C.muted, strokeWidth: 2, strokeDasharray: '6 5' }" />
      <path :d="pathOf(XS.map((x, i) => [sx(x), syT(yHat[i])]))" :style="{ fill: 'none', stroke: C.amber, strokeWidth: 3 }" />
      <circle v-for="t in terms" :key="`k${t.xk}`" :cx="sx(t.xk)" :cy="syT(g(t.xk))" r="3.5" :style="{ fill: C.amber }" />
      <text x="44" y="16" :style="{ fill: C.amber, fontSize: '14px' }">network output ŷ(x)</text>
      <text x="210" y="16" :style="{ fill: C.muted, fontSize: '14px' }">- - target</text>
      <!-- bottom: the individual hinge terms -->
      <line :x1="sx(0)" :x2="sx(1)" :y1="syB(0)" :y2="syB(0)" :style="{ stroke: C.grid }" />
      <line v-for="t in terms" :key="`h${t.xk}`" :x1="sx(t.xk)" :x2="sx(t.xk)" :y1="syB(0) - 5" :y2="syB(0) + 5" :style="{ stroke: C.amber, strokeWidth: 2 }" />
      <path v-for="(t, k) in terms" :key="k" :d="pathOf(XS.map((x, i) => [sx(x), syB(t.P[i])]))" :style="{ fill: 'none', stroke: t.ak >= 0 ? C.teal : C.violet, strokeWidth: 1.6, strokeOpacity: 0.75 }" />
      <text x="44" :y="HT + 12" :style="{ fill: C.muted, fontSize: '12px' }">each hidden unit: aₖ · ReLU(x − xₖ)</text>
    </svg>
    <div class="flex justify-center gap-10 font-mono text-lg mt-1">
      <span>hidden units: <span class="text-teal-300">{{ n }}</span></span>
      <span>worst error: <span class="text-amber-300">{{ maxErr.toFixed(3) }}</span></span>
    </div>
  </div>
</template>
