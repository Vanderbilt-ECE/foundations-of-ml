// A tiny fully connected network, trained in the browser for the live demos.
// Hidden layers use one activation (relu or tanh); the output head sets the problem type:
//   linear  + mean squared error   -> regression
//   sigmoid + binary cross-entropy -> yes/no classification
//   softmax + cross-entropy        -> one of K classes
// Gradients come from ordinary backpropagation; updates use Adam (the optimizer is a topic for the next deck).
// Plain TypeScript with no Vue imports, so it can be tested in node (scripts/check_mlp.ts).
import { rng } from './rng.ts'

export type Act = 'relu' | 'tanh'
export type Head = 'linear' | 'sigmoid' | 'softmax'

const actF = (a: Act, z: number) => (a === 'relu' ? (z > 0 ? z : 0) : Math.tanh(z))
// derivative written in terms of the activation output h (and pre-activation z for relu)
const actD = (a: Act, z: number, h: number) => (a === 'relu' ? (z > 0 ? 1 : 0) : 1 - h * h)

export class MLP {
  sizes: number[]
  act: Act
  head: Head
  W: number[][][] // W[l][j][i]: weight from unit i in layer l to unit j in layer l+1
  b: number[][]
  // Adam state
  mW: number[][][]; vW: number[][][]; mb: number[][]; vb: number[][]; t = 0

  constructor(sizes: number[], act: Act = 'tanh', head: Head = 'linear', seed = 1, initScale = 1) {
    this.sizes = sizes; this.act = act; this.head = head
    const R = rng(seed)
    this.W = []; this.b = []
    for (let l = 0; l < sizes.length - 1; l++) {
      const nIn = sizes[l]; const nOut = sizes[l + 1]
      const s = initScale * Math.sqrt((act === 'relu' ? 2 : 1) / nIn)
      this.W.push(Array.from({ length: nOut }, () => Array.from({ length: nIn }, () => s * R.n())))
      this.b.push(Array.from({ length: nOut }, () => 0))
    }
    const zeros3 = () => this.W.map(M => M.map(r => r.map(() => 0)))
    const zeros2 = () => this.b.map(v => v.map(() => 0))
    this.mW = zeros3(); this.vW = zeros3(); this.mb = zeros2(); this.vb = zeros2()
  }

  // Returns pre-activations zs and activations hs for every layer (hs[0] is the input).
  forwardAll(x: number[]) {
    const hs: number[][] = [x]; const zs: number[][] = []
    const L = this.W.length
    for (let l = 0; l < L; l++) {
      const Wl = this.W[l]; const bl = this.b[l]; const h = hs[l]
      const z = Wl.map((row, j) => { let s = bl[j]; for (let i = 0; i < row.length; i++) s += row[i] * h[i]; return s })
      zs.push(z)
      if (l < L - 1) hs.push(z.map(v => actF(this.act, v)))
      else hs.push(this.output(z))
    }
    return { hs, zs }
  }

  output(z: number[]) {
    if (this.head === 'linear') return z
    if (this.head === 'sigmoid') return z.map(v => 1 / (1 + Math.exp(-v)))
    const m = Math.max(...z); const e = z.map(v => Math.exp(v - m)); const s = e.reduce((a, c) => a + c, 0)
    return e.map(v => v / s)
  }

  predict(x: number[]) { return this.forwardAll(x).hs[this.W.length] }

  // Loss of one example. y: target vector (regression values, 0/1, or one-hot).
  lossOf(p: number[], y: number[]) {
    const eps = 1e-12
    if (this.head === 'linear') return p.reduce((s, v, k) => s + 0.5 * (v - y[k]) ** 2, 0)
    if (this.head === 'sigmoid') return p.reduce((s, v, k) => s - (y[k] * Math.log(v + eps) + (1 - y[k]) * Math.log(1 - v + eps)), 0)
    return -p.reduce((s, v, k) => s + y[k] * Math.log(v + eps), 0)
  }

  // Mean loss and gradients over a batch. Every head is paired with its matching loss,
  // so dLoss/dz at the output is simply (prediction - target).
  grads(X: number[][], Y: number[][]) {
    const gW = this.W.map(M => M.map(r => r.map(() => 0)))
    const gb = this.b.map(v => v.map(() => 0))
    let loss = 0
    const L = this.W.length; const n = X.length
    for (let s = 0; s < n; s++) {
      const { hs, zs } = this.forwardAll(X[s])
      const p = hs[L]
      loss += this.lossOf(p, Y[s])
      let delta = p.map((v, k) => v - Y[s][k])
      for (let l = L - 1; l >= 0; l--) {
        const h = hs[l]; const Wl = this.W[l]
        for (let j = 0; j < delta.length; j++) {
          const dj = delta[j]; if (dj === 0) continue
          gb[l][j] += dj
          const gr = gW[l][j]
          for (let i = 0; i < h.length; i++) gr[i] += dj * h[i]
        }
        if (l > 0) {
          const prev = new Array(h.length).fill(0)
          for (let j = 0; j < delta.length; j++) { const dj = delta[j]; if (dj === 0) continue; const row = Wl[j]; for (let i = 0; i < h.length; i++) prev[i] += dj * row[i] }
          delta = prev.map((v, i) => v * actD(this.act, zs[l - 1][i], h[i]))
        }
      }
    }
    for (const M of gW) for (const r of M) for (let i = 0; i < r.length; i++) r[i] /= n
    for (const v of gb) for (let i = 0; i < v.length; i++) v[i] /= n
    return { loss: loss / n, gW, gb }
  }

  // One Adam step on a batch; returns the batch loss before the step.
  step(X: number[][], Y: number[][], lr = 0.01) {
    const { loss, gW, gb } = this.grads(X, Y)
    const b1 = 0.9; const b2 = 0.999; const eps = 1e-8
    this.t++
    const c1 = 1 - b1 ** this.t; const c2 = 1 - b2 ** this.t
    for (let l = 0; l < this.W.length; l++) {
      for (let j = 0; j < this.W[l].length; j++) {
        for (let i = 0; i < this.W[l][j].length; i++) {
          const g = gW[l][j][i]
          this.mW[l][j][i] = b1 * this.mW[l][j][i] + (1 - b1) * g
          this.vW[l][j][i] = b2 * this.vW[l][j][i] + (1 - b2) * g * g
          this.W[l][j][i] -= lr * (this.mW[l][j][i] / c1) / (Math.sqrt(this.vW[l][j][i] / c2) + eps)
        }
        const g = gb[l][j]
        this.mb[l][j] = b1 * this.mb[l][j] + (1 - b1) * g
        this.vb[l][j] = b2 * this.vb[l][j] + (1 - b2) * g * g
        this.b[l][j] -= lr * (this.mb[l][j] / c1) / (Math.sqrt(this.vb[l][j] / c2) + eps)
      }
    }
    return loss
  }

  meanLoss(X: number[][], Y: number[][]) {
    let s = 0
    for (let i = 0; i < X.length; i++) s += this.lossOf(this.predict(X[i]), Y[i])
    return s / X.length
  }

  nParams() { return this.W.reduce((s, M) => s + M.length * M[0].length, 0) + this.b.reduce((s, v) => s + v.length, 0) }
}

// Random mini-batch indices, from a seeded generator.
export function batchOf(n: number, size: number, R: { u: () => number }) {
  return Array.from({ length: Math.min(size, n) }, () => Math.floor(R.u() * n))
}
