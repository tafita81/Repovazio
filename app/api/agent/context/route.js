import fs from "node:fs/promises";
import path from "node:path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const ROOT = process.cwd();
const ALLOWED_DIRS = ["app", "lib", "netlify", "public"];
const SKIP_DIRS = new Set(["node_modules", ".next", ".netlify", ".git", "dist", "build"]);

async function walk(dir, out = []) {
  let entries = [];
  try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of entries) {
    if (SKIP_DIRS.has(e.name) || e.name.startsWith(".")) continue;
    const full = path.join(dir, e.name);
    if (e.isDirectory()) await walk(full, out);
    else out.push(full);
  }
  return out;
}

export async function GET() {
  const files = [];
  for (const d of ALLOWED_DIRS) {
    try { await fs.access(path.join(ROOT, d)); await walk(path.join(ROOT, d), files); } catch {}
  }
  const rels = files.map(f => path.relative(ROOT, f)).sort();
  let pkg = null;
  try { pkg = JSON.parse(await fs.readFile(path.join(ROOT, "package.json"), "utf8")); } catch {}
  return Response.json({
    fileCount: rels.length,
    files: rels,
    name: pkg?.name || null,
    dependencies: pkg?.dependencies || {},
    aiGateway: !!(process.env.OPENAI_API_KEY && process.env.OPENAI_BASE_URL),
    github: !!(process.env.GITHUB_TOKEN || process.env.GH_TOKEN) && !!process.env.GITHUB_REPO
  });
}
