<script setup lang="ts">
// PCA as dimension reduction. 500 rows × 20 features, generated from 3 hidden factors plus independent noise
// (x = W z + noise, z ~ N(0, diag(2.2², 1.5², 1²)), noise sd 1, seeded). We compute the 20 × 20 covariance and its
// eigenvalues (Jacobi), then show them as a scree chart with the cumulative share. The slider picks k:
// left, the data matrix shrinks from 20 columns to k; right, the kept eigenvalues light up.
// The PDF export shows k = 3.
import { computed, ref } from 'vue'
import { rng, useActive } from '../utils/plot'

const N = 500; const D = 20; const SD = [2.2, 1.5, 1.0]; const NOISE = 1.0
const { isPrintMode } = useActive()
const kSel = ref(3)
const k = computed(() => (isPrintMode.value ? 3 : kSel.value))

// --- data and covariance ---
const R = rng(11)
const Wl = Array.from({ length: D }, () => SD.map(() => R.n()))
const X = Array.from({ length: N }, () => {
  const z = SD.map(s => s * R.n())
  return Wl.map(w => w[0] * z[0] + w[1] * z[1] + w[2] * z[2] + NOISE * R.n())
})
const mu = Array.from({ length: D }, (_, j) => X.reduce((s, r) => s + r[j], 0) / N)
const C = Array.from({ length: D }, (_, i) => Array.from({ length: D }, (_, j) =>
  X.reduce((s, r) => s + (r[i] - mu[i]) * (r[j] - mu[j]), 0) / (N - 1)))

// Eigenvalues of a symmetric matrix by cyclic Jacobi rotations, largest first.
function eigvalsSym(M: number[][]) {
  const n = M.length; const a = M.map(r => [...r])
  for (let sweep = 0; sweep < 100; sweep++) {
    let off = 0
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += a[p][q] ** 2
    if (off < 1e-20) break
    for (let p = 0; p < n; p++) {
      for (let q = p + 1; q < n; q++) {
        if (a[p][q] === 0) continue
        const th = (a[q][q] - a[p][p]) / (2 * a[p][q])
        const t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1))
        const c = 1 / Math.sqrt(t * t + 1); const s = t * c
        for (let r = 0; r < n; r++) { const rp = a[r][p]; const rq = a[r][q]; a[r][p] = c * rp - s * rq; a[r][q] = s * rp + c * rq }
        for (let r = 0; r < n; r++) { const pr = a[p][r]; const qr = a[q][r]; a[p][r] = c * pr - s * qr; a[q][r] = s * pr + c * qr }
      }
    }
  }
  return a.map((r, i) => r[i]).sort((x, y) => y - x)
}
const lam = eigvalsSym(C)
const total = lam.reduce((s, l) => s + l, 0)
const share = lam.map(l => 100 * l / total)
const cum = share.map((_, i) => share.slice(0, i + 1).reduce((s, v) => s + v, 0))
const kept = computed(() => cum[k.value - 1])

// --- matrix-shape diagram ---
const MW = 300; const MH = 275; const CW = 5; const BH = 195; const BY = 34 // tall and narrow, like 500 × 20
const xLeft = 28; const zLeft = 196
// --- scree chart ---
const SW = 420; const SH = 250; const SL = 40; const SB = 40; const ST = 12
const bw = (SW - SL - 10) / D
const bx = (i: number) => SL + i * bw
const yv = (pct: number) => SH - SB - pct / 100 * (SH - SB - ST)
const cumPath = cum.map((c, i) => `${i ? 'L' : 'M'}${(bx(i) + bw / 2).toFixed(1)},${yv(c).toFixed(1)}`).join('')
</script>

