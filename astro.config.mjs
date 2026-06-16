import { defineConfig } from 'astro/config';

// Si despliegas en https://<user>.github.io/geohub-chile/
// deja base: '/geohub-chile'. Si usas dominio propio, vacía base.
export default defineConfig({
  site: 'https://danield-s.github.io',
  base: '/geohub-chile',
  output: 'static',
  trailingSlash: 'ignore',
});
