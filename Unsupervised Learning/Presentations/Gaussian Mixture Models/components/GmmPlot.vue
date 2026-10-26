<script setup lang="ts">
// General 2D Gaussian-mixture view used by most slides.
//   pts       data points
//   mix       mixture parameters {w, mu, cov}; changes are tweened, so ellipses glide to new values (ms = 0: no tween,
//             for parents that animate the parameters themselves every frame)
//   colorMix  parameters used to color the points (default: the drawn, tweened mix). Passing it separately
//             lets EM show the M-step (ellipses move) and the E-step (points recolor) as two moves.
//   mode      soft: blend component colors by responsibility · hard: color of the largest responsibility
//             lab: color from `lab` · gray: no color (what we actually observe)
//   levels    ellipse outlines at these Mahalanobis distances (1 and 2 by default)
//   field     shade the background by 'argmax' component or by mixture 'density'
// Colors use inline style: UnoCSS attributify rewrites fill / stroke attributes.
import { computed } from 'vue'
import type { Domain } from '../utils/clusters'
import { color, domainOf, equalScale, useTween } from '../utils/clusters'
import type { Mix } from '../utils/gmm'
import { blend, ellipsePath, mixPdf, resp } from '../utils/gmm'

const props = withDefaults(defineProps<{
  pts: number[][]
  mix?: Mix | null
  colorMix?: Mix | null
  mode?: 'soft' | 'hard' | 'lab' | 'gray'
  lab?: number[] | null
  levels?: number[]
  means?: boolean
  field?: 'none' | 'argmax' | 'density'
  domain?: Domain
  w?: number
  h?: number
  r?: number
  equal?: boolean
  frame?: boolean
  focus?: number[] | null
  ms?: number
  fieldRes?: number
  label?: string
}>(), { mix: null, colorMix: null, mode: 'soft', lab: null, levels: () => [1, 2], means: true, field: 'none', w: 520, h: 400, r: 3, equal: true, frame: false, focus: null, ms: 650, fieldRes: 70 })

const dom = computed(() => props.domain ?? domainOf(props.pts, 0.08))
const S = computed(() => equalScale(dom.value, props.w, props.h, props.equal))

// Tween the parameters as one nested array [w, mu, cov] whenever the number of components stays the same.
const flat = useTween(() => (props.mix ? [props.mix.w, props.mix.mu, props.mix.cov] : []) as any, props.ms)
const M = computed<Mix | null>(() => {
  const f = flat.value as any
  if (!props.mix) return null
  if (props.ms <= 0 || !f.length || f[0].length !== props.mix.w.length) return props.mix
  return { w: f[0], mu: f[1], cov: f[2] }
})

const R = computed(() => {
  const m = props.colorMix ?? M.value
  if (!m || props.mode === 'gray' || props.mode === 'lab') return null
  return props.pts.map(p => resp(p, m))
})
const fills = computed(() => props.pts.map((_, i) => {
  if (props.mode === 'gray') return '#94a3b8'
  if (props.mode === 'lab') return color(props.lab?.[i])
  const g = R.value?.[i]
  if (!g) return '#94a3b8'
  return props.mode === 'soft' ? blend(g) : color(g.indexOf(Math.max(...g)))
}))
const focusSet = computed(() => (props.focus ? new Set(props.focus) : null))

const ellipses = computed(() => {
  const m = M.value
  if (!m) return []
  const { sx, sy } = S.value
  return m.mu.flatMap((mu, k) => props.levels.map((s, j) => ({ k, d: ellipsePath(mu, m.cov[k], s, sx, sy), outer: j > 0 })))
})

const cells = computed(() => {
  const m = M.value
  if (!m || props.field === 'none') return []
  const v = S.value.vis
  const nx = props.fieldRes; const ny = Math.round(nx * props.h / props.w)
  const dx = (v.x[1] - v.x[0]) / nx; const dy = (v.y[1] - v.y[0]) / ny
  const out: { x: number, y: number, c: string, o: number }[] = []
  let top = 0
  const vals: number[] = []
  for (let j = 0; j < ny; j++) {
    for (let i = 0; i < nx; i++) {
      const p = [v.x[0] + (i + 0.5) * dx, v.y[0] + (j + 0.5) * dy]
      if (props.field === 'density') {
        const d = mixPdf(p, m)
        vals.push(d); top = Math.max(top, d)
        out.push({ x: i, y: j, c: '#2dd4bf', o: 0 })
      }
      else {
        const g = resp(p, m)
        const k = g.indexOf(Math.max(...g))
        out.push({ x: i, y: j, c: color(k), o: 0.06 + 0.16 * (2 * g[k] - 1) ** 4 })
      }
    }
  }
  if (props.field === 'density') out.forEach((c, i) => { c.o = 0.55 * Math.sqrt(vals[i] / top) })
  const cw = props.w / nx; const ch = props.h / ny
  return out.map(c => ({ ...c, x: c.x * cw, y: props.h - (c.y + 1) * ch, cw: cw + 0.5, ch: ch + 0.5 }))
})
</script>

<template>
  <svg :viewBox="`0 0 ${w} ${h}`" class="w-full" role="img" :aria-label="label ?? 'Scatter plot with Gaussian components drawn as ellipses'">
    <rect v-if="frame" x="1" y="1" :width="w - 2" :height="h - 2" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)', stroke: 'rgba(255,255,255,0.08)' }" />
    <g v-if="cells.length">
      <rect v-for="(c, i) in cells" :key="`f${i}`" :x="c.x" :y="c.y" :width="c.cw" :height="c.ch" :style="{ fill: c.c, fillOpacity: c.o }" />
    </g>
    <g>
      <circle
        v-for="(p, i) in pts" :key="i" :cx="S.sx(p[0])" :cy="S.sy(p[1])" :r="r"
        :class="{ pt: !!colorMix || mode !== 'soft' || !mix }"
        :style="{ fill: fills[i], fillOpacity: focusSet && !focusSet.has(i) ? 0.18 : 0.88, stroke: focusSet?.has(i) ? '#fff' : 'none', strokeWidth: 1.4 }"
      />
    </g>
    <g v-if="M">
      <path
        v-for="(e, i) in ellipses" :key="`e${i}`" :d="e.d"
        :style="{ fill: e.outer ? 'none' : color(e.k), fillOpacity: 0.07, stroke: color(e.k), strokeWidth: e.outer ? 1.4 : 2.4, strokeDasharray: e.outer ? '5 4' : 'none', strokeOpacity: 0.95 }"
      />
      <g v-if="means">
        <g v-for="(mu, k) in M.mu" :key="`m${k}`" :transform="`translate(${S.sx(mu[0]).toFixed(1)},${S.sy(mu[1]).toFixed(1)})`">
          <circle r="7" :style="{ fill: color(k), stroke: '#0b1020', strokeWidth: 2.2 }" />
          <path d="M-3.2,0H3.2M0,-3.2V3.2" :style="{ stroke: '#0b1020', strokeWidth: 2 }" />
        </g>
      </g>
    </g>
    <slot :sx="S.sx" :sy="S.sy" :mix="M" />
  </svg>
</template>

<style scoped>
.pt { transition: fill 0.45s ease, fill-opacity 0.4s ease; }
</style>
