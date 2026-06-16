---
nombre: "Monitor de Riesgos Meteorológicos Chile"
valoracionIssue: 5
categoria: riesgo
icono: "🔥❄️"
iconoBg: "linear-gradient(135deg,rgba(230,57,70,0.15),rgba(255,107,53,0.1))"
estado: activo
estadoTexto: "En línea · Live"
categoriaExtra: { label: "Meteorología", color: "#4cc9f0" }
descripcion: "Visor integrado con 9 secciones: incendios forestales en tiempo real (NASA FIRMS + CONAF), fenómenos invernales (heladas, nevazones, precipitaciones extremas, temporales), pronóstico 7 días, historial ERA5 y script QGIS Python descargable. Todo en un único HTML estático, sin servidor."
tags: "incendios invierno heladas nieve precipitación alertas qgis firms conaf open-meteo"
orden: 30
capas:
  - "Focos calor FIRMS"
  - "Alertas meteorológicas"
  - "Pronóstico 7 días"
  - "Historial ERA5"
  - "Script QGIS .py"
  - "13 zonas monitoreadas"
  - "Mapa Leaflet"
  - "Guía ciudadana"
  - "Carga CSV propio"
stats:
  - { label: "zonas", valor: "13" }
  - { label: "secciones", valor: "9" }
  - { label: "Open-Meteo · CONAF · NASA FIRMS" }
acciones:
  - { tipo: github, texto: "GitHub", url: "https://github.com/DanielD-S/Capas_IDE_CHILE" }
  - { tipo: ver, texto: "Ver detalle" }
  - { tipo: externo, texto: "Abrir visor ↗", url: "./visor_riesgos_chile.html" }
archivos:
  release: "v2 · Jun 2026 · IBM Plex"
  grupos:
    - titulo: "Pestañas del visor"
      items:
        - { nombre: "⚡ Situación actual — Open-Meteo API (Live)", size: "Live", url: "https://open-meteo.com" }
        - { nombre: "📅 Pronóstico 7 días — ECMWF + DWD (Live)", size: "Live", url: "https://open-meteo.com" }
        - { nombre: "🗺️ Mapa nacional — Leaflet · CARTO (Live)", size: "Live", url: "https://leafletjs.com" }
        - { nombre: "🔥 Incendios FIRMS — NASA FIRMS + CONAF (CSV)", size: "CSV", url: "https://firms.modaps.eosdis.nasa.gov" }
        - { nombre: "📊 Historial climatológico — ERA5", size: "Estático", url: "https://cds.climate.copernicus.eu" }
        - { nombre: "❄️ Fenómenos — Didáctico todos los públicos", size: "Didáctico", url: "https://github.com/DanielD-S/Capas_IDE_CHILE" }
        - { nombre: "📖 Guía ciudadana — Emergencias", size: "Didáctico", url: "https://www.senapred.cl" }
        - { nombre: "🔗 Fuentes — 8 fuentes oficiales", size: "Links", url: "https://github.com/DanielD-S/Capas_IDE_CHILE" }
        - { nombre: "🐍 Script QGIS Python — .py · 7 pasos", size: "Descargable", url: "https://github.com/DanielD-S/Capas_IDE_CHILE" }
---
