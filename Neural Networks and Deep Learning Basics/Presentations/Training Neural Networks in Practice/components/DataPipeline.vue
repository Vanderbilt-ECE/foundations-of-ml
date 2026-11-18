<script setup lang="ts">
// Where training data lives and how it moves: disk → RAM (CPU) → VRAM (GPU). Each square is one batch.
//   mode 'ram' (dataset fits in RAM, not in VRAM):
//     step 0: hardware only · 1: read the whole dataset into RAM once, CPU preprocesses it
//     2: training loop, one batch copied to VRAM per step · ≥3: batch size doubled (half the steps, twice the activations)
//   mode 'disk' (dataset bigger than RAM):
//     step 0: hardware only · ≥1: streaming pipeline: the CPU reads and preprocesses upcoming batches
//     into a small queue in RAM while the GPU computes the current one
// One training step = T seconds: copy → forward → backward → update. Print shows a still frame.
import { computed, ref, watch } from 'vue'
import { C, arrow, clamp, ease, useActive, useLoop } from '../utils/plot'

const props = defineProps<{ step: number; mode: 'ram' | 'disk' }>()
const { isPrintMode } = useActive()
const W = 920; const H = 300
const T = 3.2 // seconds per training step

const t = ref(0)
useLoop((dt) => { t.value += dt }, () => { t.value = 0 })
watch(() => props.step, () => { t.value = 0 })

const isRam = computed(() => props.mode === 'ram')
const training = computed(() => props.step >= (isRam.value ? 2 : 1))
const bs = computed(() => (isRam.value && props.step >= 3 ? 2 : 1)) // batches (squares) per training step
const clock = computed(() => (isPrintMode.value ? (training.value ? T * 0.42 : 99) : t.value))
const n = computed(() => Math.floor(clock.value / T))
const u = computed(() => clock.value / T - n.value)

// ---- layout ----
type P = number[]
const grid = (x0: number, y0: number, cols: number, s: number, g: number) => (i: number): P => [x0 + (i % cols) * (s + g), y0 + Math.floor(i / cols) * (s + g)]
const N = computed(() => (isRam.value ? 12 : 40))
const DS = computed(() => (isRam.value ? 20 : 18))
const diskPos = computed(() => (isRam.value ? grid(55, 96, 6, 20, 8) : grid(42, 84, 8, 18, 6)))
const ramPos = grid(365, 88, 6, 20, 8)
const vramPos = (j: number): P => [722 + j * 28, 150]
const BOX = { disk: [20, 230], ram: [330, 230], vram: [650, 250] }

const RAW = C.dim; const PREP = C.blue
const hex = (c: string) => [1, 3, 5].map(i => parseInt(c.slice(i, i + 2), 16))
const mix = (a: string, b: string, e: number) => `rgb(${hex(a).map((v, i) => Math.round(v + (hex(b)[i] - v) * e)).join(',')})`
const lerp = (a: P, b: P, e: number): P => [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e]

// ---- which batches are on the GPU this step ----
const PERM = [7, 2, 10, 4, 0, 9, 5, 11, 1, 6, 3, 8] // shuffled order (mode 'ram')
const perEpoch = computed(() => 12 / bs.value)
const batchIds = computed(() => {
  const e = Math.floor(n.value / perEpoch.value); const k = n.value % perEpoch.value
  return Array.from({ length: bs.value }, (_, j) => (PERM[k * bs.value + j] + 5 * e) % 12)
})
const diskIdx = (m: number) => (m * 17) % 40 // random-access reads (mode 'disk')

// ---- GPU phase within one training step ----
const phase = computed(() => (!training.value ? 'idle' : u.value < 0.25 ? 'copy' : u.value < 0.55 ? 'forward' : u.value < 0.85 ? 'backward' : 'update'))
const actFrac = computed(() => phase.value === 'forward' ? (u.value - 0.25) / 0.3 : phase.value === 'backward' ? 1 - (u.value - 0.55) / 0.3 : 0)
const GPU = {
  idle: ['idle', C.muted], copy: ['receiving batch', C.blue], forward: ['forward pass', C.amber],
  backward: ['backward pass', C.red], update: ['update weights', C.teal],
} as Record<string, [string, string]>
const fade = computed(() => clamp(1 - (u.value - 0.85) / 0.12))

