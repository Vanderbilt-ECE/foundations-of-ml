<script setup lang="ts">
// Worked example (data/hand.json): five points on a number line, single linkage by hand.
// Clicks 1-4 perform the merges: a bracket appears over the number line at the merge height,
// and the distance table shrinks by one row. The amber cell is the next merge.
// Click 5 overlays complete linkage's brackets (dashed) for comparison.
import { useSlideContext } from '@slidev/client'
import { computed } from 'vue'
import d from '../data/hand.json'

const { $clicks } = useSlideContext()
const t = computed(() => Math.min($clicks.value, 5))
const W = 440; const H = 290; const L = 24; const R = 424; const base = 236; const top = 20
const hmax = 9
const X = (v: number) => L + v / 10.5 * (R - L)
const Y = (h: number) => base - h / hmax * (base - top)
const pos = (name: string) => [...name].reduce((s, c) => s + d.x[d.names.indexOf(c)], 0) / name.length

function brackets(steps: typeof d.single) {
  const born: Record<string, number> = {}
  return steps.map((s) => {
    const a = s.names[s.merge[0]]; const b = s.names[s.merge[1]]
    const ha = born[a] ?? 0; const hb = born[b] ?? 0
    born[a + b] = s.h
    return `M${X(pos(a))},${Y(ha)}V${Y(s.h)}H${X(pos(b))}V${Y(hb)}`
  })
}
const single = brackets(d.single)
const complete = brackets(d.complete)
const step = computed(() => (t.value < 4 ? d.single[t.value] : null))
</script>

<template>
  <div class="grid grid-cols-[1.15fr_1fr] gap-6 items-center">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" aria-label="Five points on a number line with merge brackets drawn at their merge heights">
      <line :x1="L" :x2="R" :y1="base" :y2="base" :style="{ stroke: '#64748b', strokeWidth: 1.5 }" />
      <g v-for="v in [0, 2, 4, 6, 8, 10]" :key="v">
        <line :x1="X(v)" :x2="X(v)" :y1="base" :y2="base + 5" :style="{ stroke: '#64748b' }" />
        <text :x="X(v)" :y="base + 18" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ v }}</text>
      </g>
      <g v-for="v in [2, 4, 6, 8]" :key="`h${v}`">
        <line :x1="L" :x2="R" :y1="Y(v)" :y2="Y(v)" :style="{ stroke: '#334155', strokeDasharray: '2 5' }" />
        <text :x="R" :y="Y(v) - 4" text-anchor="end" :style="{ fill: '#64748b', fontSize: '10px' }">h = {{ v }}</text>
      </g>
      <path v-for="(p, i) in complete" :key="`c${i}`" :d="p" class="br" :style="{ stroke: '#fbbf24', strokeWidth: 2, strokeDasharray: '6 4', fill: 'none', opacity: t >= 5 ? 0.9 : 0 }" />
      <path v-for="(p, i) in single" :key="`s${i}`" :d="p" class="br" :style="{ stroke: '#2dd4bf', strokeWidth: 3, fill: 'none', opacity: i < t ? 1 : 0 }" />
      <g v-for="(x, i) in d.x" :key="i">
        <circle :cx="X(x)" :cy="base" r="7" :style="{ fill: '#e2e8f0', stroke: '#0b1020', strokeWidth: 2 }" />
        <text :x="X(x)" :y="base + 36" text-anchor="middle" :style="{ fill: '#e2e8f0', fontSize: '15px', fontWeight: 700 }">{{ d.names[i] }}</text>
      </g>
      <g v-if="t >= 5">
        <text :x="L + 4" :y="Y(8.5) - 6" :style="{ fill: '#fbbf24', fontSize: '12px' }">complete linkage</text>
      </g>
    </svg>
    <div style="min-height: 16.5em" class="text-left">
      <template v-if="step">
        <div class="text-xs uppercase tracking-wider opacity-60 mb-2">Single-linkage distances · step {{ t + 1 }} of 4</div>
        <table class="dm">
          <thead><tr><th /><th v-for="nm in step.names" :key="nm">{{ nm }}</th></tr></thead>
          <tbody>
            <tr v-for="(row, i) in step.D" :key="i">
              <th>{{ step.names[i] }}</th>
              <td v-for="(v, j) in row" :key="j" :class="{ hit: (i === step.merge[0] && j === step.merge[1]) || (i === step.merge[1] && j === step.merge[0]), diag: i === j }">{{ i === j ? '·' : v.toFixed(1) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="text-sm mt-3">Next merge: <b class="text-amber-300">{{ step.names[step.merge[0]] }} + {{ step.names[step.merge[1]] }}</b> at <b class="font-mono">{{ step.h.toFixed(1) }}</b></div>
      </template>
      <template v-else>
        <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>
          <div class="font-bold text-teal-300">Single linkage</div>
          <div class="text-sm mt-1">Merge heights <span class="font-mono">{{ d.single.map(s => s.h.toFixed(1)).join(', ') }}</span></div>
        </div>
        <div class="mt-3 reveal" :class="{ shown: t >= 5 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-4 py-3>
          <div class="font-bold text-amber-300">Complete linkage</div>
          <div class="text-sm mt-1">Merge heights <span class="font-mono">{{ d.complete.map(s => s.h.toFixed(1)).join(', ') }}</span></div>
          <div class="text-xs opacity-80 mt-1">Same merges here, but each height is the farthest pair, so the last merge sits at 8.5 (A to E).</div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.br { transition: opacity 0.6s ease; }
.dm { border-collapse: separate; border-spacing: 3px; font-size: 0.9rem; }
.dm th { font-weight: 700; opacity: 0.75; padding: 2px 8px; }
.dm td { font-family: ui-monospace, monospace; text-align: center; padding: 3px 10px; border-radius: 5px; background: rgba(255, 255, 255, 0.05); }
.dm td.diag { opacity: 0.4; }
.dm td.hit { background: rgba(251, 191, 36, 0.35); color: #fde68a; font-weight: 700; }
.reveal { opacity: 0; transform: translateY(8px); transition: opacity 0.6s ease, transform 0.6s ease; }
.reveal.shown { opacity: 1; transform: none; }
</style>
