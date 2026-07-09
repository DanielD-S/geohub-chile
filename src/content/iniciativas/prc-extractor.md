---
nombre: "PRC Extractor — QA topológica de Planes Reguladores"
categoria: admin
estado: beta
estadoTexto: "Comunidad — Jul 2026"
descripcion: "Notebook Jupyter que descarga el catálogo completo de Planes Reguladores Comunales desde el servicio ArcGIS de MINVU y audita su calidad topológica: solapamientos de zonas, geometrías inválidas y duplicados exactos, con respaldo normativo (LGUC y jurisprudencia de Contraloría). Exporta GeoPackage y mapas interactivos. Autor: Negentropy Technologies."
tags: "prc minvu ipt topologia qa jupyter notebook geopandas shapely zonificacion comunidad"
orden: 16
capas:
  - "Descarga catálogo IPT completo"
  - "Solapamientos de zonas"
  - "Geometrías inválidas"
  - "Duplicados exactos"
stats:
  - { label: "validaciones", valor: "3" }
  - { label: "salida", valor: "GeoPackage" }
  - { label: "Apache 2.0 · Colab o local" }
acciones:
  - { tipo: github, texto: "GitHub", url: "https://github.com/negentropy-technologies/PRC_extractor_notebook" }
  - { tipo: desc, texto: "Abrir en Colab ↗", url: "https://colab.research.google.com/github/negentropy-technologies/PRC_extractor_notebook/blob/master/notebook/minvu_ipt_topologia.ipynb" }
---

Proyecto de la comunidad (Negentropy Technologies, Apache 2.0). Complementa la
iniciativa de [Planes Reguladores e IPT (MINVU)](#iniciativas): mientras esa
entrega los servicios con la zonificación oficial, este notebook los audita —
detecta zonas que se solapan, polígonos inválidos y registros duplicados, casos
reales que aparecen en los PRC publicados y que pueden alterar un análisis
normativo.

Corre en Google Colab o local (pip/conda) con GeoPandas y Shapely 2. Consume el
mismo servicio público `geoide.minvu.cl/server/rest/services/IPT` (verificado
julio 2026: 76 servicios disponibles) y no requiere token ni cuenta.
