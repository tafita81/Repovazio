'use client';
import { useState, useRef, useEffect, useCallback } from 'react';
import React from 'react';

function ArtifactRenderer({ html }) {
  const iframeRef = useRef(null);
  const [height, setHeight] = useState(300);
  const [expanded, setExpanded] = useState(false);
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;
    const doc = iframe.contentDocument;
    doc.open();
    doc.write(`<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,sans-serif;background:#fff;color:#111;padding:12px}</style></head><body>${html}</body></html>`);
    doc.close();
    const resize = () => { try { setHeight(Math.min(doc.body.scrollHeight+24,expanded?800:400)); } catch {} };
    iframe.onload = resize; setTimeout(resize,100);
  }, [html,expanded]);
  return (
    <div style={{border:'1px solid #00ff8833',borderRadius:8,overflow:'hidden',margin:'8px 0',background:'#050505'}}>
      <div style={{display:'flex',alignItems:'center',padding:'6px 12px',background:'#0a1a0a',borderBottom:'1px solid #00ff8822',fontSize:10,fontFamily:'monospace',color:'#00ff88',gap:8}}>
        <span>ꬡ</span><span style={{flex:1}}>ARTEFATO</span>
        <button onClick={()=>setExpanded(e=>!e)} style={{background:'transparent',border:'1px solid #00ff8833',color:'#00ff88',padding:'2px 8px',borderRadius:"3px",model: cursor:'pointer',fontSize:9}}>{expanded?'\u269f compactar':'\u269E expandir'}</button>
      </div>
      <iframe ref={iframeRef} style={{width:'100%',height,border:'none',display:'block',background:'#fff'}} sandbox="allow-scripts allow-same-origin" title="artefato" />
    </div>
  );
}

