<script setup lang="ts">
// General 2D clustering view used by most slides.
//   pts        data points
//   lab        cluster index per point (null = unassigned, drawn gray)
//   centroids  centroid positions; changes are tweened, and the Voronoi cells and
//              point-to-centroid lines follow the moving centroids
//   trails     past centroid positions per centroid (drawn as dashed paths)
// Colors use inline style: UnoCSS attributify rewrites fill / stroke attributes.
import { computed } from 'vue'
import type { Domain, Pt } from '../utils/kmeans'
import { color, domainOf, equalScale, polyPath, useTween, voronoi } from '../utils/kmeans'

const props = withDefaults(defineProps<{
  pts: Pt[]
  lab?: (number | null)[] | null
  centroids?: Pt[] | null
  trails?: Pt[][] | null
  domain?: Domain
  w?: number
  h?: number
  r?: number
  cells?: boolean
  lines?: boolean
  frame?: boolean
  highlight?: number | null
  dimOthers?: boolean
  cR?: number
  label?: string
}>(), { lab: null, centroids: null, trails: null, w: 520, h: 400, r: 3.6, cells: false, lines: false, frame: false, highlight: null, dimOthers: false, cR: 9 })

const dom = computed(() => props.domain ?? domainOf(props.pts))
const S = computed(() => equalScale(dom.value, props.w, props.h))
const C = useTween(() => (props.centroids ?? []) as number[][], 750)
const cellPaths = computed(() => (props.cells && C.value.length > 1 ? voronoi(C.value, S.value.vis).map(p => polyPath(p, S.value.sx, S.value.sy)) : []))
const showC = computed(() => C.value.length > 0 && props.centroids)
const linePath = computed(() => {
  if (!props.lines || !props.lab || !C.value.length) return []
  const { sx, sy } = S.value
  const by: string[] = C.value.map(() => '')
  props.pts.forEach((p, i) => {
    const k = props.lab![i]
    if (k == null || !C.value[k]) return
    by[k] += `M${sx(p[0]).toFixed(1)},${sy(p[1]).toFixed(1)}L${sx(C.value[k][0]).toFixed(1)},${sy(C.value[k][1]).toFixed(1)}`
  })
  return by
})
const trailPaths = computed(() => (props.trails ?? []).map(t => t.map((p, i) => `${i ? 'L' : 'M'}${S.value.sx(p[0]).toFixed(1)},${S.value.sy(p[1]).toFixed(1)}`).join('')))
</script>

<template>
  <svg :viewBox="`0 0 ${w} ${h}`" class="w-full" role="img" :aria-label="label ?? 'Scatter plot of data points colored by cluster'">
    <rect v-if="frame" x="1" y="1" :width="w - 2" :height="h - 2" rx="8" :style="{ fill: 'rgba(255,255,255,0.025)', stroke: 'rgba(255,255,255,0.08)' }" />
    <g v-if="cells">
      <path v-for="(d, k) in cellPaths" :key="`c${k}`" :d="d" :style="{ fill: color(k), fillOpacity: 0.1, stroke: color(k), strokeOpacity: 0.45, strokeWidth: 1.2 }" />
    </g>
    <g v-if="lines">
      <path v-for="(d, k) in linePath" :key="`l${k}`" :d="d" :style="{ stroke: color(k), strokeOpacity: 0.28, strokeWidth: 1, fill: 'none' }" />
    </g>
    <g>
      <circle
        v-for="(p, i) in pts" :key="i"
        :cx="S.sx(p[0])" :cy="S.sy(p[1])" :r="highlight === i ? r * 2.2 : r"
        class="pt"
        :style="{
          fill: color(lab ? lab[i] : null),
          fillOpacity: dimOthers && highlight !== null && highlight !== i ? 0.25 : 0.88,
          stroke: highlight === i ? '#fff' : 'none',
          strokeWidth: 2,
          transitionDelay: `${(i % 37) * 8}ms`,
        }"
      />
    </g>
    <g v-if="trails">
      <path v-for="(d, k) in trailPaths" :key="`t${k}`" :d="d" :style="{ stroke: color(k), strokeWidth: 2, strokeDasharray: '4 4', fill: 'none', opacity: 0.9 }" />
    </g>
    <g v-if="showC">
      <g v-for="(c, k) in C" :key="`m${k}`" :transform="`translate(${S.sx(c[0]).toFixed(1)},${S.sy(c[1]).toFixed(1)})`">
        <circle :r="cR + 5" :style="{ fill: color(k), fillOpacity: 0.18 }" />
        <circle :r="cR" :style="{ fill: color(k), stroke: '#0b1020', strokeWidth: 2.5 }" />
        <path :d="`M${-cR * 0.45},0H${cR * 0.45}M0,${-cR * 0.45}V${cR * 0.45}`" :style="{ stroke: '#0b1020', strokeWidth: 2.4 }" />
      </g>
    </g>
    <slot :sx="S.sx" :sy="S.sy" />
  </svg>
</template>

<style scoped>
.pt {
  transition: fill 0.55s ease, fill-opacity 0.4s ease, r 0.3s ease;
}
</style>
