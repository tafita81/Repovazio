import fs from "node:fs/promises";
import path from "node:path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const maxDuration = 60;

const ROOT = process.cwd();

const ALLOWED_DIRS = ["app", "lib", "netlify", "public"];
const ALLOWED_ROOT_FILES = ["package.json", "netlify.toml", "next.config.js", "jsconfig.json", "README.md"];
const SKIP_DIRS = new Set(["node_modules", ".next", ".netlify", ".git", "dist", "build"]);
const SKIP_EXT = new Set([".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".mp4", ".mov", ".zip"]);

async function walk(dir, out = []) {
  let entries = [];
  try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    if (SKIP_DIRS.has(e.name) || e.name.startsWith(".")) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) await walk(full, out);
    else if (!SKIP_EXT.has(path.extname(e.name).toLowerCase())) out.push(full);
  }
  return out;
}

async function listProjectFiles() {
  const files = [];
  for (const d of ALLOWED_DIRS) {
    const full = path.join(ROOT, d);
    try { await fs.access(full); await walk(full, files); } catch {}
  }
  for (const f of ALLOWED_ROOT_FILES) {
    const full = path.join(ROOT, f);
    try { await fs.access(full); files.push(full); } catch {}
  }
  return files.map(f => path.relative(ROOT, f));
}

function isSafePath(rel) {
  if (!rel || rel.includes("..") || path.isAbsolute(rel)) return false;
  const norm = path.normalize(rel).replace(/\\/g, "/");
  if (norm.startsWith(".git/") || norm.startsWith("node_modules/") || norm.startsWith(".next/") || norm.startsWith(".netlify/")) return false;
  if (ALLOWED_ROOT_FILES.includes(norm)) return true;
  return ALLOWED_DIRS.some(d => norm === d || norm.startsWith(d + "/"));
}

async function readFileSafe(rel, maxBytes = 80_000) {
  if (!isSafePath(rel)) return null;
  try {
    const full = path.join(ROOT, rel);
    const buf = await fs.readFile(full);
    if (buf.byteLength > maxBytes) return buf.subarray(0, maxBytes).toString("utf8") + "\n\n... [TRUNCATED " + (buf.byteLength - maxBytes) + " bytes]";
    return buf.toString("utf8");
  } catch { return null; }
}

async function buildContext(prompt) {
  const files = await listProjectFiles();
  const always = ["package.json", "netlify.toml", "next.config.js", "app/page.js", "app/layout.js"];
  const chosen = new Set(always.filter(f => files.includes(f)));

  const promptLc = (prompt || "").toLowerCase();
  const scored = files
    .filter(f => !chosen.has(f))
    .map(f => {
      const base = f.toLowerCase();
      let score = 0;
      for (const w of promptLc.split(/\W+/).filter(w => w.length > 3)) {
        if (base.includes(w)) score += 2;
      }
      if (base.endsWith(".js") || base.endsWith(".jsx") || base.endsWith(".ts") || base.endsWith(".tsx")) score += 1;
      if (base.startsWith("app/api/")) score += 1;
      return { f, score };
    })
    .sort((a, b) => b.score - a.score);

  let used = 0;
  const BUDGET = 180_000;
  const contents = {};
  for (const f of [...chosen, ...scored.map(s => s.f)]) {
    if (used > BUDGET) break;
    const text = await readFileSafe(f);
    if (text == null) continue;
    contents[f] = text;
    used += text.length;
  }
  return { files, contents };
}

function extractJsonBlock(text) {
  if (!text) return null;
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidate = fence ? fence[1] : text;
  const start = candidate.indexOf("{");
  const end = candidate.lastIndexOf("}");
  if (start === -1 || end === -1 || end < start) return null;
  try { return JSON.parse(candidate.slice(start, end + 1)); } catch { return null; }
}

