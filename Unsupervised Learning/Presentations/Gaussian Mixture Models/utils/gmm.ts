// Gaussian mixture math for the slides: densities, responsibilities, ellipse outlines, color blending,
// a seeded random generator, and a requestAnimationFrame loop that only runs while its slide is showing.
// Everything is 2D unless the name says otherwise. Covariances are full 2x2 (or 3x3) matrices.
import { useNav, useSlideContext } from '@slidev/client'
import { computed, onBeforeUnmount, watch } from 'vue'
import { PALETTE } from './clusters'

export interface Mix { w: number[], mu: number[][], cov: number[][][] }

const LOG2PI = Math.log(2 * Math.PI)

export function chol2(S: number[][]) {
  const a = Math.sqrt(Math.max(S[0][0], 1e-12))
  const b = S[1][0] / a
  const c = Math.sqrt(Math.max(S[1][1] - b * b, 1e-12))
  return [[a, 0], [b, c]]
}

// Squared Mahalanobis distance (x-mu)^T S^-1 (x-mu).
export function maha2(x: number[], mu: number[], S: number[][]) {
  const det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
  const dx = x[0] - mu[0]; const dy = x[1] - mu[1]
  return (S[1][1] * dx * dx - 2 * S[0][1] * dx * dy + S[0][0] * dy * dy) / det
}

export function logpdf(x: number[], mu: number[], S: number[][]) {
  const det = S[0][0] * S[1][1] - S[0][1] * S[1][0]
  return -LOG2PI - 0.5 * Math.log(det) - 0.5 * maha2(x, mu, S)
}

export const pdf1 = (x: number, mu: number, sd: number) => Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI))

export function mixPdf(x: number[], m: Mix) {
  return m.w.reduce((s, w, k) => s + w * Math.exp(logpdf(x, m.mu[k], m.cov[k])), 0)
}

// gamma_ik = pi_k N(x_i | mu_k, S_k) / sum_j pi_j N(x_i | mu_j, S_j), with log-sum-exp for stability.
export function resp(x: number[], m: Mix) {
  const l = m.w.map((w, k) => Math.log(w) + logpdf(x, m.mu[k], m.cov[k]))
  const top = Math.max(...l)
  const e = l.map(v => Math.exp(v - top))
  const s = e.reduce((a, b) => a + b, 0)
  return e.map(v => v / s)
}

// Total log-likelihood sum_i log p(x_i).
export function logLik(pts: number[][], m: Mix) {
  let s = 0
  for (const p of pts) {
    const l = m.w.map((w, k) => Math.log(w) + logpdf(p, m.mu[k], m.cov[k]))
    const top = Math.max(...l)
    s += top + Math.log(l.reduce((a, v) => a + Math.exp(v - top), 0))
  }
  return s
}

// Eigen-decomposition of a symmetric 2x2: radii (sqrt eigenvalues, largest first) and the major-axis angle.
export function eig2(S: number[][]) {
  const a = S[0][0]; const b = S[0][1]; const c = S[1][1]
  const t = (a + c) / 2; const d = Math.sqrt(((a - c) / 2) ** 2 + b * b)
  const l1 = t + d; const l2 = Math.max(t - d, 0)
  const ang = Math.abs(b) < 1e-12 ? (a >= c ? 0 : Math.PI / 2) : Math.atan2(l1 - a, b)
  return { l1, l2, r1: Math.sqrt(l1), r2: Math.sqrt(l2), ang }
}

// Outline of { x : maha2(x) = s^2 } as an SVG path: mu + s L (cos t, sin t), mapped through the plot's scales.
// Drawing it in data space (rather than <ellipse transform=rotate>) stays correct under any axis scaling.
export function ellipsePath(mu: number[], S: number[][], s: number, sx: (x: number) => number, sy: (y: number) => number, n = 72) {
  const L = chol2(S)
  let d = ''
  for (let i = 0; i <= n; i++) {
    const t = (i / n) * 2 * Math.PI
    const u = s * Math.cos(t); const v = s * Math.sin(t)
    const x = mu[0] + L[0][0] * u
    const y = mu[1] + L[1][0] * u + L[1][1] * v
    d += `${i ? 'L' : 'M'}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`
  }
  return `${d}Z`
}

const hex = (c: string) => [1, 3, 5].map(i => Number.parseInt(c.slice(i, i + 2), 16))
const RGB = PALETTE.map(hex)

// Mix the component colors in proportion to the responsibilities: a 50/50 point is drawn halfway between.
export function blend(g: number[], palette = RGB) {
  let r = 0; let gg = 0; let b = 0
  g.forEach((v, k) => {
    const c = palette[k % palette.length]
    r += v * c[0]; gg += v * c[1]; b += v * c[2]
  })
  return `rgb(${r.toFixed(0)},${gg.toFixed(0)},${b.toFixed(0)})`
}

// Normalized entropy of a responsibility vector: 0 = certain, 1 = evenly split.
export const entropy = (g: number[]) => -g.reduce((s, v) => s + (v > 1e-12 ? v * Math.log(v) : 0), 0) / Math.log(g.length)

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

// Draw one point from component k: mu + L z.
export function draw(m: Mix, k: number, z: [number, number]) {
  const L = chol2(m.cov[k])
  return [m.mu[k][0] + L[0][0] * z[0], m.mu[k][1] + L[1][0] * z[0] + L[1][1] * z[1]]
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

// 3D ellipsoid { mu + s L u : |u| = 1 } as parametric surface grids for a Plotly 'surface' trace.
export function ellipsoid(mu: number[], S: number[][], s: number, n = 24) {
  // Cholesky of a 3x3
  const L = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j <= i; j++) {
      let v = S[i][j]
      for (let k = 0; k < j; k++) v -= L[i][k] * L[j][k]
      L[i][j] = i === j ? Math.sqrt(Math.max(v, 1e-12)) : v / L[j][j]
    }
  }
  const X: number[][] = []; const Y: number[][] = []; const Z: number[][] = []
  for (let i = 0; i <= n; i++) {
    const th = (i / n) * Math.PI
    const rx: number[] = []; const ry: number[] = []; const rz: number[] = []
    for (let j = 0; j <= n; j++) {
      const ph = (j / n) * 2 * Math.PI
      const u = [s * Math.sin(th) * Math.cos(ph), s * Math.sin(th) * Math.sin(ph), s * Math.cos(th)]
      rx.push(mu[0] + L[0][0] * u[0])
      ry.push(mu[1] + L[1][0] * u[0] + L[1][1] * u[1])
      rz.push(mu[2] + L[2][0] * u[0] + L[2][1] * u[1] + L[2][2] * u[2])
    }
    X.push(rx); Y.push(ry); Z.push(rz)
  }
  return { x: X, y: Y, z: Z }
}
