// Seeded random numbers, so "random" demos replay identically in the browser and in the PDF.
// mulberry32 uniforms plus Box-Muller normals.
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
