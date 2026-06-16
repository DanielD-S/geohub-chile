#!/usr/bin/env node
// Lee cada .md en src/content/iniciativas/, busca `valoracionIssue: N`
// y actualiza `score: N` con el conteo de 👍 reactions del issue.
//
// Uso local:    node scripts/sync-scores.mjs
// Uso en CI:    se ejecuta desde .github/workflows/sync-scores.yml
//
// Requiere GITHUB_TOKEN (en CI viene automático). Sin token funciona
// pero con rate limit de 60 req/hora.

import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const REPO  = process.env.GITHUB_REPOSITORY || 'DanielD-S/geohub-chile';
const TOKEN = process.env.GITHUB_TOKEN || '';
const DIR   = 'src/content/iniciativas';

const headers = {
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
};

async function thumbsUpCount(issueNumber) {
  const url = `https://api.github.com/repos/${REPO}/issues/${issueNumber}`;
  const r = await fetch(url, { headers });
  if (r.status === 404) return null; // issue no existe (¿borrado?)
  if (!r.ok) throw new Error(`${r.status} ${r.statusText} en ${url}`);
  const data = await r.json();
  return data.reactions?.['+1'] ?? 0;
}

function patchFrontmatter(src, count) {
  const hasScore = /^score:\s*-?\d+\s*$/m.test(src);
  if (hasScore) {
    return src.replace(/^score:\s*-?\d+\s*$/m, `score: ${count}`);
  }
  // Insertar `score: N` justo después de `valoracionIssue: N`
  return src.replace(
    /^(valoracionIssue:\s*\d+[ \t]*)$/m,
    `$1\nscore: ${count}`
  );
}

const files = readdirSync(DIR).filter(f => f.endsWith('.md'));
let updated = 0, skipped = 0, errors = 0;

for (const f of files) {
  const path = join(DIR, f);
  const src  = readFileSync(path, 'utf8');
  const m    = src.match(/^valoracionIssue:\s*(\d+)\s*$/m);
  if (!m) { skipped++; continue; }
  const issue = +m[1];
  try {
    const count = await thumbsUpCount(issue);
    if (count === null) {
      console.warn(`⚠  ${f}: issue #${issue} no encontrado (404)`);
      errors++; continue;
    }
    const newSrc = patchFrontmatter(src, count);
    if (newSrc !== src) {
      writeFileSync(path, newSrc);
      updated++;
      console.log(`✓ ${f}: issue #${issue} → score: ${count}`);
    } else {
      console.log(`= ${f}: issue #${issue} → score: ${count} (sin cambios)`);
    }
  } catch (e) {
    console.error(`✗ ${f}: ${e.message}`);
    errors++;
  }
}

console.log(`\nResumen: ${updated} actualizadas · ${skipped} sin valoracionIssue · ${errors} errores`);

// Si llamamos desde Actions, exportamos `changed` para el siguiente step.
if (process.env.GITHUB_OUTPUT) {
  const fs = await import('node:fs');
  fs.appendFileSync(process.env.GITHUB_OUTPUT, `changed=${updated > 0}\n`);
}

process.exit(errors > 0 ? 1 : 0);