async function callOpenAI({ systemPrompt, userPrompt, model, jsonMode }) {
  const base = process.env.OPENAI_BASE_URL;
  const key = process.env.OPENAI_API_KEY;
  if (!base || !key) {
    throw new Error("OpenAI não está configurado. Netlify AI Gateway requer pelo menos um deploy de produção. Faça deploy primeiro, ou defina OPENAI_API_KEY nas variáveis de ambiente.");
  }
  const body = {
    model: model || "gpt-5-mini",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt }
    ]
  };
  if (jsonMode) body.response_format = { type: "json_object" };

  const res = await fetch(`${base}/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${key}` },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`OpenAI HTTP ${res.status}: ${t.slice(0, 500)}`);
  }
  const data = await res.json();
  return data.choices?.[0]?.message?.content || "";
}

export async function POST(req) {
  let payload;
  try { payload = await req.json(); } catch { return Response.json({ error: "JSON inválido" }, { status: 400 }); }
  const { prompt, mode } = payload || {};
  if (!prompt || typeof prompt !== "string") return Response.json({ error: "prompt obrigatório" }, { status: 400 });

  const ctx = await buildContext(prompt);
  const fileListText = ctx.files.join("\n");
  const sourcesText = Object.entries(ctx.contents)
    .map(([p, c]) => `===== FILE: ${p} =====\n${c}`)
    .join("\n\n");

  const isOptimize = mode === "optimize";
  const sys = isOptimize
    ? `Você é um agente de engenharia de software que modifica um app Next.js (App Router) hospedado na Netlify. Responda SEMPRE em português do Brasil. Analise o pedido do usuário e o código-fonte real fornecido e proponha alterações de arquivos. REGRAS:
- Só edite arquivos dentro de: app/, lib/, netlify/, public/ e arquivos-raiz permitidos (package.json, netlify.toml, next.config.js).
- Não inclua segredos, tokens ou chaves em nenhum arquivo.
- Preserve o estilo e estrutura do código existente.
- Para cada arquivo alterado ou criado, forneça o CONTEÚDO COMPLETO novo (não diff).
- Retorne APENAS JSON válido com este formato:
{
  "summary": "o que foi feito e por quê, em português",
  "answer": "resposta em texto claro, em português, com quebras de linha \\n para o usuário ler",
  "changes": [ { "path": "app/...", "newContent": "arquivo completo aqui" } ],
  "deploy": true
}
Se o pedido for apenas uma pergunta e nenhuma alteração for necessária, retorne changes: [] e deploy: false.`
    : `Você é um agente que consulta o aplicativo Next.js real (App Router) hospedado na Netlify, respondendo perguntas sobre ele. Responda em português do Brasil. Use APENAS o código-fonte e arquivos reais fornecidos abaixo — nada de simulação. Retorne APENAS JSON válido:
{
  "summary": "resumo curto",
  "answer": "resposta completa em português, com quebras de linha \\n, citando trechos e caminhos de arquivo reais quando relevante",
  "changes": [],
  "deploy": false
}`;

  const usr = `PEDIDO DO USUÁRIO:\n${prompt}\n\n===== LISTA DE ARQUIVOS DO PROJETO =====\n${fileListText}\n\n===== CÓDIGO-FONTE RELEVANTE =====\n${sourcesText}`;

  let raw;
  try {
    raw = await callOpenAI({ systemPrompt: sys, userPrompt: usr, jsonMode: true });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 502 });
  }

  const parsed = extractJsonBlock(raw) || { summary: "", answer: raw, changes: [], deploy: false };
  const safeChanges = Array.isArray(parsed.changes)
    ? parsed.changes.filter(c => c && typeof c.path === "string" && typeof c.newContent === "string" && isSafePath(c.path))
    : [];

  return Response.json({
    summary: parsed.summary || "",
    answer: parsed.answer || "",
    changes: safeChanges,
    deploy: !!parsed.deploy && safeChanges.length > 0,
    filesIncluded: Object.keys(ctx.contents),
    model: "gpt-5-mini"
  });
}
