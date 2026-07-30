import { defineAppSetup } from '@slidev/types'

// Workaround for Slidev 52.x routing bug under a sub-path base
// (e.g. GitHub project pages served from /my-presentation/).
// getSlidePath() prepends BASE_URL, then router.push() prepends it again → doubled path.
// Fix: strip the duplicate before it reaches the router.
export default defineAppSetup(({ router }) => {
  const base = import.meta.env.BASE_URL
  if (!base || base === '/')
    return

  const strip = (path: string) =>
    path.startsWith(base) ? path.slice(base.length - 1) : path

  for (const method of ['push', 'replace'] as const) {
    const original = router[method].bind(router)
    router[method] = ((to: any) => {
      if (typeof to === 'string')
        to = strip(to)
      else if (to && typeof to.path === 'string')
        to = { ...to, path: strip(to.path) }
      return original(to)
    }) as typeof router[typeof method]
  }
})
