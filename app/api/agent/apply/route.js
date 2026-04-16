import path from "node:path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";
export const maxDuration = 60;

const ALLOWED_DIRS = ["app", "lib", "netlify", "public"];
const ALLOWED_ROOT_FILES = ["package.json", "netlify.toml", "next.config.js", "jsconfig.json", "README.md"];

function isSafePath(rel) {
  if (!rel || rel.includes("..") || path.isAbsolute(rel)) return false;
  const norm = path.normalize(rel).replace(/\\/g, "/");
  if (norm.startsWith(".git/") || norm.startsWith("node_modules/") || norm.startsWith(".next/") || norm.startsWith(".netlify/")) return false;
  if (ALLOWED_ROOT_FILES.includes(norm)) return true;
  return ALLOWED_DIRS.some(d => norm === d || norm.startsWith(d + "/"));
}

function b64(str) {
  return Buffer.from(str, "utf8").toString("base64");
}

async function gh(token, urlPath, init = {}) {
  const res = await fetch(`https://api.github.com${urlPath}`, {
    ...init,
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "psicologia-doc-agent",
      ...(init.headers || {})
    }
  });
  return res;
}

export async function POST(req) {
  const token = process.env.GITHUB_TOKEN || process.env.GH_TOKEN;
  const repo = process.env.GITHUB_REPO;
  const branch = process.env.GITHUB_BRANCH || "main";

  if (!token || !repo) {
    return Response.json({
      error: "GitHub não configurado",
      detail: "Defina GITHUB_TOKEN (fine-grained PAT com permissão Contents: read/write) e GITHUB_REPO (ex: 'usuario/repositorio') nas variáveis de ambiente da Netlify. Depois, cada clique em Go fará commit e o Netlify publicará automaticamente."
    }, { status: 503 });
  }

  let payload;
  try { payload = await req.json(); } catch { return Response.json({ error: "JSON inválido" }, { status: 400 }); }
  const { changes, message } = payload || {};
  if (!Array.isArray(changes) || changes.length === 0) return Response.json({ error: "Nenhuma alteração para aplicar" }, { status: 400 });

  const unsafe = changes.find(c => !c || typeof c.path !== "string" || typeof c.newContent !== "string" || !isSafePath(c.path));
  if (unsafe) return Response.json({ error: "Caminho inválido ou bloqueado", path: unsafe?.path }, { status: 400 });

  const commitMsg = (typeof message === "string" && message.trim()) ? message.trim() : "chore(agent): atualização via Go button";

  const results = [];
  for (const c of changes) {
    const shaRes = await gh(token, `/repos/${repo}/contents/${encodeURIComponent(c.path)}?ref=${encodeURIComponent(branch)}`);
    let sha;
    if (shaRes.status === 200) {
      const info = await shaRes.json();
      sha = info?.sha;
    } else if (shaRes.status !== 404) {
      const t = await shaRes.text().catch(() => "");
      return Response.json({ error: "Falha ao consultar arquivo no GitHub", status: shaRes.status, detail: t.slice(0, 400), path: c.path }, { status: 502 });
    }

    const putRes = await gh(token, `/repos/${repo}/contents/${encodeURIComponent(c.path)}`, {
      method: "PUT",
      body: JSON.stringify({
        message: commitMsg,
        content: b64(c.newContent),
        branch,
        ...(sha ? { sha } : {})
      })
    });
    if (!putRes.ok) {
      const t = await putRes.text().catch(() => "");
      return Response.json({ error: "Falha ao fazer commit no GitHub", status: putRes.status, detail: t.slice(0, 400), path: c.path }, { status: 502 });
    }
    const info = await putRes.json();
    results.push({
      path: c.path,
      commit: info?.commit?.sha,
      url: info?.commit?.html_url
    });
  }

  return Response.json({
    success: true,
    repo,
    branch,
    committed: results,
    note: "Alterações enviadas ao GitHub. O Netlify iniciará um novo deploy automaticamente."
  });
}
