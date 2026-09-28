<script setup>
defineProps({step:{type:Number,default:0}})
const curve=g=>Array.from({length:121},(_,i)=>{const d=i/40;return `${i?'L':'M'}${60+120*d},${320-260*Math.exp(-g*d*d)}`}).join(' ')
</script>
<template>
<svg viewBox="0 0 480 400" role="img" aria-label="RBF similarity versus distance: gamma 0.5 decays slowly and gamma 2 decays rapidly">
 <path d="M60 45 V320 H440" fill="none" stroke="#94a3b8" stroke-width="2"/>
 <g fill="#94a3b8" style="font-size: 14px"><text x="42" y="65" style="font-size: 16px">1</text><text x="42" y="325" style="font-size: 16px">0</text><text x="60" y="345" style="font-size: 16px">0</text><text x="180" y="345" style="font-size: 16px">1</text><text x="300" y="345" style="font-size: 16px">2</text><text x="420" y="345" style="font-size: 16px">3</text></g>
 <text x="65" y="28" fill="#cbd5e1" style="font-size: 16px">similarity K(x, x′)</text>
 <text x="240" y="378" fill="#cbd5e1" style="font-size: 16px" text-anchor="middle">distance ‖x − x′‖</text>
 <path :d="curve(.5)" fill="none" stroke="#5eead4" stroke-width="3"/>
 <text x="250" y="92" fill="#5eead4" style="font-size: 17px">γ = 0.5: broader</text>
 <g v-if="step>=3"><path :d="curve(2)" fill="none" stroke="#f472b6" stroke-width="3"/><text x="250" y="120" fill="#f9a8d4" style="font-size: 17px">γ = 2: more local</text></g>
</svg>
</template>
