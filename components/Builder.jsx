"use client";
import { useState, useEffect } from "react";

export default function Builder() {
  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetch("/api/config")
      .then(r => r.json())
      .then(setConfig);
  }, []);

  if (!config) return <div>Loading...</div>;

  function update(path, value) {
    const updated = { ...config };
    path.split(".").reduce((acc, key, i, arr) => {
      if (i === arr.length - 1) acc[key] = value;
      else acc[key] = acc[key] || {};
      return acc[key];
    }, updated);
    setConfig(updated);
  }

  async function save() {
    await fetch("/api/config", {
      method: "POST",
      body: JSON.stringify(config)
    });
    alert("Config salva");
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Builder Visual</h1>

      <div>
        <label>Cor principal</label>
        <input
          type="color"
          value={config.theme?.primaryColor || "#00ff88"}
          onChange={e => update("theme.primaryColor", e.target.value)}
        />
      </div>

      <div>
        <label>Título</label>
        <input
          value={config.texts?.title || ""}
          onChange={e => update("texts.title", e.target.value)}
        />
      </div>

      <div>
        <label>Mostrar relógio</label>
        <input
          type="checkbox"
          checked={config.widgets?.clock}
          onChange={e => update("widgets.clock", e.target.checked)}
        />
      </div>

      <button onClick={save}>Salvar</button>
    </div>
  );
}
