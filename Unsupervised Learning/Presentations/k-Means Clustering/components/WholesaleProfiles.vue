<script setup lang="ts">
// Wholesale K = 4 cluster profiles (data/wholesale.json → profiles).
// Cell color = cluster mean of the standardized log spend (teal above average, red below);
// cell text = the cluster's median annual spend in that category.
// Right: how many of each cluster's customers are hotels/restaurants/cafés vs retailers,
// a column k-means never saw. `show` = number of rows revealed; `channel` reveals the last column.
import d from '../data/wholesale.json'
import { color } from '../utils/kmeans'

withDefaults(defineProps<{ show?: number, channel?: boolean }>(), { show: 4, channel: true })
const names = ['Small food-service accounts', 'Small grocery-type shops', 'Fresh-heavy restaurants', 'Big grocery retailers']
const cols = d.cols.map(c => c.replace('Detergents_Paper', 'Detergent/Paper').replace('Delicassen', 'Deli'))
const bg = (z: number) => {
  const a = Math.min(Math.abs(z) / 1.3, 1) * 0.75
  return z >= 0 ? `rgba(45, 212, 191, ${a})` : `rgba(248, 113, 113, ${a})`
}
const money = (v: number) => (v >= 1000 ? `${(v / 1000).toFixed(1)}k` : `${Math.round(v)}`)
</script>

<template>
  <table class="prof">
    <thead>
      <tr>
        <th class="text-left">cluster</th>
        <th>n</th>
        <th v-for="c in cols" :key="c">{{ c }}</th>
        <th class="ch" :class="{ off: !channel }">Hotel/Rest./Café · Retail</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(p, k) in d.profiles" :key="k" class="row" :class="{ off: k >= show }">
        <td class="name font-bold whitespace-nowrap"><span class="dot" :style="{ background: color(k) }" />{{ names[k] }}</td>
        <td class="font-mono opacity-80">{{ p.n }}</td>
        <td v-for="(z, j) in p.z" :key="j" class="cell font-mono" :style="{ background: bg(z) }">{{ money(p.median[j]) }}</td>
        <td class="ch" :class="{ off: !channel }">
          <div class="flex h-4 rounded overflow-hidden w-36 mx-auto">
            <div :style="{ flexGrow: p.horeca, background: '#fbbf24' }" />
            <div :style="{ flexGrow: p.retail, background: '#60a5fa' }" />
          </div>
          <div class="text-xs font-mono opacity-80 mt-0.5">{{ p.horeca }} · {{ p.retail }}</div>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.prof { width: 100%; border-collapse: separate; border-spacing: 3px; font-size: 0.82rem; }
.prof th { font-weight: 600; opacity: 0.75; font-size: 0.72rem; padding: 2px 4px; }
.prof td { padding: 6px 6px; text-align: center; }
.prof td.name { text-align: left; }
.cell { border-radius: 5px; }
.dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }
.row, .ch { transition: opacity 0.5s ease; }
.off { opacity: 0; }
</style>
