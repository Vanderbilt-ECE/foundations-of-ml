<script setup lang="ts">
// Title figure (data/em.json): the converged EM fit of three Gaussians, shown static.
import d from '../data/em.json'

const LAST = 12 // iteration shown; the fit has converged by then
const mix = d.frames[LAST]
</script>

<template>
  <GmmPlot
    :pts="d.pts" :mix="mix" :color-mix="mix" mode="soft" :levels="[1, 2]"
    :w="760" :h="280" :r="2.6" :ms="0" label="Three fitted Gaussian ellipses over unlabeled points"
  />
</template>
