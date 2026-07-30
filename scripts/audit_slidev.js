async page => {
  const origin = page.url().split('/').slice(0, 3).join('/')
  const consoleErrors = []
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text())
  })
  page.on('pageerror', error => consoleErrors.push(error.message))

  await page.goto(`${origin}/1?clicks=99`)
  await page.locator('.slidev-page-1').waitFor({ state: 'visible' })
  const totalTexts = await page.locator('.slide-number').allTextContents()
  const total = Math.max(...totalTexts.map(text => Number(text.split('/').at(-1).trim())))
  const problems = []

  for (let slide = 1; slide <= total; slide++) {
    await page.goto(`${origin}/${slide}?clicks=99`)
    const active = page.locator(`.slidev-page-${slide}`)
    await active.waitFor({ state: 'visible' })
    await page.evaluate(() => document.fonts.ready)
    await page.waitForTimeout(80)

    const result = await page.evaluate(current => {
      const root = document.querySelector(`.slidev-page-${current}`)
      const frame = root.getBoundingClientRect()
      const visible = element => {
        const style = getComputedStyle(element)
        const rect = element.getBoundingClientRect()
        return style.display !== 'none' && style.visibility !== 'hidden'
          && Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0
      }
      const outside = []
      for (const element of root.querySelectorAll('*')) {
        if (!visible(element) || element.closest('defs') || element.closest('.katex-mathml')) continue
        if (element instanceof SVGElement && element.tagName.toLowerCase() !== 'svg'
          && element.tagName.toLowerCase() !== 'text') continue
        const rect = element.getBoundingClientRect()
        if (rect.left < frame.left - 3 || rect.right > frame.right + 3
          || rect.top < frame.top - 3 || rect.bottom > frame.bottom + 3) {
          outside.push({
            tag: element.tagName.toLowerCase(),
            class: String(element.className).slice(0, 100),
            text: (element.textContent || '').trim().slice(0, 80),
            edges: [rect.left - frame.left, rect.top - frame.top,
              rect.right - frame.right, rect.bottom - frame.bottom].map(Math.round),
          })
        }
      }
      return {
        katexErrors: root.querySelectorAll('.katex-error').length,
        outside: outside.slice(0, 8),
      }
    }, slide)
    if (result.katexErrors || result.outside.length)
      problems.push({ slide, ...result })
  }

  let clickReveal = null
  for (let slide = 2; slide <= total; slide++) {
    await page.goto(`${origin}/${slide}?clicks=0`)
    await page.locator(`.slidev-page-${slide}`).waitFor({ state: 'visible' })
    const before = await page.locator(`.slidev-page-${slide} .slidev-vclick-hidden`).count()
    if (!before) continue
    await page.keyboard.press('ArrowRight')
    await page.waitForTimeout(120)
    const after = await page.locator(`.slidev-page-${slide} .slidev-vclick-hidden`).count()
    clickReveal = { slide, before, after, passed: after < before }
    break
  }

  return {
    title: await page.title(),
    total,
    problems,
    clickReveal,
    consoleErrors: [...new Set(consoleErrors)].slice(0, 10),
    passed: problems.length === 0 && clickReveal?.passed === true && consoleErrors.length === 0,
  }
}
