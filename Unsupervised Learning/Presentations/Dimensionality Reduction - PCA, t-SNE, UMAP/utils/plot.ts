// Shared helpers for the dimensionality-reduction slides: palette, digit images, pointer mapping,
// a seeded random generator, tweens, and a requestAnimationFrame loop that only runs while its slide is showing.
import type { Ref } from 'vue'
import { useNav, useSlideContext } from '@slidev/client'
import { computed, onBeforeUnmount, ref, watch } from 'vue'

// One color per digit class 0-9. Template accents first, then extras; plots also print the digit itself.
export const PALETTE = ['#2dd4bf', '#fbbf24', '#a78bfa', '#60a5fa', '#f87171', '#fb923c', '#f472b6', '#a3e635', '#e2e8f0', '#fda4af']
export const GRAY = '#64748b'
export const color = (k: number | null | undefined) => (k == null || k < 0 ? GRAY : PALETTE[k % PALETTE.length])

// Continuous ramp for a position in [0, 1] (violet -> blue -> teal -> lime -> amber -> red), e.g. along a manifold.
const RAMP = ['#a78bfa', '#60a5fa', '#2dd4bf', '#a3e635', '#fbbf24', '#f87171'].map(c => [1, 3, 5].map(i => Number.parseInt(c.slice(i, i + 2), 16)))
export function ramp(t: number) {
  const x = Math.max(0, Math.min(1, t)) * (RAMP.length - 1)
  const i = Math.min(RAMP.length - 2, Math.floor(x)); const f = x - i
  return `rgb(${RAMP[i].map((v, k) => Math.round(v + (RAMP[i + 1][k] - v) * f)).join(',')})`
}

// An Archimedean spiral (a 1D manifold in 2D), sampled evenly by arc length with a little noise.
// s = arc length from the inner end, so the distance *along the curve* between i and j is |s_i - s_j|.
export function spiral(n = 220, seed = 9, noise = 0.03) {
  const a = 0.1; const b = 0.13; const t0 = 1.5 * Math.PI; const t1 = 5 * Math.PI
  const fine = 4000
  const arc = [0]
  for (let i = 1; i <= fine; i++) {
    const t = t0 + (t1 - t0) * i / fine; const tp = t0 + (t1 - t0) * (i - 1) / fine
    const p = [(a + b * t) * Math.cos(t), (a + b * t) * Math.sin(t)]; const q = [(a + b * tp) * Math.cos(tp), (a + b * tp) * Math.sin(tp)]
    arc.push(arc[i - 1] + Math.hypot(p[0] - q[0], p[1] - q[1]))
  }
  const total = arc[fine]
  const R = rng(seed)
  const pts: number[][] = []; const s: number[] = []
  let j = 0
  for (let i = 0; i < n; i++) {
    const target = total * i / (n - 1)
    while (j < fine && arc[j + 1] < target) j++
    const t = t0 + (t1 - t0) * j / fine
    pts.push([(a + b * t) * Math.cos(t) + noise * R.n(), (a + b * t) * Math.sin(t) + noise * R.n()])
    s.push(target)
  }
  return { pts, s, total }
}

// An 8x8 digit stored by make_data.py as 64 base-17 characters ('0'-'9', 'a'-'g'), pixel values 0-16.
export const decode = (s: string) => Array.from(s, c => Number.parseInt(c, 17))

export const fmt = (v: number, d = 1) => v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })

// Pointer position -> viewBox coordinates. The slide is CSS-scaled and an SVG/canvas may be letterboxed
// (preserveAspectRatio meet, centered), so map through the bounding box rather than offsetX.
export function toLocal(e: PointerEvent | MouseEvent, el: Element, W: number, H: number) {
  const r = el.getBoundingClientRect()
  const k = Math.min(r.width / W, r.height / H)
  return [(e.clientX - r.left - (r.width - W * k) / 2) / k, (e.clientY - r.top - (r.height - H * k) / 2) / k]
}

// Small seeded generator (mulberry32) plus Box-Muller normals, so "random" animations replay identically.
export function rng(seed: number) {
  let a = seed >>> 0
  const u = () => {
    a = (a + 0x6D2B79F5) >>> 0
    let t = a
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
  const n = () => Math.sqrt(-2 * Math.log(1 - u())) * Math.cos(2 * Math.PI * u())
  return { u, n }
}

export const ease = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2)

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

// Covariance, eigen-decomposition and ellipse outline for 2D point sets (the PCA slides).
export function cov2(P: number[][]) {
  const n = P.length
  const mx = P.reduce((s, p) => s + p[0], 0) / n; const my = P.reduce((s, p) => s + p[1], 0) / n
  let a = 0; let b = 0; let c = 0
  for (const p of P) { a += (p[0] - mx) ** 2; b += (p[0] - mx) * (p[1] - my); c += (p[1] - my) ** 2 }
  return [[a / (n - 1), b / (n - 1)], [b / (n - 1), c / (n - 1)]]
}

// Symmetric 2x2: eigenvalues (largest first) and the unit eigenvector of the largest.
export function eig2(S: number[][]) {
  const a = S[0][0]; const b = S[0][1]; const c = S[1][1]
  const t = (a + c) / 2; const d = Math.sqrt(((a - c) / 2) ** 2 + b * b)
  const l1 = t + d; const l2 = t - d
  const ang = Math.abs(b) < 1e-12 ? (a >= c ? 0 : Math.PI / 2) : Math.atan2(l1 - a, b)
  return { l1, l2, ang, v1: [Math.cos(ang), Math.sin(ang)], v2: [-Math.sin(ang), Math.cos(ang)] }
}

// Outline of { mu + s * (sqrt(l1) cos t v1 + sqrt(l2) sin t v2) }: the s-standard-deviation ellipse of S.
export function ellipsePath(mu: number[], S: number[][], s: number, sx: (x: number) => number, sy: (y: number) => number, n = 72) {
  const { l1, l2, v1, v2 } = eig2(S)
  let d = ''
  for (let i = 0; i <= n; i++) {
    const t = (i / n) * 2 * Math.PI
    const u = s * Math.sqrt(Math.max(l1, 0)) * Math.cos(t); const v = s * Math.sqrt(Math.max(l2, 0)) * Math.sin(t)
    d += `${i ? 'L' : 'M'}${sx(mu[0] + u * v1[0] + v * v2[0]).toFixed(1)},${sy(mu[1] + u * v1[1] + v * v2[1]).toFixed(1)}`
  }
  return `${d}Z`
}
