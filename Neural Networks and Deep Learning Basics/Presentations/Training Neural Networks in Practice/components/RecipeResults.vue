<script setup lang="ts">
// The recipe's result on California Housing's held-out test set (measured), plus how to reproduce it.
</script>

<template>
  <div border="2 solid white/10" bg="white/5" rounded-lg px-4 py-3 class="text-left">
    <div class="font-bold mb-1">California Housing, test set</div>
    <div class="text-sm opacity-80 mb-2">Typical error per district, data never used for training or tuning:</div>
    <BaselineBars :width="400" />
    <div class="text-xs opacity-75 mt-2"><code>uv run california_housing_mlp.py</code> reproduces every number in this lecture.</div>
  </div>
</template>
