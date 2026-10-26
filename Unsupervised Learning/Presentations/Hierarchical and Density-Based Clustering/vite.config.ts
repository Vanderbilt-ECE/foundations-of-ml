import { fileURLToPath } from 'node:url'

const deckRoot = fileURLToPath(new URL('.', import.meta.url))
const templateRoot = fileURLToPath(new URL('../../../slidev_template', import.meta.url))

export default {
  resolve: {
    alias: { '@data': `${deckRoot}data` },
  },
  server: {
    fs: { allow: [deckRoot, templateRoot] },
  },
}
