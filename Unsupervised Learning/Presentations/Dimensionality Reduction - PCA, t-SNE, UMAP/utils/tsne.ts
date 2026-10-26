// Exact t-SNE in the browser, the same recipe as tsne_np() in scripts/make_data.py (and sklearn's exact method):
// Gaussian conditional affinities with sigma_i set by bisection on the perplexity, symmetrized;
// Student-t affinities in the map; gradient descent on KL(P || Q) with momentum, gains and early exaggeration.
// O(n^2) per iteration, fine for a few hundred points.

export function sqdist(X: number[][]) {
  const n = X.length
  const D = Array.from({ length: n }, () => new Float64Array(n))
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      let s = 0
      for (let k = 0; k < X[i].length; k++) s += (X[i][k] - X[j][k]) ** 2
      D[i][j] = D[j][i] = s
    }
  }
  return D
}

// Row i of the conditional affinities p_{j|i}, with the precision beta = 1/(2 sigma^2) found by bisection
// so that the perplexity 2^H (H = entropy in bits) hits the target. Returns the row and sigma_i.
export function condRow(d: ArrayLike<number>, i: number, perp: number) {
  const n = d.length
  const target = Math.log(perp)
  let lo = 0; let hi = Infinity; let beta = 1
  let dmin = Infinity
  for (let j = 0; j < n; j++) if (j !== i) dmin = Math.min(dmin, d[j])
  const p = new Float64Array(n)
  for (let step = 0; step < 60; step++) {
    let s = 0; let sd = 0
    for (let j = 0; j < n; j++) {
      if (j === i) { p[j] = 0; continue }
      p[j] = Math.exp(-(d[j] - dmin) * beta)
      s += p[j]; sd += p[j] * (d[j] - dmin)
    }
    const H = Math.log(s) + beta * sd / s
    for (let j = 0; j < n; j++) p[j] /= s
    if (Math.abs(H - target) < 1e-5) break
    if (H > target) { lo = beta; beta = hi === Infinity ? beta * 2 : (beta + hi) / 2 }
    else { hi = beta; beta = (beta + lo) / 2 }
  }
  return { p, sigma: Math.sqrt(1 / (2 * beta)) }
}

export function jointP(D: Float64Array[], perp: number) {
  const n = D.length
  const rows = D.map((d, i) => condRow(d, i, perp).p)
  const P = Array.from({ length: n }, () => new Float64Array(n))
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) P[i][j] = Math.max((rows[i][j] + rows[j][i]) / (2 * n), 1e-12)
  return P
}

export interface TsneState { Y: number[][], upd: number[][], gains: number[][], it: number, kl: number }

export function tsneInit(n: number, normal: () => number): TsneState {
  return {
    Y: Array.from({ length: n }, () => [1e-4 * normal(), 1e-4 * normal()]),
    upd: Array.from({ length: n }, () => [0, 0]),
    gains: Array.from({ length: n }, () => [1, 1]),
    it: 0,
    kl: Number.NaN,
  }
}

export const EXAGGERATION_ITERS = 250

// One gradient step. Also records the current KL divergence (cheap: the same pass computes Q).
export function tsneStep(s: TsneState, P: Float64Array[]) {
  const n = s.Y.length
  const ex = s.it < EXAGGERATION_ITERS ? 12 : 1
  const mom = s.it < EXAGGERATION_ITERS ? 0.5 : 0.8
  const lr = Math.max(n / 12 / 4, 50)
  const num = Array.from({ length: n }, () => new Float64Array(n))
  let Z = 0
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const v = 1 / (1 + (s.Y[i][0] - s.Y[j][0]) ** 2 + (s.Y[i][1] - s.Y[j][1]) ** 2)
      num[i][j] = num[j][i] = v
      Z += 2 * v
    }
  }
  let kl = 0
  for (let i = 0; i < n; i++) {
    let gx = 0; let gy = 0
    for (let j = 0; j < n; j++) {
      if (i === j) continue
      const q = Math.max(num[i][j] / Z, 1e-12)
      const m = (ex * P[i][j] - q) * num[i][j]
      gx += m * (s.Y[i][0] - s.Y[j][0]); gy += m * (s.Y[i][1] - s.Y[j][1])
      kl += P[i][j] * Math.log(P[i][j] / q)
    }
    const g = [4 * gx, 4 * gy]
    for (let k = 0; k < 2; k++) {
      s.gains[i][k] = Math.max(0.01, Math.sign(g[k]) !== Math.sign(s.upd[i][k]) ? s.gains[i][k] + 0.2 : s.gains[i][k] * 0.8)
      s.upd[i][k] = mom * s.upd[i][k] - lr * s.gains[i][k] * g[k]
    }
  }
  for (let i = 0; i < n; i++) { s.Y[i][0] += s.upd[i][0]; s.Y[i][1] += s.upd[i][1] }
  s.it++
  s.kl = kl
}
