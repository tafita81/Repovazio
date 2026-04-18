"use client";
import { useEffect, useState } from "react";

export default function Admin() {
  const [json, setJson] = useState("");

  useEffect(() => {
    fetch("/api/config")
      .then(r => r.json())
      .then(data => setJson(JSON.stringify(data, null, 2)));
  }, []);

  async function save() {
    await fetch("/api/config", {
      method: "POST",
      body: json
    });
    alert("Salvo");
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Configuração Dashboard</h1>

      <textarea
        value={json}
        onChange={e => setJson(e.target.value)}
        style={{ width: "100%", height: 300 }}
      />

      <button onClick={save}>Salvar</button>
    </div>
  );
}
