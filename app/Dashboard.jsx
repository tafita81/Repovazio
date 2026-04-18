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
  const avgCtr = data.length
    ? (data.reduce((acc, i) => acc + (i.ctr || 0), 0) / data.length) * 100
    : 0;

  return (
    <div style={{ padding: 20, color: "white", background: "#0b0f1a", minHeight: "100vh" }}>
      <h1>🧠 Autopilot Dashboard</h1>

      {/* KPIs */}
      <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
        <div>👁 Views: {totalViews}</div>
        <div>📈 CTR médio: {avgCtr.toFixed(1)}%</div>
        <div>📦 Conteúdos: {data.length}</div>
      </div>

      {/* Ações */}
      <div style={{ marginBottom: 20 }}>
        <button onClick={runPipeline} disabled={loading}>
          {loading ? "Executando..." : "🚀 Rodar Pipeline"}
        </button>
        <button onClick={load} style={{ marginLeft: 10 }}>
          🔄 Atualizar
        </button>
      </div>

      {/* Tabela */}
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
              <td>{item.views}</td>
              <td>{item.clicks}</td>
              <td>{((item.ctr || 0) * 100).toFixed(1)}%</td>
              <td>{item.action}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Próximos conteúdos */}
      <h2>🚀 Próximos Conteúdos</h2>
      <ul>
        {topics.map((t, i) => (
          <li key={i}>{t}</li>
        ))}
      </ul>
    </div>
  );
}
