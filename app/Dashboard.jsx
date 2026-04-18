"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);

  async function load() {
    const res = await fetch("/api/learning");
    const json = await res.json();
    setData(json.learned || []);
    setTopics(json.nextTopics || []);
  }

  async function runPipeline() {
    setLoading(true);
    await fetch("/api/pipeline", { method: "POST" });
    await load();
    setLoading(false);
  }

  useEffect(() => {
    load();
  }, []);

  const totalViews = data.reduce((acc, i) => acc + (i.views || 0), 0);
  const totalClicks = data.reduce((acc, i) => acc + (i.clicks || 0), 0);
  const avgCtr = data.length
    ? (data.reduce((acc, i) => acc + (i.ctr || 0), 0) / data.length) * 100
    : 0;

  return (
    <div style={{ padding: 30, color: "white", background: "#0b0f1a", minHeight: "100vh", fontFamily: "Arial" }}>
      <h1 style={{ marginBottom: 20 }}>🧠 Autopilot Dashboard</h1>

      {/* CARDS */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20, marginBottom: 30 }}>
        <div style={{ background: "#111827", padding: 20, borderRadius: 10 }}>
          <div>👁 Views</div>
          <strong style={{ fontSize: 22 }}>{totalViews}</strong>
        </div>

        <div style={{ background: "#111827", padding: 20, borderRadius: 10 }}>
          <div>🖱 Clicks</div>
          <strong style={{ fontSize: 22 }}>{totalClicks}</strong>
        </div>

        <div style={{ background: "#111827", padding: 20, borderRadius: 10 }}>
          <div>📈 CTR Médio</div>
          <strong style={{ fontSize: 22 }}>{avgCtr.toFixed(1)}%</strong>
        </div>
      </div>

      {/* ACTIONS */}
      <div style={{ marginBottom: 30 }}>
        <button onClick={runPipeline} disabled={loading} style={{ marginRight: 10 }}>
          {loading ? "Executando..." : "🚀 Rodar Pipeline"}
        </button>
        <button onClick={load}>🔄 Atualizar</button>
      </div>

      {/* TABLE */}
      <h2>📊 Performance</h2>

      <table style={{ width: "100%", marginTop: 10, borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ textAlign: "left", borderBottom: "1px solid #333" }}>
            <th>Views</th>
            <th>Clicks</th>
            <th>CTR</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {data.length === 0 && (
            <tr>
              <td colSpan={4} style={{ padding: 10, opacity: 0.6 }}>
                Sem dados ainda...
              </td>
            </tr>
          )}

          {data.map((item, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #222" }}>
              <td>{item.views || 0}</td>
              <td>{item.clicks || 0}</td>
              <td>{((item.ctr || 0) * 100).toFixed(1)}%</td>
              <td>{item.action || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* TOPICS */}
      <h2 style={{ marginTop: 30 }}>🚀 Próximos Conteúdos</h2>

      <div style={{ marginTop: 10 }}>
        {topics.length === 0 && <p style={{ opacity: 0.6 }}>Nenhuma sugestão ainda...</p>}

        <ul>
          {topics.map((t, i) => (
            <li key={i}>{t}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
