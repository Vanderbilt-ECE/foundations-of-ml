<script setup lang="ts">
// Thin Plotly.js wrapper. Plotly is loaded on first use so it stays out of the main bundle.
// Explicit width/height (Slidev scales the whole canvas; Plotly's auto-sizing gets confused).
// spin: slowly orbit a 3D scene's camera while this slide is on screen; stops once the pointer enters the chart.
// In print/PDF export (no WebGL in the headless browser) 3D traces are drawn as a static SVG projection instead:
// markers as dots, mode 'lines' traces as polylines (null breaks a line). globe: hide what is behind the sphere.
// A #print slot replaces the fallback entirely (used for surfaces, which the projection does not draw).
import { useNav, useSlideContext } from '@slidev/client'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{
  data: any[]
  layout?: Record<string, any>
  width?: number
  height?: number
  spin?: boolean
  globe?: boolean
}>(), { layout: () => ({}), width: 520, height: 400, spin: false, globe: false })

const el = ref<HTMLDivElement>()
let Plotly: any = null
let raf = 0
let stopped = false
const { $page } = useSlideContext()
const { currentSlideNo, isPrintMode } = useNav()
const active = computed(() => currentSlideNo.value === $page.value)

const base = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'DM Sans, sans-serif', color: '#cbd5e1', size: 12 },
  margin: { l: 0, r: 0, t: 0, b: 0 },
  showlegend: false,
  uirevision: 'keep', // keep the user's/orbit camera when data changes
}
const fullLayout = () => ({ ...base, ...props.layout, width: props.width, height: props.height })

let angle = 0
function orbit() {
  if (!Plotly || stopped || !el.value) return
  if (active.value) {
    angle += 0.004
    const eye = (props.layout.scene?.camera?.eye) ?? { x: 1.6, y: 1.6, z: 0.9 }
    const r = Math.hypot(eye.x, eye.y)
    const a0 = Math.atan2(eye.y, eye.x)
    Plotly.relayout(el.value, { 'scene.camera.eye': { x: r * Math.cos(a0 + angle), y: r * Math.sin(a0 + angle), z: eye.z } })
  }
  raf = requestAnimationFrame(() => setTimeout(orbit, 33))
}

