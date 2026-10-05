<script setup lang="ts">
import {computed,ref} from 'vue'
import bins from '../examples/fraud-data.json'
const threshold=ref(.5)
const counts=computed(()=>bins.reduce((a,b)=>{const flag=b.score>=threshold.value;a[flag?'tp':'fn']+=b.positive;a[flag?'fp':'tn']+=b.negative;return a},{tp:0,fp:0,tn:0,fn:0}))
const precision=computed(()=>counts.value.tp/(counts.value.tp+counts.value.fp))
const recall=computed(()=>counts.value.tp/100)
const f1=computed(()=>2*counts.value.tp/(2*counts.value.tp+counts.value.fp+counts.value.fn))
const pct=(x:number)=>Number.isFinite(x)?(100*x).toFixed(1)+'%':'undefined'
</script>
<template>
<div class="lab">
<div style="display:flex;align-items:center;gap:20px;margin-bottom:14px"><label for="threshold">Flag when score ≥ <strong>{{threshold.toFixed(2)}}</strong></label><input id="threshold" v-model.number="threshold" type="range" min="0" max="1" step=".01" style="width:320px" /></div>
<div style="margin-bottom:14px"><button v-for="t in [.8,.5,.2]" :key="t" @click="threshold=t">t = {{t.toFixed(2)}}</button></div>
<div class="columns"><ConfusionTable v-bind="counts"/><div>
<p>Alerts: <strong>{{counts.tp+counts.fp}}</strong> of 1,000</p>
<p>Recall (sensitivity): <strong>{{pct(recall)}}</strong></p>
<p>Precision: <strong>{{pct(precision)}}</strong></p>
<p>F1: <strong>{{f1.toFixed(3)}}</strong></p>
<p>Accuracy: <strong>{{pct((counts.tp+counts.tn)/1000)}}</strong></p>
</div></div>
<p class="caption">Illustrative validation cohort. Scores occur at 0.90, 0.70, 0.50, 0.30, and 0.10.</p>
</div>
</template>
