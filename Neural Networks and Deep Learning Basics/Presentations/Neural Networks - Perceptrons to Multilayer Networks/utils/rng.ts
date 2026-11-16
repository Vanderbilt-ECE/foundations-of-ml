// Seeded random numbers and the small synthetic datasets used on the slides.
// No Vue imports, so the training checks in scripts/ can run these in node.

// mulberry32 uniforms plus Box-Muller normals: "random" demos replay identically, in the browser and in the PDF.
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

// Perceptron demo: two groups that a straight line can separate.
// "Admitted?" from two standardized scores; labels +1 / -1.
export function separable(n = 40, seed = 3) {
  const R = rng(seed)
  const pts: { x: number[], y: number }[] = []
  while (pts.length < n) {
    const x = [R.u() * 2 - 1, R.u() * 2 - 1]
    const m = 0.9 * x[0] + 0.6 * x[1] - 0.1
    if (Math.abs(m) < 0.12) continue // leave a visible margin
    pts.push({ x, y: m > 0 ? 1 : -1 })
  }
  return pts
}

export const XOR = [
  { x: [0, 0], y: -1 },
  { x: [0, 1], y: 1 },
  { x: [1, 0], y: 1 },
  { x: [1, 1], y: -1 },
]

// Regression: daily electricity use (kWh) vs. outdoor temperature (°C).
// Heating on cold days and cooling on hot days give a U shape no straight line can fit.
export function energy(n = 70, seed = 5) {
  const R = rng(seed)
  return Array.from({ length: n }, () => {
    const t = -5 + R.u() * 40
    const kwh = 18 + 0.045 * (t - 17) ** 2 + 0.6 * Math.max(0, t - 26) + 1.6 * R.n()
    return { t, kwh }
  })
}

// Binary classification: a machine is OK when temperature and pressure (standardized) are both near nominal.
// The "OK" region is a disc, so the boundary has to curve all the way around.
export function ring(n = 220, seed = 8) {
  const R = rng(seed)
  return Array.from({ length: n }, () => {
    const x = [R.u() * 2 - 1, R.u() * 2 - 1]
    const r = Math.hypot(x[0] / 0.95, x[1] / 0.75)
    const ok = r + 0.08 * R.n() < 0.62
    return { x, y: ok ? 1 : 0 }
  })
}

// An 8x8 digit stored as 64 base-17 characters ('0'-'9', 'a'-'g'), pixel values 0-16.
export const decode = (s: string) => Array.from(s, c => Number.parseInt(c, 17))
