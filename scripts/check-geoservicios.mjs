#!/usr/bin/env node
// Verifica el estado de los geoservicios de src/data/geoservicios.json
// y escribe src/data/geoservicios-estado.json con semáforo, latencia e historial.
//
// Niveles de chequeo:
//   1. ¿Responde? — HTTP OK dentro del timeout.
//   2. ¿Habla el protocolo? — capabilities XML válido (WMS/WFS), JSON sin
//      clave "error" (ArcGIS), JSON parseable (geojson/json). Un 200 con
//      HTML o ServiceException cuenta como fallo de protocolo.
//   3. ¿Entrega datos? — para capas ArcGIS (URL terminada en /N) un
//      query returnCountOnly; para el resto, contenido con capas/features.
//
// Semáforo:
//   ok   (🟢) — los 3 niveles pasan.
//   warn (🟡) — responde pero el contenido no es el esperado, o latencia alta.
//   down (🔴) — no responde, HTTP >= 400, error ArcGIS o ServiceException.
//
// Uso local: node scripts/check-geoservicios.mjs
// En CI:     .github/workflows/check-geoservicios.yml

import { readFileSync, writeFileSync, existsSync } from 'node:fs';

const CATALOGO = 'src/data/geoservicios.json';
const ESTADO = 'src/data/geoservicios-estado.json';
const TIMEOUT_MS = 15_000;
const WARN_LATENCIA_MS = 8_000;
const REINTENTOS = 2;
const HISTORIAL_MAX = 30;

async function fetchTimeout(url, opts = {}) {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try {
    return await fetch(url, { ...opts, signal: ctrl.signal, redirect: 'follow' });
  } finally {
    clearTimeout(t);
  }
}

function conParams(url, params) {
  return url + (url.includes('?') ? '&' : '?') + params;
}

// ─── Chequeos por tipo ───────────────────────────────────────────────

async function checkArcgis(url) {
  const r = await fetchTimeout(conParams(url, 'f=json'));
  if (!r.ok) return { estado: 'down', detalle: `HTTP ${r.status}` };
  const texto = await r.text();
  let meta;
  try {
    meta = JSON.parse(texto);
  } catch {
    return { estado: 'warn', detalle: 'Responde pero no entrega JSON (¿portal HTML?)' };
  }
  if (meta.error) {
    return { estado: 'down', detalle: `Error ArcGIS: ${meta.error.message || meta.error.code}` };
  }
  const out = { estado: 'ok', detalle: 'Servicio operativo' };
  if (meta.editingInfo?.lastEditDate) {
    out.lastEdit = new Date(meta.editingInfo.lastEditDate).toISOString().slice(0, 10);
  }
  const esCapa = /\/\d+$/.test(url);
  if (esCapa) {
    const q = await fetchTimeout(conParams(url + '/query', 'where=1%3D1&returnCountOnly=true&f=json'));
    if (!q.ok) return { ...out, estado: 'warn', detalle: `Metadata OK pero query falla (HTTP ${q.status})` };
    let data;
    try {
      data = JSON.parse(await q.text());
    } catch {
      return { ...out, estado: 'warn', detalle: 'Metadata OK pero query no entrega JSON' };
    }
    if (data.error) return { ...out, estado: 'warn', detalle: `Metadata OK pero query falla: ${data.error.message || data.error.code}` };
    if (typeof data.count !== 'number') return { ...out, estado: 'warn', detalle: 'Query sin conteo — capa posiblemente no consultable' };
    out.registros = data.count;
    out.detalle = 'Entrega datos';
  } else {
    const n = (meta.layers?.length ?? 0) + (meta.services?.length ?? 0) + (meta.folders?.length ?? 0);
    if (n === 0) return { ...out, estado: 'warn', detalle: 'Responde pero sin capas ni servicios' };
    out.capas = meta.layers?.length ?? undefined;
    out.detalle = 'Servicio operativo';
  }
  return out;
}

async function checkOgc(url, servicio) {
  const r = await fetchTimeout(conParams(url, `SERVICE=${servicio}&REQUEST=GetCapabilities`));
  if (!r.ok) return { estado: 'down', detalle: `HTTP ${r.status}` };
  const texto = await r.text();
  if (/ServiceException/i.test(texto)) {
    return { estado: 'down', detalle: 'El servidor devuelve ServiceExceptionReport' };
  }
  const esWms = /WMS_Capabilities|WMT_MS_Capabilities/i.test(texto);
  const esWfs = /WFS_Capabilities/i.test(texto);
  if ((servicio === 'WMS' && !esWms) || (servicio === 'WFS' && !esWfs)) {
    return { estado: 'warn', detalle: `Responde pero no entrega capabilities ${servicio} (¿HTML o servicio movido?)` };
  }
  const capas = (texto.match(servicio === 'WMS' ? /<Layer/g : /<(?:wfs:)?FeatureType/g) || []).length;
  if (capas === 0) return { estado: 'warn', detalle: 'Capabilities OK pero sin capas publicadas' };
  return { estado: 'ok', detalle: 'Entrega datos', capas };
}

