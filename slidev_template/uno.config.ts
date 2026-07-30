// @ts-expect-error - missing types for the slidev client uno config
import config from '@slidev/client/uno.config'
import { mergeConfigs, presetAttributify, presetIcons, presetWebFonts, presetWind3 } from 'unocss'

export default mergeConfigs([
  config,
  {
    presets: [
      presetWind3({
        dark: 'class',
      }),
      presetAttributify(),
      presetIcons({
        prefix: 'i-',
        extraProperties: {
          'display': 'inline-block',
          'vertical-align': 'middle',
        },
        warn: true,
      }),
      presetWebFonts({
        fonts: {
          sans: 'DM Sans',
          serif: 'DM Sans',
        },
      }),
    ],
  },
])
