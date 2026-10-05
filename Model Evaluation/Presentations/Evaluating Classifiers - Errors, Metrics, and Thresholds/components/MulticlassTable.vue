<script setup lang="ts">
withDefaults(defineProps<{ focus?: string }>(), { focus: '' })
const labels = ['Deer', 'Fox', 'Dog']
const counts = [[45, 3, 2], [1, 12, 7], [0, 4, 26]]
function highlighted(row: number, col: number) {
  return (focus === 'precision' && col === 1) || (focus === 'recall' && row === 1)
}
function outcome(row: number, col: number) {
  if (row === 1 && col === 1) return 'TP'
  if (col === 1) return 'FP'
  if (row === 1) return 'FN'
  return 'TN'
}
</script>

<template>
  <table class="matrix multiclass-matrix" aria-label="Wildlife confusion matrix: actual rows, predicted columns">
    <thead><tr><th>Actual /<br>predicted</th><th v-for="label in labels" :key="label">{{ label }}</th></tr></thead>
    <tbody>
      <tr v-for="(row, i) in counts" :key="labels[i]">
        <th>{{ labels[i] }}</th>
        <td v-for="(count, j) in row" :key="j" :class="[i === j ? 'correct' : 'error', { focus: highlighted(i, j) }]">
          {{ count }}<small v-if="focus === 'one-vs-rest'">{{ outcome(i, j) }}</small>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.multiclass-matrix td { padding: 12px 8px; }
.multiclass-matrix th { padding: 8px 5px; font-size: 16px; }
</style>
