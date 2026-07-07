---
nombre: "Catastro Nacional de Campamentos"
categoria: social
estado: activo
estadoTexto: "Activo — Jul 2026"
descripcion: "Catastro oficial de campamentos de Chile georreferenciado: asentamientos vigentes, histórico y totales por región. Dato muy citado en estudios sociales y urbanos, difícil de encontrar como capa consultable — este es el servicio ArcGIS público de MINVU, verificado y sin token."
tags: "minvu campamentos asentamientos vivienda social catastro"
orden: 45
capas:
  - "Campamentos vigentes"
  - "Histórico"
  - "Totales regionales"
stats:
  - { label: "cobertura", valor: "nacional" }
  - { label: "capas", valor: "3" }
  - { label: "ArcGIS REST · sin token" }
acciones:
  - { tipo: ver, texto: "Ver servicios" }
  - { tipo: externo, texto: "Geoportal MINVU ↗", url: "https://ide.minvu.cl" }
archivos:
  release: "Servicio verificado · Jul 2026"
  grupos:
    - titulo: "Servicio ArcGIS (FeatureServer)"
      items:
        - { nombre: "Campamentos vigentes (capa 2)", size: "puntos", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/Datos_Compamentos/FeatureServer/2" }
        - { nombre: "Histórico (capa 0)", size: "series", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/Datos_Compamentos/FeatureServer/0" }
        - { nombre: "Totales por región (capa 1)", size: "resumen", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/Datos_Compamentos/FeatureServer/1" }
---
