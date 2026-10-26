<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import TemplateBottom from '../../../slidev_template/global-bottom.vue'

// Sliders and buttons on the slides keep keyboard focus after a click, and then swallow the arrow keys, space and
// page up/down that a presenter's clicker sends. Release focus as soon as the mouse lets go.
function release() {
  const el = document.activeElement as HTMLElement | null
  if (el?.matches('input[type=range], button')) el.blur()
}
onMounted(() => document.addEventListener('pointerup', release))
onBeforeUnmount(() => document.removeEventListener('pointerup', release))
</script>

<template>
  <TemplateBottom />
</template>
