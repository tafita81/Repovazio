"use client";
import { useState, useEffect, useCallback, useRef } from "react";

const PENDENCIAS = [
  {n:1,cat:"🎙️ Voz",txt:"ElevenLabs API Key",desc:"Narração cinematográfica PT-BR",link:"https://elevenlabs.io/app",ok:false},
  {n:2,cat:"🎬 Vídeo",txt:"HeyGen API Key",desc:"Avatar IA vídeo 4K automático",link:"https://app.heygen.com",ok:false},
  {n:3,cat:"▶️ YouTube",txt:"YouTube OAuth Token",desc:"Publicação automática de vídeos",link:"https://console.cloud.google.com/apis/credentials",ok:false},
  {n:4,cat:"📸 Instagram",txt:"Instagram Access Token",desc:"Publicação automática de Reels",link:"https://business.facebook.com",ok:false},
  {n:5,cat:"🎵 TikTok",txt:"TikTok Content API",desc:"Publicação automática TikTok",link:"https://developers.tiktok.com",ok:false},
  {n:6,cat:"📌 Pinterest",txt:"Pinterest API Token",desc:"Publicação automática de Pins",link:"https://developers.pinterest.com/apps",ok:false},
  {n:7,cat:"🚀 Lançamento",txt:"Publicar 1º vídeo YouTube",desc:"Ativa o Dia 1 automaticamente",link:"https://studio.youtube.com",ok:false},
  {n:8,cat:"💰 AdSense",txt:"1.000 inscritos + 4.000h",desc:"Solicitar monetização YouTube",link:"https://youtube.com/account_monetization",ok:false},
  {n:9,cat:"💬 WhatsApp",txt:"WhatsApp Business",desc:"Conectar ao @psicologiadoc",link:"https://business.whatsapp.com",ok:false},
  {n:10,cat:"📱 Instagram",txt:"Perfil Profissional",desc:"Verificar conta Instagram",link:"https://instagram.com/accounts/professional_account",ok:false},
];

const TOKENS_INFO = {
  requests_per_day: 1500,
  tokens_per_day: 1_000_000,
  tokens_per_minute: 32_000,
};

