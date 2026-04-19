'use client';
import { useState, useEffect, useRef, useCallback } from 'react';

const CEREBRO_INTERVAL = 2 * 60 * 60 * 1000; // 2h — alinhado com cron
const STATUS_INTERVAL = 45 * 1000; // 45s — status refresh
const WA_INTERVAL = 6 * 60 * 60 * 1000; // 6h — agente WhatsApp

export default function IAPage() {
  const [aba, setAba] = useState('assistente');
  const [msgs, setMsgs] = useState([{ role: 'model', text: '🧠 Cerebro Executor ativo. Posso editar codigo, analisar metricas, otimizar o sistema. O que executar?' }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [waStatus, setWaStatus] = useState(null);
  const [autoLog, setAutoLog] = useState([]);
  const [proximoCiclo, setProximoCiclo] = useState(null);
  const [proximoWA, setProximoWA] = useState(null);
  const chatRef = useRef(null);
  const lastCerebroRef = useRef(0);
  const lastWARef = useRef(0);

  const log = useCallback((msg) => {
    const hora = new Date().toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo' });
    setAutoLog(prev => [{ hora, msg }, ...prev].slice(0, 50));
  }, []);

  // Auto-ciclo cerebro
  const runCiclo = useCallback(async (forcado = false) => {
    const agora = Date.now();
    if (!forcado && agora - lastCerebroRef.current < CEREBRO_INTERVAL) return;
    lastCerebroRef.current = agora;
    log('⚡ Ciclo cerebro iniciado...');
    try {
      const r = await fetch('/api/cerebro');
      const d = await r.json();
      if (d.status === 'cerebro_ok') {
        log(`✅ Roteiro: "${d.topic}" score:${d.score} modelo:${d.model}`);
      } else {
        log('⚠️ Ciclo: ' + (d.error || 'resposta vazia'));
      }
    } catch (e) { log('❌ Erro ciclo: ' + e.message); }
  }, [log]);

  // Auto-ciclo WhatsApp
  const runWA = useCallback(async () => {
    const agora = Date.now();
    if (agora - lastWARef.current < WA_INTERVAL) return;
    lastWARef.current = agora;
    try {
      const r = await fetch('/api/whatsapp');
      const d = await r.json();
      if (d.mensagem && d.mensagem !== 'horario de silencio') {
        log(`💬 WA enviou: "${d.mensagem.slice(0, 60)}..."`);
        setWaStatus(d);
      }
    } catch {}
  }, [log]);

  // Status loop
  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch('/api/cerebro/status');
      const d = await r.json();
      setStatus(d);
    } catch {}
  }, []);

  // Calcular proximos ciclos
  useEffect(() => {
    const tick = () => {
      const agora = Date.now();
      const diffCerebro = Math.max(0, CEREBRO_INTERVAL - (agora - lastCerebroRef.current));
      const diffWA = Math.max(0, WA_INTERVAL - (agora - lastWARef.current));
      const fmt = (ms) => {
        const h = Math.floor(ms / 3600000);
        const m = Math.floor((ms % 3600000) / 60000);
        const s = Math.floor((ms % 60000) / 1000);
        return h > 0 ? `${h}h ${m}m` : `${m}m ${s}s`;
      };
      setProximoCiclo(fmt(diffCerebro));
      setProximoWA(fmt(diffWA));
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  // Iniciar automacoes
  useEffect(() => {
    fetchStatus();
    runCiclo(true); // ciclo imediato ao abrir
    runWA();

    const statusId = setInterval(fetchStatus, STATUS_INTERVAL);
    const cerebroId = setInterval(() => runCiclo(false), 60000); // checar a cada 1min se é hora
    const waId = setInterval(() => runWA(), 60000);

    return () => { clearInterval(statusId); clearInterval(cerebroId); clearInterval(waId); };
  }, [fetchStatus, runCiclo, runWA]);

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight;
  }, [msgs]);

  const enviar = async () => {
    if (!input.trim() || loading) return;
    const pergunta = input.trim();
    setInput('');
    setMsgs(prev => [...prev, { role: 'user', text: pergunta }]);
    setLoading(true);
    try {
      const r = await fetch('/api/assistente', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta, historico: msgs.slice(-8) })
      });
      const d = await r.json();
      const resp = d.resposta || d.erro || 'Sem resposta';
      setMsgs(prev => [...prev, { role: 'model', text: resp, model: d.model, execResult: d.execResult }]);
      if (d.execResult) log('🔧 Executor: ' + d.execResult);
    } catch (e) {
      setMsgs(prev => [...prev, { role: 'model', text: 'Erro: ' + e.message }]);
    } finally { setLoading(false); }
  };

  const s = { background: '#0d0d0d', color: '#e8e8e8', minHeight: '100vh', fontFamily: 'Inter, sans-serif', display: 'flex', flexDirection: 'column' };
  const btn = (ativo) => ({ padding: '8px 20px', borderRadius: 8, border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: 13, background: ativo ? '#7c3aed' : '#1a1a2e', color: ativo ? '#fff' : '#888', transition: 'all .2s' });
  const card = { background: '#111', border: '1px solid #222', borderRadius: 12, padding: 16, marginBottom: 12 };

  return (
    <div style={s}>
      {/* Header */}
      <div style={{ background: '#111', borderBottom: '1px solid #222', padding: '14px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10 }}>
        <div>
          <span style={{ fontSize: 18, fontWeight: 700, color: '#7c3aed' }}>🧠 psicologia.doc</span>
          <span style={{ fontSize: 12, color: '#555', marginLeft: 8 }}>Cérebro Autônomo v7</span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: '#4ade80', background: '#0a2a1a', padding: '3px 10px', borderRadius: 20 }}>● ATIVO</span>
          {status && <span style={{ fontSize: 11, color: '#888' }}>{status.total_producoes || 0} roteiros</span>}
        </div>
      </div>

      {/* Auto-status bar */}
      <div style={{ background: '#0a0a1a', borderBottom: '1px solid #1a1a3a', padding: '8px 20px', display: 'flex', gap: 20, flexWrap: 'wrap', fontSize: 11, color: '#555' }}>
        <span>⏱ Próx. cérebro: <b style={{ color: '#7c3aed' }}>{proximoCiclo}</b></span>
        <span>💬 Próx. WhatsApp: <b style={{ color: '#06b6d4' }}>{proximoWA}</b></span>
        <span>📊 Score médio: <b style={{ color: '#4ade80' }}>{status?.score_medio || '—'}</b></span>
        <span>🤖 Groq→Gemini→GPT-4o-mini</span>
      </div>

      {/* Abas */}
      <div style={{ padding: '12px 20px 0', display: 'flex', gap: 8, borderBottom: '1px solid #1a1a1a' }}>
        {['assistente', 'status', 'whatsapp', 'log'].map(a => (
          <button key={a} style={btn(aba === a)} onClick={() => setAba(a)}>
            {a === 'assistente' ? '🧠 Executor IA' : a === 'status' ? '📊 Status' : a === 'whatsapp' ? '💬 WhatsApp' : '📋 Log Auto'}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: 20 }}>

        {/* ASSISTENTE EXECUTOR */}
        {aba === 'assistente' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '70vh' }}>
            <div ref={chatRef} style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 12, paddingBottom: 12 }}>
              {msgs.map((m, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div style={{ maxWidth: '85%', background: m.role === 'user' ? '#3b1d8a' : '#151520', border: '1px solid ' + (m.role === 'user' ? '#5b2ed4' : '#222'), borderRadius: 12, padding: '10px 14px' }}>
                    <div style={{ fontSize: 13, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{m.text}</div>
                    {m.model && <div style={{ fontSize: 10, color: '#444', marginTop: 4 }}>{m.model}</div>}
                    {m.execResult && <div style={{ fontSize: 11, color: '#4ade80', marginTop: 6, padding: '4px 8px', background: '#0a1a0a', borderRadius: 6 }}>🔧 {m.execResult}</div>}
                  </div>
                </div>
              ))}
              {loading && <div style={{ color: '#555', fontSize: 13 }}>⟳ processando...</div>}
            </div>
            <div style={{ display: 'flex', gap: 8, paddingTop: 12, borderTop: '1px solid #222' }}>
              <input
                value={input} onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && !e.shiftKey && enviar()}
                placeholder="Peça para analisar, otimizar, criar código, planejar estratégia..."
                style={{ flex: 1, background: '#111', border: '1px solid #333', borderRadius: 10, padding: '10px 14px', color: '#e8e8e8', fontSize: 13, outline: 'none' }}
              />
              <button onClick={enviar} disabled={loading} style={{ background: '#7c3aed', border: 'none', borderRadius: 10, padding: '10px 20px', color: '#fff', cursor: 'pointer', fontWeight: 600 }}>
                {loading ? '...' : 'Enviar'}
              </button>
            </div>
          </div>
        )}

        {/* STATUS */}
        {aba === 'status' && status && (
          <div>
            <div style={card}>
              <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>Métricas do sistema</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 12 }}>
                {[
                  ['Roteiros', status.total_producoes],
                  ['Score Médio', status.score_medio],
                  ['Tópicos Memória', status.topicos_em_memoria],
                  ['Hora SP', new Date().toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo' })],
                ].map(([k, v]) => (
                  <div key={k} style={{ background: '#0d0d0d', borderRadius: 8, padding: 12, border: '1px solid #1a1a1a' }}>
                    <div style={{ fontSize: 10, color: '#555' }}>{k}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: '#7c3aed' }}>{v ?? '—'}</div>
                  </div>
                ))}
              </div>
            </div>
            {status.ultimas_producoes?.length > 0 && (
              <div style={card}>
                <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>Últimas produções</div>
                {status.ultimas_producoes.map((p, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid #1a1a1a', fontSize: 12 }}>
                    <span>{p.topic}</span>
                    <span style={{ color: p.score >= 85 ? '#4ade80' : '#f59e0b' }}>{p.score} pts</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* WHATSAPP */}
        {aba === 'whatsapp' && (
          <div>
            <div style={card}>
              <div style={{ fontSize: 13, color: '#888', marginBottom: 12 }}>Agente WhatsApp Autônomo</div>
              <div style={{ fontSize: 12, color: '#555', lineHeight: 1.8 }}>
                <p>✅ <b style={{ color: '#4ade80' }}>Modo automático ativo</b> — agente envia mensagens humanizadas a cada 6h no período 8h-22h (SP)</p>
                <p>👥 Grupo limite: <b style={{ color: '#7c3aed' }}>1.024 membros</b></p>
                <p>🎭 Persona: membro anônimo empático, 28-35 anos, respostas aleatórias indetectáveis</p>
                <p>🗓 Revelação Daniela Coelho: <b style={{ color: '#f59e0b' }}>Dia 261 ~31/dez/2026</b></p>
                <p>📱 Para ativar: configure WHATSAPP_TOKEN e WHATSAPP_PHONE_ID no Vercel</p>
              </div>
              {waStatus && (
                <div style={{ marginTop: 12, background: '#0a1a0a', borderRadius: 8, padding: 10, fontSize: 12 }}>
                  <div style={{ color: '#4ade80' }}>Última mensagem enviada:</div>
                  <div style={{ color: '#e8e8e8', marginTop: 4 }}>"{waStatus.mensagem}"</div>
                </div>
              )}
            </div>
            <div style={card}>
              <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>Bio automática para redes sociais</div>
              <div style={{ fontSize: 11, background: '#0d0d0d', borderRadius: 8, padding: 12, color: '#aaa', fontFamily: 'monospace', lineHeight: 1.8 }}>
                {"🧠 psicologia.doc | Documentários anônimos de psicologia\n📺 YouTube: @psicologiadoc\n📸 Instagram: @psicologiadoc\n🎵 TikTok: @psicologiadoc\n📌 Pinterest: psicologiadoc\n💬 Grupo VIP WhatsApp (1.024 vagas):"}
                <br />{"👇 Entre antes de fechar"}
              </div>
            </div>
          </div>
        )}

        {/* LOG AUTOMÁTICO */}
        {aba === 'log' && (
          <div style={card}>
            <div style={{ fontSize: 13, color: '#888', marginBottom: 8 }}>Log de automação em tempo real</div>
            {autoLog.length === 0 && <div style={{ fontSize: 12, color: '#444' }}>Aguardando eventos...</div>}
            {autoLog.map((l, i) => (
              <div key={i} style={{ fontSize: 11, padding: '4px 0', borderBottom: '1px solid #111', display: 'flex', gap: 10 }}>
                <span style={{ color: '#555', flexShrink: 0 }}>{l.hora}</span>
                <span style={{ color: '#ccc' }}>{l.msg}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}