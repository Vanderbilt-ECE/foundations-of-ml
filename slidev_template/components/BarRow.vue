<script setup lang="ts">
defineProps<{
  label: string
  value: string
  pct: string | number
  color?: string
}>()
</script>

<template>
  <div class="bar-row">
    <div class="bar-label">{{ label }}</div>
    <div class="bar-track">
      <div
        class="bar-fill"
        :style="{ width: pct + '%', backgroundColor: color || '#2dd4bf' }"
      />
    </div>
    <div class="bar-value">{{ value }}</div>
  </div>
</template>

<style scoped>
.bar-row {
  display: grid;
  grid-template-columns: 9rem 1fr 3.5rem;
  align-items: center;
  gap: 0.6rem;
  margin: 0.45rem 0;
}
.bar-label {
  font-size: 0.85rem;
  text-align: right;
  opacity: 0.85;
}
.bar-track {
  background: rgba(148, 163, 184, 0.18);
  border-radius: 9999px;
  height: 0.85rem;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.6s ease;
}
.bar-value {
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