// ---- squares ----
interface Sq { key: string; p: P; s: number; fill: string; ring?: string; op?: number }
const squares = computed<Sq[]>(() => {
  const out: Sq[] = []
  const c = clock.value; const uu = u.value
  if (isRam.value) {
    if (props.step === 1) {
      for (let i = 0; i < 12; i++) {
        const ta = i * 0.12
        if (c < ta) continue
        const e = ease(clamp((c - ta) / 0.6))
        const prep = clamp((c - (2.2 + i * 0.08)) / 0.3)
        out.push({ key: `r${i}`, p: lerp(diskPos.value(i), ramPos(i), e), s: 20, fill: mix(RAW, PREP, prep) })
      }
    }
    else if (props.step >= 2) {
      for (let i = 0; i < 12; i++) out.push({ key: `r${i}`, p: ramPos(i), s: 20, fill: PREP, ring: batchIds.value.includes(i) ? C.text : undefined })
      batchIds.value.forEach((id, j) => {
        out.push({ key: `g${j}`, p: lerp(ramPos(id), vramPos(j), ease(clamp(uu / 0.22))), s: 20, fill: PREP, op: fade.value })
      })
    }
  }
  else if (training.value) {
    const m = n.value; const e = ease(clamp(uu / 0.22))
    out.push({ key: `q${m}`, p: lerp(ramPos(0), vramPos(0), e), s: 20, fill: PREP, op: fade.value })
    out.push({ key: `q${m + 1}`, p: lerp(ramPos(1), ramPos(0), e), s: 20, fill: PREP })
    out.push({ key: `q${m + 2}`, p: lerp(ramPos(2), ramPos(1), e), s: 20, fill: PREP })
    if (uu >= 0.05) {
      const er = ease(clamp((uu - 0.05) / 0.35))
      out.push({ key: `q${m + 3}`, p: lerp(diskPos.value(diskIdx(m + 3)), ramPos(2), er), s: 18 + 2 * er, fill: mix(RAW, PREP, clamp((uu - 0.45) / 0.3)) })
    }
  }
  return out
})
const reading = computed(() => (!isRam.value && training.value && u.value > 0.05 && u.value < 0.4 ? diskIdx(n.value + 3) : -1))

// ---- status lines and arrows ----
const cpu = computed<[string, string]>(() => {
  const c = clock.value; const uu = u.value
  if (isRam.value) {
    if (props.step === 0) return ['idle', C.muted]
    if (props.step === 1) return c < 2 ? ['reading from disk', C.text] : c < 3.7 ? ['preprocessing', C.blue] : ['done: data ready', C.teal]
    return phase.value === 'copy' ? ['sending batch', C.blue] : ['waiting', C.muted]
  }
  if (!training.value) return ['idle', C.muted]
  return uu > 0.05 && uu < 0.4 ? ['reading next batch', C.text] : uu >= 0.45 && uu < 0.75 ? ['preprocessing', C.blue] : ['waiting', C.muted]
})
const diskArrowOn = computed(() => (isRam.value ? props.step === 1 && clock.value < 2 : reading.value >= 0))
const copyArrowOn = computed(() => phase.value === 'copy')
const a1 = arrow(254, 150, 326, 150, 10)
const a2 = arrow(564, 150, 646, 150, 10)
const counter = computed(() => {
  if (!training.value) return ''
  if (isRam.value) return `epoch ${Math.floor(n.value / perEpoch.value) + 1} · step ${(n.value % perEpoch.value) + 1} of ${perEpoch.value}`
  return `GPU: batch ${n.value + 1} · CPU: batch ${n.value + 4}`
})
const actW = computed(() => 222 * 0.32 * bs.value * actFrac.value)
</script>

