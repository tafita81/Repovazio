'use client';
import { useState, useRef, useEffect, useCallback } from 'react';

// Ã¢ÂÂÃ¢ÂÂ ARTIFACT RENDERER Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
function ArtifactRenderer({ html }) {
  const iframeRef = useRef(null);
  const [height, setHeight] = useState(300);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    const doc = iframe.contentDocument;
    doc.open();
    doc.write(`<!DOCTYPE html><html><head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; background: #fff; color: #111; padding: 12px; }
      </style>
    </head><body>${html}</body></html>`);
    doc.close();
    const resize = () => {
      try { setHeight(Math.min(doc.body.scrollHeight + 24, expanded ? 800 : 400)); } catch { }
    };
    iframe.onload = resize;
    setTimeout(resize, 100);
  }, [html, expanded]);

  return (
    <div style={{ border: '1px solid #00ff8833', borderRadius: 8, overflow: 'hidden', margin: '8px 0', background: '#050505' }}>
      <div style={{ display: 'flex', alignItems: 'center', padding: '6px 12px', background: '#0a1a0a', borderBottom: '1px solid #00ff8822', fontSize: 10, fontFamily: 'monospace', color: '#00ff88', gap: 8 }}>
        <span>Ã¢Â¬Â¡</span><span style={{ flex: 1 }}>ARTEFATO</span>
        <button onClick={() => setExpanded(e => !e)} style={{ background: 'transparent', border: '1px solid #00ff8833', color: '#00ff88', padding: '2px 8px', borderRadius: 3, cursor: 'pointer', fontSize: 9 }}>
          {expanded ? 'Ã¢ÂÂ compactar' : 'Ã¢ÂÂ expandir'}
        </button>
      </div>
      <iframe ref={iframeRef} style={{ width: '100%', height, border: 'none', display: 'block', background: '#fff' }} sandbox="allow-scripts allow-same-origin" title="artefato" />
    </div>
  );
}

