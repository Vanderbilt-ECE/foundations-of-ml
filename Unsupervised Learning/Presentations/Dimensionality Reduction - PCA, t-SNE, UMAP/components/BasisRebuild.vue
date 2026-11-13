<script setup lang="ts">
// One point, two bases. Same 48 centered points and eigenvectors as EigenProject (data/drag.json, same sign convention).
// step 0: x = x₁e₁ + x₂e₂, walked along the standard axes (gray legs)
// step 1: x = z₁q₁ + z₂q₂, walked along the principal axes (amber, then violet); same endpoint, new coordinates
// step 2: keep only z₁: x̂ = z₁q₁, and the dropped z₂q₂ leg turns red, the reconstruction error
// Click any point to decompose it instead. The PDF export shows step 2.
import { computed, ref } from 'vue'
import d from '../data/drag.json'
import { useActive } from '../utils/plot'

const props = withDefaults(defineProps<{ step?: number }>(), { step: 0 })
const { isPrintMode } = useActive()
const s = computed(() => (isPrintMode.value ? 2 : props.step))

const W = 460; const H = 370; const U = 64
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U

const q1 = d.v1
const q2 = [-q1[1], q1[0]]
const sel = ref(22)
const x = computed(() => d.pts[sel.value])
const z1 = computed(() => x.value[0] * q1[0] + x.value[1] * q1[1])
const z2 = computed(() => x.value[0] * q2[0] + x.value[1] * q2[1])
const a = computed(() => [z1.value * q1[0], z1.value * q1[1]]) // z₁q₁, also the k = 1 reconstruction x̂
const err = computed(() => Math.hypot(x.value[0] - a.value[0], x.value[1] - a.value[1]))

const f = (v: number) => (v < 0 ? '−' : '') + Math.abs(v).toFixed(2)
const t = (v: number) => (v < 0 ? ' − ' : ' + ') + Math.abs(v).toFixed(2) // a signed term after the first
const vec = (v: number[]) => `(${f(v[0])}, ${f(v[1])})`
const AMBER = '#fbbf24'; const VIOLET = '#a78bfa'; const RED = '#f87171'; const SLATE = '#94a3b8'
// A leg from p to r in screen space. The line stops HEAD px short of where the tip should be, and the tip itself
// stops `gap` px short of r (outside the dot drawn there). The arrowhead is then drawn from the line's end.
// A leg too short to fit a head gets none (hasHead false).
const HEAD = 9
function leg(p: number[], r: number[], gap = 0) {
  const a = [sx(p[0]), sy(p[1])]; const b = [sx(r[0]), sy(r[1])]
  const L = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1
  const hasHead = L > gap + HEAD + 4
  const end = hasHead ? L - gap - HEAD : L
  const u = [(b[0] - a[0]) / L, (b[1] - a[1]) / L]
  return { x1: a[0], y1: a[1], x2: a[0] + u[0] * end, y2: a[1] + u[1] * end, hasHead }
}
const gx = computed(() => leg([0, 0], [x.value[0], 0], 2))
const gy = computed(() => leg([x.value[0], 0], x.value, 9))
const la = computed(() => leg([0, 0], a.value, 7))
const lb = computed(() => leg(a.value, x.value, 9))
const e1 = leg([0, 0], [1, 0]); const e2 = leg([0, 0], [0, 1])
const u1 = leg([0, 0], q1); const u2 = leg([0, 0], q2)
const mk = (l: { hasHead: boolean }, id: string) => (l.hasHead ? `url(#br-${id})` : undefined)
// z₁q₁ label: beside the middle of the amber leg, on the side away from x so it never sits on either leg
const lab1 = computed(() => {
  const n = [-q1[1], q1[0]]
  const side = n[0] * x.value[0] + n[1] * x.value[1] > 0 ? -1 : 1
  return [sx(a.value[0] / 2 + side * 0.32 * n[0]), sy(a.value[1] / 2 + side * 0.32 * n[1])]
})
// a label a little off the middle of a leg, on the side away from the origin
function mid(p: number[], r: number[], off = 0.32) {
  const m = [(p[0] + r[0]) / 2, (p[1] + r[1]) / 2]
  const n = Math.hypot(m[0], m[1]) || 1
  return [sx(m[0] + off * m[0] / n), sy(m[1] + off * m[1] / n)]
}
</script>

