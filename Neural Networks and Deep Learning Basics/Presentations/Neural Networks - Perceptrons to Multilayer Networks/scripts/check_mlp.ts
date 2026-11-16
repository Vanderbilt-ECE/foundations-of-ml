// Sanity checks for utils/mlp.ts, run with: node scripts/check_mlp.ts
// 1. backprop gradients match finite differences for every head
// 2. each live demo's settings actually train (loss falls, accuracy high) with its fixed seed
import { readFileSync } from 'node:fs'
import { batchOf, MLP } from '../utils/mlp.ts'
import { decode, energy, ring, rng } from '../utils/rng.ts'

// ---- 1. gradient check ----
for (const head of ['linear', 'sigmoid', 'softmax'] as const) {
  for (const act of ['tanh', 'relu'] as const) {
    const net = new MLP([3, 5, 4, head === 'sigmoid' ? 1 : 3], act, head, 11)
    const R = rng(2)
    const X = Array.from({ length: 6 }, () => [R.n(), R.n(), R.n()])
    const Y = X.map((_, i) => head === 'linear' ? [R.n(), R.n(), R.n()] : head === 'sigmoid' ? [i % 2] : [0, 1, 2].map(k => +(k === i % 3)))
    const { gW, gb } = net.grads(X, Y)
    let worst = 0; const h = 1e-6
    for (let l = 0; l < net.W.length; l++) {
      for (let j = 0; j < net.W[l].length; j++) {
        for (let i = 0; i < net.W[l][j].length; i++) {
          const w0 = net.W[l][j][i]
          net.W[l][j][i] = w0 + h; const lp = net.meanLoss(X, Y)
          net.W[l][j][i] = w0 - h; const lm = net.meanLoss(X, Y)
          net.W[l][j][i] = w0
          worst = Math.max(worst, Math.abs((lp - lm) / (2 * h) - gW[l][j][i]))
        }
        const b0 = net.b[l][j]
        net.b[l][j] = b0 + h; const lp = net.meanLoss(X, Y)
        net.b[l][j] = b0 - h; const lm = net.meanLoss(X, Y)
        net.b[l][j] = b0
        worst = Math.max(worst, Math.abs((lp - lm) / (2 * h) - gb[l][j]))
      }
    }
    console.log(`gradcheck ${head.padEnd(7)} ${act.padEnd(4)} max abs err ${worst.toExponential(2)} ${worst < 1e-6 ? 'OK' : 'FAIL'}`)
  }
}

// ---- 2. the demos ----
const t0 = performance.now()
// regression: energy vs temperature, inputs/outputs standardized the same way the component does
{
  const D = energy()
  const X = D.map(d => [(d.t - 15) / 12]); const Y = D.map(d => [(d.kwh - 25) / 8])
  const net = new MLP([1, 16, 16, 1], 'tanh', 'linear', 4)
  const lin = new MLP([1, 1], 'tanh', 'linear', 4)
  for (let s = 0; s <= 1500; s++) {
    net.step(X, Y, 0.01); lin.step(X, Y, 0.02)
    if (s % 300 === 0) console.log(`energy step ${s} mlp mse ${(2 * net.meanLoss(X, Y)).toFixed(4)}  line mse ${(2 * lin.meanLoss(X, Y)).toFixed(4)}`)
  }
}
// binary: ring
{
  const D = ring()
  const X = D.map(d => d.x); const Y = D.map(d => [d.y])
  for (const hid of [[], [8], [16, 16]]) {
    const net = new MLP([2, ...hid, 1], 'tanh', 'sigmoid', 3)
    for (let s = 0; s <= 1200; s++) net.step(X, Y, 0.02)
    const acc = X.reduce((a, x, i) => a + +((net.predict(x)[0] > 0.5) === (Y[i][0] === 1)), 0) / X.length
    console.log(`ring hidden=[${hid}] loss ${net.meanLoss(X, Y).toFixed(3)} acc ${(100 * acc).toFixed(1)}%`)
  }
}
// multiclass: digits
{
  const d = JSON.parse(readFileSync(new URL('../data/digits.json', import.meta.url), 'utf8'))
  const prep = (s: string) => decode(s).map(v => v / 16)
  const Xtr = d.train.img.map(prep); const Ytr = d.train.y.map((y: number) => Array.from({ length: 10 }, (_, k) => +(k === y)))
  const Xte = d.test.img.map(prep); const yte = d.test.y
  const net = new MLP([64, 32, 10], 'relu', 'softmax', 1)
  const R = rng(9)
  const acc = () => Xte.reduce((a: number, x: number[], i: number) => { const p = net.predict(x); return a + +(p.indexOf(Math.max(...p)) === yte[i]) }, 0) / Xte.length
  for (let s = 0; s <= 600; s++) {
    if (s % 50 === 0) console.log(`digits step ${s} test acc ${(100 * acc()).toFixed(1)}%`)
    const idx = batchOf(Xtr.length, 32, R)
    net.step(idx.map(i => Xtr[i]), idx.map(i => Ytr[i]), 0.003)
  }
}
console.log(`total ${(performance.now() - t0).toFixed(0)} ms`)
