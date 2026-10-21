<script setup lang="ts">
// rows: one string per classifier, '1' = correct on that test example, '0' = wrong
const props = defineProps<{ title: string, rows: string[], color?: string }>()

const cell = 22
const gap = 4
const left = 40
const k = props.rows.length
const n = props.rows[0].length
const vote = Array.from({ length: n }, (_, j) => props.rows.filter(r => r[j] === '1').length * 2 > k ? '1' : '0').join('')
const all = [...props.rows, vote]
const rowY = (i: number) => i * (cell + gap) + (i === k ? 12 : 0)
const cells = all.flatMap((r, i) => r.split('').map((c, j) => ({
  key: `${i}-${j}`,
  x: left + j * (cell + gap),
  y: rowY(i),
  // inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
  style: { fill: c === '1' ? '#2dd4bf' : '#f87171', fillOpacity: i === k ? 0.95 : 0.55 },
})))
const labels = all.map((_, i) => ({ text: i === k ? 'vote' : 'ABCDEFG'[i], y: rowY(i) + 16 }))
const pct = (s: string) => Math.round(s.split('').filter(c => c === '1').length / n * 100)
const width = left + n * (cell + gap)
const height = rowY(k) + cell + 2
const ruleY = rowY(k) - 8
</script>

<template>
  <div>
    <div class="font-bold mb-1" :class="color ?? 'text-teal-300'">{{ title }}</div>
    <svg role="img" :aria-label="`${title}: majority vote accuracy ${pct(vote)} percent`" :viewBox="`0 0 ${width} ${height}`" class="w-full">
      <text v-for="l in labels" :key="l.text" x="0" :y="l.y" fill="#94a3b8" style="font-size: 12px">{{ l.text }}</text>
      <rect v-for="c in cells" :key="c.key" :x="c.x" :y="c.y" :width="cell" :height="cell" rx="4" :style="c.style" />
      <line :x1="left" :x2="width - gap" :y1="ruleY" :y2="ruleY" stroke="#64748b" stroke-width="1.5" />
    </svg>
    <div class="text-sm mt-1 opacity-90">each row {{ pct(rows[0]) }}% correct → vote <span class="font-bold">{{ pct(vote) }}%</span></div>
  </div>
</template>
