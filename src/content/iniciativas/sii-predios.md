---
nombre: "SII Predios — Catastro predial por comuna"
tipo: comunidad
categoria: admin
icono: "🏠"
estado: activo
estadoTexto: "Activo"
descripcion: "Pipeline que descarga predios catastrales del Servicio de Impuestos Internos (SII) por comuna: vectoriza polígonos desde el WMS público y los cruza con la API tabular del SII. Exporta un GeoPackage con geometría + rol, avalúo (total/afecto/exento), dirección, destino, ubicación urbano/rural, superficies y manzana. Datos referenciales — para efectos legales consultar sii.cl."
tags: "sii predios rol catastro avalúo wms geopackage python chile impuestos manzana"
orden: 35
capas:
  - "Polígonos prediales (EPSG:4326)"
  - "Rol predial"
  - "Avalúo total / afecto / exento"
  - "Dirección + destino"
  - "Superficie terreno + construida"
  - "Urbano / Rural"
  - "Manzana / predio"
  - "GeoPackage por comuna"
stats:
  - { label: "Python", valor: "Pipeline" }
  - { label: "Output", valor: "GeoPackage" }
  - { label: "EPSG:4326 · Open source" }
acciones:
  - { tipo: github, texto: "GitHub", url: "https://github.com/DanielD-S/sii-predios" }
  - { tipo: desc, texto: "Ver SII oficial ↗", url: "https://www.sii.cl" }
---
