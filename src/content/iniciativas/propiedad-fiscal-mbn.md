---
nombre: "Propiedad Fiscal y Rutas Patrimoniales (MBN)"
categoria: admin
estado: activo
estadoTexto: "Activo — Jul 2026"
descripcion: "Capas oficiales del Ministerio de Bienes Nacionales como servicios consultables sin token: propiedad fiscal administrada (9.074 predios), SNAP en propiedad fiscal, Bienes Nacionales Protegidos, rutas patrimoniales, vértices geodésicos y estaciones GNSS. GeoServer WMS/WFS público + descargas shapefile directas desde la IDE MBN, verificados. Fuente: IDE MBN."
tags: "bienes nacionales propiedad fiscal snap rutas patrimoniales geodesia gnss vertices wms wfs geoserver"
orden: 18
capas:
  - "Propiedad fiscal administrada"
  - "SNAP fiscal"
  - "Bienes Nacionales Protegidos"
  - "Rutas patrimoniales"
  - "Vértices geodésicos"
  - "Estaciones GNSS"
stats:
  - { label: "predios fiscales", valor: "9.074" }
  - { label: "capas", valor: "8" }
  - { label: "GeoServer WMS/WFS · sin token" }
acciones:
  - { tipo: ver, texto: "Ver capas" }
  - { tipo: desc, texto: "Dashboard MBN ↗", url: "https://idembn.bienes.cl/idembn/dashboard/2035" }
  - { tipo: externo, texto: "IDE MBN ↗", url: "https://ide.bienes.cl" }
archivos:
  release: "Servicios y descargas verificados · Jul 2026"
  grupos:
    - titulo: "Servicios conectables (GeoServer, sin token)"
      items:
        - { nombre: "Propiedad Fiscal Administrada — WFS GeoJSON directo", size: "9.074 predios", url: "https://idembn.bienes.cl/geoserver/ppff_admin/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=ppff_admin:propiedad_fiscal_administrada__abril_2026&outputFormat=application/json" }
        - { nombre: "SNAP fiscal — WMS", size: "WMS", url: "https://idembn.bienes.cl/geoserver/SNAP/wms?service=WMS&request=GetCapabilities" }
        - { nombre: "Bienes Nacionales Protegidos — WMS", size: "WMS", url: "https://idembn.bienes.cl/geoserver/BNP/wms?service=WMS&request=GetCapabilities" }
        - { nombre: "Rutas Patrimoniales: Ámbitos — WMS", size: "WMS", url: "https://idembn.bienes.cl/geoserver/AmbitosRutasPatrimoniales/wms?service=WMS&request=GetCapabilities" }
    - titulo: "Descargas oficiales (shapefile ZIP)"
      items:
        - { nombre: "Propiedad Fiscal Administrada · abril 2026", size: "3.1 MB", url: "https://idembn.bienes.cl/catastro/layer/downloadLayer/3130/shapefile?slug=produccion_y_almacenamiento&module=layer" }
        - { nombre: "SNAP en Propiedad Fiscal · mayo 2026", size: "137 MB", url: "https://idembn.bienes.cl/catastro/catalog/download/ca3c267b-5270-39d0-97d2-6e4694a11877" }
        - { nombre: "Bienes Nacionales Protegidos · mayo 2026", size: "1.4 MB", url: "https://idembn.bienes.cl/catastro/catalog/download/f3368931-ce28-3012-84d3-4e0f93041822" }
        - { nombre: "Rutas Patrimoniales: Circuitos · octubre 2025", size: "6.6 MB", url: "https://idembn.bienes.cl/ugtp/layer/downloadLayer/2830/shapefile?slug=produccion_y_almacenamiento&module=layer" }
        - { nombre: "Rutas Patrimoniales: Hitos · octubre 2025", size: "118 KB", url: "https://idembn.bienes.cl/ugtp/layer/downloadLayer/2829/shapefile?slug=produccion_y_almacenamiento&module=layer" }
        - { nombre: "Rutas Patrimoniales: Ámbitos · enero 2024", size: "6 KB", url: "https://idembn.bienes.cl/idembn/catalog/download/9eaec749-40fd-3946-9234-e8a656bcad8a" }
        - { nombre: "Vértices Geodésicos · mayo 2024", size: "24 KB", url: "https://idembn.bienes.cl/catastro/catalog/download/dfe2d684-951a-38c4-9f0a-dcda0af03c59" }
        - { nombre: "Estaciones de Referencia GNSS · mayo 2024", size: "6 KB", url: "https://idembn.bienes.cl/catastro/catalog/download/8e3141d6-4c05-3999-ad8f-53d1cf975fa2" }
---

Para conectar los servicios en QGIS: **Capa → Añadir capa WMS/WMTS** con la URL
del servicio (por ejemplo `https://idembn.bienes.cl/geoserver/SNAP/wms`), o
**Añadir capa WFS** con `https://idembn.bienes.cl/geoserver/ppff_admin/wfs`.
No requieren cuenta ni token. El WFS de propiedad fiscal entrega los datos
directamente en WGS84 (EPSG:4326).

**Advertencias**: el MBN versiona estas capas por mes y a veces renombra los
workspaces del GeoServer al actualizar (los de Circuitos e Hitos de octubre
2025 ya no responden como servicio; quedan solo como descarga). Si un enlace
deja de funcionar, el [dashboard público de la IDE MBN](https://idembn.bienes.cl/idembn/dashboard/2035)
siempre tiene los links vigentes. La representación del límite internacional
(DIFROL) está autorizada a escala 1:50.000; representaciones a escalas mayores
pueden no corresponder al trazado oficial.
