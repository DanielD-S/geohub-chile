---
nombre: "Hydrotrack — Monitoreo satelital de la Laguna de Aculeo"
categoria: hidrico
estado: beta
estadoTexto: "Comunidad — v0.1.0"
descripcion: "Notebook autocontenido que narra la desaparición y recuperación parcial de la Laguna de Aculeo (2013–2026) con Landsat 8/9: índices MNDWI/NDWI, clasificación GMM + árbol de decisión y segmentación SAM3 de Meta AI (zero-shot), benchmarkeadas sobre 705 escenas. Sin base de datos ni servidor; corre en Colab o local y es replicable para cualquier cuerpo de agua (descarga de escenas nuevas requiere registro gratuito en la API M2M del USGS). Autor: Negentropy Technologies."
tags: "aculeo laguna sequia landsat sam3 mndwi ndwi agua monitoreo satelital jupyter notebook comunidad"
orden: 52
capas:
  - "Serie 2013–2026 (705 escenas)"
  - "Índices MNDWI / NDWI"
  - "GMM + Decision Tree"
  - "SAM3 Tracker (Meta AI)"
stats:
  - { label: "escenas analizadas", valor: "705" }
  - { label: "concordancia detectores", valor: "IoU 0.95" }
  - { label: "Apache 2.0 · Colab o local" }
acciones:
  - { tipo: github, texto: "GitHub", url: "https://github.com/negentropy-technologies/hydrotrack_notebook" }
  - { tipo: desc, texto: "Abrir en Colab ↗", url: "https://colab.research.google.com/github/negentropy-technologies/hydrotrack_notebook/blob/main/notebook/aculeo_story.ipynb" }
---

Proyecto de la comunidad (Negentropy Technologies, Apache 2.0). Documenta con
datos satelitales la crisis hídrica de la Laguna de Aculeo: lago pleno de
~10 km² en 2013, sequía crítica en 2018, cero superficie de agua en 2019 y
recuperación parcial (~9,3 km²) en 2026. El método es replicable para otros
cuerpos de agua chilenos.

Para descargar escenas nuevas requiere credenciales gratuitas de la
[API M2M del USGS](https://m2m.cr.usgs.gov/) (registro sin costo); también
funciona sobre GeoTIFF locales. La segmentación SAM3 puede correr en CPU, pero
se acelera con GPU (CUDA 12.8). Roadmap del autor: Sentinel-2 (v0.2.0) y
Sentinel-1 SAR (v0.3.0).
