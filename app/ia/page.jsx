"use client";
import { useState, useEffect, useRef } from "react";

const PEND = [
  {n:1,c:"Voz",t:"ElevenLabs API Key",d:"Voz cinematografica PT-BR",l:"https://elevenlabs.io/app"},
  {n:2,c:"Video",t:"HeyGen API Key",d:"Avatar IA video 4K automatico",l:"https://app.heygen.com"},
  {n:3,c:"YouTube",t:"YouTube OAuth Token",d:"Publicacao automatica de videos",l:"https://console.cloud.google.com/apis/credentials"},
  {n:4,c:"Instagram",t:"Instagram Access Token",d:"Publicacao automatica de Reels",l:"https://business.facebook.com"},
  {n:5,c:"TikTok",t:"TikTok Content API",d:"Publicacao automatica TikTok",l:"https://developers.tiktok.com"},
  {n:6,c:"Pinterest",t:"Pinterest API Token",d:"Publicacao automatica de Pins",l:"https://developers.pinterest.com/apps"},
  {n:7,c:"Lancamento",t:"Publicar 1o video YouTube",d:"Ativa o Dia 1 automaticamente",l:"https://studio.youtube.com"},
  {n:8,c:"AdSense",t:"1.000 inscritos + 4.000h",d:"Solicitar monetizacao YouTube",l:"https://youtube.com/account_monetization"},
  {n:9,c:"WhatsApp",t:"WhatsApp Business",d:"Conectar ao psicologiadoc",l:"https://business.whatsapp.com"},
  {n:10,c:"Instagram",t:"Perfil Profissional",d:"Verificar conta Instagram",l:"https://instagram.com/accounts/professional_account"},
];

