<script setup>
import { computed, ref, watch, onBeforeUnmount } from 'vue'
const props = defineProps({ step: {type:Number,default:0} })
const points = [
  ...Array.from({length:16},(_,i)=>{ const a=2*Math.PI*i/16,r=1.9+.15*(i%3);return {x:r*Math.cos(a),y:r*Math.sin(a),outer:true} }),
  ...Array.from({length:8},(_,i)=>{const a=2*Math.PI*i/8+.2,r=.45+.2*(i%3);return {x:r*Math.cos(a),y:r*Math.sin(a),outer:false}}),
  {x:.05,y:-.05,outer:false},
].map((p,i)=>({...p,z:p.x*p.x+p.y*p.y,id:i}))
const target = computed(()=>props.step>=2?1:0)
const t=ref(target.value);let frame
watch(target,to=>{cancelAnimationFrame(frame);const from=t.value,started=performance.now();const tick=now=>{const u=Math.min((now-started)/1800,1);t.value=from+(to-from)*u*u*(3-2*u);if(u<1)frame=requestAnimationFrame(tick)};frame=requestAnimationFrame(tick)})
onBeforeUnmount(()=>cancelAnimationFrame(frame))
const project=(x,y,z=0)=>({x:340+90*x+t.value*(-10*x+40*y),y:230-90*y+t.value*(130+18*x+62*y-45*z)})
const path=ps=>ps.map((p,i)=>`${i?'L':'M'}${project(...p).x},${project(...p).y}`).join(' ')+' Z'
const plane=computed(()=>path([[-2.3,-2.3,2],[2.3,-2.3,2],[2.3,2.3,2],[-2.3,2.3,2]]))
const floor=computed(()=>path([[-2.3,-2.3,0],[2.3,-2.3,0],[2.3,2.3,0],[-2.3,2.3,0]]))
const circle=computed(()=>path(Array.from({length:65},(_,i)=>[Math.sqrt(2)*Math.cos(i*Math.PI/32),Math.sqrt(2)*Math.sin(i*Math.PI/32),0])))
</script>
<template>
<svg viewBox="0 0 680 500" role="img" class="ring-lift" :data-progress="t" :data-step="step" aria-label="An inner orange class surrounded by a blue ring lifts from the x1 x2 plane to height x1 squared plus x2 squared; the plane z equals 2 separates the classes">
  <path :d="floor" fill="#94a3b808" stroke="#94a3b8" stroke-opacity=".2"/>
  <g stroke="#94a3b8" stroke-width="1.5">
    <line :x1="project(-2.5,0).x" :y1="project(-2.5,0).y" :x2="project(2.5,0).x" :y2="project(2.5,0).y"/>
    <line :x1="project(0,-2.5).x" :y1="project(0,-2.5).y" :x2="project(0,2.5).x" :y2="project(0,2.5).y"/>
  </g>
  <text :x="project(2.5,0).x+10" :y="project(2.5,0).y+5" fill="#cbd5e1" style="font-size: 18px">x₁</text>
  <text :x="project(0,2.5).x+8" :y="project(0,2.5).y+4" fill="#cbd5e1" style="font-size: 18px">x₂</text>
  <text :x="project(0,0).x-15" :y="project(0,0).y+20" fill="#94a3b8" style="font-size: 14px">0</text>
  <g v-if="step === 1" opacity=".85">
    <line x1="165" y1="65" x2="515" y2="395" stroke="#f472b6" stroke-width="2" stroke-dasharray="7 5"/>
    <text x="50" y="30" fill="#f9a8d4" style="font-size: 17px">a line leaves blue points on both sides</text>
  </g>
  <g :opacity="t">
    <line :x1="project(-2.3,-2.3,0).x" :y1="project(-2.3,-2.3,0).y" :x2="project(-2.3,-2.3,6).x" :y2="project(-2.3,-2.3,6).y" stroke="#94a3b8" stroke-width="2"/>
    <text x="35" y="84" fill="#cbd5e1" style="font-size: 18px">z = x₁² + x₂²</text>
    <g v-for="p in points" :key="p.id">
      <line :x1="project(p.x,p.y).x" :y1="project(p.x,p.y).y" :x2="project(p.x,p.y,p.z).x" :y2="project(p.x,p.y,p.z).y" stroke="#94a3b8" stroke-opacity=".3" stroke-dasharray="3 4"/>
      <circle :cx="project(p.x,p.y).x" :cy="project(p.x,p.y).y" r="3" :fill="p.outer?'#60a5fa':'#fb923c'" opacity=".35"/>
    </g>
  </g>
  <circle v-for="p in points.filter(p=>!p.outer)" :key="p.id" class="ring-point" :data-id="p.id" :data-z="p.z" :cx="project(p.x,p.y,p.z).x" :cy="project(p.x,p.y,p.z).y" r="7" fill="#fb923c" stroke="#0b1220" stroke-width="1.5"/>
  <g v-if="step>=3 && t>.99">
    <path :d="plane" fill="#2dd4bf25" stroke="#5eead4" stroke-width="2"/>
    <text x="505" y="330" fill="#5eead4" style="font-size: 18px">plane: z = 2</text>
  </g>
  <circle v-for="p in points.filter(p=>p.outer)" :key="p.id" class="ring-point" :data-id="p.id" :data-z="p.z" :cx="project(p.x,p.y,p.z).x" :cy="project(p.x,p.y,p.z).y" r="7" fill="#60a5fa" stroke="#0b1220" stroke-width="1.5"/>
  <g v-if="step>=4 && t>.99">
    <path :d="circle" fill="none" stroke="#f472b6" stroke-width="2.5" stroke-dasharray="5 4"/>
    <text x="155" y="483" fill="#f9a8d4" style="font-size: 17px">original-space boundary: x₁² + x₂² = 2</text>
  </g>
</svg>
</template>
