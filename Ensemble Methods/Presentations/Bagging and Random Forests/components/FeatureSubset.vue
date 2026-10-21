<script setup lang="ts">
// Three nodes of one random-forest tree on California housing. Each node draws a fresh random
// subset of m = 3 of the 8 features (lit chips) and splits on the best of those (outlined chip).
// Colors use inline style: UnoCSS attributify rewrites fill / fill-opacity attributes
const names = ['MedInc', 'HouseAge', 'AveRooms', 'AveBedrms', 'Population', 'AveOccup', 'Latitude', 'Longitude']
const nodes = [
  { key: 'root', x: 130, y: 10, drawn: [0, 4, 5], best: 0 },
  { key: 'left', x: 10, y: 196, drawn: [1, 2, 6], best: 6 },
  { key: 'right', x: 250, y: 196, drawn: [3, 5, 7], best: 5 },
]
const bw = 200
const chipW = 44
const chipH = 26
const chip = (k: number) => ({ dx: 8 + (k % 4) * (chipW + 2), dy: 30 + Math.floor(k / 4) * (chipH + 4) })
const bh = 30 + 2 * (chipH + 4) + 30
</script>

<template>
  <svg role="img" aria-label="Three tree nodes each drawing 3 of 8 features: the root draws MedInc, Population and AveOccup and splits on MedInc; the left child draws HouseAge, AveRooms and Latitude and splits on Latitude; the right child draws AveBedrms, AveOccup and Longitude and splits on AveOccup." viewBox="0 0 460 330" class="w-full">
    <line x1="230" :y1="10 + bh" x2="110" y2="196" :style="{ stroke: '#475569', strokeWidth: 2 }" />
    <line x1="230" :y1="10 + bh" x2="350" y2="196" :style="{ stroke: '#475569', strokeWidth: 2 }" />
    <g v-for="n in nodes" :key="n.key" :transform="`translate(${n.x} ${n.y})`">
      <rect :width="bw" :height="bh" rx="10" :style="{ fill: '#0f172a', stroke: '#2dd4bf', strokeWidth: 2 }" />
      <text :x="bw / 2" y="20" text-anchor="middle" :style="{ fill: '#94a3b8', fontSize: '12px' }">draw 3 of 8 features</text>
      <g v-for="(nm, k) in names" :key="nm" :transform="`translate(${chip(k).dx} ${chip(k).dy})`">
        <rect :width="chipW" :height="chipH" rx="5"
          :style="{ fill: n.drawn.includes(k) ? '#2dd4bf' : '#334155', fillOpacity: n.drawn.includes(k) ? 0.3 : 0.35, stroke: k === n.best ? '#fbbf24' : 'none', strokeWidth: 2.5 }" />
        <text :x="chipW / 2" y="17" text-anchor="middle" :style="{ fill: n.drawn.includes(k) ? '#e2e8f0' : '#64748b', fontSize: '9.5px' }">{{ nm.replace('Ave', '').replace('Population', 'Pop').replace('HouseAge', 'Age').replace('Latitude', 'Lat').replace('Longitude', 'Long') }}</text>
      </g>
      <text :x="bw / 2" :y="bh - 10" text-anchor="middle" :style="{ fill: '#fbbf24', fontSize: '13px', fontWeight: 700 }">split on {{ names[n.best] }}</text>
    </g>
  </svg>
</template>