export default function PageIA() {
  const [q, setQ] = useState("");
  const [resp, setResp] = useState("");
  const [loading, setLoading] = useState(false);
  const [hist, setHist] = useState([]);
  const [tk, setTk] = useState(null);
  const [tab, setTab] = useState("ia");
  const endRef = useRef(null);

  useEffect(() => {
    const load = async () => {
      try { const r = await fetch("/api/tokens"); if(r.ok) setTk(await r.json()); } catch {}
    };
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, []);

  const send = async () => {
    if (!q.trim() || loading) return;
    const pergunta = q.trim();
    setQ("");
    setLoading(true);
    setResp("Pensando...");
    try {
      const r = await fetch("/api/assistente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta, historico: hist }),
      });
      const d = await r.json();
      const resposta = d.resposta || ("Erro: " + (d.erro || "sem resposta"));
      setResp(resposta);
      setHist(h => [...h.slice(-8), { role: "user", text: pergunta }, { role: "model", text: resposta }]);
    } catch (e) {
      setResp("Erro: " + e.message);
    }
    setLoading(false);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
  };

  const bg = "#0a0a0f";
  const surf = "#13131a";
  const border = "#252535";
  const text = "#f0f0f8";
  const muted = "#55556a";
  const text2 = "#b0b0c8";
  const purple = "#7c3aed";
  const blue = "#2563eb";
  const green = "#059669";

  const saude = tk?.saude || "saudavel";
  const corS = saude === "critico" ? "#dc2626" : saude === "atencao" ? "#d97706" : green;

  return (
    <div style={{ minHeight:"100dvh", background:bg, color:text, fontFamily:"system-ui,sans-serif", paddingBottom:40 }}>
      <div style={{ background:"rgba(10,10,15,0.95)", backdropFilter:"blur(16px)", borderBottom:"1px solid "+border, padding:"12px 16px", display:"flex", alignItems:"center", gap:10, position:"sticky", top:0, zIndex:50 }}>
        <a href="/" style={{ textDecoration:"none", color:purple, fontSize:20 }}>{String.fromCodePoint(0x2190)}</a>
        <div style={{ width:32, height:32, borderRadius:9, background:"linear-gradient(135deg,#7c3aed,#a855f7)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:16 }}>*</div>
        <div style={{ flex:1 }}>
          <div style={{ fontWeight:800, fontSize:16 }}>Cerebro IA - psicologia.doc</div>
          <div style={{ fontSize:10, color:muted }}>Assistente completo - Gemini 2.0 Flash - Tokens gratuitos</div>
        </div>
        {tk && <div style={{ fontSize:11, fontWeight:700, color:corS, background:corS+"22", padding:"3px 9px", borderRadius:20, border:"1px solid "+corS+"44" }}>{tk.percentuais.tokens.toFixed(3)}%</div>}
      </div>

      <div style={{ maxWidth:520, margin:"0 auto", padding:"14px 12px" }}>
        <div style={{ display:"flex", gap:4, marginBottom:14, background:surf, borderRadius:10, padding:4, border:"1px solid "+border }}>
          {[["ia","IA Assistente"],["pendencias","Pendencias"],["tokens","Quota Gemini"]].map(([id,lb]) => (
            <button key={id} style={{ padding:"8px 14px", borderRadius:8, cursor:"pointer", fontSize:13, fontWeight:600, background:tab===id?"rgba(124,58,237,0.15)":"transparent", color:tab===id?purple:muted, border:"none", flex:1 }} onClick={() => setTab(id)}>{lb}</button>
          ))}
        </div>

        {tab === "ia" && (
          <div>
            <div style={{ background:surf, border:"1px solid "+border, borderRadius:14, padding:14, marginBottom:12 }}>
              <div style={{ fontSize:12, color:text2, marginBottom:10, lineHeight:1.6 }}>Pergunte qualquer coisa: estrategia, codigo, APIs, monetizacao, configuracoes...</div>
              <textarea value={q} onChange={e => setQ(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) send(); }} placeholder="Ex: Como configurar YouTube? Qual estrategia para o primeiro video viral? (Ctrl+Enter envia)" style={{ width:"100%", minHeight:100, padding:"10px 12px", borderRadius:10, border:"1.5px solid rgba(37,99,235,0.3)", background:"rgba(0,0,0,0.3)", color:text, fontSize:12, lineHeight:1.6, resize:"vertical", fontFamily:"inherit", outline:"none", boxSizing:"border-box" }} />
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginTop:8 }}>
                <span style={{ fontSize:10, color:muted }}>Ctrl+Enter para enviar - {Math.floor(hist.length/2)} perguntas no historico</span>
                <div style={{ display:"flex", gap:6 }}>
                  {hist.length > 0 && <button onClick={() => { setHist([]); setResp(""); }} style={{ padding:"6px 12px", borderRadius:8, border:"1px solid "+border, background:"#1c1c26", color:muted, fontSize:11, cursor:"pointer" }}>Limpar</button>}
                  <button onClick={send} disabled={!q.trim() || loading} style={{ padding:"10px 20px", borderRadius:10, border:"none", cursor:"pointer", fontWeight:700, fontSize:13, background:(!q.trim()||loading)?"#1c1c26":"linear-gradient(135deg,#2563eb,#3b82f6)", color:(!q.trim()||loading)?muted:"white" }}>
                    {loading ? "Pensando..." : "Enviar"}
                  </button>
                </div>
              </div>
            </div>
            {resp && (
              <div ref={endRef} style={{ background:"rgba(37,99,235,0.05)", border:"1px solid rgba(37,99,235,0.2)", borderRadius:14, padding:14, marginBottom:12 }}>
                <div style={{ fontSize:10, color:blue, fontWeight:700, marginBottom:8 }}>RESPOSTA DO CEREBRO IA</div>
                <div style={{ fontSize:12, lineHeight:1.75, color:text2, whiteSpace:"pre-wrap", wordBreak:"break-word", maxHeight:500, overflowY:"auto" }}>{resp}</div>
              </div>
            )}
          </div>
        )}

        {tab === "pendencias" && (
          <div>
            <div style={{ background:"rgba(124,58,237,0.05)", border:"1px solid rgba(124,58,237,0.2)", borderRadius:14, padding:14, marginBottom:14 }}>
              <div style={{ fontWeight:700, fontSize:13, color:purple, marginBottom:4 }}>Para o app funcionar 100%</div>
              <div style={{ fontSize:12, color:text2, lineHeight:1.6 }}>Complete cada etapa em ordem. Clique para abrir o link de configuracao.</div>
            </div>
            {PEND.map(p => (
              <a key={p.n} href={p.l} target="_blank" rel="noopener noreferrer" style={{ display:"flex", gap:12, padding:"12px 14px", marginBottom:8, background:surf, border:"1px solid "+border, borderRadius:12, textDecoration:"none", alignItems:"flex-start" }}>
                <div style={{ width:32, height:32, borderRadius:9, background:"rgba(124,58,237,0.1)", border:"2px solid "+purple, color:purple, display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:800, flexShrink:0 }}>{p.n}</div>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:11, fontWeight:700, color:muted, marginBottom:2 }}>{p.c}</div>
                  <div style={{ fontSize:13, fontWeight:700, color:text, marginBottom:2 }}>{p.t}</div>
                  <div style={{ fontSize:11, color:text2 }}>{p.d}</div>
                </div>
              </a>
            ))}
          </div>
        )}

        {tab === "tokens" && tk && (
          <div style={{ background:surf, border:"1px solid "+border, borderRadius:14, padding:14 }}>
            <div style={{ fontWeight:700, fontSize:13, marginBottom:12 }}>Gemini 2.0 Flash - Free Tier</div>
            <div style={{ marginBottom:10 }}>
              <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4 }}><span style={{ color:text2 }}>Tokens usados hoje</span><span style={{ fontWeight:800, color:corS }}>{tk.percentuais.tokens.toFixed(4)}%</span></div>
              <div style={{ height:12, background:"#1c1c26", borderRadius:6, overflow:"hidden", border:"1px solid "+border }}><div style={{ height:"100%", borderRadius:6, background:corS, width:Math.max(0.3,tk.percentuais.tokens)+"%" }} /></div>
              <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:muted, marginTop:3 }}><span>{(tk.uso_hoje.tokens_estimados||0).toLocaleString("pt-BR")} usados</span><span>{(tk.tokens_restantes||0).toLocaleString("pt-BR")} restantes / 1.000.000</span></div>
            </div>
            <div style={{ marginBottom:10 }}>
              <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4 }}><span style={{ color:text2 }}>Requests hoje</span><span style={{ fontWeight:800, color:blue }}>{tk.percentuais.requests.toFixed(4)}%</span></div>
              <div style={{ height:8, background:"#1c1c26", borderRadius:4, overflow:"hidden", border:"1px solid "+border }}><div style={{ height:"100%", borderRadius:4, background:blue, width:Math.max(0.3,tk.percentuais.requests)+"%" }} /></div>
              <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:muted, marginTop:3 }}><span>{tk.uso_hoje.requests_total} requests</span><span>{tk.requests_restantes} restantes / 1.500</span></div>
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8 }}>
              <div style={{ background:"#1c1c26", borderRadius:10, padding:"8px 10px", textAlign:"center", border:"1px solid "+border }}><div style={{ fontSize:9, color:muted }}>Meta 85%</div><div style={{ fontWeight:800, fontSize:14, color:purple }}>{(tk.percentuais?.meta_85pct||0).toFixed(1)}%</div></div>
              <div style={{ background:"#1c1c26", borderRadius:10, padding:"8px 10px", textAlign:"center", border:"1px solid "+border }}><div style={{ fontSize:9, color:muted }}>Ciclos livres</div><div style={{ fontWeight:800, fontSize:14, color:green }}>{tk.ciclos_restantes_hoje||0}</div></div>
              <div style={{ background:"#1c1c26", borderRadius:10, padding:"8px 10px", textAlign:"center", border:"1px solid "+border }}><div style={{ fontSize:9, color:muted }}>Status</div><div style={{ fontWeight:800, fontSize:12, color:corS }}>{(tk.saude||"ok").toUpperCase()}</div></div>
            </div>
          </div>
        )}
        {tab === "tokens" && !tk && <div style={{ textAlign:"center", padding:20, color:muted }}>Carregando...</div>}
      </div>
    </div>
  );
}