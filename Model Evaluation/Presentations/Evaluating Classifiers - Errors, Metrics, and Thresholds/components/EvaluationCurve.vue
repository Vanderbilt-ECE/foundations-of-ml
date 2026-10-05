<script setup lang="ts">
import {computed} from 'vue'
import bins from '../examples/fraud-data.json'
const props=withDefaults(defineProps<{kind?:string}>(),{kind:'roc'})
const points=computed(()=>{let tp=0,fp=0;const a=[props.kind==='roc'?[0,0]:[0,1]];for(const b of bins){const prev=props.kind==='roc'?[fp/900,tp/100]:[tp/100,tp/(tp+fp)];tp+=b.positive;fp+=b.negative;const next=props.kind==='roc'?[fp/900,tp/100]:[tp/100,tp/(tp+fp)];if(props.kind!=='roc')a.push([prev[0],next[1]]);a.push(next)}return a})
const xy=(p:number[])=>[65+400*p[0],285-235*p[1]]
const path=computed(()=>points.value.map((p,i)=>`${i?'L':'M'}${xy(p).join(',')}`).join(' '))
const selected=computed(()=>xy(props.kind==='roc'?[.1,.8]:[.8,80/170]))
</script>
<template>
<svg viewBox="0 0 510 345" role="img" :aria-label="kind==='roc'?'ROC curve computed from the illustrative fraud scores':'Precision-recall step curve computed from the illustrative fraud scores'" style="width:100%;max-height:335px">
<path d="M65,50 V285 H465" fill="none" stroke="#94a3b8" stroke-width="2"/>
<path v-if="kind==='roc'" d="M65,285 L465,50" stroke="#94a3b8" stroke-dasharray="6 5"/>
<path v-else d="M65,261.5 H465" stroke="#94a3b8" stroke-dasharray="6 5"/>
<path :d="path" fill="none" stroke="#2dd4bf" stroke-width="4"/>
<circle :cx="selected[0]" :cy="selected[1]" r="6" fill="#fbbf24"/>
<g fill="#cbd5e1" font-size="17"><text x="57" y="310">0</text><text x="453" y="310">1</text><text x="35" y="289">0</text><text x="35" y="55">1</text><text x="240" y="336" text-anchor="middle">{{kind==='roc'?'False-positive rate':'Recall'}}</text><text transform="translate(20 165) rotate(-90)" text-anchor="middle">{{kind==='roc'?'Recall / TPR':'Precision'}}</text></g>
<text :x="selected[0]+12" :y="selected[1]+22" fill="#fbbf24" font-size="17">t = 0.50</text>
</svg>
</template>

<style scoped>
svg text { font-size: 17px !important; }
</style>