<template>
  <div class="grid grid-cols-[1.3fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="max-height: 340px" role="img" aria-label="One data point written as a combination of the standard basis vectors, then as a combination of the two eigenvectors, then rebuilt from the first eigenvector alone">
      <defs>
        <marker v-for="c in [['g', SLATE], ['w', '#e2e8f0'], ['a', AMBER], ['v', VIOLET], ['r', RED]]" :id="`br-${c[0]}`" :key="c[0]" viewBox="0 0 9 8" refX="0" refY="4" markerWidth="9" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto">
          <path d="M0,0 L9,4 L0,8 Z" :style="{ fill: c[1] }" />
        </marker>
      </defs>

      <!-- standard axes, and the principal axes through the (zero) mean -->
      <line :x1="0" :x2="W" :y1="sy(0)" :y2="sy(0)" :style="{ stroke: '#475569', strokeOpacity: 0.6 }" />
      <line :x1="sx(0)" :x2="sx(0)" :y1="0" :y2="H" :style="{ stroke: '#475569', strokeOpacity: 0.6 }" />
      <g :style="{ opacity: s >= 1 ? 1 : 0, transition: 'opacity 0.5s' }">
        <line v-for="(q, k) in [q1, q2]" :key="`ax${k}`" :x1="sx(-8 * q[0])" :y1="sy(-8 * q[1])" :x2="sx(8 * q[0])" :y2="sy(8 * q[1])" :style="{ stroke: k ? VIOLET : AMBER, strokeOpacity: 0.3, strokeWidth: 1.2 }" />
      </g>

      <!-- the data; click one to decompose it -->
      <circle
        v-for="(p, i) in d.pts" :key="`p${i}`" :cx="sx(p[0])" :cy="sy(p[1])" :r="i === sel ? 0 : 3.8"
        :style="{ fill: '#e2e8f0', fillOpacity: 0.45, stroke: '#0b1020', strokeWidth: 1, cursor: 'pointer' }" @click="sel = i"
      />

      <!-- step 0: standard basis legs x₁e₁ then x₂e₂ (stay faint afterwards for comparison) -->
      <g :style="{ opacity: s === 0 ? 1 : 0.28, transition: 'opacity 0.5s' }">
        <line v-bind="gx" :marker-end="mk(gx, 'g')" :style="{ stroke: SLATE, strokeWidth: 3, strokeDasharray: '6 4' }" />
        <line v-bind="gy" :marker-end="mk(gy, 'g')" :style="{ stroke: SLATE, strokeWidth: 3, strokeDasharray: '6 4' }" />
        <g :style="{ opacity: s === 0 ? 1 : 0, transition: 'opacity 0.5s' }">
          <text :x="sx(x[0] / 2)" :y="sy(0) + (x[1] >= 0 ? 20 : -10)" text-anchor="middle" :style="{ fill: SLATE, fontSize: '15px', fontWeight: 700 }">x₁e₁</text>
          <text :x="sx(x[0]) + (x[0] >= 0 ? 8 : -8)" :y="sy(x[1] / 2) + 5" :text-anchor="x[0] >= 0 ? 'start' : 'end'" :style="{ fill: SLATE, fontSize: '15px', fontWeight: 700 }">x₂e₂</text>
        </g>
      </g>

      <!-- step 1+: eigenbasis legs z₁q₁ then z₂q₂ -->
      <g :style="{ opacity: s >= 1 ? 1 : 0, transition: 'opacity 0.5s' }">
        <line v-bind="la" :marker-end="mk(la, 'a')" :style="{ stroke: AMBER, strokeWidth: 3.5 }" />
        <line
          v-bind="lb" :marker-end="mk(lb, s >= 2 ? 'r' : 'v')"
          :style="{ stroke: s >= 2 ? RED : VIOLET, strokeWidth: 3.5, strokeDasharray: s >= 2 ? '5 4' : 'none', transition: 'stroke 0.5s' }"
        />
        <text :x="lab1[0]" :y="lab1[1] + 5" text-anchor="middle" :style="{ fill: AMBER, fontSize: '15px', fontWeight: 700 }">z₁q₁</text>
        <text :x="mid(a, x, 0.45)[0]" :y="mid(a, x, 0.45)[1] + 5" text-anchor="middle" :style="{ fill: s >= 2 ? RED : VIOLET, fontSize: '15px', fontWeight: 700, transition: 'fill 0.5s' }">{{ s >= 2 ? 'error' : 'z₂q₂' }}</text>
      </g>

      <!-- unit basis vectors at the origin: e₁, e₂ (step 0) or q₁, q₂ (step 1+) -->
      <g :style="{ opacity: s === 0 ? 1 : 0, transition: 'opacity 0.5s' }">
        <line v-bind="e1" marker-end="url(#br-w)" :style="{ stroke: '#e2e8f0', strokeWidth: 2.5 }" />
        <line v-bind="e2" marker-end="url(#br-w)" :style="{ stroke: '#e2e8f0', strokeWidth: 2.5 }" />
        <text :x="sx(1) - 4" :y="sy(0) - 8" text-anchor="end" :style="{ fill: '#e2e8f0', fontSize: '13px' }">e₁</text>
        <text :x="sx(0) - 8" :y="sy(1) + 4" text-anchor="end" :style="{ fill: '#e2e8f0', fontSize: '13px' }">e₂</text>
      </g>
      <g :style="{ opacity: s >= 1 ? 1 : 0, transition: 'opacity 0.5s' }">
        <line v-for="(q, k) in [q1, q2]" :key="`u${k}`" v-bind="k ? u2 : u1" :marker-end="k ? 'url(#br-v)' : 'url(#br-a)'" :style="{ stroke: k ? VIOLET : AMBER, strokeWidth: 2.5 }" />
        <text :x="sx(-0.25 * q1[0])" :y="sy(-0.25 * q1[1]) + 16" text-anchor="middle" :style="{ fill: AMBER, fontSize: '13px' }">q₁</text>
        <text :x="sx(q2[0]) - 6" :y="sy(q2[1]) - 6" text-anchor="end" :style="{ fill: VIOLET, fontSize: '13px' }">q₂</text>
      </g>

      <!-- origin, the reconstruction x̂ (step 2), and the chosen point x -->
      <circle :cx="sx(0)" :cy="sy(0)" r="3" :style="{ fill: '#0b1020', stroke: '#e2e8f0', strokeWidth: 1.5 }" />
      <circle :cx="sx(a[0])" :cy="sy(a[1])" r="6" :style="{ fill: '#0b1020', stroke: AMBER, strokeWidth: 2.5, opacity: s >= 2 ? 1 : 0, transition: 'opacity 0.5s' }" />
      <text :x="sx(a[0])" :y="sy(a[1]) - 14" text-anchor="middle" :style="{ fill: AMBER, fontSize: '15px', fontWeight: 700, opacity: s >= 2 ? 1 : 0, transition: 'opacity 0.5s' }">x̂</text>
      <circle :cx="sx(x[0])" :cy="sy(x[1])" r="6.5" :style="{ fill: '#2dd4bf', stroke: '#0b1020', strokeWidth: 1.5 }" />
      <text :x="sx(x[0]) + (x[0] >= 0 ? 12 : -12)" :y="sy(x[1]) + 6" :text-anchor="x[0] >= 0 ? 'start' : 'end'" :style="{ fill: '#2dd4bf', fontSize: '16px', fontWeight: 700 }">x</text>
    </svg>

    <div class="text-left space-y-3 text-sm">
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-2>
        <b class="text-slate-300">Standard basis</b>
        <div class="font-mono mt-1">x = {{ f(x[0]) }}·e₁{{ t(x[1]) }}·e₂</div>
        <div class="opacity-70 text-xs mt-1">Its coordinates are the raw feature values.</div>
      </div>

      <div class="reveal" :class="{ shown: s >= 1 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-2>
        <b class="text-amber-300">Eigenbasis: same point, new coordinates</b>
        <div class="font-mono mt-1 text-xs space-y-0.5">
          <div><span class="text-amber-300">z₁ = q₁ᵀx = {{ f(z1) }}</span> · <span class="text-violet-300">z₂ = q₂ᵀx = {{ f(z2) }}</span></div>
          <div class="text-sm pt-1">
            x = <span class="text-amber-300">{{ f(z1) }}·q₁</span><span class="text-violet-300">{{ t(z2) }}·q₂</span> = Qz
          </div>
        </div>
        <div class="opacity-70 text-xs mt-1">Dot products give the new coordinates (z = Qᵀx); the linear combination gives the point back exactly.</div>
      </div>

      <div class="reveal" :class="{ shown: s >= 2 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-4 py-2>
        <b class="text-red-300">Keep k = 1: drop z₂</b>
        <div class="font-mono mt-1">x̂ = <span class="text-amber-300">{{ f(z1) }}·q₁</span> = {{ vec(a) }}</div>
        <div class="opacity-70 text-xs mt-1">Error ‖x − x̂‖ = |z₂| = {{ f(err) }}: exactly the coordinate we threw away.</div>
      </div>

      <div class="text-xs opacity-60">Click any point to decompose it instead.</div>
    </div>
  </div>
</template>
