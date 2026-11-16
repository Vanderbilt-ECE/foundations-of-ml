<script setup lang="ts">
// The demo's real early-stopping run, replayed epoch by epoch: the best validation score so far (star),
// the patience window since then (shaded), and the stop. Print shows the end state.
import { computed, ref } from 'vue'
import demo from '../data/demo.json'
import { C, useActive, useLoop } from '../utils/plot'

const { isPrintMode } = useActive()
const E = demo.early
const N = E.val.length; const PATIENCE = 20
const t = ref(0)
useLoop((dt) => { t.value = (t.value + dt * 7) % (N + 18) }, () => { t.value = 0 })
const epoch = computed(() => (isPrintMode.value ? N : Math.max(1, Math.min(N, Math.floor(t.value)))))
const best = computed(() => {
  let b = 0
  for (let i = 1; i < epoch.value; i++) if (E.val[i] < E.val[b]) b = i
  return { epoch: b + 1, val: E.val[b] }
})
const waited = computed(() => epoch.value - best.value.epoch)
const stopped = computed(() => epoch.value >= N)
const series = [
  { y: E.train, color: C.blue, width: 2.5 },
  { y: E.val, color: C.amber, width: 3 },
]
</script>

<template>
  <div class="grid grid-cols-[1.75fr_1fr] gap-5 items-center mt-3 text-left">
    <LineChart
      :series="series" :draw="(epoch - 1) / 47" :width="620" :height="340" :x-range="[1, 48]" :y-range="[0.38, 0.76]"
      :x-ticks="[1, 10, 20, 30, 40]" :y-ticks="[0.5, 0.6, 0.7]" x-label="epoch" y-label="RMSE ($100k)" :font="13"
      :bands="waited > 0 ? [{ x0: best.epoch, x1: epoch, color: C.violet, opacity: 0.16, label: `patience ${waited}/${PATIENCE}` }] : []"
      :points="[{ x: best.epoch, y: best.val, color: C.teal, r: 7, label: 'best', dy: -12 }]"
      :vlines="stopped ? [{ x: N, color: C.red, label: 'stop', dy: -4, anchor: 'end' }] : []"
      :legend="[{ color: C.blue, text: 'training' }, { color: C.amber, text: 'validation' }]" legend-at="bl"
    />
    <div class="flex flex-col gap-3 text-sm">
      <div border="2 solid teal-800" bg="teal-800/20" rounded-lg px-3 py-2>
        <b class="text-teal-300">Epoch {{ epoch }}.</b> Best validation so far: <b>{{ best.val.toFixed(3) }}</b> at epoch <b>{{ best.epoch }}</b> (checkpoint saved).
      </div>
      <div border="2 solid violet-800" bg="violet-800/20" rounded-lg px-3 py-2>
        <b class="text-violet-300">Epochs without improvement:</b> {{ waited }} of {{ PATIENCE }}
      </div>
      <div class="reveal" :class="{ shown: stopped }" border="2 solid red-800" bg="red-800/20" rounded-lg px-3 py-2>
        <b class="text-red-300">Stopped at epoch {{ N }}.</b> Reload the epoch-{{ E.best_epoch }} weights. Test RMSE: <b>{{ demo.test.mlp.toFixed(3) }}</b> (about ${{ Math.round(demo.test.mlp * 100) }}k).
      </div>
    </div>
  </div>
</template>
