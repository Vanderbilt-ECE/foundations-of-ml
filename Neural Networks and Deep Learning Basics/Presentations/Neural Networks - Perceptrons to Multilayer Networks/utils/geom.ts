// Geometry for drawing a linear decision boundary w·x + b = 0 inside a rectangular plot.

// Clip a convex polygon to the half-plane w·x + b >= 0 (sign = +1) or <= 0 (sign = -1)
// (one Sutherland–Hodgman pass). Points are in data coordinates.
export function clip(poly: number[][], w: number[], b: number, sign = 1) {
  const f = (p: number[]) => sign * (w[0] * p[0] + w[1] * p[1] + b)
  const out: number[][] = []
  for (let i = 0; i < poly.length; i++) {
    const p = poly[i]; const q = poly[(i + 1) % poly.length]
    const fp = f(p); const fq = f(q)
    if (fp >= 0) out.push(p)
    if ((fp >= 0) !== (fq >= 0)) {
      const t = fp / (fp - fq)
      out.push([p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])])
    }
  }
  return out
}

export const boxPoly = ([x0, x1, y0, y1]: number[]) => [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]

// The part of the box [x0,x1]×[y0,y1] on one side of the line w·x + b = 0.
export const halfPlane = (w: number[], b: number, box: number[], sign = 1) => clip(boxPoly(box), w, b, sign)

// The segment of the line w·x + b = 0 inside the box (empty if it misses).
export function lineInBox(w: number[], b: number, box: number[]) {
  const [x0, x1, y0, y1] = box
  const pts: number[][] = []
  if (Math.abs(w[1]) > 1e-9) {
    for (const x of [x0, x1]) { const y = -(w[0] * x + b) / w[1]; if (y >= y0 - 1e-9 && y <= y1 + 1e-9) pts.push([x, y]) }
  }
  if (Math.abs(w[0]) > 1e-9) {
    for (const y of [y0, y1]) { const x = -(w[1] * y + b) / w[0]; if (x > x0 + 1e-9 && x < x1 - 1e-9) pts.push([x, y]) }
  }
  return pts.slice(0, 2)
}
