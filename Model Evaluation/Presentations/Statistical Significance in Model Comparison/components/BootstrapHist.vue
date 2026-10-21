<script setup lang="ts">
defineProps<{ step: number }>()

// 10,000 paired bootstrap resamples of the worked example (500 cases: 400 both right,
// 8 A only, 22 B only, 70 both wrong); accuracy gap B − A in points, bins 0.4 pts wide
const lo0 = -1.5, w = 0.4
const counts = [2, 5, 8, 40, 110, 230, 481, 789, 1043, 1317, 1417, 1394, 1211, 852, 513, 295, 162, 79, 32, 15, 4]
const ciLo = 0.6, ciHi = 5.0, observed = 2.8

const L = 30, R = 510, base = 200, top = 40, xLo = -1.5, xHi = 6.9
const X = (v: number) => L + ((v - xLo) / (xHi - xLo)) * (R - L)
const maxC = Math.max(...counts)
const bars = counts.map((c, i) => {
  const a = lo0 + i * w
  const mid = a + w / 2
  return { x: X(a) + 1, width: X(a + w) - X(a) - 2, y: base - (c / maxC) * (base - top), h: (c / maxC) * (base - top), inside: mid >= ciLo && mid <= ciHi }
})
const rectPath = (b: { x: number, y: number, width: number, h: number }) =>
  `M${b.x.toFixed(1)} ${base}V${b.y.toFixed(1)}H${(b.x + b.width).toFixed(1)}V${base}Z`
const allBars = bars.map(rectPath).join(' ')
const insideBars = bars.filter(b => b.inside).map(rectPath).join(' ')
const outsideBars = bars.filter(b => !b.inside).map(rectPath).join(' ')
const ticks = [0, 2, 4, 6]
</script>

<template>
  <svg role="img" aria-label="Histogram of 10,000 bootstrap accuracy gaps, B minus A, for the worked example. The gaps center near the observed 2.8 points. The middle 95 percent runs from plus 0.6 to plus 5.0 points, which does not include zero." viewBox="0 0 540 260" class="w-full">
    <line :x1="L" :y1="base" :x2="R" :y2="base" stroke="#64748b" stroke-width="2" />
    <g v-show="step >= 3">
      <path v-if="step < 4" :d="allBars" fill="#2dd4bf" style="fill-opacity: .75" />
      <path v-if="step >= 4" :d="insideBars" fill="#2dd4bf" style="fill-opacity: .75" />
      <path v-if="step >= 4" :d="outsideBars" fill="#64748b" style="fill-opacity: .45" />
    </g>
    <g v-show="step >= 2">
      <line :x1="X(observed)" :y1="top - 14" :x2="X(observed)" :y2="base" stroke="#e2e8f0" stroke-width="2" />
      <text :x="X(observed)" :y="top - 20" fill="#e2e8f0" text-anchor="middle" style="font-size:13px">observed +2.8</text>
    </g>
    <g v-show="step >= 4">
      <line :x1="X(ciLo)" :y1="top + 10" :x2="X(ciLo)" :y2="base + 4" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5" />
      <line :x1="X(ciHi)" :y1="top + 10" :x2="X(ciHi)" :y2="base + 4" stroke="#f59e0b" stroke-width="2.5" stroke-dasharray="6 5" />
      <text :x="X(ciLo) - 6" :y="top + 22" fill="#fbbf24" text-anchor="end" style="font-size:13px">+0.6</text>
      <text :x="X(ciHi) + 6" :y="top + 22" fill="#fbbf24" style="font-size:13px">+5.0</text>
      <line :x1="X(0)" :y1="top + 40" :x2="X(0)" :y2="base + 4" stroke="#f87171" stroke-width="2.5" />
      <text :x="X(0) - 6" :y="top + 52" fill="#f87171" text-anchor="end" style="font-size:13px">0</text>
    </g>
    <g fill="#cbd5e1" style="font-size:13px" text-anchor="middle">
      <text v-for="t in ticks" :key="t" :x="X(t)" :y="base + 18">{{ t > 0 ? '+' + t : t }}</text>
    </g>
    <text :x="(L + R) / 2" :y="base + 42" fill="#e2e8f0" text-anchor="middle" style="font-size:14px">accuracy gap, B − A (points)</text>
  </svg>
</template>