// Ã¢ÂÂÃ¢ÂÂ MARKDOWN RENDERER Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
function MsgContent({ text }) {
  const parts = [];
  const artifactRe = /<ARTIFACT[^>]*type="html"[^>]*>([\s\S]*?)<\/ARTIFACT>/gi;
  let last = 0, m;
  while ((m = artifactRe.exec(text)) !== null) {
    if (m.index > last) parts.push({ type: 'text', content: text.slice(last, m.index) });
    parts.push({ type: 'artifact', content: m[1].trim() });
    last = m.index + m[0].length;
  }
  if (last < text.length) parts.push({ type: 'text', content: text.slice(last) });

  function renderText(t) {
    return t
      .replace(/```([\w]*)\n([\s\S]*?)```/g, '<pre style="background:#000;border:1px solid #1e1e1e;border-radius:6px;padding:12px;margin:8px 0;overflow-x:auto;font-family:monospace;font-size:11px;white-space:pre-wrap;word-break:break-word;line-height:1.6">$2</pre>')
      .replace(/`([^`]+)`/g, '<code style="background:#1a1a1a;padding:2px 5px;border-radius:3px;font-family:monospace;font-size:11px;color:#00ff88">$1</code>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em style="color:#aaa">$1</em>')
      .replace(/^#{3}\s+(.+)$/gm, '<div style="font-size:14px;font-weight:700;color:#e0e0e0;margin:10px 0 4px">$1</div>')
      .replace(/^#{2}\s+(.+)$/gm, '<div style="font-size:15px;font-weight:700;color:#e0e0e0;margin:12px 0 6px">$1</div>')
      .replace(/^#{1}\s+(.+)$/gm, '<div style="font-size:16px;font-weight:700;color:#00ff88;margin:12px 0 6px">$1</div>')
      .replace(/^[-Ã¢ÂÂ¢]\s+(.+)$/gm, '<div style="padding-left:16px;margin:2px 0">Ã¢ÂÂ¢ $1</div>')
      .replace(/^\d+\.\s+(.+)$/gm, '<div style="padding-left:16px;margin:2px 0">$1</div>')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" style="color:#5599ff;text-decoration:underline">$1</a>')
      .replace(/\n/g, '<br>');
  }

  return (
    <div>
      {parts.map((p, i) =>
        p.type === 'artifact'
          ? <ArtifactRenderer key={i} html={p.content} />
          : <div key={i} dangerouslySetInnerHTML={{ __html: renderText(p.content) }} />
      )}
    </div>
  );
}

// Ã¢ÂÂÃ¢ÂÂ IMAGE UPLOAD Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
function ImageUpload({ onImage, onClear, image }) {
  const fileRef = useRef(null);
  const handleFile = (e) => {
    const files=Array.from(e.target.files||[]);
    files.forEach(file=>{
      if(!file)return;
      const reader=new FileReader();
      if(file.type.startsWith('image/')){
        reader.onload=(ev)=>{const b64=ev.target.result.split(',')[1];onImage({b64,mime:file.type,name:file.name,size:file.size,isFile:false});};
        reader.readAsDataURL(file);
      }else{
        reader.onload=(ev)=>{onImage({text:ev.target.result,mime:file.type,name:file.name,size:file.size,isFile:true});};
        reader.readAsText(file);
      }
    });
  };
  const handlePaste = useCallback((e) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of items) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        const reader = new FileReader();
        reader.onload = (ev) => {
          const b64 = ev.target.result.split(',')[1];
          onImage({ b64, mime: item.type, name: 'clipboard.png', size: file.size });
        };
        reader.readAsDataURL(file);
      }
    }
  }, [onImage]);

  useEffect(() => {
    document.addEventListener('paste', handlePaste);
    return () => document.removeEventListener('paste', handlePaste);
  }, [handlePaste]);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <button onClick={() => fileRef.current?.click()} title="Clique para enviar foto, PDF, TXT, codigo... ou cole imagem com Ctrl+V"
        style={{ minWidth: 48, height: 48, background: image ? '#00ff8820' : '#111', border: `2px solid ${image ? '#00ff88' : '#333'}`, borderRadius: 10, cursor: 'pointer', fontSize: 20, color: image ? '#00ff88' : '#666', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4, padding: '0 8px', transition:'all .15s', flexDirection:'column', lineHeight:1 }}>
        Ã°ÂÂÂ
      </button>
      {image && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, background: '#00ff8815', border: '1px solid #00ff8833', borderRadius: 4, padding: '2px 6px', fontSize: 9, color: '#00ff88', fontFamily: 'monospace' }}>
          <span>Ã°ÂÂÂ¼ {image.name.substring(0, 15)}</span>
          <button onClick={onClear} style={{ background: 'none', border: 'none', color: '#ff3355', cursor: 'pointer', fontSize: 10 }}>Ã¢ÂÂ</button>
        </div>
      )}
      <input ref={fileRef} type="file" accept="image/*,application/pdf,text/plain,text/markdown,application/json,.js,.jsx,.ts,.tsx,.csv,.py,.html,.css,.md" multiple onChange={handleFile} style={{ display: 'none' }} />
    </div>
  );
}

// Ã¢ÂÂÃ¢ÂÂ MAIN CHAT COMPONENT Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
export default function ChatIA({ sessionId }) {
  const [msgs, setMsgs] = useState([]);
  const [inp, setInp] = useState('');
  const [busy, setBusy] = useState(false);
  const [modelo, setModelo] = useState('llama-3.3-70b-versatile');
  const [info, setInfo] = useState(null);
  const [stats, setStats] = useState({ n: 0, tok: 0 });
  const [image, setImage] = useState(null);
  const [sid] = useState(sessionId || `s${Date.now()}`);
  const chatRef = useRef(null);
  const inpRef = useRef(null);

  useEffect(() => {
    fetch('/api/ia-chat').then(r => r.json()).then(setInfo).catch(() => {});
    inpRef.current?.focus();
  }, []);

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
  }, [msgs, busy]);

  const hist = msgs.filter(m => !['e'].includes(m.r)).map(m => ({
    role: m.r === 'u' ? 'user' : 'assistant', content: m.c
  }));

  async function send() {
    if (!inp.trim() || busy) return;
    const msg = inp.trim();
    const img = image;
    setInp(''); setImage(null); setBusy(true);
    setMsgs(p => [...p, { r: 'u', c: msg, id: Date.now(), img: img?.b64 ? `data:${img.mime};base64,${img.b64}` : null }]);

    try {
      const body = {
        mensagem: msg,
        historico: hist.slice(-15),
        modelo,
        max_tokens: 4096,
        session_id: sid,
        usar_memoria: true
      };
      if (img?.b64) { body.imagem_base64 = img.b64; body.imagem_mime = img.mime; }

      const r = await fetch('/api/ia-chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      });
      const d = await r.json();
      if (d.resposta) {
        setMsgs(p => [...p, {
          r: 'a', c: d.resposta, id: Date.now(),
          m: { k: d.kid, ms: d.ms, tok: d.uso?.total_tokens, tools: d.tools_usadas, prov: d.provider, img: d.tem_imagem }
        }]);
        setStats(s => ({ n: s.n + 1, tok: s.tok + (d.uso?.total_tokens || 0) }));
      } else {
        setMsgs(p => [...p, { r: 'e', c: d.erro || 'Erro desconhecido', id: Date.now() }]);
      }
    } catch (e) {
      setMsgs(p => [...p, { r: 'e', c: 'Falha: ' + e.message, id: Date.now() }]);
    } finally { setBusy(false); inpRef.current?.focus(); }
  }

  const provColor = { groq: '#00ff88', gemini: '#4285f4', together: '#ff6600', github: '#888', cache: '#ffaa22' };
  const MODELS = [
    { v: 'llama-3.3-70b-versatile', l: 'Ã°ÂÂ¦Â Llama 3.3 70B' },
    { v: 'llama-3.1-8b-instant', l: 'Ã¢ÂÂ¡ Llama 3.1 8B' },
    { v: 'mixtral-8x7b-32768', l: 'Ã°ÂÂÂ Mixtral 8ÃÂ7B' },
    { v: 'gemma2-9b-it', l: 'Ã°ÂÂÂ Gemma 2 9B' }
  ];
  const SUGS = [
    'status do sistema', 'ver commits recentes', 'listar tabelas Supabase',
    'status YouTube e redes', 'listar arquivos em app/api', 'criar uma pÃÂ¡gina de teste HTML'
  ];

  const connectors = info?.connectors || {};
  const hasNotion = connectors.notion;
  const hasSlack = connectors.slack;
  const hasDrive = connectors.drive;
  const hasBrowser = connectors.browser;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 600, background: '#080808', borderRadius: 10, overflow: 'hidden', border: '1px solid #1a1a1a' }}>

      {/* Status bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '7px 14px', background: '#0e0e0e', borderBottom: '1px solid #1a1a1a', fontSize: 10, fontFamily: 'monospace', color: '#555', flexWrap: 'wrap' }}>
        <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#00ff88', boxShadow: '0 0 5px #00ff88', flexShrink: 0 }} />
        {info ? (
          <>
            <span style={{ color: '#00ff88' }}>{info.providers?.groq?.keys || 0}ÃÂ Groq</span>
            {info.providers?.gemini?.ok && <span style={{ color: '#4285f4' }}>+ Gemini Vision</span>}
            {info.providers?.together?.ok && <span style={{ color: '#ff6600' }}>+ Together 128k</span>}
            <span style={{ color: '#333' }}>|</span>
            {hasNotion && <span style={{ color: '#666' }}>Notion</span>}
            {hasSlack && <span style={{ color: '#666' }}>Slack</span>}
            {hasDrive && <span style={{ color: '#666' }}>Drive</span>}
            {hasBrowser && <span style={{ color: '#666' }}>Browser</span>}
          </>
        ) : <span>carregando...</span>}
        <div style={{ marginLeft: 'auto' }}>
          <select value={modelo} onChange={e => setModelo(e.target.value)}
            style={{ background: '#111', border: '1px solid #222', color: '#888', padding: '2px 5px', borderRadius: 3, fontFamily: 'monospace', fontSize: 10, outline: 'none', cursor: 'pointer' }}>
            {MODELS.map(m => <option key={m.v} value={m.v}>{m.l}</option>)}
          </select>
        </div>
      </div>

      {/* Messages */}
      <div ref={chatRef} style={{ flex: 1, overflowY: 'auto', padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {msgs.length === 0 && (
          <div style={{ margin: 'auto', textAlign: 'center', maxWidth: 480, padding: 28 }}>
            <div style={{ fontSize: 32, marginBottom: 10, filter: 'drop-shadow(0 0 12px #00ff88)' }}>Ã°ÂÂ¤Â</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#00ff88', marginBottom: 6, fontFamily: 'monospace' }}>IA Chat V5 Ã¢ÂÂ Ultra</div>
            <div style={{ fontSize: 11, color: '#444', lineHeight: 1.8, marginBottom: 16 }}>
              VisÃÂ£o ÃÂ· Artefatos HTML ÃÂ· Contexto 128k ÃÂ· MemÃÂ³ria semÃÂ¢ntica<br />
              Notion ÃÂ· Slack ÃÂ· Drive ÃÂ· Browser ÃÂ· GitHub ÃÂ· Supabase
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, justifyContent: 'center' }}>
              {SUGS.map(s => (
                <button key={s} onClick={() => { setInp(s); inpRef.current?.focus(); }}
                  style={{ background: 'transparent', border: '1px solid #1a1a1a', color: '#444', padding: '4px 8px', borderRadius: 4, cursor: 'pointer', fontFamily: 'monospace', fontSize: 9, transition: 'all .15s' }}
                  onMouseOver={e => { e.target.style.borderColor = '#00ff88'; e.target.style.color = '#00ff88'; }}
                  onMouseOut={e => { e.target.style.borderColor = '#1a1a1a'; e.target.style.color = '#444'; }}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {msgs.map(m => (
          <div key={m.id} style={{ maxWidth: '90%', display: 'flex', flexDirection: 'column', alignSelf: m.r === 'u' ? 'flex-end' : 'flex-start' }}>
            {/* Imagem anexada */}
            {m.img && (
              <div style={{ alignSelf: 'flex-end', marginBottom: 4 }}>
                <img src={m.img} alt="anexo" style={{ maxWidth: 200, maxHeight: 150, borderRadius: 6, border: '1px solid #333', objectFit: 'cover' }} />
              </div>
            )}
            <div style={{
              padding: '10px 14px',
              borderRadius: m.r === 'u' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
              fontSize: 13, lineHeight: 1.65, wordBreak: 'break-word',
              background: m.r === 'u' ? '#4c35d4' : m.r === 'e' ? '#150808' : '#111',
              color: m.r === 'u' ? '#fff' : m.r === 'e' ? '#ff3355' : '#ddd',
              border: m.r === 'a' ? '1px solid #1e1e1e' : m.r === 'e' ? '1px solid #ff3355' : 'none',
              borderLeft: m.r === 'a' ? '2px solid #00ff88' : undefined
            }}>
              {m.r === 'u' ? <div dangerouslySetInnerHTML={{ __html: m.c.replace(/\n/g, '<br>') }} /> : <MsgContent text={m.c} />}
            </div>
            {m.m && (
              <div style={{ fontFamily: 'monospace', fontSize: 9, color: '#2a2a2a', marginTop: 3, padding: '0 3px', display: 'flex', gap: 5, flexWrap: 'wrap', justifyContent: m.r === 'u' ? 'flex-end' : 'flex-start' }}>
                {m.m.k && <span style={{ background: `${provColor[m.m.prov] || '#888'}15`, color: provColor[m.m.prov] || '#888', border: `1px solid ${provColor[m.m.prov] || '#888'}25`, padding: '1px 5px', borderRadius: 3 }}>
                  {m.m.img ? 'Ã°ÂÂÂ ' : ''}{m.m.k}
                  </span>}
                {m.m.ms && <span>{m.m.ms}ms</span>}
                {m.m.tok && <span>{m.m.tok}tok</span>}
                {m.m.tools?.length > 0 && <span style={{ color: '#4488ff' }}>Ã°ÂÂÂ§ {m.m.tools.join(', ')}</span>}
              </div>
            )}
          </div>
        ))}

        {busy && (
          <div style={{ alignSelf: 'flex-start', padding: '12px 16px', borderRadius: '14px 14px 14px 2px', background: '#111', border: '1px solid #1e1e1e', borderLeft: '2px solid #00ff88', display: 'flex', gap: 4, alignItems: 'center' }}>
            {[0, 200, 400].map(d => <span key={d} style={{ width: 5, height: 5, borderRadius: '50%', background: '#00ff88', animation: `ciaD 1.2s ${d}ms ease-in-out infinite` }} />)}
          </div>
        )}
      </div>

      {/* Stats */}
      {stats.n > 0 && (
        <div style={{ padding: '3px 14px', fontFamily: 'monospace', fontSize: 9, color: '#1e1e1e', borderTop: '1px solid #0e0e0e', background: '#0a0a0a' }}>
          {stats.n} msgs ÃÂ· {stats.tok.toLocaleString('pt-BR')} tokens ÃÂ· sessÃÂ£o: {sid.substring(0, 14)}
        </div>
      )}

      {/* Input */}
      <div style={{ borderTop: '1px solid #1a1a1a', padding: '10px 12px', background: '#0e0e0e' }}>
        <div style={{ display: 'flex', gap: 7, alignItems: 'flex-end' }}>
          <ImageUpload onImage={setImage} onClear={() => setImage(null)} image={image} />
          <textarea ref={inpRef} value={inp}
            onChange={e => { setInp(e.target.value); e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'; }}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
            placeholder="Escreva... Cole imagem com Ctrl+V ÃÂ· Enter = enviar ÃÂ· Shift+Enter = linha"
            disabled={busy}
            style={{ flex: 1, background: '#111', border: '1px solid #1e1e1e', color: '#e0e0e0', padding: '9px 12px', borderRadius: 8, fontFamily: 'inherit', fontSize: 13, resize: 'none', outline: 'none', minHeight: 40, maxHeight: 150, lineHeight: 1.5, transition: 'border-color .15s' }}
            rows={1}
            onFocus={e => { e.target.style.borderColor = '#00ff88'; }}
            onBlur={e => { e.target.style.borderColor = '#1e1e1e'; }}
          />
          <button onClick={send} disabled={busy || !inp.trim()}
            style={{ width: 40, height: 40, background: busy || !inp.trim() ? '#1a1a1a' : '#00ff88', border: 'none', borderRadius: 8, cursor: busy || !inp.trim() ? 'not-allowed' : 'pointer', fontSize: 17, fontWeight: 700, color: busy || !inp.trim() ? '#333' : '#000', flexShrink: 0 }}>
            {busy ? 'Ã¢ÂÂ³' : 'Ã¢ÂÂ'}
          </button>
        </div>
      </div>

      <style>{`@keyframes ciaD{0%,100%{opacity:.2;transform:scale(.8)}50%{opacity:1;transform:scale(1)}}`}</style>
    </div>
  );
}
