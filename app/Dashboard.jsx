"use client";
import { useState, useEffect, useCallback } from "react";

// ─── Utilitários ────────────────────────────────────────────────────
function formatTime(date) {
  return date.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatDate(date) {
  return date.toLocaleDateString("pt-BR", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });
}

// ─── Componente de compartilhamento WhatsApp ─────────────────────────
function WhatsAppShare({ text }) {
  const share = () => {
    const msg = encodeURIComponent(text);
    window.open(`https://wa.me/?text=${msg}`, "_blank");
  };
  return (
    <button
      onClick={share}
      style={{
        background: "#25D366",
        color: "#fff",
        border: "none",
        borderRadius: 8,
        padding: "8px 16px",
        cursor: "pointer",
        fontWeight: 700,
        fontSize: 13,
        display: "flex",
        alignItems: "center",
        gap: 6,
      }}
    >
      <span>📲</span> Compartilhar no WhatsApp
    </button>
  );
}

// ─── Componente principal do Dashboard ──────────────────────────────
export default function Dashboard() {
  const [time, setTime] = useState(new Date());
  const [registros, setRegistros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);

  // Relógio em tempo real
  useEffect(() => {
    const tick = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(tick);
  }, []);

  // Busca dados do Supabase via API route
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch("/api/analytics", { cache: "no-store" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setRegistros(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Auto-refresh a cada 30s
    const interval = setInterval(fetchData, 30_000);
    return () => clearInterval(interval);
  }, [fetchData, retryCount]);

  const timeStr = formatTime(time);
  const dateStr = formatDate(time);
  const total = registros.length;
  const shareText =
    `🧠 *psicologia.doc — Cérebro Autônomo* está online!\n\n` +
    `✅ ${total} registros processados\n` +
    `⏰ ${timeStr}\n\n` +
    `Acesse: https://psicologia.doc`;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0a0a0f 0%, #12121a 50%, #0a0f1a 100%)",
        color: "#e8e8f0",
        fontFamily: "'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif",
        padding: "0",
        margin: "0",
      }}
    >
      {/* Header */}
      <header
        style={{
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          padding: "16px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backdropFilter: "blur(12px)",
          position: "sticky",
          top: 0,
          zIndex: 10,
          background: "rgba(10,10,15,0.8)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: "linear-gradient(135deg, #7c3aed, #3b82f6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 18,
            }}
          >
            🧠
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: 15, letterSpacing: "-0.02em" }}>
              psicologia.doc
            </div>
            <div style={{ fontSize: 11, color: "#6b7280", marginTop: 1 }}>
              Cérebro Autônomo 24/7
            </div>
          </div>
        </div>

        {/* Status ao vivo */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#22c55e",
              display: "inline-block",
              boxShadow: "0 0 8px #22c55e",
              animation: "pulse 2s infinite",
            }}
          />
          <span style={{ fontSize: 12, color: "#22c55e", fontWeight: 600 }}>
            ONLINE
          </span>
        </div>
      </header>

      {/* Main */}
      <main style={{ padding: "32px 32px 48px", maxWidth: 900, margin: "0 auto" }}>
        {/* Relógio */}
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <div
            style={{
              fontFamily: "monospace",
              fontSize: "clamp(40px, 8vw, 72px)",
              fontWeight: 800,
              letterSpacing: "0.05em",
              lineHeight: 1,
              background: "linear-gradient(135deg, #FFD600, #FF6B35)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              backgroundClip: "text",
            }}
          >
            {timeStr}
          </div>
          <div style={{ fontSize: 14, color: "#6b7280", marginTop: 8, textTransform: "capitalize" }}>
            {dateStr}
          </div>
        </div>

        {/* Métricas */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 16,
            marginBottom: 32,
          }}
        >
          {[
            {
              label: "Total de Registros",
              value: loading ? "..." : error ? "—" : total,
              icon: "📊",
              color: "#7c3aed",
            },
            {
              label: "Status do Sistema",
              value: loading ? "Carregando" : error ? "Offline" : "Online",
              icon: loading ? "⏳" : error ? "❌" : "✅",
              color: error ? "#ef4444" : "#22c55e",
            },
            {
              label: "Última Atualização",
              value: formatTime(new Date()),
              icon: "🔄",
              color: "#3b82f6",
            },
          ].map((card) => (
            <div
              key={card.label}
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
                borderRadius: 16,
                padding: "20px 24px",
                transition: "transform 0.2s, border-color 0.2s",
              }}
            >
              <div style={{ fontSize: 24, marginBottom: 8 }}>{card.icon}</div>
              <div
                style={{
                  fontSize: 28,
                  fontWeight: 800,
                  color: card.color,
                  letterSpacing: "-0.03em",
                }}
              >
                {card.value}
              </div>
              <div style={{ fontSize: 12, color: "#6b7280", marginTop: 4 }}>
                {card.label}
              </div>
            </div>
          ))}
        </div>

        {/* Tabela de registros */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 16,
            overflow: "hidden",
            marginBottom: 24,
          }}
        >
          <div
            style={{
              padding: "16px 24px",
              borderBottom: "1px solid rgba(255,255,255,0.07)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span style={{ fontWeight: 700, fontSize: 14 }}>📋 Registros Recentes</span>
            <button
              onClick={fetchData}
              disabled={loading}
              style={{
                background: "rgba(124,58,237,0.2)",
                color: "#a78bfa",
                border: "1px solid rgba(124,58,237,0.3)",
                borderRadius: 8,
                padding: "6px 14px",
                cursor: "pointer",
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {loading ? "⏳ Atualizando..." : "↻ Atualizar"}
            </button>
          </div>

          <div style={{ padding: "16px 24px" }}>
            {loading && (
              <div style={{ color: "#6b7280", fontSize: 14, textAlign: "center", padding: 24 }}>
                ⏳ Carregando dados...
              </div>
            )}

            {!loading && error && (
              <div
                style={{
                  background: "rgba(239,68,68,0.1)",
                  border: "1px solid rgba(239,68,68,0.2)",
                  borderRadius: 10,
                  padding: 16,
                }}
              >
                <div style={{ color: "#f87171", fontWeight: 600, marginBottom: 8 }}>
                  ⚠️ Erro ao carregar dados
                </div>
                <div style={{ color: "#6b7280", fontSize: 12, marginBottom: 12 }}>
                  {error}
                </div>
                {error.includes("not configured") && (
                  <div style={{ color: "#9ca3af", fontSize: 12 }}>
                    Configure as variáveis{" "}
                    <code style={{ color: "#a78bfa" }}>NEXT_PUBLIC_SUPABASE_URL</code> e{" "}
                    <code style={{ color: "#a78bfa" }}>SUPABASE_SERVICE_KEY</code> no Netlify.
                  </div>
                )}
                <button
                  onClick={() => setRetryCount((c) => c + 1)}
                  style={{
                    marginTop: 12,
                    background: "rgba(239,68,68,0.2)",
                    color: "#f87171",
                    border: "none",
                    borderRadius: 6,
                    padding: "6px 12px",
                    cursor: "pointer",
                    fontSize: 12,
                  }}
                >
                  Tentar novamente
                </button>
              </div>
            )}

            {!loading && !error && registros.length === 0 && (
              <div style={{ color: "#6b7280", fontSize: 14, textAlign: "center", padding: 24 }}>
                Nenhum registro encontrado ainda.
              </div>
            )}

            {!loading && !error && registros.length > 0 && (
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr>
                      {Object.keys(registros[0]).map((k) => (
                        <th
                          key={k}
                          style={{
                            textAlign: "left",
                            padding: "8px 12px",
                            color: "#6b7280",
                            fontWeight: 600,
                            fontSize: 11,
                            textTransform: "uppercase",
                            letterSpacing: "0.05em",
                            borderBottom: "1px solid rgba(255,255,255,0.06)",
                          }}
                        >
                          {k}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {registros.slice(0, 20).map((row, i) => (
                      <tr key={i}>
                        {Object.values(row).map((val, j) => (
                          <td
                            key={j}
                            style={{
                              padding: "10px 12px",
                              borderBottom: "1px solid rgba(255,255,255,0.04)",
                              color: "#d1d5db",
                              maxWidth: 200,
                              overflow: "hidden",
                              textOverflow: "ellipsis",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {String(val ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
                {registros.length > 20 && (
                  <p style={{ color: "#6b7280", fontSize: 12, marginTop: 8, textAlign: "center" }}>
                    Mostrando 20 de {registros.length} registros
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Social Share */}
        <div
          style={{
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 16,
            padding: "20px 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <div>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>
              📣 Compartilhe o sistema
            </div>
            <div style={{ fontSize: 12, color: "#6b7280" }}>
              Ajude mais pessoas a conhecerem a psicologia.doc
            </div>
          </div>
          <WhatsAppShare text={shareText} />
        </div>
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}
