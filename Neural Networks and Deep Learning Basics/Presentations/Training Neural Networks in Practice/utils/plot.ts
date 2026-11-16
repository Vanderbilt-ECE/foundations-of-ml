// Shared helpers for the slide components: palette, pointer mapping, tweens, and a
// requestAnimationFrame loop that only runs while its slide is showing.
// (Adapted from the Dimensionality Reduction deck's utils/plot.ts.)
import type { Ref } from 'vue'
import { useNav, useSlideContext } from '@slidev/client'
import { computed, onBeforeUnmount, ref, watch } from 'vue'

export { rng } from './rng.ts'

export const C = {
  teal: '#2dd4bf',
  blue: '#60a5fa',
  violet: '#a78bfa',
  amber: '#fbbf24',
  orange: '#fb923c',
  red: '#f87171',
  text: '#e2e8f0',
  muted: '#94a3b8',
  dim: '#64748b',
  grid: '#334155',
  bg: '#0b1020',
}

export const fmt = (v: number, d = 1) => v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x))
export const ease = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2)

// Pointer position -> viewBox coordinates (the slide is CSS-scaled and the SVG may be letterboxed).
export function toLocal(e: PointerEvent | MouseEvent, el: Element, W: number, H: number) {
  const r = el.getBoundingClientRect()
  const k = Math.min(r.width / W, r.height / H)
  return [(e.clientX - r.left - (r.width - W * k) / 2) / k, (e.clientY - r.top - (r.height - H * k) / 2) / k]
}

// Is this component's slide on screen? In print/PDF export nothing animates.
export function useActive() {
  const { $page } = useSlideContext()
  const { currentSlideNo, isPrintMode } = useNav()
  const active = computed(() => currentSlideNo.value === $page.value && !isPrintMode.value)
  return { active, isPrintMode }
}

// Call tick(dt seconds, elapsed seconds) every animation frame while the slide is showing.
// onStart runs each time the slide becomes active (to restart an animation from the beginning).
export function useLoop(tick: (dt: number, t: number) => void, onStart?: () => void) {
  const { active } = useActive()
  let raf = 0; let last = 0; let t0 = 0
  const frame = (now: number) => {
    const dt = Math.min(0.05, (now - last) / 1000)
    last = now
    tick(dt, (now - t0) / 1000)
    raf = requestAnimationFrame(frame)
  }
  watch(active, (on) => {
    cancelAnimationFrame(raf)
    if (!on) return
    onStart?.()
    last = t0 = performance.now()
    raf = requestAnimationFrame(frame)
  }, { immediate: true })
  onBeforeUnmount(() => cancelAnimationFrame(raf))
  return { active }
}

// Animate a number, an array, or an array of points toward each new target value.
// Starts at the current target, so a freshly mounted slide (or a PDF export) shows the final state immediately.
export function useTween<T extends number | number[] | number[][]>(target: () => T, ms = 700): Ref<T> {
  const clone = (v: T) => JSON.parse(JSON.stringify(v)) as T
  const cur = ref(clone(target())) as Ref<T>
  let raf = 0
  watch(target, (to) => {
    const from = clone(cur.value) as any
    const t0 = performance.now()
    cancelAnimationFrame(raf)
    const lerp = (a: any, b: any, e: number): any =>
      Array.isArray(b) ? b.map((v, i) => lerp(a?.[i], v, e)) : (typeof a === 'number' ? a + (b - a) * e : b)
    const tick = (t: number) => {
      const u = Math.min(1, (t - t0) / ms)
      cur.value = lerp(from, to, ease(u))
      if (u < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
  })
  onBeforeUnmount(() => cancelAnimationFrame(raf))
  return cur
}

// SVG arrow from (x1, y1) to (x2, y2): the shaft and an open arrowhead, as two path strings.
export function arrow(x1: number, y1: number, x2: number, y2: number, head = 9) {
  const a = Math.atan2(y2 - y1, x2 - x1)
  const h = (o: number) => `${(x2 - head * Math.cos(a + o)).toFixed(1)},${(y2 - head * Math.sin(a + o)).toFixed(1)}`
  return { line: `M${x1.toFixed(1)},${y1.toFixed(1)}L${x2.toFixed(1)},${y2.toFixed(1)}`, head: `M${h(0.45)}L${x2.toFixed(1)},${y2.toFixed(1)}L${h(-0.45)}` }
}

// Polyline path string from points already in SVG coordinates.
export const pathOf = (P: number[][]) => P.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('')
