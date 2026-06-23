# {{TITULO}}

Webmap generado con [GeoHub Chile](https://geohub.cl) — kit estático, 100% client-side, sin backend.

Este kit contiene **{{NUM_CAPAS}} capa(s)** de datos geográficos con leyenda, selector de capas, escala y botón de pantalla completa.

## 📁 Qué incluye el kit

```
{{NOMBRE_ARCHIVO}}/
├── index.html               ← página del mapa (editable)
├── config.json              ← título, basemap, capas + simbología (editable)
├── data/
│   ├── capa-0.geojson       ← datos de la capa 1 (reemplazable)
│   ├── capa-1.geojson       ← datos de la capa 2
│   └── ...
├── style.css                ← estilos del mapa y popups (editable)
└── README.md                ← este archivo
```

La única dependencia es **Leaflet 1.9.4** desde CDN. No hay build, no hay `npm install`, no hay framework.

---

## 🚀 Publicar en internet

### Opción A — Netlify (drag & drop, sin cuenta)

1. Entra a [https://app.netlify.com/drop](https://app.netlify.com/drop).
2. Arrastra **la carpeta completa** a la zona de drop.
3. En segundos te da una URL pública.
4. Para dominio propio o URL fija, crea cuenta gratis y *claim* el deploy.

### Opción B — GitHub Pages

1. Crea un repo nuevo en GitHub (público).
2. Sube todos los archivos del kit a la raíz del repo (mantén la carpeta `data/`).
3. **Settings → Pages** → fuente: `main` / carpeta: `/ (root)` → **Save**.
4. En 1-2 min tu mapa estará en `https://<usuario>.github.io/<repo>/`.

### Opción C — abrir localmente

Doble click en `index.html` **funciona en muchos navegadores**, pero algunos bloquean `fetch()` desde `file://`. Si ves el error "no pude cargar config.json", sirve la carpeta con un servidor estático:

```bash
# con Node.js
npx serve .

# con Python 3
python -m http.server 8000
```

Abre la URL que te dé (`http://localhost:3000` o similar).

---

## ✏️ Cómo modificar

### Cambiar el título o basemap inicial

Edita `config.json`:

```json
{
  "titulo": "Mi nuevo título",
  "basemap": "carto-light"
}
```

Basemaps disponibles: `carto-dark`, `carto-light`, `osm`, `esri-sat`, `opentopo`.

### Reemplazar los datos de una capa

Sustituye el archivo correspondiente en `data/` por uno nuevo con el mismo nombre (`capa-0.geojson`, etc.). Mantén la estructura GeoJSON con `FeatureCollection`.

### Cambiar nombre, color o simbología de una capa

Edita `config.json`. Cada capa tiene esta forma:

```json
{
  "nombre": "Estaciones",
  "color": "#2cd4e0",
  "simbologia": { "modo": "unico" },
  "archivo": "data/capa-0.geojson"
}
```

**Simbología por categoría** — color distinto por valor de un campo:

```json
"simbologia": {
  "modo": "categorico",
  "campo": "tipo",
  "paleta": {
    "Hidrología":   "#2cd4e0",
    "Meteorología": "#f4820a",
    "Sísmica":      "#e63946"
  }
}
```

Los valores no incluidos en `paleta` salen en gris (`#7a8a9a`) y aparecen como "Otros" en la leyenda.

### Agregar una capa nueva

1. Pon tu GeoJSON en `data/capa-N.geojson` (con el siguiente número libre).
2. Agrega una entrada al array `capas` en `config.json`.

### Cambiar colores generales / popups

Edita `style.css` — las variables CSS al inicio (`--verde`, `--surface`, `--t1`...) y la sección "Leaflet overrides" para los popups.

---

## 🧩 Controles del mapa

- **Buscador de direcciones** (arriba izquierda): busca por nombre, dirección o lugar (Nominatim/OpenStreetMap, global). Click en un resultado vuela hasta él.
- **Zoom + Fullscreen** (arriba derecha): + / − / pantalla completa.
- **Selector de capas** (ícono ◈ arriba derecha): cambia basemap y muestra/oculta capas completas.
- **Leyenda interactiva** (abajo izquierda): muestra colores y categorías. En capas con simbología por categoría, **cada entrada tiene un checkbox** que filtra esos features sin recargar.
- **Escala** (abajo izquierda): en kilómetros.
- **Popup**: click sobre una geometría muestra sus propiedades (configurable vía `popupCampos`); las URLs son clicables.

### Limitar campos en el popup

Por defecto el popup muestra todas las propiedades del feature. Para mostrar solo algunas, agrega `popupCampos` a la capa en `config.json`:

```json
{
  "nombre": "Estaciones",
  "color": "#2cd4e0",
  "simbologia": { "modo": "unico" },
  "popupCampos": ["nombre", "tipo", "fecha"],
  "archivo": "data/capa-0.geojson"
}
```

Si omites `popupCampos` (o lo dejas como un arreglo vacío), el popup vuelve al modo "todos los campos".

---

## 🛠 Tecnologías

- [Leaflet](https://leafletjs.com) — BSD-2.
- [CARTO Basemaps](https://carto.com/basemaps/) y [OpenStreetMap](https://www.openstreetmap.org) — tiles base.

Sin tracking, sin cookies, sin analytics. Tus datos viven solo en tu navegador y en el hosting donde lo subas.

---

## 📜 Licencia

Tú eres dueñ@ del contenido (`config.json`, `data/`, título). La plantilla (`index.html`, `style.css`) es MIT — úsala como quieras.

Generado por **GeoHub Chile** · [geohub.cl](https://geohub.cl)
