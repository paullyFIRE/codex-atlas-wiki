import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  output: 'static',
  site: 'https://war-inc-rising.codex-atlas.com',
  integrations: [sitemap()],
});
