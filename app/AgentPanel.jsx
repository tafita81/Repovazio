"use client";
import { useEffect, useRef, useState } from "react";

export default function AgentPanel() {
  const [prompt, setPrompt] = useState("");
  const [mode, setMode] = useState("optimize");
  const [busy, setBusy] = useState(false);
  const [output, setOutput] = useState("");
  const [changes, setChanges] = useState([]);
  const [summary, setSummary] = useState("");
  const [filesIncluded, setFilesIncluded] = useState([]);
  const [deployPending, setDeployPending] = useState(false);
  const [applyBusy, setApplyBusy] = useState(false);
  const [ctxInfo, setCtxInfo] = useState(null);
  const outRef = useRef(null);

  useEffect(() => {
    fetch("/api/agent/context").then(r => r.ok ? r.json() : null).then(d => d && setCtxInfo(d)).catch(() => {});
  }, []);

  function append(line) {
    setOutput(prev => (prev ? prev + "\n" : "") + line);
    setTimeout(() => { if (outRef.current) outRef.current.scrollTop = outRef.current.scrollHeight; }, 30);
  }

  async function onGo() {
    const p = prompt.trim();
    if (!p || busy) return;
    setBusy(true);
    setChanges([]);
    setSummary("");
    setFilesIncluded([]);
    setDeployPending(false);
    setOutput("");
    const ts = new Date().toLocaleTimeString("pt-BR");
    append(`[${ts}] ▶ Enviando pedido ao agente (modo: ${mode})...`);
    append(`[${ts}] 📝 Pedido: ${p}`);

    try {
      const res = await fetch("/api/agent", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: p, mode })
      });
      const data = await res.json();
      if (!res.ok) {
        append(`❌ Erro ${res.status}: ${data?.error || "falha"}`);
        if (data?.detail) append(data.detail);
        setBusy(false);
        return;
      }
      const t2 = new Date().toLocaleTimeString("pt-BR");
      append(`[${t2}] ✅ Resposta recebida (modelo: ${data.model || "gpt-5-mini"})`);
      if (data.filesIncluded?.length) {
        setFilesIncluded(data.filesIncluded);
        append(`[${t2}] 📂 Arquivos consultados: ${data.filesIncluded.length}`);
      }
      if (data.summary) {
        setSummary(data.summary);
        append(`\n📋 RESUMO\n${"─".repeat(40)}\n${data.summary}`);
      }
      if (data.answer) {
        append(`\n💬 RESPOSTA\n${"─".repeat(40)}\n${data.answer}`);
      }
      if (Array.isArray(data.changes) && data.changes.length > 0) {
        setChanges(data.changes);
        setDeployPending(!!data.deploy);
        append(`\n🛠 ALTERAÇÕES PROPOSTAS (${data.changes.length} arquivo(s))\n${"─".repeat(40)}`);
        for (const c of data.changes) {
          const preview = (c.newContent || "").slice(0, 600);
          append(`\n▸ ${c.path}`);
          append(preview.split("\n").slice(0, 20).join("\n") + (c.newContent.length > 600 ? "\n... [truncado no preview — será aplicado por completo]" : ""));
        }
      } else {
        append(`\nℹ️ Nenhuma alteração de arquivo proposta.`);
      }
    } catch (e) {
      append(`❌ Exceção: ${e?.message || String(e)}`);
    } finally {
      setBusy(false);
    }
  }

  async function onApply() {
    if (!changes.length || applyBusy) return;
    setApplyBusy(true);
    const ts = new Date().toLocaleTimeString("pt-BR");
    append(`\n[${ts}] 🚀 Enviando alterações ao GitHub...`);
    try {
      const res = await fetch("/api/agent/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          changes,
          message: "chore(agent): " + (summary || prompt).slice(0, 72)
        })
      });
      const data = await res.json();
      if (!res.ok) {
        append(`❌ Falha ao aplicar (${res.status}): ${data?.error || ""}`);
        if (data?.detail) append(data.detail);
        setApplyBusy(false);
        return;
      }
      const t2 = new Date().toLocaleTimeString("pt-BR");
      append(`[${t2}] ✅ Commit enviado em ${data.repo}@${data.branch}`);
      for (const r of data.committed || []) {
        append(`  • ${r.path} → ${r.commit?.slice(0, 7)}${r.url ? " (" + r.url + ")" : ""}`);
      }
      if (data.note) append(`[${t2}] ${data.note}`);
      setDeployPending(false);
      setChanges([]);
    } catch (e) {
      append(`❌ Exceção ao aplicar: ${e?.message || String(e)}`);
    } finally {
      setApplyBusy(false);
    }
  }

  const aiReady = ctxInfo?.aiGateway;
  const ghReady = ctxInfo?.github;

  return (
    <div className="card mb12" style={{ borderColor: "rgba(124,58,237,0.35)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#7c3aed,#a855f7)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>🤖</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 800, fontSize: 14 }}>Agente IA — Otimização & Perguntas</div>
          <div style={{ fontSize: 11, color: "var(--muted)" }}>Consulta o app real, otimiza backend/frontend e publica no GitHub → Netlify</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 8, fontSize: 10 }}>
        <span style={{ padding: "3px 8px", borderRadius: 20, background: aiReady ? "var(--gl)" : "var(--al)", color: aiReady ? "var(--green)" : "var(--amber)", fontWeight: 700 }}>
          {aiReady ? "✅ AI Gateway" : "⚠️ AI Gateway (após 1º deploy)"}
        </span>
        <span style={{ padding: "3px 8px", borderRadius: 20, background: ghReady ? "var(--gl)" : "var(--al)", color: ghReady ? "var(--green)" : "var(--amber)", fontWeight: 700 }}>
          {ghReady ? "✅ GitHub conectado" : "⚠️ GitHub: defina GITHUB_TOKEN + GITHUB_REPO"}
        </span>
        {ctxInfo && <span style={{ padding: "3px 8px", borderRadius: 20, background: "var(--surf2)", color: "var(--muted)", fontWeight: 700 }}>📁 {ctxInfo.fileCount} arquivos</span>}
      </div>

      <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
        <button
          type="button"
          onClick={() => setMode("optimize")}
          style={{
            flex: 1, padding: "8px 10px", borderRadius: 10, fontSize: 12, fontWeight: 700, cursor: "pointer",
            border: "1.5px solid " + (mode === "optimize" ? "var(--purple)" : "var(--border)"),
            background: mode === "optimize" ? "var(--pl)" : "var(--surf2)",
            color: mode === "optimize" ? "var(--purple)" : "var(--muted)"
          }}
        >⚙️ Otimizar & Publicar</button>
        <button
          type="button"
          onClick={() => setMode("ask")}
          style={{
            flex: 1, padding: "8px 10px", borderRadius: 10, fontSize: 12, fontWeight: 700, cursor: "pointer",
            border: "1.5px solid " + (mode === "ask" ? "var(--blue)" : "var(--border)"),
            background: mode === "ask" ? "var(--bl)" : "var(--surf2)",
            color: mode === "ask" ? "var(--blue)" : "var(--muted)"
          }}
        >❓ Perguntar sobre o app</button>
      </div>

      <textarea
        value={prompt}
        onChange={e => setPrompt(e.target.value)}
        placeholder={mode === "optimize"
          ? "Ex.: Otimize o carregamento da página principal, reduza tamanho do bundle e melhore contraste do tema claro."
          : "Ex.: Quais métricas o dashboard mostra e de onde vêm? Quais APIs estão em produção?"}
        rows={4}
        style={{
          width: "100%", padding: "10px 12px", borderRadius: 10, border: "1.5px solid var(--border)",
          background: "var(--surf2)", color: "var(--text)", fontSize: 13, fontFamily: "var(--font)",
          resize: "vertical", outline: "none", marginBottom: 8, lineHeight: 1.5
        }}
      />

      <div style={{ display: "flex", gap: 6 }}>
        <button
          type="button"
          onClick={onGo}
          disabled={busy || !prompt.trim()}
          style={{
            flex: 1, padding: "12px", borderRadius: 12, border: "none",
            background: busy || !prompt.trim() ? "var(--surf2)" : "linear-gradient(135deg,var(--purple),#a855f7)",
            color: busy || !prompt.trim() ? "var(--muted)" : "white",
            fontWeight: 800, fontSize: 15, cursor: busy || !prompt.trim() ? "not-allowed" : "pointer",
            letterSpacing: "0.02em"
          }}
        >
          {busy ? "⏳ Processando..." : "🚀 Go"}
        </button>
        {changes.length > 0 && (
          <button
            type="button"
            onClick={onApply}
            disabled={applyBusy || !ghReady}
            title={ghReady ? "Aplicar e publicar via GitHub" : "Configure GITHUB_TOKEN + GITHUB_REPO nas env vars da Netlify"}
            style={{
              padding: "12px 14px", borderRadius: 12, border: "none",
              background: applyBusy || !ghReady ? "var(--surf2)" : "linear-gradient(135deg,#059669,#10b981)",
              color: applyBusy || !ghReady ? "var(--muted)" : "white",
              fontWeight: 800, fontSize: 13, cursor: applyBusy || !ghReady ? "not-allowed" : "pointer"
            }}
          >
            {applyBusy ? "⏳ Publicando..." : deployPending ? "📦 Publicar → Produção" : "📦 Aplicar"}
          </button>
        )}
      </div>

      <div style={{ marginTop: 10 }}>
        <div style={{ fontSize: 10, color: "var(--muted)", fontWeight: 700, textTransform: "uppercase", marginBottom: 6 }}>📄 Saída do Agente</div>
        <textarea
          ref={outRef}
          readOnly
          value={output || "Aguardando. Digite seu pedido acima e clique em Go."}
          style={{
            width: "100%", minHeight: 240, maxHeight: 420, padding: "10px 12px",
            borderRadius: 10, border: "1.5px solid var(--border)",
            background: "#0a0a0f", color: "#d1d5db",
            fontFamily: "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
            fontSize: 12, lineHeight: 1.55, whiteSpace: "pre-wrap", wordBreak: "break-word",
            resize: "vertical", outline: "none"
          }}
        />
        {filesIncluded.length > 0 && (
          <div style={{ marginTop: 6, fontSize: 10, color: "var(--muted)" }}>
            Base real consultada: {filesIncluded.join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}
