'use client';
import { useState, useEffect, useRef, useCallback } from 'react';

const STATUS_INTERVAL = 30000;
const WA_CHECK = 8 * 60 * 1000;

export default function IAPage() {
  const [aba, setAba] = useState('executor');
  const [msgs, setMsgs] = useState([{ role: 'model', text: '🧠 Executor IA ativo. Posso analisar métricas, criar rotas, fazer deploy, planejar estratégias. O que executar?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [waStatus, setWaStatus] = useState(null);
  const [plano, setPlano] = useState([]);
  const [autoLog, setAutoLog] = useState([]);
  const [membrosWA, setMembrosWA] = useState(0);
  const chatRef = useRef(null);

  const log = useCallback((msg) => {
    const hora = new Date().toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo' });
    setAutoLog(prev => [{ hora, msg }, ...prev].slice(0, 100));
  }, []);

  const fetchStatus = useCallback(async () => {
    try { const d = await fetch('/api/cerebro/status').then(r => r.json()); setStatus(d); } catch {}
  }, []);

  const fetchState = useCallback(async () => {
    try {
      const d = await fetch('/api/state').then(r => r.json());
      if (d.plano) setPlano(d.plano);
      if (typeof d.membros_wa === 'number') setMembrosWA(d.membros_wa);
    } catch {}
  }, []);

  const checkWA = useCallback(async () => {
    try {
      const d = await fetch('/api/whatsapp').then(r => r.json());
      if (d.status === 'ok' && d.mensagem) { log('💬 WA: "' + d.mensagem.slice(0, 60) + '"'); setWaStatus(d); }
    } catch {}
  }, [log]);

  useEffect(() => {
    fetchStatus(); fetchState();
    const s = setInterval(fetchStatus, STATUS_INTERVAL);
    const w = setInterval(checkWA, WA_CHECK);
    return () => { clearInterval(s); clearInterval(w); };
  }, [fetchStatus, fetchState, checkWA]);

  useEffect(() => { if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight; }, [msgs]);

  const enviar = async () => {
    if (!input.trim() || loading) return;
    const q = input.trim(); setInput('');
    setMsgs(p => [...p, { role: 'user', text: q }]);
    setLoading(true);
    try {
      const d = await fetch('/api/assistente', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pergunta: q, historico: msgs.slice(-10) }) }).then(r => r.json());
      setMsgs(p => [...p, { role: 'model', text: d.resposta || d.erro || 'Sem resposta', model: d.model, exec: d.execResult }]);
      if (d.execResult) log('🔧 ' + d.execResult.slice(0, 80));
    } catch (e) { setMsgs(p => [...p, { role: 'model', text: 'Erro: ' + e.message }]); }
    finally { setLoading(false); }
  };

  const S = { background:'#080810', color:'#e0e0f0', minHeight:'100vh', fontFamily:'Inter,sans-serif', display:'flex', flexDirection:'column' };
  const btnAba = (a) => ({ padding:'8px 18px', borderRadius:8, border:'none', cursor:'pointer', fontWeight:600, fontSize:12, background: aba===a ? '#7c3aed' : '#111', color: aba===a ? '#fff' : '#555' });
  const card = { background:'#0f0f1a', border:'1px solid #1a1a2e', borderRadius:14, padding:18, marginBottom:14 };
  const met = { background:'#080810', borderRadius:10, padding:'12px 14px', border:'1px solid #151530', textAlign:'center' };

  const BIO = '🧠 psicologia.doc\nDocumentários anônimos de psicologia\n\n📺 @psicologiadoc no YouTube\n📸 Instagram: @psicologiadoc\n🎵 TikTok: @psicologiadoc\n📌 Pinterest: psicologiadoc\n\n💬 Grupo VIP WhatsApp (1.024 vagas):\nwa.me/[LINK_DO_GRUPO]\n👆 Entre antes de fechar';

  return (
    <div style={S}>
      <div style={{ background:'#0d0d1a', borderBottom:'1px solid #1a1a2e', padding:'12px 20px', display:'flex', alignItems:'center', justifyContent:'space-between', flexWrap:'wrap', gap:10 }}>
        <div><span style={{ fontSize:17, fontWeight:700, color:'#7c3aed' }}>🧠 psicologia.doc</span><span style={{ fontSize:11, color:'#444', marginLeft:8 }}>Cérebro Autônomo v7 • Daniela Coelho Dia 261</span></div>
        <div style={{ display:'flex', gap:8, alignItems:'center' }}>
          <span style={{ fontSize:11, color:'#4ade80', background:'#051a0d', padding:'2px 10px', borderRadius:20 }}>● ATIVO</span>
          <span style={{ fontSize:11, color:'#7c3aed', background:'#150a2e', padding:'2px 10px', borderRadius:20 }}>Groq→Gemini→GPT-4o-mini</span>
        </div>
      </div>
      <div style={{ background:'#0a0a16', borderBottom:'1px solid #141428', padding:'8px 20px', display:'flex', gap:24, flexWrap:'wrap', fontSize:11, color:'#444' }}>
        <span>📊 Score: <b style={{ color:'#4ade80' }}>{status?.score_medio || '—'}</b></span>
        <span>💬 WA: <b style={{ color:'#06b6d4' }}>{membrosWA}/1024</b></span>
        <span>🗓 Dia: <b style={{ color:'#f59e0b' }}>{status?.dia_atual || 1}</b></span>
        <span>🎭 Revelação: <b style={{ color:'#a78bfa' }}>Dia 261 ~31/dez/2026</b></span>
        <span>📡 <b style={{ color:'#555' }}>{status?.total_producoes || 0} roteiros</b></span>
      </div>
      <div style={{ padding:'12px 20px 0', display:'flex', gap:6, borderBottom:'1px solid #111', flexWrap:'wrap' }}>
        {[['executor','🧠 Executor IA'],['status','📊 Status'],['whatsapp','💬 WhatsApp'],['plano','🗓 Plano'],['bios','📣 Bios'],['log','📋 Log']].map(([a,l]) => (
          <button key={a} style={btnAba(a)} onClick={() => setAba(a)}>{l}</button>
        ))}
      </div>
      <div style={{ flex:1, overflow:'auto', padding:20 }}>

        {aba === 'executor' && (
          <div style={{ display:'flex', flexDirection:'column', height:'72vh' }}>
            <div style={{ marginBottom:10, fontSize:12, color:'#333' }}>⚡ Pode pedir: analise métricas · otimize código · faça deploy · crie nova rota · estratégia de crescimento</div>
            <div ref={chatRef} style={{ flex:1, overflow:'auto', display:'flex', flexDirection:'column', gap:10, paddingBottom:10 }}>
              {msgs.map((m, i) => (
                <div key={i} style={{ display:'flex', justifyContent: m.role==='user' ? 'flex-end' : 'flex-start' }}>
                  <div style={{ maxWidth:'88%', background: m.role==='user' ? '#2a0d6e' : '#0f0f1e', border:'1px solid '+(m.role==='user' ? '#4a1da4' : '#1a1a2e'), borderRadius:12, padding:'10px 14px' }}>
                    <div style={{ fontSize:13, lineHeight:1.65, whiteSpace:'pre-wrap' }}>{m.text}</div>
                    {m.model && <div style={{ fontSize:10, color:'#333', marginTop:4 }}>{m.model}</div>}
                    {m.exec && <div style={{ fontSize:11, color:'#4ade80', marginTop:6, padding:'4px 8px', background:'#030f03', borderRadius:6 }}>✅ {m.exec}</div>}
                  </div>
                </div>
              ))}
              {loading && <div style={{ color:'#333', fontSize:13, textAlign:'center' }}>⟳ executando...</div>}
            </div>
            <div style={{ display:'flex', gap:8, paddingTop:10, borderTop:'1px solid #111' }}>
              <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key==='Enter' && !e.shiftKey && enviar()}
                placeholder="Ex: analise roteiros com maior score · faça deploy · crie rota de ranking"
                style={{ flex:1, background:'#0f0f1a', border:'1px solid #1a1a2e', borderRadius:10, padding:'10px 14px', color:'#e0e0f0', fontSize:13, outline:'none' }} />
              <button onClick={enviar} disabled={loading} style={{ background: loading ? '#2a1a4e' : '#7c3aed', border:'none', borderRadius:10, padding:'10px 22px', color:'#fff', cursor: loading ? 'not-allowed' : 'pointer', fontWeight:700, fontSize:14 }}>
                {loading ? '...' : '▶'}
              </button>
            </div>
          </div>
        )}

        {aba === 'status' && (
          <div>
            <div style={card}>
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(130px,1fr))', gap:10 }}>
                {[['Roteiros', status?.total_producoes], ['Score Médio', status?.score_medio], ['Memória', status?.topicos_em_memoria], ['WA', membrosWA+'/1024']].map(([k,v]) => (
                  <div key={k} style={met}><div style={{ fontSize:10, color:'#444', marginBottom:4 }}>{k}</div><div style={{ fontSize:22, fontWeight:700, color:'#7c3aed' }}>{v ?? '—'}</div></div>
                ))}
              </div>
            </div>
            {status?.ultimas_producoes?.length > 0 && (
              <div style={card}>
                <div style={{ fontSize:12, color:'#555', marginBottom:10 }}>Últimas produções</div>
                {status.ultimas_producoes.map((p, i) => (
                  <div key={i} style={{ display:'flex', justifyContent:'space-between', padding:'6px 0', borderBottom:'1px solid #111', fontSize:12 }}>
                    <span style={{ color:'#bbb' }}>{p.topic}</span>
                    <div style={{ display:'flex', gap:10 }}>
                      <span style={{ color: p.score>=90 ? '#4ade80' : p.score>=80 ? '#f59e0b' : '#f87171', fontSize:11 }}>{p.score} pts</span>
                      <span style={{ color:'#333', fontSize:11 }}>{p.modelo || 'groq'}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {aba === 'whatsapp' && (
          <div>
            <div style={card}>
              <div style={{ fontSize:13, color:'#555', marginBottom:12 }}>Agente WhatsApp Autônomo</div>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12, marginBottom:14 }}>
                <div style={met}><div style={{ fontSize:10, color:'#444' }}>Membros</div><div style={{ fontSize:24, fontWeight:700, color:'#06b6d4' }}>{membrosWA}/1024</div></div>
                <div style={met}><div style={{ fontSize:10, color:'#444' }}>Revelação</div><div style={{ fontSize:16, fontWeight:700, color:'#f59e0b' }}>Dia 261</div></div>
              </div>
              <div style={{ fontSize:12, color:'#444', lineHeight:2 }}>
                <div>✅ <b style={{ color:'#4ade80' }}>Agente ativo</b> — mensagens humanizadas, delay aleatório 2-45min (8h-22h SP)</div>
                <div>🎭 Persona: membro anônimo 28-35 anos, nunca revela que é IA</div>
                <div>🔍 Lê e responde mensagens do grupo quando detecta angústia ou tristeza</div>
                <div>🎯 Meta: 1.024 membros até Dia 261 — depois viram clientes da Daniela</div>
              </div>
              {waStatus && <div style={{ marginTop:14, background:'#030f03', borderRadius:8, padding:12, fontSize:12 }}>
                <div style={{ color:'#4ade80', marginBottom:4 }}>Última mensagem:</div>
                <div style={{ color:'#ccc', fontStyle:'italic' }}>"{waStatus.mensagem}"</div>
                <div style={{ color:'#333', fontSize:10, marginTop:4 }}>modelo: {waStatus.modelo} • delay: {waStatus.delay_min}min</div>
              </div>}
            </div>
            <div style={card}>
              <div style={{ fontSize:12, color:'#555', marginBottom:10 }}>Configurar envio real</div>
              <div style={{ fontSize:11, color:'#333', lineHeight:2 }}>
                <div>1. Meta Business → WhatsApp Business API</div>
                <div>2. Vercel env vars: <code style={{ color:'#7c3aed' }}>WHATSAPP_TOKEN</code>, <code style={{ color:'#7c3aed' }}>WHATSAPP_PHONE_ID</code>, <code style={{ color:'#7c3aed' }}>WHATSAPP_GROUP_ID</code></div>
                <div>3. Webhook: <code style={{ color:'#06b6d4' }}>repovazio.vercel.app/api/whatsapp</code></div>
                <div>4. Token verificação: <code style={{ color:'#4ade80' }}>psicologiadoc_webhook</code></div>
              </div>
            </div>
          </div>
        )}

        {aba === 'plano' && (
          <div style={card}>
            <div style={{ fontSize:13, color:'#555', marginBottom:14 }}>Planejamento — Daniela Coelho 31/dez/2026</div>
            {plano.length === 0 && <div style={{ fontSize:12, color:'#333' }}>Carregando plano...</div>}
            {plano.map((p, i) => (
              <div key={i} style={{ display:'flex', gap:14, padding:'10px 0', borderBottom:'1px solid #111', alignItems:'flex-start' }}>
                <div style={{ fontSize:18, fontWeight:700, color: p.executado ? '#4ade80' : '#333', minWidth:50, textAlign:'center' }}>
                  {p.executado ? '✅' : '◯'}<div style={{ fontSize:10, color:'#333', fontWeight:400 }}>Dia {p.dia}</div>
                </div>
                <div>
                  <div style={{ fontSize:12, color: p.fase==='revelacao' ? '#f59e0b' : '#7c3aed', fontWeight:600, marginBottom:2 }}>{p.fase}</div>
                  <div style={{ fontSize:13, color:'#bbb' }}>{p.acao}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {aba === 'bios' && (
          <div>
            <div style={card}>
              <div style={{ fontSize:13, color:'#555', marginBottom:12 }}>Bio Universal — copiar para todas as redes</div>
              <pre style={{ fontSize:12, background:'#080810', borderRadius:8, padding:14, color:'#aaa', lineHeight:1.9, border:'1px solid #111', whiteSpace:'pre-wrap' }}>{BIO}</pre>
              <div style={{ fontSize:11, color:'#333', marginTop:10, lineHeight:1.8 }}>
                ✅ Substituir [LINK_DO_GRUPO] pelo link real do grupo WhatsApp<br/>
                ✅ Colocar em: YouTube · Instagram · TikTok · Pinterest<br/>
                ✅ Limite 1.024 cria urgência e exclusividade
              </div>
            </div>
            <div style={card}>
              <div style={{ fontSize:12, color:'#555', marginBottom:10 }}>Estratégia cross-platform</div>
              <div style={{ fontSize:12, color:'#444', lineHeight:2.1 }}>
                <div>📺 <b style={{ color:'#aaa' }}>YouTube</b> — vídeos 22-28min + Shorts → bio com link WA</div>
                <div>📸 <b style={{ color:'#aaa' }}>Instagram</b> — Reels + Stories CTA grupo WA</div>
                <div>🎵 <b style={{ color:'#aaa' }}>TikTok</b> — clips 60-90s + link WA fixado</div>
                <div>📌 <b style={{ color:'#aaa' }}>Pinterest</b> — frases visuais → tráfego para YouTube</div>
                <div>💬 <b style={{ color:'#aaa' }}>WhatsApp</b> — 1.024 membros → clientes Daniela dez/2026</div>
              </div>
            </div>
          </div>
        )}

        {aba === 'log' && (
          <div style={card}>
            <div style={{ fontSize:12, color:'#555', marginBottom:10 }}>Log automático em tempo real</div>
            {autoLog.length === 0 && <div style={{ fontSize:12, color:'#222' }}>Aguardando eventos...</div>}
            {autoLog.map((l, i) => (
              <div key={i} style={{ fontSize:11, padding:'4px 0', borderBottom:'1px solid #0a0a0a', display:'flex', gap:10 }}>
                <span style={{ color:'#333', flexShrink:0, fontFamily:'monospace' }}>{l.hora}</span>
                <span style={{ color:'#888' }}>{l.msg}</span>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}