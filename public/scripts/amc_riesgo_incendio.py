# -*- coding: utf-8 -*-
"""
AMC — Susceptibilidad a incendios forestales (GeoHub Chile)
============================================================

Script de Processing para QGIS 3.28+ que calcula un mapa de susceptibilidad
a incendios forestales mediante análisis multicriterio (suma lineal ponderada).

Criterios (pesos por defecto, editables):
  1. Combustible vegetal (uso de suelo reclasificado)   30%
  2. Pendiente                                          15%
  3. Orientación de ladera (exposición norte)           10%
  4. Clima (t° máxima estival u otro proxy, opcional)   12%
  5. Viento (velocidad media estival, opcional)          8%
  6. Distancia a caminos (ignición antrópica)           12%
  7. Distancia a zonas pobladas (interfaz urbano-rural) 13%

Si un criterio opcional no se entrega, su peso se redistribuye
proporcionalmente entre los demás.

Validación: si entregas focos históricos (p. ej. NASA FIRMS), el reporte
indica qué porcentaje de focos reales cae en las clases Alta y Muy alta.

Salidas:
  - Ráster de susceptibilidad 0-100 (float)
  - Ráster clasificado en 5 clases (1=Muy baja … 5=Muy alta)
  - Reporte HTML con pesos, parámetros y validación

IMPORTANTE: este mapa representa SUSCEPTIBILIDAD ESTRUCTURAL del territorio
(qué zonas tienden a arder según sus condiciones), no el riesgo operacional
de un día concreto (que depende del clima en tiempo real).

Instalación: Caja de herramientas de Procesos → Scripts → Añadir script
Fuente: https://danield-s.github.io/geohub-chile/herramientas/amc-riesgo-incendio
Licencia: MIT
"""

import math
import unicodedata

