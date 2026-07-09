---
nombre: "Planes Reguladores e IPT (MINVU)"
categoria: admin
estado: activo
estadoTexto: "Activo — Jul 2026"
descripcion: "Zonificación urbana oficial de Chile como servicios consultables sin token: Planes Reguladores Comunales (PRC) de 11 regiones + PRMS metropolitano, límites urbanos de todo el país y Zonas de Interés Público. Normalmente esta información hay que pedirla municipio por municipio o extraerla de PDFs — aquí están los servicios ArcGIS públicos de MINVU, verificados. Fuente: IDE MINVU."
tags: "minvu prc plan regulador ipt zonificacion urbanismo limite urbano zip prms arcgis"
orden: 15
capas:
  - "PRC 11 regiones"
  - "PRMS Metropolitano"
  - "Límites urbanos Chile"
  - "ZIP 2023"
  - "Seccionales"
capasExtra: "+270 capas en total"
stats:
  - { label: "servicios regionales", valor: "12" }
  - { label: "capas", valor: "270+" }
  - { label: "ArcGIS REST · sin token" }
acciones:
  - { tipo: ver, texto: "Ver servicios" }
  - { tipo: desc, texto: "Portal IPT ↗", url: "https://portalipt.minvu.cl" }
  - { tipo: externo, texto: "Geoportal MINVU ↗", url: "https://ide.minvu.cl" }
archivos:
  release: "Servicios verificados · Jul 2026"
  grupos:
    - titulo: "Planes Reguladores Comunales por región (FeatureServer)"
      items:
        - { nombre: "PRC Antofagasta", size: "26 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/02__PRC_Antofagasta/FeatureServer" }
        - { nombre: "PRC Atacama", size: "7 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/03_PRC_Atacama/FeatureServer" }
        - { nombre: "PRC Coquimbo", size: "11 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/04_PRC_Coquimbo/FeatureServer" }
        - { nombre: "PRC Valparaíso", size: "55 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/05_PRC_Valparaiso/FeatureServer" }
        - { nombre: "PRC O'Higgins", size: "36 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/06_PRC_OHiggins222/FeatureServer" }
        - { nombre: "PRC La Araucanía", size: "37 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/09_PRC_La_Araucania/FeatureServer" }
        - { nombre: "PRC Los Lagos", size: "24 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/10_PRC_Los_Lagos/FeatureServer" }
        - { nombre: "PRC Aysén", size: "10 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/11_PRC_Aysen/FeatureServer" }
        - { nombre: "PRC Magallanes", size: "7 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/12_PRC_Magallanes/FeatureServer" }
        - { nombre: "PRC Los Ríos", size: "16 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/14_PRC_Los_Ríos/FeatureServer" }
        - { nombre: "PRC Ñuble", size: "18 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/PRC_NUBLE/FeatureServer" }
    - titulo: "Metropolitana y nacional"
      items:
        - { nombre: "PRMS — Plan Regulador Metropolitano de Santiago", size: "7 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/13_PRMS_2/FeatureServer" }
        - { nombre: "Límites urbanos IPT — todo Chile", size: "17 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/LU_IPT_CHILE/FeatureServer" }
        - { nombre: "Zonas de Interés Público (ZIP 2023 + histórico)", size: "8 capas", url: "./herramientas/descargador-arcgis?url=https://services3.arcgis.com/cTnMkBRk4HWkUCRo/arcgis/rest/services/DGU_ZIP/FeatureServer" }
---

Cada enlace abre el [descargador de capas ArcGIS](./herramientas/descargador-arcgis)
de GeoHub: verás las capas del servicio con nombre y tipo, listas para bajar
como GeoJSON o copiar la URL para QGIS — sin cuenta ni token.

**Regiones sin servicio público en este listado**: Tarapacá, Arica y
Parinacota, Maule y Biobío publican sus PRC solo en el servidor interno de
MINVU (requiere token) o como documentos en el
[Portal IPT](https://portalipt.minvu.cl). Para esas regiones, el portal es
el camino oficial.

**¿Necesitas validar la topología de estos PRC?** La iniciativa comunitaria
[PRC Extractor](https://github.com/negentropy-technologies/PRC_extractor_notebook)
descarga este mismo catálogo y detecta solapamientos de zonas, geometrías
inválidas y duplicados (ver su card en esta sección).
