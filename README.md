# GeoHub Chile

Directorio colaborativo y abierto de iniciativas, capas, catastros y herramientas de información geográfica pública de Chile.

> Construido con [Astro](https://astro.build) y publicado en GitHub Pages. Sin servidor, sin costos, todo open source.

---

## Stack

- **Astro 4** — generador de sitio estático con componentes `.astro`.
- **Content Collections** + **zod** — cada iniciativa/fuente es un archivo Markdown validado en build.
- **JS vanilla** para filtros, búsqueda y modal (sin React/Vue).
- **GitHub Pages** + **GitHub Actions** para deploy automático.

---

## Desarrollo local

```bash
npm install
npm run dev      # http://localhost:4321/geohub-chile
npm run build    # genera dist/ + valida tipos y schema
npm run preview  # sirve el build con el base /geohub-chile
```

Requiere Node 18+.

---

## Estructura

```
src/
├── components/        # Header, Hero, FiltrosBar, IniciativaCard, ...
├── content/
│   ├── config.ts      # schemas zod
│   ├── iniciativas/   # un .md por iniciativa
│   └── fuentes/       # un .json por fuente institucional
├── layouts/Base.astro
├── pages/index.astro
└── styles/global.css
public/
└── visor_riesgos_chile.html   # visor standalone existente
```

---

## Cómo contribuir

### Agregar una iniciativa

1. Fork del repo.
2. Crea `src/content/iniciativas/<slug>.md` siguiendo el frontmatter de los archivos existentes (mira [`catastro-minero.md`](src/content/iniciativas/catastro-minero.md) como ejemplo).
3. `npm run build` — el schema zod valida los metadatos.
4. Abre un PR.

Frontmatter mínimo:

```yaml
---
nombre: "Mi catastro"
categoria: ambiental      # mineria | ambiental | riesgo | hidrico | social | admin | energia
icono: "🌿"
estado: activo            # activo | beta | wip
estadoTexto: "Activo — Mes Año"
descripcion: "Qué contiene, cobertura, fuente."
capas:
  - "Capa A"
  - "Capa B"
tags: "palabras clave para buscador"
stats:
  - { label: "registros", valor: "1.000" }
acciones:
  - { tipo: github, texto: "GitHub", url: "https://github.com/..." }
---
```

Campos opcionales: `capasExtra`, `archivos` (grupos de descargas).

### Agregar una fuente institucional

Crea `src/content/fuentes/<slug>.json`:

```json
{
  "logo": "SERNAGEOMIN",
  "nombre": "Geología y Minería",
  "descripcion": "Catastro minero, geología, volcanes.",
  "url": "https://www.sernageomin.cl"
}
```

### Criterios de calidad

- ✅ Fuente oficial o citable.
- ✅ Formato abierto (GeoJSON, Shapefile, CSV, WMS/WFS).
- ✅ Licencia libre.
- ✅ Metadatos completos (incluido sistema de referencia).

---

## Deploy

Push a `main` → la GitHub Action en `.github/workflows/deploy.yml` construye y publica en `https://<user>.github.io/geohub-chile/`.

En el repo: **Settings → Pages → Source: GitHub Actions** (una sola vez).

Para usar un dominio propio, vacía `base` en `astro.config.mjs` y agrega `public/CNAME`.

---

## Valoraciones (👍) — cómo se actualizan

Las cards se ordenan por `score` (cantidad de 👍). El score viene de **GitHub Reactions** sobre un issue dedicado por iniciativa.

### Setup por iniciativa (una vez)

1. Crear el hilo de valoración:
   ```bash
   gh issue create \
     --title "[Valoración] Catastro Minero Chile" \
     --label valoracion \
     --body "Hilo de valoración. Reacciona con 👍 si te resultó útil."
   # → te devuelve: https://github.com/.../issues/42
   ```
2. Anotar el número en el frontmatter de la iniciativa:
   ```yaml
   ---
   nombre: "Catastro Minero Chile"
   valoracionIssue: 42  # ← agregar
   ---
   ```

### Sincronización automática

`.github/workflows/sync-scores.yml` corre **cada día a las 06:00 UTC** y:
1. Lee todos los `.md` que tienen `valoracionIssue`.
2. Llama a GitHub API → cuenta los 👍 del issue.
3. Reemplaza `score: N` en el `.md` con el conteo real.
4. Si hubo cambios → commit + push + redeploy automático.

También se puede correr manualmente: **Actions → Sync valoraciones → Run workflow**.

### Test local

```bash
GITHUB_TOKEN=ghp_xxx node scripts/sync-scores.mjs
```
(Sin token funciona pero con rate limit de 60 req/hora.)

---

## Monitor de geoservicios — cómo funciona

`/herramientas/monitor-geoservicios` muestra un semáforo del estado de los
geoservicios públicos chilenos (WMS, WFS, ArcGIS REST, GeoJSON).

- **Catálogo**: `src/data/geoservicios.json` — cada endpoint fue verificado
  manualmente antes de agregarse. Para proponer uno nuevo: issue con el
  título `[Monitor] Agregar geoservicio` (o PR directo al JSON).
- **Checker**: `scripts/check-geoservicios.mjs` verifica en 3 niveles
  (¿responde? · ¿habla el protocolo? · ¿entrega datos?) con reintentos, y
  escribe `src/data/geoservicios-estado.json` (semáforo, latencia, conteo de
  registros, `lastEditDate` de capas ArcGIS e historial de hasta 30 corridas).
- **Automatización**: `.github/workflows/check-geoservicios.yml` corre a
  diario (09:00 UTC). Solo commitea (y redeploya) si algún semáforo cambió o
  si el estado guardado tiene más de 3 días.
- La página además incluye un **tester client-side** para probar cualquier
  endpoint que no esté en el listado, con manejo de CORS.

Test local:

```bash
node scripts/check-geoservicios.mjs
```

---

## Licencia

MIT — el código.
Los datos enlazados pertenecen a sus instituciones publicadoras (dominio público / licencias abiertas).