async function checkJson(url, esperaGeojson) {
  const r = await fetchTimeout(url, { headers: { Accept: 'application/json' } });
  if (!r.ok) return { estado: 'down', detalle: `HTTP ${r.status}` };
  let data;
  try {
    data = JSON.parse(await r.text());
  } catch {
    return { estado: 'warn', detalle: 'Responde pero no entrega JSON válido' };
  }
  if (esperaGeojson) {
    const features = data?.features;
    if (!Array.isArray(features)) {
      return { estado: 'warn', detalle: 'JSON válido pero no es GeoJSON (sin features)' };
    }
    return { estado: 'ok', detalle: 'Entrega datos', registros: features.length };
  }
  return { estado: 'ok', detalle: 'Entrega datos' };
}

async function checkUno(svc) {
  const t0 = Date.now();
  try {
    let res;
    if (svc.tipo === 'arcgis') res = await checkArcgis(svc.url);
    else if (svc.tipo === 'wms') res = await checkOgc(svc.url, 'WMS');
    else if (svc.tipo === 'wfs') res = await checkOgc(svc.url, 'WFS');
    else res = await checkJson(svc.url, svc.tipo === 'geojson');
    res.latenciaMs = Date.now() - t0;
    if (res.estado === 'ok' && res.latenciaMs > WARN_LATENCIA_MS) {
      res.estado = 'warn';
      res.detalle = `Operativo pero lento (${(res.latenciaMs / 1000).toFixed(1)}s)`;
    }
    return res;
  } catch (e) {
    const msg = e.name === 'AbortError' ? `Timeout (${TIMEOUT_MS / 1000}s)` : (e.cause?.code || e.message);
    return { estado: 'down', detalle: `Sin respuesta: ${msg}`, latenciaMs: Date.now() - t0 };
  }
}

async function checkConReintentos(svc) {
  let res;
  for (let i = 0; i <= REINTENTOS; i++) {
    res = await checkUno(svc);
    if (res.estado !== 'down') return res;
  }
  return res;
}

// ─── Main ────────────────────────────────────────────────────────────

const { servicios } = JSON.parse(readFileSync(CATALOGO, 'utf8'));
const previo = existsSync(ESTADO) ? JSON.parse(readFileSync(ESTADO, 'utf8')) : { resultados: {} };

const LETRA = { ok: 'v', warn: 'a', down: 'r' };
const resultados = {};

for (const svc of servicios) {
  const res = await checkConReintentos(svc);
  const anterior = previo.resultados?.[svc.id];
  const historial = ((anterior?.historial || '') + LETRA[res.estado]).slice(-HISTORIAL_MAX);
  resultados[svc.id] = { ...res, historial };
  const icono = { ok: '🟢', warn: '🟡', down: '🔴' }[res.estado];
  console.log(`${icono} ${svc.institucion} · ${svc.nombre} — ${res.detalle} (${res.latenciaMs} ms)`);
}

const salida = { generado: new Date().toISOString(), resultados };
writeFileSync(ESTADO, JSON.stringify(salida, null, 2) + '\n');

const conteo = Object.values(resultados).reduce((acc, r) => ((acc[r.estado] = (acc[r.estado] || 0) + 1), acc), {});
console.log(`\nResumen: ${conteo.ok || 0} operativos · ${conteo.warn || 0} degradados · ${conteo.down || 0} caídos`);

// Para CI: `changed` = cambió algún semáforo, o el archivo previo tiene más
// de 3 días (heartbeat para que "última verificación" no quede añeja).
if (process.env.GITHUB_OUTPUT) {
  const estadosCambiaron = servicios.some(
    (s) => previo.resultados?.[s.id]?.estado !== resultados[s.id].estado
  );
  const antiguedadMs = previo.generado ? Date.now() - new Date(previo.generado).getTime() : Infinity;
  const changed = estadosCambiaron || antiguedadMs > 3 * 24 * 3600 * 1000;
  const fs = await import('node:fs');
  fs.appendFileSync(process.env.GITHUB_OUTPUT, `changed=${changed}\n`);
}
