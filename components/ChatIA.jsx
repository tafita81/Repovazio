'use client';
import { useState, useRef, useEffect, useCallback } from 'react';
import { useSession } from 'next-auth/react';

export default function ChatIA() {
  const { data: session } = useSession();
  const [msgs, setMsgs] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('llama-3.3-70b-versatile');
  const [showModels, setShowModels] = useState(false);
  const [imgB64, setImgB64] = useState(null);
  const [imgMime, setImgMime] = useState(null);
  const [skills, setSkills] = useState([]);
  const msgEndRef = useRef(null);
  const fileRef = useRef(null);
  const sessionId = useRef('s' + Date.now().toString(36));

  const MODELS = [
    { id: 'llama-3.3-70b-versatile', n: 'Llama 3.3 70B ⚪', g: 'groq' },
    { id: 'llama-3.1-8b-instant', n: 'Llama 3.1 8B ➤', g: 'groq' },
    { id: 'gemini-1.5-flash', n: 'Gemini 1.5 Flash <br/>(👂) visão', g: 'gemini' },
    { id: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free', n: 'Together.ai 128k 🖀', g: 'together' },
  ];

  useEffect(() => { msgEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs]);

  useEffect(() => {
    fetch('/api/skills?acao=listar').then(r => r.json()).then(d => {
      if (d.skills) setSkills(d.skills.slice(0, 6));
    }).catch(() => {});
  }, []);

  const handleFile = useCallback((e) => {
    const file = e.target.files[0]; if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const b64 = reader.result.split(',')[1];
      setImgB64(b64); setImgMime(file.type);
    };
    reader.readAsDataURL(file);
  }, []);

  const send = useCallback(async () => {
    if (!input.trim() && !imgB64) return;
    const userMsg = { role: 'user', content: input, img: imgB64 ? `data:${imgMime};base64,${imgB64}` : null, ts: Date.now() };
    setMsgs(m => [...m, userMsg]); setInput(''); setImgB64(null); setImgMime(null); setLoading(true);
    if (fileRef.current) fileRef.current.value = '';
    try {
      const res = await fetch('/api/ia-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mensagem: userMsg.content, historico: msgs.slice(-10).map(m => ({ role: m.role, content: m.content })),
          modelo: model, max_tokens: 2048, usar_memoria: true,
          session_id: sessionId.current,
          imagem_b64: imgB64, imagem_mime: imgMime,
        }),
      });
      const data = await res.json();
      if (data.erro) throw new Error(data.erro);
      const assistMsg = { role: 'assistant', content: data.resposta, kid: data.kid, provider: data.provider, ms: data.ms, ts: Date.now() };
      setMsgs(m => [...m, assistMsg]);
    } catch (e) {
      setMsgs(m => [...m, { role: 'assistant', content: '❌ Erro: ' + e.message, ts: Date.now() }]);
    } finally { setLoading(false); }
  }, [input, imgB64, imgMime, model, msgs]);

  const renderContent = (text) => {
    if (!text) return null;
    const htmlMatch = text.match(/```html\n([\s\S]*?)\n```/);
    if (htmlMatch) {
      return <div className="relative my-2">
        <span className="text-xs text-green-400 font-mono">🏘 Artefato HTML</span>
        <iframe srcDoc={htmlMatch[1]} className="w-full border-0 rounded bg-white" style={{height: '300px'}} sandbox="allow-scripts" />
      </div>;
    }
    return <pre className="whitespace-pre-wrap font-sans text-sm">{text}</pre>;
  };

  return (
    <div style={{fontFamily: 'monospace', background: '#050505', minHeight: '100vh', color: '#00ff88', display: 'flex', flexDirection: 'column' }}>

      <div style={{padding: '8px 16px 4px', opacity: 0.6, fontSize: '11px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #1a1a1a'}}>
        <span>🧢</span><span>IA Chat V7 Ultra</span>
        <button onClick={() => setShowModels(s => !s)} style={{marginLeft: 'auto', background: '#111111', border: '1px solid #333333', color: '#00ff88', padding: '2px 10px', borderRadius: '4px', cursor: 'pointer', fontSize: '10px'}}>
          {MODELS.find(m => m.id === model)?.n || model.split('/').pop()} ⁢
        </button>
      </div>

      {showModels && (
        <div style={{padding: '8px 16px', display: 'flex', gap: '6px', flexWrap: 'wrap', background: '#0a0a0a', borderBottom: '1px solid #111111'}}>
          {MODELS.map(m => (
            <button key={m.id} onClick={() => { setModel(m.id); setShowModels(false); }}
              style={{background: model === m.id ? '#00ff8822' : '#111', border: `1px solid ${model === m.id ? '#00ff88' : '#333'}`, color: '#eee', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '10px',-webkitUserSelect:'none'}}>
              {m.n}
            </button>
          ))}
        </div>
      )}

      {skills.length > 0 && (
        <div style={{padding: '6px 8px', display: 'flex', gap: '4px', overflowX: 'auto', borderBottom: '1px solid #111111'}}>
          {skills.map(s => (
            <span key={s.id} style={{padding: '2px 8px', background: '#0a0a0a', border: '1px solid #222', borderRadius: '10px', fontSize: '9px', color: '#666', whiteSpace: 'nowrap', cursor: 'default'}}>
              {s.name} • {s.score}
            </span>
          ))}
        </div>
      )}

      <div style={{flex: 1, overflowY: 'auto', padding: '12px 16px'}}>
        {msgs.length === 0 && (
          <div style={{textAlign: 'center', opacity: 0.3, marginTop: '40px', lineHeight: 2}}>
            <div style={{fontSize: '32px'}}>🧢</div>
            <div>IP Chat V7 Ultra</div>
            <div style={{fontSize: '11px', marginTop: '8px'}}>Groq ⦜️ Gemini <span style={{color: '#4285f4'}}>👢</span> · Together.ai 128k</div>
            <div style={{fontSize: '11px'}}>Skills eternas * Memória pgvector * Artefatos HTML</div>
          </div>
        )}
        {msgs.map((msg, i) => (
          <div key={i} style={{marginBottom: '12px', display: 'flex', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row', gap: '8px'}}>
            <div style={{maxWidth: '85%', padding: '8px 12px', borderRadius: '8px', background: msg.role === 'user' ? '#031a0b' : '#0a0a0a', border: '1px solid ' + (msg.role === 'user' ? '#00ff8828' : '#161616'), fontSize: '12px', lineHeight: 1.7}}>
              {msg.img && <img src={msg.img} style={{maxHeight: '150px', maxWidth: '100%', borderRadius: '4px', marginBottom: '6px', display: 'block'}} alt="Upload" />}
              {renderContent(msg.content)}
              {msg.provider && <span style={{fontSize: '9px', opacity: 0.4, display: 'block', marginTop: '4px'}}>{msg.provider} ({msg.kid}) {msg.ms}ms</span>}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{display: 'flex', gap: '4px', alignItems: 'center'}}>
            {[0,1,2].map(i => <span key={i} style={{width: '6px', height: '6px', background: '#00ff88', borderRadius: '50%', animation: `ciaD 0.8s ${i*0.2}s infinite`}} />)}
          </div>
        )}
        <div id="end" ref={msgEndRef} />
      </div>

      <div style={{padding: '8px 12px', borderTop: '1px solid #111111', display: 'flex', gap: '8px', alignItems: 'flex-end'}}>
        {imgB64 && <img src={data:${imgMime};base64,${imgB64}} style={{height: '40px', width: '40px', objectFit: 'cover', borderRadius: '4px'}} alt="" />}
        <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} style={{display: 'none'}} />
        <button onClick={() => fileRef.current?.click()} style={{background: 'none', border: '1px solid #222', color: '#444', padding: '6px' , borderRadius: '6px', cursor: 'pointer', fontSize: '14px'}}>
          👂
        </button>
        <textarea value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
          placeholder="Mensagem... (Shift+Enter para quebra)"
          style={{flex: 1, background: '#0a0a0a', border: '1px solid #222', color: '#eee', padding: '8px 8px', borderRadius: '6px', resize: 'none', fontSize: '12px', minHeight: '38px', maxHeight: '100px', fontFamily: 'monospace'}}
          rows={1}
        