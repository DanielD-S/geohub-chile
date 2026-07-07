import { defineCollection, z } from 'astro:content';

// URL absoluta (https://...) o ruta relativa (./algo.html, /algo, algo.html)
const urlOrPath = z
  .string()
  .refine(
    (v) => /^(https?:)?\/\//.test(v) || v.startsWith('/') || v.startsWith('./') || /^[\w.-]+\.[a-z]+/i.test(v),
    { message: 'Debe ser URL absoluta o ruta relativa' }
  );

const accionSchema = z.object({
  tipo: z.enum(['github', 'ver', 'desc', 'externo']),
  texto: z.string(),
  url: urlOrPath.optional(),
  toggleId: z.string().optional(), // para botones que abren panel local (ver)
});

const archivoSchema = z.object({
  nombre: z.string(),
  size: z.string(),
  // URL absoluta o ruta relativa al sitio (p.ej. herramientas con deep-link)
  url: urlOrPath,
});

const grupoArchivosSchema = z.object({
  titulo: z.string(),
  items: z.array(archivoSchema),
});

const iniciativas = defineCollection({
  type: 'content',
  schema: z.object({
    nombre: z.string(),
    // 'comunidad' = creado por la comunidad (datasets pre-procesados, visores, scripts).
    // 'oficial'   = portal oficial del Estado (IDE Chile, BCN, etc.) — lo referenciamos pero no lo administramos.
    tipo: z.enum(['comunidad', 'oficial']).default('comunidad'),
    categoria: z.enum([
      'mineria',
      'ambiental',
      'riesgo',
      'hidrico',
      'social',
      'admin',
      'energia',
    ]),
    categoriaExtra: z
      .object({ label: z.string(), color: z.string() })
      .optional(),
    // Ícono legacy (emoji). Ya no se renderiza — IniciativaCard usa SVGs
    // outline por slug/categoría. Se acepta opcionalmente para no romper
    // archivos antiguos, pero no agregarlo en iniciativas nuevas.
    icono: z.string().optional(),
    iconoBg: z.string().optional(), // p.ej. "rgba(245,197,24,0.12)"
    estado: z.enum(['activo', 'beta', 'wip']),
    estadoTexto: z.string(),
    descripcion: z.string(),
    capas: z.array(z.string()).default([]),
    capasExtra: z.string().optional(),
    tags: z.string(),
    stats: z
      .array(
        z.object({
          label: z.string(),
          valor: z.string().optional(),
        })
      )
      .default([]),
    acciones: z.array(accionSchema).default([]),
    archivos: z
      .object({
        release: z.string(),
        grupos: z.array(grupoArchivosSchema),
      })
      .optional(),
    orden: z.number().default(100),
    // Puntaje de valoración. Hoy se asigna manualmente; en una fase futura
    // se sobreescribe en build con el conteo real de 👍 reactions desde
    // GitHub API sobre el issue ligado a `valoracionIssue`.
    score: z.number().default(0),
    // Número del issue de valoración en el repo del hub (ej. 42). Si está
    // presente, el botón "👍 Valorar" lleva directo a ese issue; si no,
    // abre un issue nuevo pre-rellenado con el slug.
    valoracionIssue: z.number().int().positive().optional(),
  }),
});

const fuentes = defineCollection({
  type: 'data',
  schema: z.object({
    logo: z.string(),
    nombre: z.string(),
    descripcion: z.string(),
    url: z.string().url(),
    orden: z.number().default(100),
  }),
});

export const collections = { iniciativas, fuentes };
