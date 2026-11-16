// Optimizers on a 2-weight quadratic loss  L(w) = ½ (a·w₁² + b·w₂²), minimum at (0, 0).
// A long narrow valley (a ≪ b) is what badly scaled inputs produce; a ≈ b is a round bowl.
// Plain JS math (no Vue), so the paths can be checked in node.

export type Opt = 'sgd' | 'momentum' | 'adam'
export interface Bowl { a: number, b: number }

export const loss = (B: Bowl, w: number[]) => 0.5 * (B.a * w[0] ** 2 + B.b * w[1] ** 2)
export const grad = (B: Bowl, w: number[]) => [B.a * w[0], B.b * w[1]]

// Run `steps` steps from w0 and return every point visited (steps + 1 points). Stops early on blow-up.
export function run(B: Bowl, opt: Opt, w0: number[], steps: number, lr: number, beta = 0.9) {
  let w = [...w0]; let v = [0, 0]; let m = [0, 0]; let s = [0, 0]
  const path = [[...w]]
  for (let t = 1; t <= steps; t++) {
    const g = grad(B, w)
    if (opt === 'sgd') {
      w = [w[0] - lr * g[0], w[1] - lr * g[1]]
    }
    else if (opt === 'momentum') {
      v = [beta * v[0] + g[0], beta * v[1] + g[1]]
      w = [w[0] - lr * v[0], w[1] - lr * v[1]]
    }
    else {
      const b1 = 0.9; const b2 = 0.999; const eps = 1e-8
      m = [b1 * m[0] + (1 - b1) * g[0], b1 * m[1] + (1 - b1) * g[1]]
      s = [b2 * s[0] + (1 - b2) * g[0] ** 2, b2 * s[1] + (1 - b2) * g[1] ** 2]
      const mh = m.map(x => x / (1 - b1 ** t)); const sh = s.map(x => x / (1 - b2 ** t))
      w = [w[0] - lr * mh[0] / (Math.sqrt(sh[0]) + eps), w[1] - lr * mh[1] / (Math.sqrt(sh[1]) + eps)]
    }
    path.push([...w])
    if (Math.abs(w[0]) > 1e3 || Math.abs(w[1]) > 1e3) break
  }
  return path
}

// Contour ellipses  ½(a x² + b y²) = c  as SVG paths, given a mapping to screen coordinates.
export function contours(B: Bowl, levels: number[], map: (x: number, y: number) => number[], n = 96) {
  return levels.map((c) => {
    const rx = Math.sqrt(2 * c / B.a); const ry = Math.sqrt(2 * c / B.b)
    const P = Array.from({ length: n + 1 }, (_, i) => {
      const t = 2 * Math.PI * i / n
      return map(rx * Math.cos(t), ry * Math.sin(t))
    })
    return `${P.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('')}Z`
  })
}
