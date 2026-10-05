<script setup lang="ts">
const n = 10
const f1 = (p: number, r: number) => p + r === 0 ? 0 : 2 * p * r / (p + r)
const project = (p: number, r: number, f: number) => [72 + 220 * p + 100 * r, 220 + 33 * p - 33 * r - 216 * f]
const line = (points: number[][]) => points.map(([x, y], i) => `${i ? 'L' : 'M'}${x.toFixed(1)},${y.toFixed(1)}`).join(' ')
const precisionLines = Array.from({length: n + 1}, (_, i) => {
  const p = i / n
  return line(Array.from({length: n + 1}, (_, j) => { const r = j / n; return project(p, r, f1(p, r)) }))
})
const recallLines = Array.from({length: n + 1}, (_, j) => {
  const r = j / n
  return line(Array.from({length: n + 1}, (_, i) => { const p = i / n; return project(p, r, f1(p, r)) }))
})
const origin = project(0, 0, 0)
const pEnd = project(1, 0, 0)
const rEnd = project(0, 1, 0)
const fEnd = project(0, 0, 1)
const peak = project(1, 1, 1)
</script>

<template>
  <svg class="f1-surface" viewBox="0 0 430 330" role="img" aria-label="Three-dimensional wireframe surface of F1 score, the harmonic mean of precision and recall. F1 rises toward one as both precision and recall rise, and stays low when either is low.">
    <g fill="none" stroke="#94a3b8" stroke-width="1.4">
      <path :d="`M${origin} L${pEnd} M${origin} L${rEnd} M${origin} L${fEnd}`" />
      <path :d="`M${project(0.5,0,0)} L${project(0.5,1,0)} M${project(1,0.5,0)} L${project(0,0.5,0)}`" stroke-dasharray="3 5" opacity=".55" />
    </g>
    <g fill="none" stroke="#2dd4bf" stroke-width="1.35" opacity=".84">
      <path v-for="(d, i) in precisionLines" :key="`p${i}`" :d="d" />
      <path v-for="(d, i) in recallLines" :key="`r${i}`" :d="d" />
    </g>
    <circle :cx="peak[0]" :cy="peak[1]" r="4" fill="#fbbf24" />
    <g fill="#cbd5e1" font-size="15">
      <text :x="origin[0]-8" :y="origin[1]+19">0</text>
      <text :x="pEnd[0]-3" :y="pEnd[1]+19">1</text>
      <text :x="rEnd[0]-13" :y="rEnd[1]+14">1</text>
      <text :x="fEnd[0]-19" :y="fEnd[1]+20">1</text>
      <text x="270" y="282" text-anchor="middle">Precision</text>
      <text x="133" y="220" transform="rotate(-34 133 220)" text-anchor="middle">Recall</text>
      <text x="20" y="95" transform="rotate(-90 20 95)" text-anchor="middle">F1</text>
      <text :x="peak[0]-10" :y="peak[1]-10" fill="#fcd34d">1</text>
    </g>
  </svg>
</template>

<style scoped>
.f1-surface { width: 100%; max-height: 300px; margin-top: 4px; }
.f1-surface text { font-size: 15px !important; }
</style>
