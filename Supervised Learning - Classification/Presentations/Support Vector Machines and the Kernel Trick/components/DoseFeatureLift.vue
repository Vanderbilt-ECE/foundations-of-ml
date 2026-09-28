<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
const props = defineProps({ step: { type: Number, default: 0 }, problem: Boolean })
const doses = [5, 10, 15, 38, 44, 50, 56, 62, 85, 90, 95]
const effective = d => d > 25 && d < 75
const target = computed(() => !props.problem && props.step >= 1 ? 1 : 0)
const t = ref(target.value)
let frame
watch(target, to => {
  cancelAnimationFrame(frame)
  const from = t.value, started = performance.now()
  const animate = now => {
    const u = Math.min((now - started) / 1500, 1), ease = u*u*(3-2*u)
    t.value = from + (to-from)*ease
    if (u < 1) frame = requestAnimationFrame(animate)
  }
  frame = requestAnimationFrame(animate)
})
onBeforeUnmount(() => cancelAnimationFrame(frame))
const px = d => 60 + 8*d
const baseline = computed(() => 190+150*t.value)
const py = d => baseline.value - .03*d*d*t.value
const curve = computed(() => Array.from({length:101},(_,d)=>`${d?'L':'M'}${px(d)},${py(d)}`).join(' '))
const sep = computed(() => !props.problem && props.step >= 2 && t.value > .99)
</script>

<template>
<svg class="dose-lift" viewBox="0 0 920 410" role="img" :data-progress="t" :data-step="step" :aria-label="problem ? 'Illustrative trial: ineffective at low and high doses, effective in the middle; no single threshold separates the classes' : 'The same dosage points animate vertically into coordinates dose and dose squared, followed by a linear separating boundary'">
  <g v-if="problem" fill="#cbd5e1" style="font-size: 17px" text-anchor="middle">
    <text x="145" y="75" fill="#93c5fd" style="font-size: 16px">too low: ineffective</text>
    <text x="460" y="75" fill="#fdba74" style="font-size: 16px">middle doses: effective</text>
    <text x="770" y="75" fill="#93c5fd" style="font-size: 16px">too high: ineffective</text>
  </g>
  <g v-if="problem && step >= 1 && step < 2">
    <rect x="260" y="105" width="600" height="130" fill="#fb923c12"/>
    <line x1="260" y1="100" x2="260" y2="240" stroke="#f8fafc" stroke-width="3"/>
    <text x="270" y="125" fill="#f8fafc" style="font-size: 16px">predict effective to the right?</text>
    <g v-for="d in [85,90,95]" :key="d"><circle :cx="px(d)" cy="190" r="16" fill="none" stroke="#f472b6" stroke-width="2"/></g>
    <text x="705" y="275" fill="#f9a8d4" style="font-size: 17px">high doses are wrong</text>
  </g>
  <g v-if="problem && step >= 2">
    <rect x="60" y="105" width="600" height="130" fill="#fb923c12"/>
    <line x1="660" y1="100" x2="660" y2="240" stroke="#f8fafc" stroke-width="3"/>
    <text x="310" y="125" fill="#f8fafc" style="font-size: 16px">predict effective to the left?</text>
    <g v-for="d in [5,10,15]" :key="d"><circle :cx="px(d)" cy="190" r="16" fill="none" stroke="#f472b6" stroke-width="2"/></g>
    <text x="75" y="275" fill="#f9a8d4" style="font-size: 17px">low doses are wrong</text>
  </g>
  <g :opacity="t">
    <line x1="60" y1="340" x2="60" y2="32" stroke="#94a3b8" stroke-width="2"/>
    <g v-for="v in [0,2500,5000,7500,10000]" :key="v">
      <line x1="54" :y1="340-.03*v" x2="860" :y2="340-.03*v" stroke="#94a3b8" stroke-opacity=".14"/>
      <text x="49" :y="345-.03*v" text-anchor="end" fill="#94a3b8" style="font-size: 12px">{{ v.toLocaleString('en-US') }}</text>
    </g>
    <text x="70" y="23" fill="#cbd5e1" style="font-size: 15px">dose² (mg²)</text>
    <path :d="curve" fill="none" stroke="#94a3b8" stroke-opacity=".45" stroke-width="1.5"/>
    <line v-for="d in doses" :key="d" :x1="px(d)" y1="340" :x2="px(d)" :y2="py(d)" stroke="#94a3b8" stroke-opacity=".2" stroke-dasharray="3 4"/>
  </g>
  <line x1="50" :y1="baseline" x2="878" :y2="baseline" stroke="#94a3b8" stroke-width="2.5"/>
  <polygon :points="`878,${baseline-6} 890,${baseline} 878,${baseline+6}`" fill="#94a3b8"/>
  <g v-for="d in [0,10,20,30,40,50,60,70,80,90,100]" :key="d">
    <line :x1="px(d)" :y1="baseline-5" :x2="px(d)" :y2="baseline+6" stroke="#94a3b8"/>
    <text :x="px(d)" :y="baseline+26" text-anchor="middle" fill="#94a3b8" style="font-size: 14px">{{ d }}</text>
  </g>
  <text x="870" :y="baseline+53" text-anchor="end" fill="#cbd5e1" style="font-size: 16px">dose d (mg)</text>
  <g v-if="sep">
    <path d="M210 340 L860 96.25" stroke="#5eead4" stroke-width="3"/>
    <text x="472" y="174" fill="#5eead4" style="font-size: 17px">z = 100d − 1875</text>
    <text x="386" y="320" fill="#fdba74" style="font-size: 16px">effective below the line</text>
  </g>
  <g v-if="!problem && step >= 3 && t > .99">
    <line v-for="d in [25,75]" :key="d" :x1="px(d)" :x2="px(d)" :y1="py(d)" y2="340" stroke="#f472b6" stroke-width="1.5" stroke-dasharray="4 4"/>
    <circle v-for="d in [25,75]" :key="d" :cx="px(d)" :cy="py(d)" r="5" fill="#f472b6"/>
    <text x="260" y="389" text-anchor="middle" fill="#f9a8d4" style="font-size: 15px">25</text>
    <text x="660" y="389" text-anchor="middle" fill="#f9a8d4" style="font-size: 15px">75</text>
  </g>
  <circle v-for="d in doses" :key="d" class="dose-point" :data-dose="d" :data-class="effective(d)?1:-1" :cx="px(d)" :cy="py(d)" r="8" :fill="effective(d)?'#fb923c':'#60a5fa'" stroke="#0b1220" stroke-width="2"/>
</svg>
</template>