import numpy as np
from osgeo import gdal
from qgis.core import (
    QgsField,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFileDestination,
    QgsProcessingParameterNumber,
    QgsProcessingParameterRasterDestination,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QCoreApplication, QVariant

gdal.UseExceptions()

NODATA = -9999.0

# Reclasificación de combustible por palabra clave (minúsculas, sin tildes se
# comparan igual porque usamos `in`). Basada en categorías del Catastro de
# Uso de Suelo y Vegetación CONAF/CIREN. 0-1 = inflamabilidad relativa.
# None = zona excluida (no arde: agua, nieve, urbano consolidado).
COMBUSTIBLE_KEYWORDS = [
    ("eucal", 0.95), ("pino", 0.95), ("plantac", 0.95),
    ("matorral arborescente", 0.80), ("matorral", 0.75),
    ("pradera", 0.65), ("pastizal", 0.65), ("estepa", 0.60),
    ("renoval", 0.55), ("bosque mixto", 0.60), ("bosque nativo", 0.50),
    ("bosque", 0.55),
    ("rotacion", 0.35), ("agricola", 0.30), ("cultivo", 0.30),
    ("frutal", 0.25), ("vina", 0.25), ("viña", 0.25),
    ("humedal", 0.10), ("vega", 0.10),
    ("sin vegetacion", 0.05), ("suelo desnudo", 0.05), ("afloramiento", 0.05),
    ("playa", 0.05), ("duna", 0.10), ("mina", 0.05),
    ("urban", None), ("ciudad", None), ("industrial", None),
    ("agua", None), ("lago", None), ("rio", None), ("río", None),
    ("embalse", None), ("mar ", None),
    ("nieve", None), ("glaciar", None), ("hielo", None),
]
COMBUSTIBLE_DEFAULT = 0.50  # categoría no reconocida → medio, y se reporta


def tr(texto):
    return QCoreApplication.translate("AMCIncendio", texto)


def _norm(s):
    """Minúsculas sin acentos, para comparar categorías con las palabras clave
    (las categorías de CONAF vienen con tildes: 'Agrícolas', 'Áreas', etc.)."""
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


class AmcRiesgoIncendio(QgsProcessingAlgorithm):
    DEM = "DEM"
    USO = "USO"
    CAMPO_USO = "CAMPO_USO"
    CAMINOS = "CAMINOS"
    POBLADO = "POBLADO"
    CLIMA = "CLIMA"
    VIENTO = "VIENTO"
    AREA = "AREA"
    RESOLUCION = "RESOLUCION"
    P_COMBUSTIBLE = "P_COMBUSTIBLE"
    P_PENDIENTE = "P_PENDIENTE"
    P_ORIENTACION = "P_ORIENTACION"
    P_CLIMA = "P_CLIMA"
    P_VIENTO = "P_VIENTO"
    P_CAMINOS = "P_CAMINOS"
    P_POBLADO = "P_POBLADO"
    FOCOS = "FOCOS"
    OUT_SUSCEPTIBILIDAD = "OUT_SUSCEPTIBILIDAD"
    OUT_CLASES = "OUT_CLASES"
    OUT_REPORTE = "OUT_REPORTE"

    # ── Metadata ──────────────────────────────────────────────────────
    def name(self):
        return "amc_riesgo_incendio"

    def displayName(self):
        return tr("AMC — Susceptibilidad a incendios forestales")

    def group(self):
        return tr("GeoHub Chile")

    def groupId(self):
        return "geohub_chile"

    def shortHelpString(self):
        return tr(
            "Calcula susceptibilidad a incendios forestales por suma lineal "
            "ponderada de 5-7 criterios. Los pesos por defecto provienen de "
            "literatura AMC en clima mediterráneo y son editables. "
            "Entrega ráster 0-100, clasificación en 5 clases y reporte HTML "
            "con la metodología (incluye validación contra focos históricos "
            "si se entregan, p. ej. NASA FIRMS). "
            "El área de estudio debe estar en un CRS proyectado en metros "
            "(p. ej. EPSG:32718/32719). "
            "Documentación completa: "
            "https://danield-s.github.io/geohub-chile/herramientas/amc-riesgo-incendio"
        )

    def createInstance(self):
        return AmcRiesgoIncendio()

    # ── Parámetros ────────────────────────────────────────────────────
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.AREA, tr("Área de estudio (polígono, CRS proyectado en metros)"),
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.DEM, tr("DEM (modelo de elevación)")))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.USO, tr("Uso de suelo / vegetación (polígonos, p. ej. Catastro CONAF)"),
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterField(
            self.CAMPO_USO, tr("Campo con la categoría de uso/vegetación"),
            parentLayerParameterName=self.USO))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.CAMINOS, tr("Caminos (líneas, p. ej. OSM)"),
            [QgsProcessing.TypeVectorLine]))
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.POBLADO, tr("Zonas pobladas / límites urbanos (polígonos, p. ej. MINVU LU_IPT)"),
            [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.CLIMA, tr("OPCIONAL — Clima: t° máxima estival u otro proxy de sequedad (ráster)"),
            optional=True))
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.VIENTO, tr("OPCIONAL — Viento: velocidad media estival (ráster)"),
            optional=True))
        self.addParameter(QgsProcessingParameterNumber(
            self.RESOLUCION, tr("Resolución de salida (m)"),
            QgsProcessingParameterNumber.Double, defaultValue=100.0, minValue=10.0))

        pesos = [
            (self.P_COMBUSTIBLE, "Peso: combustible vegetal", 30.0),
            (self.P_PENDIENTE, "Peso: pendiente", 15.0),
            (self.P_ORIENTACION, "Peso: orientación (exposición N)", 10.0),
            (self.P_CLIMA, "Peso: clima", 12.0),
            (self.P_VIENTO, "Peso: viento", 8.0),
            (self.P_CAMINOS, "Peso: distancia a caminos", 12.0),
            (self.P_POBLADO, "Peso: interfaz urbano-rural", 13.0),
        ]
        for clave, nombre, defecto in pesos:
            self.addParameter(QgsProcessingParameterNumber(
                clave, tr(nombre), QgsProcessingParameterNumber.Double,
                defaultValue=defecto, minValue=0.0, maxValue=100.0))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.FOCOS, tr("OPCIONAL — Focos históricos para validación (puntos, p. ej. NASA FIRMS)"),
            [QgsProcessing.TypeVectorPoint], optional=True))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUT_SUSCEPTIBILIDAD, tr("Susceptibilidad (0-100)")))
        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUT_CLASES, tr("Susceptibilidad clasificada (5 clases)")))
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUT_REPORTE, tr("Reporte de metodología (HTML)"),
            fileFilter="HTML (*.html)"))

    # ── Utilidades ráster ─────────────────────────────────────────────
    def _grid(self, area, res):
        ext = area.extent()
        xmin = math.floor(ext.xMinimum() / res) * res
        ymin = math.floor(ext.yMinimum() / res) * res
        xmax = math.ceil(ext.xMaximum() / res) * res
        ymax = math.ceil(ext.yMaximum() / res) * res
        ancho = max(1, int(round((xmax - xmin) / res)))
        alto = max(1, int(round((ymax - ymin) / res)))
        return xmin, ymin, xmax, ymax, ancho, alto

    def _leer(self, ruta):
        ds = gdal.Open(ruta)
        banda = ds.GetRasterBand(1)
        arr = banda.ReadAsArray().astype(np.float64)
        nd = banda.GetNoDataValue()
        if nd is not None:
            arr[arr == nd] = np.nan
        ds = None
        return arr

    def _alinear(self, capa_ruta, ctx, fb, resample="bilinear"):
        """Reproyecta/remuestrea un ráster a la grilla común y devuelve array."""
        import processing
        salida = processing.run("gdal:warpreproject", {
            "INPUT": capa_ruta,
            "TARGET_CRS": self._crs,
            "RESAMPLING": {"near": 0, "bilinear": 1}[resample],
            "TARGET_RESOLUTION": self._res,
            "TARGET_EXTENT": f"{self._xmin},{self._xmax},{self._ymin},{self._ymax} [{self._crs.authid()}]",
            "NODATA": NODATA,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]
        arr = self._leer(salida)
        arr[arr == NODATA] = np.nan
        return arr

    def _rasterizar(self, capa, ctx, fb, campo=None, quemar=1.0):
        import processing
        params = {
            "INPUT": capa,
            "UNITS": 1,
            "WIDTH": self._res,
            "HEIGHT": self._res,
            "EXTENT": f"{self._xmin},{self._xmax},{self._ymin},{self._ymax} [{self._crs.authid()}]",
            "NODATA": 0.0,
            "DATA_TYPE": 5,
            "INIT": 0.0,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }
        if campo:
            params["FIELD"] = campo
        else:
            params["BURN"] = quemar
        return processing.run("gdal:rasterize", params,
                              context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]

    def _proximidad(self, raster_ruta, ctx, fb):
        import processing
        salida = processing.run("gdal:proximity", {
            "INPUT": raster_ruta,
            "BAND": 1,
            "VALUES": "1",
            "UNITS": 0,  # coordenadas georreferenciadas (metros en CRS proyectado)
            "NODATA": NODATA,
            "DATA_TYPE": 5,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]
        return self._leer(salida)

    def _minmax(self, arr):
        vmin = np.nanmin(arr)
        vmax = np.nanmax(arr)
        if not np.isfinite(vmin) or vmax - vmin < 1e-9:
            return np.where(np.isnan(arr), np.nan, 0.5)
        return (arr - vmin) / (vmax - vmin)

    def _guardar(self, arr, ruta, tipo=gdal.GDT_Float32):
        drv = gdal.GetDriverByName("GTiff")
        ds = drv.Create(ruta, self._ancho, self._alto, 1, tipo,
                        options=["COMPRESS=DEFLATE"])
        ds.SetGeoTransform((self._xmin, self._res, 0, self._ymax, 0, -self._res))
        ds.SetProjection(self._crs.toWkt())
        banda = ds.GetRasterBand(1)
        salida = np.where(np.isnan(arr), NODATA, arr)
        banda.WriteArray(salida.astype(np.float32))
        banda.SetNoDataValue(NODATA)
        ds.FlushCache()
        ds = None

    # ── Algoritmo principal ───────────────────────────────────────────
    def processAlgorithm(self, parameters, ctx, fb):
        import processing
        area = self.parameterAsVectorLayer(parameters, self.AREA, ctx)
        dem = self.parameterAsRasterLayer(parameters, self.DEM, ctx)
        uso = self.parameterAsVectorLayer(parameters, self.USO, ctx)
        campo_uso = self.parameterAsString(parameters, self.CAMPO_USO, ctx)
        caminos = self.parameterAsVectorLayer(parameters, self.CAMINOS, ctx)
        poblado = self.parameterAsVectorLayer(parameters, self.POBLADO, ctx)
        clima = self.parameterAsRasterLayer(parameters, self.CLIMA, ctx)
        viento = self.parameterAsRasterLayer(parameters, self.VIENTO, ctx)
        focos = self.parameterAsSource(parameters, self.FOCOS, ctx)
        self._res = self.parameterAsDouble(parameters, self.RESOLUCION, ctx)

        self._crs = area.crs()
        if self._crs.isGeographic():
            raise QgsProcessingException(tr(
                "El área de estudio está en coordenadas geográficas. "
                "Usa un CRS proyectado en metros (p. ej. EPSG:32718 o 32719) "
                "para que las distancias y la resolución tengan sentido."))

        (self._xmin, self._ymin, self._xmax, self._ymax,
         self._ancho, self._alto) = self._grid(area, self._res)
        fb.pushInfo(tr(f"Grilla: {self._ancho} × {self._alto} celdas a {self._res} m"))

        # 1. Pendiente y orientación desde el DEM ----------------------
        fb.setProgressText(tr("1/7 · Pendiente y orientación"))
        dem_alineado = processing.run("gdal:warpreproject", {
            "INPUT": dem,
            "TARGET_CRS": self._crs,
            "RESAMPLING": 1,
            "TARGET_RESOLUTION": self._res,
            "TARGET_EXTENT": f"{self._xmin},{self._xmax},{self._ymin},{self._ymax} [{self._crs.authid()}]",
            "NODATA": NODATA,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]

        pend_ruta = processing.run("gdal:slope", {
            "INPUT": dem_alineado, "BAND": 1, "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]
        pendiente = self._leer(pend_ruta)
        # 0° → 0 · ≥30° → 1 (propagación acelerada en laderas fuertes)
        n_pendiente = np.clip(pendiente / 30.0, 0, 1)

        asp_ruta = processing.run("gdal:aspect", {
            "INPUT": dem_alineado, "BAND": 1, "ZERO_FLAT": True,
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]
        aspecto = self._leer(asp_ruta)
        # Hemisferio sur: exposición N (0°) = más insolación = 1; S (180°) = 0.
        # Celdas planas (aspecto 0 con ZERO_FLAT) quedan neutras vía pendiente.
        n_orientacion = (np.cos(np.radians(aspecto)) + 1.0) / 2.0

        # 2. Combustible (uso de suelo reclasificado) ------------------
        fb.setProgressText(tr("2/7 · Combustible vegetal"))
        idx_campo = uso.fields().indexFromName(campo_uso)
        categorias = sorted({str(f[idx_campo]) for f in uso.getFeatures()
                             if f[idx_campo] is not None})
        mapa_scores, sin_match = {}, []
        for cat in categorias:
            cat_norm = _norm(cat)
            score = COMBUSTIBLE_DEFAULT
            excluida = False
            encontrado = False
            for kw, val in COMBUSTIBLE_KEYWORDS:
                if _norm(kw) in cat_norm:
                    encontrado = True
                    if val is None:
                        excluida = True
                    else:
                        score = val
                    break
            if not encontrado:
                sin_match.append(cat)
            mapa_scores[cat] = None if excluida else score
        if sin_match:
            fb.pushWarning(tr(
                "Categorías de uso sin regla de inflamabilidad (usan 0.5 por defecto): "
                + "; ".join(sin_match[:15])))

        # Copia en memoria con campos numéricos score/excluida
        uso_mem = processing.run("native:savefeatures", {
            "INPUT": uso, "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
        }, context=ctx, feedback=fb, is_child_algorithm=True)["OUTPUT"]
        capa_uso = QgsVectorLayer(uso_mem, "uso_scores", "ogr")
        if not capa_uso.isValid():
            raise QgsProcessingException(tr("No se pudo preparar la capa de uso de suelo."))
        prov = capa_uso.dataProvider()
        prov.addAttributes([QgsField("amc_score", QVariant.Double),
                            QgsField("amc_excl", QVariant.Int)])
        capa_uso.updateFields()
        i_score = capa_uso.fields().indexFromName("amc_score")
        i_excl = capa_uso.fields().indexFromName("amc_excl")
        i_cat = capa_uso.fields().indexFromName(campo_uso)
        cambios = {}
        for f in capa_uso.getFeatures():
            cat = str(f[i_cat]) if f[i_cat] is not None else ""
            s = mapa_scores.get(cat, COMBUSTIBLE_DEFAULT)
            cambios[f.id()] = {i_score: 0.0 if s is None else float(s),
                               i_excl: 1 if s is None else 0}
        prov.changeAttributeValues(cambios)

        n_combustible = self._leer(self._rasterizar(capa_uso, ctx, fb, campo="amc_score"))
        excluidas = self._leer(self._rasterizar(capa_uso, ctx, fb, campo="amc_excl"))
        mascara_excl = excluidas >= 0.5

        # 3-4. Clima y viento (opcionales) -----------------------------
        n_clima = n_viento = None
        if clima is not None:
            fb.setProgressText(tr("3/7 · Clima"))
            n_clima = self._minmax(self._alinear(clima, ctx, fb))
        if viento is not None:
            fb.setProgressText(tr("4/7 · Viento"))
            n_viento = self._minmax(self._alinear(viento, ctx, fb))

        # 5. Distancia a caminos ---------------------------------------
        fb.setProgressText(tr("5/7 · Distancia a caminos"))
        dist_caminos = self._proximidad(self._rasterizar(caminos, ctx, fb), ctx, fb)
        # 0 m → 1 · ≥2 km → 0 (concentración de igniciones junto a rutas)
        n_caminos = np.clip(1.0 - dist_caminos / 2000.0, 0, 1)

        # 6. Interfaz urbano-rural -------------------------------------
        fb.setProgressText(tr("6/7 · Interfaz urbano-rural"))
        dist_poblado = self._proximidad(self._rasterizar(poblado, ctx, fb), ctx, fb)
        # 0 m → 1 · ≥3 km → 0
        n_poblado = np.clip(1.0 - dist_poblado / 3000.0, 0, 1)

        # 7. Suma ponderada --------------------------------------------
        fb.setProgressText(tr("7/7 · Suma ponderada y clasificación"))
        criterios = [
            ("Combustible vegetal", n_combustible,
             self.parameterAsDouble(parameters, self.P_COMBUSTIBLE, ctx)),
            ("Pendiente", n_pendiente,
             self.parameterAsDouble(parameters, self.P_PENDIENTE, ctx)),
            ("Orientación (exposición N)", n_orientacion,
             self.parameterAsDouble(parameters, self.P_ORIENTACION, ctx)),
            ("Clima", n_clima,
             self.parameterAsDouble(parameters, self.P_CLIMA, ctx)),
            ("Viento", n_viento,
             self.parameterAsDouble(parameters, self.P_VIENTO, ctx)),
            ("Distancia a caminos", n_caminos,
             self.parameterAsDouble(parameters, self.P_CAMINOS, ctx)),
            ("Interfaz urbano-rural", n_poblado,
             self.parameterAsDouble(parameters, self.P_POBLADO, ctx)),
        ]
        activos = [(nom, arr, p) for nom, arr, p in criterios
                   if arr is not None and p > 0]
        suma_pesos = sum(p for _, _, p in activos)
        if suma_pesos <= 0:
            raise QgsProcessingException(tr("Todos los pesos son 0 — nada que ponderar."))
        pesos_finales = [(nom, p / suma_pesos) for nom, _, p in activos]

        suscept = np.zeros((self._alto, self._ancho), dtype=np.float64)
        for (nom, arr, p) in activos:
            suscept += np.nan_to_num(arr, nan=0.5) * (p / suma_pesos)
        suscept *= 100.0
        suscept[mascara_excl] = np.nan
        # Fuera del DEM (bordes) → nodata
        suscept[np.isnan(pendiente)] = np.nan

        clases = np.full_like(suscept, np.nan)
        limites = [(0, 20, 1), (20, 40, 2), (40, 60, 3), (60, 80, 4), (80, 100.01, 5)]
        for lo, hi, c in limites:
            clases[(suscept >= lo) & (suscept < hi)] = c

        ruta_out = self.parameterAsOutputLayer(parameters, self.OUT_SUSCEPTIBILIDAD, ctx)
        ruta_clases = self.parameterAsOutputLayer(parameters, self.OUT_CLASES, ctx)
        self._guardar(suscept, ruta_out)
        self._guardar(clases, ruta_clases)

        # Validación con focos históricos ------------------------------
        validacion = None
        if focos is not None:
            total = en_alta = fuera = 0
            from qgis.core import QgsCoordinateTransform, QgsProject
            transf = None
            if focos.sourceCrs() != self._crs:
                transf = QgsCoordinateTransform(focos.sourceCrs(), self._crs,
                                                QgsProject.instance())
            for f in focos.getFeatures():
                geom = f.geometry()
                if geom is None or geom.isEmpty():
                    continue
                pt = geom.asPoint() if not transf else transf.transform(geom.asPoint())
                col = int((pt.x() - self._xmin) / self._res)
                fila = int((self._ymax - pt.y()) / self._res)
                if 0 <= fila < self._alto and 0 <= col < self._ancho:
                    v = clases[fila, col]
                    if np.isnan(v):
                        fuera += 1
                    else:
                        total += 1
                        if v >= 4:
                            en_alta += 1
                else:
                    fuera += 1
            if total > 0:
                validacion = {
                    "total": total,
                    "en_alta": en_alta,
                    "pct": 100.0 * en_alta / total,
                    "fuera": fuera,
                }
                fb.pushInfo(tr(
                    f"Validación: {en_alta}/{total} focos históricos "
                    f"({validacion['pct']:.1f}%) caen en clases Alta/Muy alta."))

        # Reporte HTML --------------------------------------------------
        ruta_rep = self.parameterAsFileOutput(parameters, self.OUT_REPORTE, ctx)
        self._escribir_reporte(ruta_rep, pesos_finales, sin_match, validacion,
                               clima is not None, viento is not None)

        return {
            self.OUT_SUSCEPTIBILIDAD: ruta_out,
            self.OUT_CLASES: ruta_clases,
            self.OUT_REPORTE: ruta_rep,
        }

    def _escribir_reporte(self, ruta, pesos, sin_match, val, con_clima, con_viento):
        filas = "".join(
            f"<tr><td>{nom}</td><td>{p*100:.1f}%</td></tr>" for nom, p in pesos)
        omitidos = []
        if not con_clima:
            omitidos.append("Clima")
        if not con_viento:
            omitidos.append("Viento")
        html_val = ""
        if val:
            color = "#2e7d32" if val["pct"] >= 60 else ("#e65100" if val["pct"] >= 40 else "#c62828")
            html_val = (
                f"<h2>Validación con focos históricos</h2>"
                f"<p><strong style='color:{color}'>{val['pct']:.1f}%</strong> de los "
                f"{val['total']} focos históricos dentro del área caen en las clases "
                f"Alta o Muy alta (4-5). "
                f"{val['fuera']} focos quedaron fuera del área o en zonas excluidas.</p>"
                f"<p>Referencia práctica: sobre 60% el modelo discrimina bien; "
                f"bajo 40% conviene revisar pesos y criterios.</p>")
        html_sm = ""
        if sin_match:
            html_sm = ("<h2>Categorías sin regla de inflamabilidad</h2><p>Usaron el "
                       "valor por defecto (0.5): " + "; ".join(sin_match) + "</p>")
        html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Reporte AMC — Susceptibilidad a incendios</title>
<style>body{{font-family:system-ui,sans-serif;max-width:800px;margin:2rem auto;
padding:0 1rem;color:#222;line-height:1.6}}table{{border-collapse:collapse}}
td,th{{border:1px solid #ccc;padding:4px 12px}}h1{{font-size:1.4rem}}
h2{{font-size:1.1rem;margin-top:1.5rem}}.aviso{{background:#fff3e0;
border-left:4px solid #e65100;padding:.6rem 1rem}}</style></head><body>
<h1>Susceptibilidad a incendios forestales — reporte de metodología</h1>
<p>Método: análisis multicriterio por suma lineal ponderada.
Criterios normalizados 0-1, resultado 0-100 en 5 clases
(1 Muy baja · 2 Baja · 3 Media · 4 Alta · 5 Muy alta).</p>
<h2>Pesos efectivos</h2><table><tr><th>Criterio</th><th>Peso</th></tr>{filas}</table>
{"<p>Criterios omitidos (peso redistribuido): " + ", ".join(omitidos) + "</p>" if omitidos else ""}
<h2>Normalizaciones</h2><ul>
<li>Pendiente: 0° → 0 · ≥30° → 1 (lineal)</li>
<li>Orientación: exposición N → 1 · S → 0 (coseno, hemisferio sur)</li>
<li>Combustible: reclasificación de categorías de uso de suelo (tabla en el script)</li>
<li>Clima / viento: min-max dentro del área</li>
<li>Distancia a caminos: 0 m → 1 · ≥2.000 m → 0</li>
<li>Interfaz urbano-rural: 0 m → 1 · ≥3.000 m → 0</li>
<li>Exclusiones (sin valor): agua, nieve/glaciar, urbano consolidado</li></ul>
{html_val}{html_sm}
<p class="aviso"><strong>Alcance:</strong> este mapa representa susceptibilidad
estructural del territorio, no el riesgo operacional de un día concreto
(que depende de las condiciones meteorológicas en tiempo real). No reemplaza
los productos oficiales de CONAF/SENAPRED.</p>
<p style="color:#777;font-size:.85rem">Generado con el script AMC de
GeoHub Chile · geohub-chile · MIT</p></body></html>"""
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(html)
