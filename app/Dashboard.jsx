"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState([]);
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    fetch("/api/learning")
      .then(r => r.json())
      .then(res => {
        setData(res.learned || []);
        setTopics(res.nextTopics || []);
      })
      .catch(() => {
        setData([]);
        setTopics([]);
      });
  }, []);

  return (
    <div style={{ padding: 20, color: "white", background: "#0b0f1a", minHeight: "100vh" }}>
      <h1>🧠 Autopilot Dashboard</h1>

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
              <td>{(item.ctr * 100).toFixed(1)}%</td>
              <td>{item.action}</td>
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
