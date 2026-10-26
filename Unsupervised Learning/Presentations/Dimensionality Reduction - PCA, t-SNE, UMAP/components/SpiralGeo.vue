<script setup lang="ts">
// Straight-line distance vs distance along the manifold, on a spiral (a 1D curve in 2D, see spiral() in utils).
// Click any point to make it the source; the slider sets a radius. Inside the circle: teal = genuinely nearby
// along the curve, red = only nearby through empty space (another arm). Points are shaded by their distance
// along the curve from the source. The dashed chord is the closest point on another arm.
import { computed, ref } from 'vue'
import { ramp, spiral, toLocal } from '../utils/plot'

const S = spiral()
const W = 330; const H = 320; const U = 68
const sx = (x: number) => W / 2 + x * U
const sy = (y: number) => H / 2 - y * U
const src = ref(150)
const rad = ref(0.45)
const eu = (i: number, j: number) => Math.hypot(S.pts[i][0] - S.pts[j][0], S.pts[i][1] - S.pts[j][1])
const geo = (i: number, j: number) => Math.abs(S.s[i] - S.s[j])
const inside = computed(() => S.pts.map((_, j) => j !== src.value && eu(src.value, j) <= rad.value))
const wrong = (j: number) => geo(src.value, j) > 2.5 * eu(src.value, j) + 0.3 // reached only through empty space
const nIn = computed(() => inside.value.filter(Boolean).length)
const nBad = computed(() => inside.value.filter((v, j) => v && wrong(j)).length)
const chord = computed(() => { // nearest point on another arm
  let best = -1; let bd = Infinity
  S.pts.forEach((_, j) => {
    if (wrong(j) && eu(src.value, j) < bd) { bd = eu(src.value, j); best = j }
  })
  return best
})
function pick(e: PointerEvent) {
  const [x, y] = toLocal(e, e.currentTarget as Element, W, H)
  let best = 0; let bd = Infinity
  S.pts.forEach((p, j) => {
    const dd = (sx(p[0]) - x) ** 2 + (sy(p[1]) - y) ** 2
    if (dd < bd) { bd = dd; best = j }
  })
  src.value = best
}
</script>

<template>
  <div class="grid grid-cols-[1.1fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full select-none" style="max-height: 330px; cursor: pointer" role="img" aria-label="A spiral of points; a circle around one point also captures points on the neighboring arm" @pointerdown="pick">
      <circle :cx="sx(S.pts[src][0])" :cy="sy(S.pts[src][1])" :r="rad * U" :style="{ fill: 'rgba(251,191,36,0.08)', stroke: '#fbbf24', strokeWidth: 1.5, strokeDasharray: '4 3' }" />
      <circle
        v-for="(p, j) in S.pts" :key="j" :cx="sx(p[0])" :cy="sy(p[1])" :r="inside[j] ? 4.5 : 3"
        :style="{ fill: inside[j] ? (wrong(j) ? '#f87171' : '#2dd4bf') : ramp(1 - Math.min(1, geo(src, j) / 8)), fillOpacity: inside[j] ? 1 : 0.55, stroke: inside[j] ? '#0b1020' : 'none', strokeWidth: 1.2 }"
      />
      <line v-if="chord >= 0" :x1="sx(S.pts[src][0])" :y1="sy(S.pts[src][1])" :x2="sx(S.pts[chord][0])" :y2="sy(S.pts[chord][1])" :style="{ stroke: '#f87171', strokeWidth: 2, strokeDasharray: '5 4' }" />
      <circle :cx="sx(S.pts[src][0])" :cy="sy(S.pts[src][1])" r="7" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2 }" />
    </svg>
    <div class="text-left space-y-3">
      <div class="flex items-center gap-3 text-sm font-mono">
        <span class="w-24">radius {{ rad.toFixed(2) }}</span>
        <input v-model.number="rad" type="range" min="0.1" max="1.2" step="0.01" class="flex-1" style="accent-color: #fbbf24">
      </div>
      <div border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3 class="font-mono text-sm space-y-1">
        <div>inside the circle: {{ nIn }}</div>
        <div class="text-teal-300">nearby along the curve: {{ nIn - nBad }}</div>
        <div class="text-red-300">other arm (a shortcut): {{ nBad }}</div>
      </div>
      <div v-if="chord >= 0" class="font-mono text-sm">
        nearest other-arm point:<br>
        straight line <span class="text-red-300">{{ eu(src, chord).toFixed(2) }}</span> · along the curve <span class="text-teal-300">{{ geo(src, chord).toFixed(2) }}</span>
      </div>
      <div class="text-xs opacity-60">Click any point to move the source.</div>
    </div>
  </div>
</template>