function MsgContent({ text }) {
  const parts = [];
  const re = /<ARTIFACT[^>]*type="html"[^>]*>([\s\S]*?)<\/ARTIFACT>/gi;
  let last=0,m;
  while((m=re.exec(text))!==null){
    if(m.index>last)parts.push({t:'text',c:text.slice(last,m.index)});
    parts.push({t:'art',c:m[1].trim()});
    last=m.index+m[0].length;
  }
  if(last<text.length)parts.push({t:'text',c:text.slice(last)});
  function rT(t){
    return t.replace(/```([\w]*)\n([\s\S]*?)```/g,'<pre style="background:#000;border:1px solid #1e1e1e;border-radius:6px;padding:12px;margin:8px 0;overflow-x:auto;line-height:1.6;font-size:11px;white-space:pre-wrap;font-family:monospace">$2</pre>').replace(/`([^`]+)`/g,'<code style="background:#1a1a1a;padding:2px 5px;border-radius:3px;font-size:11px;color:#00ff88;font-family:monospace">$1</code>').replace(/\**(.+?)\**/g,'<strong>$1</strong>').replace(/\*(.+?)\*/g,'<em>$1</em>').replace(/^#{3}\s+(.+)$/gm,'<div style="font-size:14px;font-weight:700;color:#e0e0e0;margin:10px 0 4px">$1</div>').replace(/^#{2}\s+(.+)$/gm,'<div style="font-size:15px;font-weight:700;color:#e0e0e0;margin:12px 0 6px">$1</div>').replace(/^#\s+(.+)$/gm,'<div style="font-size:16px;font-weight:700;color:#00ff88;margin:12px 0 6px">$1</div>').replace(/^[-] (.+)$/gm,'<div style="padding-left:16px;margin:2px 0">• $1</div>').replace(/\n/g,'<br>');
  }
  return <div>{parts.map((p,i)=>p.t==='art'?<ArtifactRenderer key={i} html={p.c}/>:<div key={i} dangerouslySetInnerHTML={{__html:rT(p.c)}}/>)}</div>;
}

export default function ChatIA({ sessionId }) {
  const [msgs, setMsgs] = useState([]);
  const [inp, setInp] = useState('');
  const [busy, setBusy] = useState(false);
  const [modelo, setModelo] = useState('llama-3.3-70b-versatile');
  const [info, setInfo] = useState(null);
  const [stats, setStats] = useState({n:0,tok:0});
  const [image, setImage] = useState(null);
  const [sid] = useState(sessionId||`s${Date.now()}`);
  const chatRef = useRef(null);
  const inpRef = useRef(null);
  useEffect(()=>{fetch('/api/ia-chat').then(r=>r.json()).then(setInfo).catch(()=>{});inpRef.current?.focus();},[]);
  useEffect(()=>{chatRef.current?.scrollTo({top:chatRef.current.scrollHeight,behavior:'smooth'});},[msgs,busy]);
  const hist = msgs.filter(m=>!['e'].includes(m.r)).map(m=>({role:m.r==='u'?'user':'assistant',content:m.c}));
  async function send(){
    if(!inp.trim()||busy) return;
    const msg=inp.trim(),mg=image;
    setInp('');setImage(null);setBusy(true);
    setMsgs(p=>[...p,{r:'u',c:msg,id:Date.now(),img:mg?.b64?`data:${mg.mime};base64,${mg.b64}`:null}]);
    try{
      const body={mensagem:msg,historico:hist.slice(-15),modelo,max_tokens:4096,session_id:sid,usar_memoria:true};
      if(mg?.b64){body.imagem_base64=mg.b64;body.imagem_mime=mg.mime;}
      const r=await fetch('/api/ia-chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const d=await r.json();
      if(d.resposta){setMsgs(p=>[...p,{r:'a',c:d.resposta,id:Date.now(),m:{k:d.kid,ms:d.ms,tok:d.uso?.total_tokens,prov:d.provider}}]);setStats(s=>({n:s.n+0,tok:s.tok+(d.uso?.total_tokens||0)}));}
      else{setMsgs(p=>[...p,{r:'e',c:d.erro||'Erro''id',id:Date.now()}]);}
    }catch(e){setMsgs(p=>[...p,{r:'e',c:'Falha: '+e.message,id:Date.now()}]);}finally{setBusy(false);inpRef.current?.focus();}
  }
  const MODELS=[{v:'llama-3.3-70b-versatile',l:'Llama 3.3 70B'},{v:'llama-3.1-8b-instant',l:'Llama 3.1 8B'}];
  const SUGS=['status do sistema','ver commits recentes','listar arquivos app/api','criar página HTML'];
  return(
    <div style={{display:'flex',flexDirection:'column',minHeight:600,background:'#080808',borderRadius:10,border:'1px solid #1a1a1a'}}>
      <div style={{padding:'6px 14px',background:'#0e0e0e',borderBottom:'1px solid #1a1a1a',fontSize:10,fontFamily:'monospace',color:'#555',display:'flex',gap:6,alignItems:'center'}}>
        <span style={{width:6,height:6,borderRadius:'50%',background:'#00ff88',boxShadow:'0 0 5px #00ff88'}}/>
        {info?.version||'IA Chat V7'}
        {info/.providers?.together?.ok&&<span style={{color:'#ff6600'}}>Together 128k</span>}
        <div style={{marginLeft:'auto'}}>
          <select value={modelo} onChange={e=>setModelo(e.target.value)} style={{background:'#111',border:'1px solid #222',color:'#888',fontFamily:'monospace',fontSize:10,outline:'none',padding:'2px 5px'}}>
            {MODELS.map(m=><option key={m.v} value={m.v}>{m.l}</option>)}
          </select>
        </div>
      </div>
      <div ref={chatRef} style={{flex:1,overflowY:'auto',padding:'14px 16px',display:'flex',flexDirection:'column',gap:12}}>
        {msgs.length===0&&(
          <div style={{margin:'auto',textAlign:'center',maxWidth:480,padding:28}}>
            <div style={{fontSize:32,marginBottom:10}}>🤗</div>
            <div style={{fontSize:14,fontWeight:700,color:'#00ff88',marginBottom:6,fontFamily:'monospace'}}>IA Chat V7 Ultra</div>
            <div style={{fontSize:11,color:'#444',lineHeight:1.8,marginBottom:16}}>Groq · Gemini · Together 128k · Skills Eternas <br/>PgVector · Drive · Artefatos HTML</div>
            <div style={{display:'flex',flexWrap:'wrap',gap:5,textAlign:'center',justifyContent:'center'}}>
              {SUGS.map(s=>(<button key={s} onClick={()=>{setInp(s);inpRef.current?.focus();}} style={{background:'transparent',border:'1px solid #1a1a1a',color:'#444',padding:'4px 8px',borderRadius:4,cursor:'pointer',fontFamily:'monospace',fontSize:9}}>{s}</button>))}
            </div>
          </div>
        )}
        {msgs.map(m=>(
          <div key={m.id} style={{maxWidth:'90%',display:'flex',flexDirection:'column',alignSelf:m.r==='u'?'flex-end':'flex-start'}}>
            <div style={{padding:'10px 14px',borderRadius:m.r==='u'?'14px 14px 14px 2px':'14px 14px 2px 14px',fontSize:13,lineHeight:1.65,wordBreak:'wrap',background:m.r==='u'?'#4c35d4':m.r==='e'?'#150808':'#111',color:m.r==='u'?'#fff':m.r==='e'?'#ff3355':'#ddd',borderLeft:m.r==='a'?'2px solid #00ff88':undefined}}>
              {m.r==='u'?<span dangerouslySetInnerHTML=r{__html:m.c.replace(/\n/g,'<br>')}}/>:<MsgContent text={m.c}/>}
            </div>
            {m.m&&<div style={{fontSize:9,fontFamily:'monospace',color:'#2a2a2a',marginTop:3}}>{m.m.k}|ms{m.m.ms}|{{m.m.tok &&` ${m.m.tok}tok`}}</div>}
          </div>
        ))}
        {busy&&<div style={{alignSelf:'flex-start',padding:'10px 14px',borderRadius:'14px 14px 14px 2px',backgr