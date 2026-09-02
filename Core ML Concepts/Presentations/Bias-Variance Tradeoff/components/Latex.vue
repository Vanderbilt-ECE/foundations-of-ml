<script setup lang="ts">
import katex from '../../../../slidev_template/node_modules/katex/dist/katex.mjs'
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  expression: string
  display?: boolean
}>(), {
  display: false,
})

const rendered = computed(() => katex.renderToString(props.expression, {
  displayMode: props.display,
  throwOnError: false,
}))
</script>

<template>
  <component :is="display ? 'div' : 'span'" v-html="rendered" />
</template>
