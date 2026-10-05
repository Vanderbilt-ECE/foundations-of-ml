<script setup lang="ts">
withDefaults(defineProps<{tn?:number;fp?:number;fn?:number;tp?:number;focus?:string;symbolic?:boolean}>(),{tn:810,fp:90,fn:20,tp:80,focus:'',symbolic:false})
</script>
<template>
<table class="matrix" aria-label="Confusion matrix: rows actual, columns predicted">
<thead><tr><th>Actual / predicted</th><th>Legitimate</th><th>Fraud</th></tr></thead>
<tbody>
<tr><th>Legitimate</th><td class="correct" :class="{focus:focus==='accuracy'||focus==='negative'}">{{symbolic?'TN':tn}}<small v-if="!symbolic">TN</small></td><td class="error" :class="{focus:focus==='precision'||focus==='negative'}">{{symbolic?'FP':fp}}<small v-if="!symbolic">FP</small></td></tr>
<tr><th>Fraud</th><td class="error" :class="{focus:focus==='recall'}">{{symbolic?'FN':fn}}<small v-if="!symbolic">FN</small></td><td class="correct" :class="{focus:focus==='precision'||focus==='recall'||focus==='accuracy'}">{{symbolic?'TP':tp}}<small v-if="!symbolic">TP</small></td></tr>
</tbody></table>
</template>