export default function PageIA() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [hist, setHist] = useState([]);
  const [tokens, setTokens] = useState(null);
  const [tab, setTab] = useState("ia");
  const respRef = useRef(null);

  const fetchTokens = useCallback(async () => {
    try {
      const r = await fetch("/api/tokens");
      if (r.ok) setTokens(await r.json());
    } catch {}
  }, []);

  useEffect(() => {
    fetchTokens();
    const t = setInterval(fetchTokens, 60000);
    return () => clearInterval(t);
  }, [fetchTokens]);

  const send = useCallback(async () => {
    if (!query.trim() || loading) return;
    const q = query.trim();
    setQuery("");
    setLoading(true);
    setResponse("⏳ Pensando...");
    try {
      const r = await fetch("/api/assistente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pergunta: q, historico: hist }),
      });
      const d = await r.json();
      const resp = d.resposta || ("❌ " + (d.erro || "Sem resposta"));
      setResponse(resp);
      setHist(h => [...h.slice(-8), { role: "user", text: q }, { role: "model", text: resp }]);
    } catch (e) {
      setResponse("❌ Erro: " + e.message);
    }
    setLoading(false);
    setTimeout(() => respRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
  }, [query, loading, hist]);

  const S = {
    page: { minHeight:"100dvh", background:"#0a0a0f", color:"#f0f0f8", fontFamily:"system-ui,sans-serif", padding:"0 0 40px" },
    header: { background:"rgba(10,10,15,0.95)", backdropFilter:"blur(16px)", borderBottom:"1px solid #252535", padding:"12px 16px", display:"flex", alignItems:"center", gap:10, position:"sticky", top:0, zIndex:50 },
    title: { fontWeight:800, fontSize:16 },
    body: { maxWidth:520, margin:"0 auto", padding:"14px 12px" },
    card: { background:"#13131a", border:"1px solid #252535", borderRadius:14, padding:14, marginBottom:12 },
    tab: (active) => ({ padding:"8px 16px", borderRadius:8, cursor:"pointer", fontSize:13, fontWeight:600, background:active?"rgba(124,58,237,0.15)":"transparent", color:active?"#7c3aed":"#55556a", border:"none" }),
    btn: (active) => ({ padding:"10px 20px", borderRadius:10, border:"none", cursor:"pointer", fontWeight:700, fontSize:13, background:active?"linear-gradient(135deg,#2563eb,#3b82f6)":"#1c1c26", color:active?"white":"#55556a" }),
    bar: (pct, color) => ({ height:"100%", borderRadius:5, background:color, width:Math.max(0.3,pct)+"%", transition:"width 0.8s" }),
  };

  const saude = tokens?.saude || "saudavel";
  const corSaude = saude==="critico"?"#dc2626":saude==="atencao"?"#d97706":"#059669";

  return (
    <div style={S.page}>
      {/* Header */}
      <div style={S.header}>
        <a href="/" style={{ textDecoration:"none", color:"#7c3aed", fontSize:20 }}>←</a>
        <div style={{ width:32, height:32, borderRadius:9, background:"linear-gradient(135deg,#7c3aed,#a855f7)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:16 }}>🤖</div>
        <div style={{ flex:1 }}>
          <div style={S.title}>Cérebro IA — psicologia.doc</div>
          <div style={{ fontSize:10, color:"#55556a" }}>Assistente completo · Gemini 2.0 Flash · Tokens gratuitos</div>
        </div>
        {tokens && (
          <div style={{ fontSize:11, fontWeight:700, color:corSaude, background:corSaude+"18", padding:"3px 9px", borderRadius:20, border:"1px solid "+corSaude+"44" }}>
            ⚡ {tokens.percentuais.tokens.toFixed(3)}%
          </div>
        )}
      </div>

      <div style={S.body}>
        {/* Tabs */}
        <div style={{ display:"flex", gap:4, marginBottom:14, background:"#13131a", borderRadius:10, padding:4, border:"1px solid #252535" }}>
          {[["ia","🤖 IA Assistente"],["pendencias","📋 Pendências"],["tokens","⚡ Quota Gemini"]].map(([id,lb]) => (
            <button key={id} style={S.tab(tab===id)} onClick={() => setTab(id)}>{lb}</button>
          ))}
        </div>

        {/* ABA: IA ASSISTENTE */}
        {tab==="ia" && (
          <>
            <div style={S.card}>
              <div style={{ fontSize:12, color:"#b0b0c8", marginBottom:10, lineHeight:1.6 }}>
                Pergunte qualquer coisa sobre o app, estratégia, código, APIs, monetização, otimizações, configurações...
              </div>
              <textarea
                value={query}
                onChange={e => setQuery(e.target.value)}
                onKeyDown={e => { if (e.key==="Enter" && (e.ctrlKey||e.metaKey)) send(); }}
                placeholder={"Ex: Como configurar o YouTube para publicação automática?
Qual a melhor estratégia para o primeiro vídeo viral?
O que falta para o app estar 100%?

Ctrl+Enter para enviar"}
                style={{ width:"100%", minHeight:100, padding:"10px 12px", borderRadius:10, border:"1.5px solid rgba(37,99,235,0.3)", background:"rgba(0,0,0,0.3)", color:"#f0f0f8", fontSize:12, lineHeight:1.6, resize:"vertical", fontFamily:"inherit", outline:"none", boxSizing:"border-box" }}
              />
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginTop:8 }}>
                <span style={{ fontSize:10, color:"#55556a" }}>Ctrl+Enter · usa tokens Gemini gratuitos · {hist.length/2|0} perguntas no histórico</span>
                <div style={{ display:"flex", gap:6 }}>
                  {hist.length>0 && <button onClick={() => { setHist([]); setResponse(""); }} style={{ padding:"6px 12px", borderRadius:8, border:"1px solid #252535", background:"#1c1c26", color:"#55556a", fontSize:11, cursor:"pointer" }}>🗑 Limpar</button>}
                  <button onClick={send} disabled={!query.trim()||loading} style={S.btn(query.trim()&&!loading)}>
                    {loading ? "⏳ Pensando..." : "🚀 Enviar"}
                  </button>
                </div>
              </div>
            </div>

            {response && (
              <div ref={respRef} style={{ ...S.card, background:"rgba(37,99,235,0.05)", border:"1px solid rgba(37,99,235,0.2)" }}>
                <div style={{ fontSize:10, color:"#2563eb", fontWeight:700, marginBottom:8 }}>🤖 RESPOSTA DO CÉREBRO IA</div>
                <div style={{ fontSize:12, lineHeight:1.75, color:"#b0b0c8", whiteSpace:"pre-wrap", wordBreak:"break-word", maxHeight:500, overflowY:"auto" }}>
                  {response}
                </div>
              </div>
            )}

            {hist.length>2 && (
              <div style={S.card}>
                <div style={{ fontSize:11, fontWeight:700, color:"#55556a", marginBottom:8 }}>📜 HISTÓRICO</div>
                {hist.slice(-6).map((h,i) => (
                  <div key={i} style={{ marginBottom:6, padding:"7px 10px", borderRadius:8, background:h.role==="user"?"rgba(124,58,237,0.07)":"rgba(37,99,235,0.05)", border:"1px solid "+(h.role==="user"?"rgba(124,58,237,0.15)":"rgba(37,99,235,0.12)") }}>
                    <div style={{ fontSize:9, fontWeight:700, color:h.role==="user"?"#7c3aed":"#2563eb", marginBottom:3 }}>{h.role==="user"?"👤 VOCÊ":"🤖 IA"}</div>
                    <div style={{ fontSize:11, color:"#b0b0c8", lineHeight:1.5, maxHeight:80, overflow:"hidden" }}>{h.text.slice(0,200)}{h.text.length>200?"...":""}</div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* ABA: PENDÊNCIAS */}
        {tab==="pendencias" && (
          <>
            <div style={{ ...S.card, background:"rgba(124,58,237,0.05)", border:"1px solid rgba(124,58,237,0.2)", marginBottom:14 }}>
              <div style={{ fontWeight:700, fontSize:13, color:"#7c3aed", marginBottom:4 }}>📋 Para o app funcionar 100%</div>
              <div style={{ fontSize:12, color:"#b0b0c8", lineHeight:1.6 }}>Complete cada etapa abaixo em ordem. Clique para abrir o link oficial de cada configuração.</div>
            </div>
            {PENDENCIAS.map(p => (
              <a key={p.n} href={p.link} target="_blank" rel="noopener noreferrer" style={{ display:"flex", gap:12, padding:"12px 14px", marginBottom:8, background:"#13131a", border:"1px solid "+(p.ok?"rgba(5,150,105,0.3)":"#252535"), borderRadius:12, textDecoration:"none", alignItems:"flex-start", cursor:"pointer" }}>
                <div style={{ width:32, height:32, borderRadius:9, background:p.ok?"rgba(5,150,105,0.15)":"rgba(124,58,237,0.1)", border:"2px solid "+(p.ok?"#059669":"#7c3aed"), color:p.ok?"#059669":"#7c3aed", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:800, flexShrink:0 }}>{p.ok?"✓":p.n}</div>
                <div style={{ flex:1 }}>
                  <div style={{ fontSize:11, fontWeight:700, color:"#55556a", marginBottom:2 }}>{p.cat}</div>
                  <div style={{ fontSize:13, fontWeight:700, color:"#f0f0f8", marginBottom:2 }}>{p.txt}</div>
                  <div style={{ fontSize:11, color:"#b0b0c8" }}>{p.desc}</div>
                </div>
                <div style={{ fontSize:16, color:"#7c3aed", flexShrink:0 }}>↗</div>
              </a>
            ))}
          </>
        )}

        {/* ABA: QUOTA GEMINI */}
        {tab==="tokens" && (
          <>
            <div style={{ ...S.card, background:"rgba(5,150,105,0.05)", border:"1px solid rgba(5,150,105,0.2)" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
                <div><div style={{ fontWeight:700, fontSize:13 }}>⚡ Gemini 2.0 Flash — Free Tier</div><div style={{ fontSize:10, color:"#55556a", marginTop:2 }}>Atualiza a cada 1 minuto automaticamente</div></div>
                <button onClick={fetchTokens} style={{ padding:"5px 12px", borderRadius:8, border:"1px solid #252535", background:"#1c1c26", color:"#b0b0c8", fontSize:11, cursor:"pointer" }}>↻ Atualizar</button>
              </div>
              {tokens ? (
                <>
                  {[
                    { label:"🔤 Tokens usados hoje", pct:tokens.percentuais.tokens, max:"1.000.000", used:(tokens.uso_hoje.tokens_estimados||0).toLocaleString("pt-BR"), rem:(tokens.tokens_restantes||0).toLocaleString("pt-BR"), color:corSaude },
                    { label:"📨 Requests usadas hoje", pct:tokens.percentuais.requests, max:"1.500", used:tokens.uso_hoje.requests_total, rem:tokens.requests_restantes, color:"#2563eb" },
                  ].map(m => (
                    <div key={m.label} style={{ marginBottom:14 }}>
                      <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4 }}><span style={{ color:"#b0b0c8" }}>{m.label}</span><span style={{ fontWeight:800, color:m.color }}>{m.pct.toFixed(4)}%</span></div>
                      <div style={{ height:12, background:"#1c1c26", borderRadius:6, overflow:"hidden", border:"1px solid #252535" }}><div style={S.bar(m.pct, m.color)}/></div>
                      <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, color:"#55556a", marginTop:3 }}><span>{m.used} usados</span><span>{m.rem} restantes / {m.max}</span></div>
                    </div>
                  ))}
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8, marginTop:4 }}>
                    {[
                      { label:"Meta 85%", val:(tokens.percentuais?.meta_85pct||0).toFixed(1)+"%", color:"#7c3aed" },
                      { label:"Ciclos livres", val:tokens.ciclos_restantes_hoje||"—", color:"#059669" },
                      { label:"Status", val:(tokens.saude||"ok").toUpperCase(), color:corSaude },
                    ].map(m => (
                      <div key={m.label} style={{ background:"#1c1c26", borderRadius:10, padding:"8px 10px", textAlign:"center", border:"1px solid #252535" }}>
                        <div style={{ fontSize:9, color:"#55556a", marginBottom:3 }}>{m.label}</div>
                        <div style={{ fontWeight:800, fontSize:14, color:m.color }}>{m.val}</div>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop:12, padding:"10px 12px", background:"#1c1c26", borderRadius:10, border:"1px solid #252535" }}>
                    <div style={{ fontSize:10, color:"#55556a", marginBottom:6 }}>📊 DETALHES DE USO HOJE</div>
                    {[
                      ["Ciclos Cérebro", tokens.uso_hoje.ciclos_cerebro, "× 1.350 tokens"],
                      ["Ciclos Aprendizado", tokens.uso_hoje.ciclos_aprender, "× 700 tokens"],
                      ["Total requests", tokens.uso_hoje.requests_total, "de 1.500/dia"],
                      ["Hora SP", tokens.agora_sp || "—", ""],
                    ].map(([k,v,s]) => (
                      <div key={k} style={{ display:"flex", justifyContent:"space-between", fontSize:11, padding:"3px 0", borderBottom:"1px solid #252535" }}>
                        <span style={{ color:"#b0b0c8" }}>{k}</span>
                        <span style={{ fontWeight:700, color:"#f0f0f8" }}>{v} <span style={{ color:"#55556a", fontWeight:400 }}>{s}</span></span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div style={{ textAlign:"center", padding:20, color:"#55556a" }}>Carregando dados...</div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}