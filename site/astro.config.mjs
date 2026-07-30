// @ts-check
import { defineConfig } from 'astro/config';

import vue from '@astrojs/vue';

// https://astro.build/config
export default defineConfig({
  site: 'https://vanderbilt-ece.github.io',
  base: '/foundations-of-ml',
  integrations: [vue()]
});