// Static fallback for export: orthographic projection of the scatter3d traces, seen from the layout's camera.
const flat = computed(() => {
  if (!isPrintMode.value) return null
  const eye = props.layout.scene?.camera?.eye ?? { x: 1.6, y: 1.6, z: 0.9 }
  const traces = props.data.filter(t => t.type === 'scatter3d' && t.visible !== false)
  const all = (k: 'x' | 'y' | 'z') => traces.flatMap(t => t[k] as number[])
  const rng = (k: 'x' | 'y' | 'z') => {
    const r = props.layout.scene?.[`${k}axis`]?.range
    const v = all(k)
    return r ?? [Math.min(...v), Math.max(...v)]
  }
  const R = { x: rng('x'), y: rng('y'), z: rng('z') }
  const n = (k: 'x' | 'y' | 'z', v: number) => (v - R[k][0]) / (R[k][1] - R[k][0]) - 0.5
  const az = Math.atan2(eye.y, eye.x)
  const el = Math.atan2(eye.z, Math.hypot(eye.x, eye.y))
  // screen axes: right = (-sin az, cos az, 0), up = (-cos az sin el, -sin az sin el, cos el)
  const proj = (x: number, y: number, z: number) => {
    const u = -Math.sin(az) * x + Math.cos(az) * y
    const w = -Math.cos(az) * Math.sin(el) * x - Math.sin(az) * Math.sin(el) * y + Math.cos(el) * z
    const depth = Math.cos(az) * Math.cos(el) * x + Math.sin(az) * Math.cos(el) * y + Math.sin(el) * z
    return [props.width / 2 + u * props.width * 0.55, props.height / 2 - w * props.height * 0.62, depth]
  }
  const pts: { x: number, y: number, d: number, r: number, c: string, s?: string }[] = []
  const lines: string[] = []
  for (const t of traces) {
    const col = t.marker?.color
    if (t.mode === 'lines') {
      let seg = ''
      t.x.forEach((_: number, i: number) => {
        if (t.x[i] == null) { seg = ''; return }
        const [x, y, d] = proj(n('x', t.x[i]), n('y', t.y[i]), n('z', t.z[i]))
        if (props.globe && d < 0) { seg = ''; return }
        seg = `${seg ? `${seg}L` : 'M'}${x.toFixed(1)},${y.toFixed(1)}`
        if (i === t.x.length - 1 || t.x[i + 1] == null) lines.push(seg)
      })
      continue
    }
    t.x.forEach((_: number, i: number) => {
      const [x, y, d] = proj(n('x', t.x[i]), n('y', t.y[i]), n('z', t.z[i]))
      if (props.globe && d < 0) return
      pts.push({ x, y, d, r: (t.marker?.size ?? 4) * 0.55, c: Array.isArray(col) ? col[i] : col, s: t.marker?.line?.color })
    })
  }
  pts.sort((a, b) => a.d - b.d) // far points first
  const corners = [[-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, 0.5]].map(p => proj(p[0], p[1], p[2]))
  const axes = [1, 2, 3].map(k => ({ x1: corners[0][0], y1: corners[0][1], x2: corners[k][0], y2: corners[k][1] }))
  const labels = ['x', 'y', 'z'].map((k, i) => ({
    x: Math.min(Math.max(corners[i + 1][0], 70), props.width - 70), y: corners[i + 1][1],
    text: props.layout.scene?.[`${k}axis`]?.title?.text ?? k,
    color: props.layout.scene?.[`${k}axis`]?.title?.font?.color ?? '#94a3b8',
  }))
  const showAxes = props.layout.scene?.xaxis?.visible !== false
  return { pts, lines, axes: showAxes ? axes : [], labels: showAxes ? labels : [] }
})

onMounted(async () => {
  if (isPrintMode.value) return
  Plotly = (await import('plotly.js-dist-min')).default
  if (!el.value) return
  await Plotly.newPlot(el.value, props.data, fullLayout(), { displayModeBar: false, responsive: false })
  if (props.spin && !isPrintMode.value) {
    el.value.addEventListener('pointerenter', () => { stopped = true }, { once: true })
    orbit()
  }
})
watch(() => [props.data, props.layout], () => {
  if (Plotly && el.value) Plotly.react(el.value, props.data, fullLayout())
})
onBeforeUnmount(() => {
  stopped = true
  cancelAnimationFrame(raf)
  if (Plotly && el.value) Plotly.purge(el.value)
})
</script>

<template>
  <slot v-if="isPrintMode && $slots.print" name="print" />
  <svg v-else-if="flat" :viewBox="`0 0 ${width} ${height}`" :style="{ width: `${width}px`, height: `${height}px` }" class="mx-auto block" role="img" aria-label="3D scatter plot (static view)">
    <path v-for="(l, i) in flat.lines" :key="`p${i}`" :d="l" :style="{ stroke: '#64748b', strokeWidth: 1, fill: 'none' }" />
    <line v-for="(a, i) in flat.axes" :key="`a${i}`" v-bind="a" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
    <circle v-for="(p, i) in flat.pts" :key="i" :cx="p.x" :cy="p.y" :r="p.r" :style="{ fill: p.c, fillOpacity: 0.9, stroke: p.s ?? 'none', strokeWidth: p.s ? 2 : 0 }" />
    <text v-for="(l, i) in flat.labels" :key="`l${i}`" :x="l.x" :y="l.y + 16" text-anchor="middle" :style="{ fill: l.color, fontSize: '13px' }">{{ l.text }}</text>
  </svg>
  <div v-else ref="el" :style="{ width: `${width}px`, height: `${height}px` }" class="mx-auto" />
</template>
