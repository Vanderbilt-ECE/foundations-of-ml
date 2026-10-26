<script setup lang="ts">
// Canvas scatter for 2D embeddings (coordinates normalized to [-1, 1] by make_data.py), colored by digit class.
// Changing `pts` morphs every point from where it is to its new position. Optional:
//   hover  — show the digit under the pointer (needs `imgs`), and emit its index (for linked plots)
//   mark   — an index drawn with a ring (the point hovered in a linked plot)
//   focus  — a class drawn at full strength, the rest dimmed
//   labels — print each class's digit at the median of its points
//   cols   — one color per point, instead of coloring by class (e.g. position along the Swiss roll)
// Canvas rather than SVG: up to 1797 points re-drawn every animation frame.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { color, ease, toLocal } from '../utils/plot'

const props = withDefaults(defineProps<{
  pts: number[][]
  lab: number[]
  w?: number
  h?: number
  r?: number
  ms?: number
  alpha?: number
  hover?: boolean
  imgs?: string[]
  mark?: number | null
  focus?: number | null
  labels?: boolean
  cols?: string[]
  label?: string
}>(), { w: 420, h: 320, r: 2.2, ms: 1100, alpha: 0.85, hover: false, mark: null, focus: null, labels: false, label: 'Scatter plot of a 2D embedding, colored by class' })
const emit = defineEmits<{ hover: [i: number | null] }>()

const S = 3 // canvas pixels per CSS pixel: the slide is scaled up on projectors, keep it crisp
const PAD = 14
const cv = ref<HTMLCanvasElement>()
const tip = ref<{ i: number, x: number, y: number } | null>(null)
let cur = props.pts.map(p => [p[0], p[1]])
let raf = 0

const k = () => Math.min((props.w - 2 * PAD) / 2, (props.h - 2 * PAD) / 2)
const px = (x: number) => props.w / 2 + x * k()
const py = (y: number) => props.h / 2 - y * k()

function median(a: number[]) {
  const s = [...a].sort((x, y) => x - y)
  return s[Math.floor(s.length / 2)]
}

function draw() {
  const c = cv.value?.getContext('2d')
  if (!c) return
  c.setTransform(S, 0, 0, S, 0, 0)
  c.clearRect(0, 0, props.w, props.h)
  const hot = tip.value?.i ?? props.mark
  for (let i = 0; i < cur.length; i++) {
    const dim = props.focus != null && props.lab[i] !== props.focus
    c.globalAlpha = dim ? 0.12 : props.alpha
    c.fillStyle = props.cols?.[i] ?? color(props.lab[i])
    c.beginPath()
    c.arc(px(cur[i][0]), py(cur[i][1]), props.r, 0, 2 * Math.PI)
    c.fill()
  }
  c.globalAlpha = 1
  if (props.labels) {
    c.font = '700 15px DM Sans, sans-serif'
    c.textAlign = 'center'; c.textBaseline = 'middle'
    for (let d = 0; d < 10; d++) {
      const idx = cur.map((_, i) => i).filter(i => props.lab[i] === d)
      if (!idx.length) continue
      const x = px(median(idx.map(i => cur[i][0]))); const y = py(median(idx.map(i => cur[i][1])))
      c.lineWidth = 4; c.strokeStyle = 'rgba(11,16,32,0.85)'; c.strokeText(String(d), x, y)
      c.fillStyle = color(d); c.fillText(String(d), x, y)
    }
  }
  if (hot != null && cur[hot]) {
    c.lineWidth = 2.5; c.strokeStyle = '#ffffff'
    c.beginPath(); c.arc(px(cur[hot][0]), py(cur[hot][1]), props.r + 5, 0, 2 * Math.PI); c.stroke()
  }
}

watch(() => props.pts, (to) => {
  if (props.ms <= 0) { // live data (e.g. an optimizer running): no tween, just redraw
    cur = to.map(p => [p[0], p[1]])
    draw()
    return
  }
  const from = cur.map(p => [p[0], p[1]])
  const t0 = performance.now()
  cancelAnimationFrame(raf)
  const tick = (t: number) => {
    const u = ease(Math.min(1, (t - t0) / props.ms))
    cur = to.map((p, i) => {
      const f = from[i] ?? p
      return [f[0] + (p[0] - f[0]) * u, f[1] + (p[1] - f[1]) * u]
    })
    draw()
    if (u < 1) raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
})
watch(() => [props.mark, props.focus, props.lab], draw)
onMounted(draw)
onBeforeUnmount(() => cancelAnimationFrame(raf))

function move(e: PointerEvent) {
  if (!props.hover || !cv.value) return
  const [x, y] = toLocal(e, cv.value, props.w, props.h)
  let best = -1; let bd = 14 ** 2
  cur.forEach((p, i) => {
    const d = (px(p[0]) - x) ** 2 + (py(p[1]) - y) ** 2
    if (d < bd) { bd = d; best = i }
  })
  tip.value = best < 0 ? null : { i: best, x: px(cur[best][0]), y: py(cur[best][1]) }
  emit('hover', best < 0 ? null : best)
  draw()
}
function leave() {
  tip.value = null
  emit('hover', null)
  draw()
}
</script>

<template>
  <div class="relative mx-auto" :style="{ width: `${w}px`, height: `${h}px` }">
    <canvas
      ref="cv" :width="w * S" :height="h * S" :style="{ width: `${w}px`, height: `${h}px`, cursor: hover ? 'crosshair' : 'default' }"
      role="img" :aria-label="label" @pointermove="move" @pointerleave="leave"
    />
    <div
      v-if="tip && imgs" class="absolute pointer-events-none rounded-md p-1.5 flex flex-col items-center gap-1"
      :style="{ left: `${tip.x + (tip.x > w - 110 ? -96 : 14)}px`, top: `${Math.min(tip.y - 30, h - 100)}px`, background: 'rgba(11,16,32,0.92)', border: `2px solid ${color(lab[tip.i])}` }"
    >
      <DigitImg :v="imgs[tip.i]" :size="64" :frame="false" />
      <div class="text-xs font-mono" :style="{ color: color(lab[tip.i]) }">label {{ lab[tip.i] }}</div>
    </div>
  </div>
</template>
