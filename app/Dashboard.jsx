"use client";

import { useEffect, useMemo, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      const res = await fetch("/api/learning", { cache: "no-store" });
      const json = await res.json();
      setData(Array.isArray(json.learned) ? json.learned : []);
      setTopics(Array.isArray(json.nextTopics) ? json.nextTopics : []);
    } catch {
      setError("Falha ao carregar dados");
      setData([]);
      setTopics([]);
    }
  }

  async function runPipeline() {
    try {
      setLoading(true);
      await fetch("/api/pipeline", { method: "POST" });
      await load();
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const kpis = useMemo(() => {
    const totalViews = data.reduce((a, i) => a + (i?.views || 0), 0);
    const totalClicks = data.reduce((a, i) => a + (i?.clicks || 0), 0);
    const avgCtr = data.length
      ? (data.reduce((a, i) => a + (i?.ctr || 0), 0) / data.length) * 100
      : 0;
    return { totalViews, totalClicks, avgCtr };
  }, [data]);

  return (
    <div style={{ padding: 20, color: "white", background: "#0b0f1a", minHeight: "100vh" }}>
      <h1>🧠 Autopilot Dashboard</h1>

      {/* KPIs adicionados sem alterar a base */}
      <div style={{ display: "flex", gap: 16, margin: "10px 0 20px 0", flexWrap: "wrap" }}>
        <div style={{ background: "#111827", padding: 12, borderRadius: 8 }}>
          <div style={{ opacity: 0.7 }}>Views</div>
          <strong>{kpis.totalViews}</strong>
        </div>
        <div style={{ background: "#111827", padding: 12, borderRadius: 8 }}>
          <div style={{ opacity: 0.7 }}>Clicks</div>
          <strong>{kpis.totalClicks}</strong>
        </div>
        <div style={{ background: "#111827", padding: 12, borderRadius: 8 }}>
          <div style={{ opacity: 0.7 }}>CTR médio</div>
          <strong>{kpis.avgCtr.toFixed(1)}%</strong>
        </div>
      </div>

      {/* Ações adicionadas */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={runPipeline} disabled={loading} style={{ marginRight: 10 }}>
          {loading ? "Executando..." : "🚀 Rodar Pipeline"}
        </button>
        <button onClick={load}>🔄 Atualizar</button>
      </div>

      {error && <p style={{ color: "#f87171" }}>{error}</p>}

      <h2>📊 Performance</h2>
      {data.length === 0 && <p>Sem dados ainda...</p>}

      <table style={{ width: "100%", marginBottom: 30 }}>
        <thead>
          <tr>
            <th>Views</th>
            <th>Clicks</th>
            <th>CTR</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item, i) => (
            <tr key={i}>
              <td>{item?.views ?? 0}</td>
              <td>{item?.clicks ?? 0}</td>
              <td>{(((item?.ctr ?? 0) * 100)).toFixed(1)}%</td>
              <td>{item?.action ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>🚀 Próximos Conteúdos</h2>
      <ul>
        {topics.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
    </div>
  );
}
