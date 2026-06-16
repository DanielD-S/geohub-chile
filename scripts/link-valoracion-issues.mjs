#!/usr/bin/env node
// Crea un issue de valoración por cada iniciativa que aún no tenga uno
// vinculado, y agrega `valoracionIssue: N` a su frontmatter.
//
// Idempotente: si una iniciativa ya tiene `valoracionIssue:`, se salta.
// Si se agrega una iniciativa nueva más adelante, basta con re-correr.
//
// Requiere `gh` autenticado.
// Uso: node scripts/link-valoracion-issues.mjs

import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { execFileSync } from 'node:child_process';

const REPO  = 'DanielD-S/geohub-chile';
const DIR   = 'src/content/iniciativas';
const LABEL = 'valoracion';

function gh(args, opts = {}) {
  return execFileSync('gh', args, { encoding: 'utf8', ...opts }).trim();
}

// 1) Asegurar que la label exista (idempotente)
try {
  gh(['label', 'create', LABEL, '-R', REPO,
      '-c', '0e8a16',
      '-d', 'Hilo de valoración de una iniciativa'],
     { stdio: 'pipe' });
  console.log(`✓ Label "${LABEL}" creada.`);
} catch {
  console.log(`= Label "${LABEL}" ya existe.`);
}

// 2) Procesar cada .md
const files = readdirSync(DIR).filter(f => f.endsWith('.md'));
const lineas = [];
let creados = 0, saltados = 0, errores = 0;

for (const f of files) {
  const path = join(DIR, f);
  let src = readFileSync(path, 'utf8');

  if (/^valoracionIssue:\s*\d+/m.test(src)) {
    lineas.push(`=  ${f}: ya tiene valoracionIssue`);
    saltados++; continue;
  }

  const m = src.match(/^nombre:\s*"([^"]+)"/m);
  if (!m) {
    lineas.push(`✗  ${f}: no encontré línea "nombre:"`);
    errores++; continue;
  }
  const nombre = m[1];

  try {
    const title = `[Valoración] ${nombre}`;
    const body = [
      `Hilo de valoración para esta iniciativa.`,
      ``,
      `**Reacciona con 👍** si te resultó útil. El conteo se sincroniza`,
      `cada día y ordena las cards del sitio por valoraciones.`,
      ``,
      `Comenta si quieres sugerir mejoras o reportar problemas.`,
      ``,
      `_Hilo auto-creado por el script \`link-valoracion-issues.mjs\`._`,
    ].join('\n');

    const url = gh(['issue', 'create',
      '-R', REPO,
      '-l', LABEL,
      '-t', title,
      '-b', body]);

    const numMatch = url.match(/\/issues\/(\d+)/);
    if (!numMatch) {
      lineas.push(`✗  ${f}: gh no devolvió URL parseable: ${url}`);
      errores++; continue;
    }
    const issueNumber = +numMatch[1];

    // Insertar `valoracionIssue: N` justo después de la línea `nombre:`
    src = src.replace(
      /^(nombre:\s*"[^"]+"[ \t]*)$/m,
      `$1\nvaloracionIssue: ${issueNumber}`
    );
    writeFileSync(path, src);
    lineas.push(`✓  ${f}: issue #${issueNumber} → ${url}`);
    creados++;
  } catch (e) {
    lineas.push(`✗  ${f}: ${e.message.split('\n')[0]}`);
    errores++;
  }
}

console.log('\n' + lineas.join('\n'));
console.log(`\nResumen: ${creados} creados · ${saltados} saltados · ${errores} errores`);
process.exit(errores > 0 ? 1 : 0);