<template>
  <div>
    <div v-if="!isPrintMode" class="flex items-center gap-4 text-sm">
      <span class="font-mono text-teal-300 text-xl w-36 shrink-0">keep k = {{ k }}</span>
      <input v-model.number="kSel" type="range" min="1" :max="D" step="1" class="flex-1" style="accent-color: #2dd4bf" aria-label="Number of components to keep">
      <span class="font-mono w-24 text-right opacity-70">of {{ D }}</span>
    </div>

    <div class="grid grid-cols-[0.8fr_1.2fr] gap-6 mt-4 items-start">
      <!-- the data matrix before and after -->
      <svg :viewBox="`0 0 ${MW} ${MH}`" class="w-full" role="img" :aria-label="`A data matrix with 500 rows and 20 columns becomes one with ${k} columns`">
        <text :x="xLeft + D * CW / 2" y="20" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '14px', fontWeight: 700 }">X</text>
        <rect v-for="j in D" :key="`x${j}`" :x="xLeft + (j - 1) * CW" :y="BY" :width="CW - 1.5" :height="BH" :style="{ fill: '#94a3b8', fillOpacity: 0.35 }" />
        <text :x="xLeft + D * CW / 2" :y="BY + BH + 20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '13px', fontFamily: 'monospace' }">500 × 20</text>

        <line :x1="xLeft + D * CW + 10" :x2="zLeft - 12" :y1="BY + BH / 2" :y2="BY + BH / 2" :style="{ stroke: '#2dd4bf', strokeWidth: 2 }" />
        <path :d="`M${zLeft - 12},${BY + BH / 2} l-8,-5 l0,10 Z`" :style="{ fill: '#2dd4bf' }" />
        <text :x="(xLeft + D * CW + zLeft) / 2" :y="BY + BH / 2 - 10" text-anchor="middle" :style="{ fill: '#2dd4bf', fontSize: '12px' }">PCA</text>

        <text :x="zLeft + Math.max(k, 3) * CW / 2" y="20" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '14px', fontWeight: 700 }">Z</text>
        <rect v-for="j in k" :key="`z${j}`" :x="zLeft + (j - 1) * CW" :y="BY" :width="CW - 1.5" :height="BH" :style="{ fill: '#2dd4bf', fillOpacity: 0.75 }" />
        <text :x="zLeft + Math.max(k, 3) * CW / 2" :y="BY + BH + 20" text-anchor="middle" :style="{ fill: '#2dd4bf', fontSize: '13px', fontFamily: 'monospace' }">500 × {{ k }}</text>
        <text :x="MW / 2" :y="MH - 4" text-anchor="middle" :style="{ fill: '#cbd5e1', fontSize: '13px' }">20 numbers per row → {{ k }}</text>
      </svg>

      <!-- scree chart -->
      <div>
        <svg :viewBox="`0 0 ${SW} ${SH}`" class="w-full" role="img" aria-label="Share of variance for each of the 20 principal components, with the cumulative share as a line">
          <line v-for="g in [0, 50, 100]" :key="g" :x1="SL" :x2="SW - 10" :y1="yv(g)" :y2="yv(g)" :style="{ stroke: '#334155', strokeDasharray: g ? '3 4' : '' }" />
          <text v-for="g in [0, 50, 100]" :key="`t${g}`" :x="SL - 6" :y="yv(g) + 4" text-anchor="end" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ g }}%</text>
          <rect v-for="(p, i) in share" :key="i" :x="bx(i) + 1.5" :y="yv(p)" :width="bw - 3" :height="yv(0) - yv(p)" :style="{ fill: i < k ? '#2dd4bf' : '#64748b', fillOpacity: i < k ? 0.9 : 0.5, transition: 'fill 0.3s' }" />
          <path :d="cumPath" :style="{ fill: 'none', stroke: '#fbbf24', strokeWidth: 2 }" />
          <circle :cx="bx(k - 1) + bw / 2" :cy="yv(kept)" r="5.5" :style="{ fill: '#fbbf24', stroke: '#0b1020', strokeWidth: 2, transition: 'cx 0.3s, cy 0.3s' }" />
          <text v-for="i in [1, 5, 10, 15, 20]" :key="`c${i}`" :x="bx(i - 1) + bw / 2" :y="SH - 24" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">{{ i }}</text>
          <text :x="(SL + SW) / 2" :y="SH - 6" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '11px' }">component</text>
          <text :x="SW - 12" :y="yv(100) + 16" text-anchor="end" :style="{ fill: '#fbbf24', fontSize: '11px' }">cumulative</text>
        </svg>
        <div class="flex justify-between items-baseline font-mono text-sm mt-1">
          <span>variance kept <span class="text-amber-300 text-base">{{ kept.toFixed(1) }}%</span></span>
          <span class="opacity-75">lost {{ (100 - kept).toFixed(1) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>