<template>
  <div class="mt-1">
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" role="img" :aria-label="isRam ? 'The whole dataset is read from disk into RAM once and preprocessed by the CPU; each training step copies one batch to the GPU memory for the forward and backward passes' : 'The dataset stays on disk; the CPU reads and preprocesses the next few batches into RAM while the GPU computes on the current one'">
      <!-- legend + counter -->
      <rect x="20" y="10" width="14" height="14" rx="2" :style="{ fill: RAW }" />
      <text x="40" y="22" style="font-size: 13px" :style="{ fill: C.muted }">raw batch</text>
      <rect x="120" y="10" width="14" height="14" rx="2" :style="{ fill: PREP }" />
      <text x="140" y="22" style="font-size: 13px" :style="{ fill: C.muted }">preprocessed batch</text>
      <text :x="W - 20" y="22" text-anchor="end" style="font-size: 14px; font-weight: 700" :style="{ fill: C.text }">{{ counter }}</text>

      <!-- boxes -->
      <g v-for="(b, name) in BOX" :key="name">
        <rect :x="b[0]" y="38" :width="b[1]" height="200" rx="10" :style="{ fill: 'rgba(255,255,255,0.03)', stroke: C.grid, strokeWidth: 2 }" />
      </g>
      <text x="34" y="64" style="font-size: 18px; font-weight: 700" :style="{ fill: C.text }">Disk</text>
      <text x="236" y="64" text-anchor="end" style="font-size: 14px" :style="{ fill: C.muted }">2 TB SSD · slow</text>
      <text x="344" y="64" style="font-size: 18px; font-weight: 700" :style="{ fill: C.text }">RAM</text>
      <text x="546" y="64" text-anchor="end" style="font-size: 14px" :style="{ fill: C.muted }">64 GB</text>
      <text x="664" y="64" style="font-size: 18px; font-weight: 700" :style="{ fill: C.text }">VRAM</text>
      <text x="886" y="64" text-anchor="end" style="font-size: 14px" :style="{ fill: C.muted }">12 GB · fast</text>

      <!-- disk contents -->
      <rect v-for="i in N" :key="`d${i}`" :x="diskPos(i - 1)[0]" :y="diskPos(i - 1)[1]" :width="DS" :height="DS" rx="2"
            :style="{ fill: RAW, stroke: reading === i - 1 ? C.amber : 'none', strokeWidth: 3 }" />
      <text x="135" y="226" text-anchor="middle" style="font-size: 14px" :style="{ fill: C.muted }">dataset: {{ isRam ? '20 GB' : '500 GB' }}</text>

      <!-- RAM capacity slots -->
      <rect v-for="i in 24" :key="`s${i}`" :x="ramPos(i - 1)[0]" :y="ramPos(i - 1)[1]" width="20" height="20" rx="2"
            :style="{ fill: 'none', stroke: C.grid, strokeDasharray: '3 3' }" />
      <text x="445" y="226" text-anchor="middle" style="font-size: 14px" :style="{ fill: isRam ? (step >= 1 ? C.teal : C.muted) : (step >= 1 ? C.teal : C.red) }">
        {{ isRam ? (step >= 1 ? 'whole dataset, loaded once' : 'room for the dataset') : (step >= 1 ? 'a queue of the next few batches' : '500 GB won\'t fit') }}
      </text>

      <!-- VRAM contents -->
      <text x="664" y="98" style="font-size: 13px" :style="{ fill: C.muted }">model</text>
      <rect x="664" y="104" width="222" height="26" rx="4"
            :style="{ fill: 'rgba(167,139,250,0.18)', stroke: phase === 'backward' ? C.red : phase === 'update' ? C.teal : C.violet, strokeWidth: phase === 'backward' || phase === 'update' ? 3 : 1.5, transition: 'stroke .2s' }" />
      <text x="775" y="122" text-anchor="middle" style="font-size: 12.5px" :style="{ fill: C.text }">weights · gradients · optimizer state</text>
      <text x="664" y="166" style="font-size: 13px" :style="{ fill: C.muted }">batch</text>
      <rect v-for="j in bs" :key="`vs${j}`" :x="vramPos(j - 1)[0]" :y="vramPos(j - 1)[1]" width="20" height="20" rx="2"
            :style="{ fill: 'none', stroke: C.grid, strokeDasharray: '3 3' }" />
      <text x="886" y="166" text-anchor="end" style="font-size: 13px; font-weight: 700" :style="{ fill: bs > 1 ? C.red : C.text }">B = {{ 128 * bs }}</text>
      <text x="664" y="198" style="font-size: 13px" :style="{ fill: C.muted }">activations (grow with B)</text>
      <rect x="664" y="204" width="222" height="18" rx="3" :style="{ fill: 'none', stroke: C.grid, strokeDasharray: '4 3' }" />
      <rect x="664" y="204" :width="actW" height="18" rx="3" :style="{ fill: phase === 'backward' ? C.red : C.amber, fillOpacity: 0.75 }" />

      <!-- arrows -->
      <g :style="{ opacity: diskArrowOn ? 1 : 0.3, transition: 'opacity .3s' }">
        <path :d="a1.line" :style="{ stroke: C.text, strokeWidth: 2.5, fill: 'none' }" />
        <path :d="a1.head" :style="{ stroke: C.text, strokeWidth: 2.5, fill: 'none' }" />
        <text x="290" y="138" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.text }">read</text>
      </g>
      <g :style="{ opacity: copyArrowOn ? 1 : 0.3, transition: 'opacity .3s' }">
        <path :d="a2.line" :style="{ stroke: C.text, strokeWidth: 2.5, fill: 'none' }" />
        <path :d="a2.head" :style="{ stroke: C.text, strokeWidth: 2.5, fill: 'none' }" />
        <text x="605" y="138" text-anchor="middle" style="font-size: 13px" :style="{ fill: C.text }">copy</text>
        <text x="605" y="170" text-anchor="middle" style="font-size: 11px" :style="{ fill: C.muted }">.to("cuda")</text>
      </g>

      <!-- moving / resident batches -->
      <rect v-for="q in squares" :key="q.key" :x="q.p[0]" :y="q.p[1]" :width="q.s" :height="q.s" rx="2"
            :style="{ fill: q.fill, opacity: q.op ?? 1, stroke: q.ring ?? 'none', strokeWidth: 2.5 }" />

      <!-- processors -->
      <rect x="340" y="252" width="210" height="40" rx="6" :style="{ fill: C.bg, stroke: cpu[1], strokeWidth: 2, transition: 'stroke .3s' }" />
      <text x="353" y="277" style="font-size: 15px; font-weight: 700" :style="{ fill: C.text }">CPU</text>
      <text x="539" y="277" text-anchor="end" style="font-size: 13px" :style="{ fill: cpu[1] }">{{ cpu[0] }}</text>
      <rect x="670" y="252" width="210" height="40" rx="6" :style="{ fill: C.bg, stroke: GPU[phase][1], strokeWidth: 2, transition: 'stroke .3s' }" />
      <text x="683" y="277" style="font-size: 15px; font-weight: 700" :style="{ fill: C.text }">GPU</text>
      <text x="869" y="277" text-anchor="end" style="font-size: 13px" :style="{ fill: GPU[phase][1] }">{{ GPU[phase][0] }}</text>
      <line x1="445" y1="238" x2="445" y2="252" :style="{ stroke: C.grid, strokeWidth: 2 }" />
      <line x1="775" y1="238" x2="775" y2="252" :style="{ stroke: C.grid, strokeWidth: 2 }" />
    </svg>

    <div v-if="isRam" class="grid grid-cols-4 gap-3 mt-2 text-sm text-left">
      <div border="2 solid white/10" bg="white/5" rounded-lg px-3 py-1.5><b>Disk</b> holds everything but is slow. <b>RAM</b> is the CPU's workspace. <b>VRAM</b> is the GPU's: fast, but small.</div>
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid blue-800" bg="blue-800/20" rounded-lg px-3 py-1.5><b class="text-blue-300">Fits in RAM:</b> read the whole dataset and preprocess it once, before training starts.</div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid amber-800" bg="amber-800/20" rounded-lg px-3 py-1.5><b class="text-amber-300">Every step:</b> copy one batch to VRAM; the GPU runs forward, backward, and the update.</div>
      <div class="reveal" :class="{ shown: step >= 3 }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-1.5><b class="text-red-300">Double B:</b> half the steps, twice the activations. Too big: <code>CUDA out of memory</code>.</div>
    </div>
    <div v-else class="grid grid-cols-[1fr_1fr_1.4fr] gap-3 mt-2 text-sm text-left">
      <div border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-1.5><b class="text-red-300">Too big for RAM:</b> the dataset stays on disk, and each batch is read only when it's needed.</div>
      <div class="reveal" :class="{ shown: step >= 1 }" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-1.5><b class="text-teal-300">Pipeline:</b> while the GPU works on one batch, the CPU reads and preprocesses the next ones.</div>
      <div class="reveal" :class="{ shown: step >= 2 }" border="2 solid white/10" bg="white/5" rounded-lg px-3 py-1.5>
        <code class="text-xs">DataLoader(ds, batch_size=128, shuffle=True, num_workers=4, pin_memory=True)</code>
        <div class="mt-1">If reading can't keep up, the GPU waits.</div>
      </div>
    </div>
  </div>
</template>
