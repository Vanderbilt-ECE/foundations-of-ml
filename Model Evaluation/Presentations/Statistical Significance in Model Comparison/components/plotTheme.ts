export const text = '#e2e8f0'
export const grid = 'rgba(148,163,184,.22)'

export const axis = (title: string, extra: Record<string, unknown> = {}) => ({
  title: { text: title, font: { size: 15, color: text }, standoff: 8 },
  tickfont: { size: 13, color: text },
  gridcolor: grid,
  zerolinecolor: grid,
  linecolor: 'rgba(148,163,184,.5)',
  ...extra,
})

export const baseLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: text, family: 'DM Sans, sans-serif' },
  margin: { l: 64, r: 16, t: 12, b: 52 },
  showlegend: false,
}

export const config = { responsive: true, displayModeBar: false }

export const erf = (x: number) => {
  const s = Math.sign(x)
  const a = Math.abs(x)
  const t = 1 / (1 + 0.3275911 * a)
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-a * a)
  return s * y
}
export const normCdf = (x: number) => 0.5 * (1 + erf(x / Math.SQRT2))
