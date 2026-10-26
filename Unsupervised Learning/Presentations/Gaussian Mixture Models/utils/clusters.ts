// Shared helpers for the clustering decks: palette, equal-aspect scales,
// Voronoi cells for a set of centroids, and a requestAnimationFrame tween.
import type { Ref } from 'vue'
import { onBeforeUnmount, ref, watch } from 'vue'

export type Pt = [number, number] | number[]

// Cluster colors, in order. Template accents first (teal, amber, violet, blue, red, orange: teal and amber stay distinct when blended), then two extras.
export const PALETTE = ['#2dd4bf', '#fbbf24', '#a78bfa', '#60a5fa', '#f87171', '#fb923c', '#f472b6', '#a3e635']
export const GRAY = '#64748b'
export const color = (k: number | null | undefined) => (k == null || k < 0 ? GRAY : PALETTE[k % PALETTE.length])

export interface Domain { x: [number, number], y: [number, number] }

export function domainOf(pts: Pt[], pad = 0.06): Domain {
  let x0 = Infinity; let x1 = -Infinity; let y0 = Infinity; let y1 = -Infinity
  for (const p of pts) {
    x0 = Math.min(x0, p[0]); x1 = Math.max(x1, p[0])
    y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1])
  }
  const px = (x1 - x0) * pad; const py = (y1 - y0) * pad
  return { x: [x0 - px, x1 + px], y: [y0 - py, y1 + py] }
}

// Equal-aspect mapping of a data domain into a W x H box (y up), centered.
// Equal aspect matters: Voronoi borders are perpendicular bisectors and should look like it.
export function equalScale(d: Domain, W: number, H: number, equal = true) {
  const dx = d.x[1] - d.x[0]; const dy = d.y[1] - d.y[0]
  const kx = equal ? Math.min(W / dx, H / dy) : W / dx
  const ky = equal ? kx : H / dy
  const ox = (W - dx * kx) / 2; const oy = (H - dy * ky) / 2
  const sx = (x: number) => ox + (x - d.x[0]) * kx
  const sy = (y: number) => H - oy - (y - d.y[0]) * ky
  // the data-space rectangle that is actually visible
  const vis: Domain = { x: [d.x[0] - ox / kx, d.x[1] + ox / kx], y: [d.y[0] - oy / ky, d.y[1] + oy / ky] }
  return { sx, sy, kx, ky, vis }
}

// Clip a convex polygon to the half-plane a·p <= b (Sutherland–Hodgman, one edge).
function clip(poly: number[][], a: number[], b: number) {
  const out: number[][] = []
  for (let i = 0; i < poly.length; i++) {
    const P = poly[i]; const Q = poly[(i + 1) % poly.length]
    const fp = a[0] * P[0] + a[1] * P[1] - b
    const fq = a[0] * Q[0] + a[1] * Q[1] - b
    if (fp <= 0) out.push(P)
    if ((fp < 0 && fq > 0) || (fp > 0 && fq < 0)) {
      const t = fp / (fp - fq)
      out.push([P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])])
    }
  }
  return out
}

// Voronoi cell of each centroid inside the rectangle d: the points closer to c_i than to any other centroid.
export function voronoi(C: Pt[], d: Domain): number[][][] {
  const box = [[d.x[0], d.y[0]], [d.x[1], d.y[0]], [d.x[1], d.y[1]], [d.x[0], d.y[1]]]
  return C.map((ci, i) => {
    let poly = box
    C.forEach((cj, j) => {
      if (i === j || poly.length === 0) return
      // |p-ci|^2 <= |p-cj|^2  <=>  2(cj-ci)·p <= |cj|^2 - |ci|^2
      const a = [2 * (cj[0] - ci[0]), 2 * (cj[1] - ci[1])]
      const b = cj[0] ** 2 + cj[1] ** 2 - ci[0] ** 2 - ci[1] ** 2
      poly = clip(poly, a, b)
    })
    return poly
  })
}

const ease = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - (-2 * u + 2) ** 3 / 2)

// Animate a numeric array (or array of points) toward each new target value.
// Starts at the current target, so a freshly mounted slide (or a PDF export) shows the final state immediately.
export function useTween<T extends number[] | number[][]>(target: () => T, ms = 700): Ref<T> {
  const clone = (v: T) => JSON.parse(JSON.stringify(v)) as T
  const cur = ref(clone(target())) as Ref<T>
  let raf = 0
  watch(target, (to) => {
    const from = clone(cur.value) as any
    const dest = to as any
    const t0 = performance.now()
    cancelAnimationFrame(raf)
    const lerp = (a: any, b: any, e: number): any =>
      Array.isArray(b) ? b.map((v, i) => lerp(a?.[i], v, e)) : (typeof a === 'number' ? a + (b - a) * e : b)
    const tick = (t: number) => {
      const u = Math.min(1, (t - t0) / ms)
      cur.value = lerp(from, dest, ease(u))
      if (u < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
  })
  onBeforeUnmount(() => cancelAnimationFrame(raf))
  return cur
}

export const polyPath = (poly: number[][], sx: (x: number) => number, sy: (y: number) => number) =>
  poly.length ? `M${poly.map(p => `${sx(p[0]).toFixed(1)},${sy(p[1]).toFixed(1)}`).join('L')}Z` : ''

export const fmt = (v: number, d = 1) => v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d })

// Dendrogram geometry written by make_data.py (tree_json): x = leaf position (internal node: midpoint
// of its children), h = merge height, kids = the two children of internal node n + i.
export interface Tree { order: number[], x: number[], h: number[], rep: number[], kids: number[][] }

// The ⊓-shaped link for internal node i: from child a up to the merge height, across, down to child b.
// `at(position, height)` maps tree coordinates to SVG coordinates, so the same code draws vertical or sideways trees.
export function linkPath(t: Tree, i: number, at: (pos: number, h: number) => [number, number]) {
  const n = t.kids.length + 1
  const [a, b] = t.kids[i]
  const h = t.h[n + i]
  const p = [at(t.x[a], t.h[a]), at(t.x[a], h), at(t.x[b], h), at(t.x[b], t.h[b])]
  return `M${p.map(q => `${q[0].toFixed(1)},${q[1].toFixed(1)}`).join('L')}`
}
