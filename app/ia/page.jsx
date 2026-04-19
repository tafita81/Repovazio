'use client'
import{useState,useEffect,useRef,useCallback}from'react'
const SI=30000
const WA=8*60*1000
export default function P(){
const[aba,sA]=useState('executor')
const[msgs,sM]=useState([{role:'model',text:'Executor IA ativo. Analiso metricas, crio rotas, faco deploy. O que executar?'}])
const[input,sI]=useState('')
const[load,sL]=useState(false)
const[status,sSt]=useState(null)
const[waSt,sW]=useState(null)
const[plano,sP]=useState([])
const[log,sLg]=useState([])
const[wa,sWa]=useState(0)
const ref=useRef(null)
const addLog=useCallback((m)=>{const h=new Date().toLocaleTimeString('pt-BR',{timeZone:'America/Sao_Paulo'});sLg(p=>[{h,m},...p].slice(0,50))},[])
const fetchSt=useCallback(async()=>{try{const d=await fetch('/api/cerebro/status').then(r=>r.json());sSt(d)}catch{}},[])
const fetchState=useCallback(async()=>{try{const d=await fetch('/api/state').then(r=>r.json());if(d.plano)sP(d.plano);if(typeof d.membros_wa==='number')sWa(d.membros_wa)}catch{}},[])
const chkWA=useCallback(async()=>{try{const d=await fetch('/api/whatsapp').then(r=>r.json());if(d.status==='ok'&&d.mensagem){addLog('WA: '+d.mensagem.slice(0,50));sW(d)}}catch{}},[addLog])
useEffect(()=>{fetchSt();fetchState();const s=setInterval(fetchSt,SI);const w=setInterval(chkWA,WA);return()=>{clearInterval(s);clearInterval(w)}},[fetchSt,fetchState,chkWA])
useEffect(()=>{if(ref.current)ref.current.scrollTop=ref.current.scrollHeight},[msgs])
const send=async()=>{
if(!input.trim()||load)return
const q=input.trim();sI('');sM(p=>[...p,{role:'user',text:q}]);sL(true)
try{const d=await fetch('/api/assistente',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pergunta:q,historico:msgs.slice(-8)})}).then(r=>r.json());sM(p=>[...p,{role:'model',text:d.resposta||d.erro||'Sem resposta',model:d.model,exec:d.execResult}]);if(d.execResult)addLog('Exec: '+d.execResult.slice(0,60))}catch(e){sM(p=>[...p,{role:'model',text:'Erro: '+e.message}])}finally{sL(false)}
}
const S={background:'#080810',color:'#e0e0f0',minHeight:'100vh',fontFamily:'Inter,sans-serif',display:'flex',flexDirection:'column'}
const bA=(a)=>({padding:'8px 16px',borderRadius:8,border:'none',cursor:'pointer',fontWeight:600,fontSize:12,background:aba===a?'#7c3aed':'#111',color:aba===a?'#fff':'#555'})
const card={background:'#0f0f1a',border:'1px solid #1a1a2e',borderRadius:12,padding:16,marginBottom:12}
const met={background:'#080810',borderRadius:8,padding:'10px 12px',border:'1px solid #151530',textAlign:'center'}
return(
<div style={S}>
<div style={{background:'#0d0d1a',borderBottom:'1px solid #1a1a2e',padding:'12px 20px',display:'flex',alignItems:'center',justifyContent:'space-between',flexWrap:'wrap',gap:10}}>
<span style={{fontSize:16,fontWeight:700,color:'#7c3aed'}}>psicologia.doc v7</span>
<div style={{display:'flex',gap:8}}>
<span style={{fontSize:11,color:'#4ade80',background:'#051a0d',padding:'2px 8px',borderRadius:20}}>ATIVO</span>
<span style={{fontSize:11,color:'#7c3aed',background:'#150a2e',padding:'2px 8px',borderRadius:20}}>Groq-Gemini-GPT4o</span>
</div>
</div>
<div style={{background:'#0a0a16',borderBottom:'1px solid #141428',padding:'6px 20px',display:'flex',gap:20,flexWrap:'wrap',fontSize:11,color:'#444'}}>
<span>Score: <b style={{color:'#4ade80'}}>{status&&status.score_medio||'-'}</b></span>
<span>WA: <b style={{color:'#06b6d4'}}>{wa}/1024</b></span>
<span>Dia: <b style={{color:'#f59e0b'}}>{status&&status.dia_atual||1}</b></span>
<span>Daniela: <b style={{color:'#a78bfa'}}>Dia 261</b></span>
<span>Roteiros: <b style={{color:'#555'}}>{status&&status.total_producoes||0}</b></span>
</div>
<div style={{padding:'10px 20px 0',display:'flex',gap:6,borderBottom:'1px solid #111',flexWrap:'wrap'}}>
{[['executor','Executor IA'],['status','Status'],['whatsapp','WhatsApp'],['plano','Plano'],['log','Log']].map(([a,l])=>(
<button key={a} style={bA(a)} onClick={()=>sA(a)}>{l}</button>
))}
</div>
<div style={{flex:1,overflow:'auto',padding:20}}>
{aba==='executor'&&(
<div style={{display:'flex',flexDirection:'column',height:'70vh'}}>
<div style={{fontSize:12,color:'#333',marginBottom:8}}>Pode pedir: analise metricas, faca deploy, otimize codigo, estrategia de crescimento</div>
<div ref={ref} style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:8,paddingBottom:8}}>
{msgs.map((m,i)=>(
<div key={i} style={{display:'flex',justifyContent:m.role==='user'?'flex-end':'flex-start'}}>
<div style={{maxWidth:'85%',background:m.role==='user'?'#2a0d6e':'#0f0f1e',border:'1px solid '+(m.role==='user'?'#4a1da4':'#1a1a2e'),borderRadius:10,padding:'8px 12px'}}>
<div style={{fontSize:13,lineHeight:1.6,whiteSpace:'pre-wrap'}}>{m.text}</div>
{m.model&&<div style={{fontSize:10,color:'#333',marginTop:3}}>{m.model}</div>}
{m.exec&&<div style={{fontSize:11,color:'#4ade80',marginTop:4,background:'#030f03',padding:'3px 6px',borderRadius:4}}>{m.exec}</div>}
</div>
</div>
))}
{load&&<div style={{color:'#444',fontSize:12,textAlign:'center'}}>processando...</div>}
</div>
<div style={{display:'flex',gap:8,paddingTop:8,borderTop:'1px solid #111'}}>
<input value={input} onChange={e=>sI(e.target.value)} onKeyDown={e=>e.key==='Enter'&&!e.shiftKey&&send()}
placeholder="analise roteiros, faca deploy, crie rota, estrategia..."
style={{flex:1,background:'#0f0f1a',border:'1px solid #1a1a2e',borderRadius:8,padding:'8px 12px',color:'#e0e0f0',fontSize:13,outline:'none'}}/>
<button onClick={send} disabled={load} style={{background:load?'#2a1a4e':'#7c3aed',border:'none',borderRadius:8,padding:'8px 18px',color:'#fff',cursor:load?'not-allowed':'pointer',fontWeight:700}}>{load?'...':'Enviar'}</button>
</div>
</div>
)}
{aba==='status'&&(
<div>
<div style={card}>
<div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(120px,1fr))',gap:8}}>
{[['Roteiros',status&&status.total_producoes],['Score',status&&status.score_medio],['Memoria',status&&status.topicos_em_memoria],['WA',wa+'/1024']].map(([k,v])=>(
<div key={k} style={met}><div style={{fontSize:10,color:'#444',marginBottom:3}}>{k}</div><div style={{fontSize:20,fontWeight:700,color:'#7c3aed'}}>{v!=null?v:'-'}</div></div>
))}
</div>
</div>
{status&&status.ultimas_producoes&&status.ultimas_producoes.length>0&&(
<div style={card}>
<div style={{fontSize:12,color:'#555',marginBottom:8}}>Ultimas producoes</div>
{status.ultimas_producoes.map((p,i)=>(
<div key={i} style={{display:'flex',justifyContent:'space-between',padding:'5px 0',borderBottom:'1px solid #111',fontSize:12}}>
<span style={{color:'#bbb'}}>{p.topic}</span>
<span style={{color:p.score>=90?'#4ade80':p.score>=80?'#f59e0b':'#f87171',fontSize:11}}>{p.score}pts</span>
</div>
))}
</div>
)}
</div>
)}
{aba==='whatsapp'&&(
<div>
<div style={card}>
<div style={{fontSize:13,color:'#555',marginBottom:10}}>Agente WhatsApp Autonomo</div>
<div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10,marginBottom:12}}>
<div style={met}><div style={{fontSize:10,color:'#444'}}>Membros</div><div style={{fontSize:22,fontWeight:700,color:'#06b6d4'}}>{wa}/1024</div></div>
<div style={met}><div style={{fontSize:10,color:'#444'}}>Revelacao</div><div style={{fontSize:14,fontWeight:700,color:'#f59e0b'}}>Dia 261</div></div>
</div>
<div style={{fontSize:12,color:'#444',lineHeight:1.9}}>
<div>Agente ativo — mensagens humanizadas, delay 2-45min (8h-22h SP)</div>
<div>Persona: membro anonimo 28-35 anos, nunca revela que e IA</div>
<div>Le e responde mensagens com angustia ou tristeza</div>
<div>Meta: 1.024 membros — viram clientes da Daniela em dez/2026</div>
</div>
{waSt&&<div style={{marginTop:12,background:'#030f03',borderRadius:6,padding:10,fontSize:12}}>
<div style={{color:'#4ade80',marginBottom:3}}>Ultima mensagem:</div>
<div style={{color:'#ccc'}}>{waSt.mensagem}</div>
</div>}
</div>
<div style={card}>
<div style={{fontSize:12,color:'#555',marginBottom:8}}>Configurar envio real</div>
<div style={{fontSize:11,color:'#333',lineHeight:1.9}}>
<div>1. Meta Business - WhatsApp Business API</div>
<div>2. Vercel env vars: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, WHATSAPP_GROUP_ID</div>
<div>3. Webhook: repovazio.vercel.app/api/whatsapp</div>
<div>4. Token: psicologiadoc_webhook</div>
</div>
</div>
</div>
)}
{aba==='plano'&&(
<div style={card}>
<div style={{fontSize:13,color:'#555',marginBottom:12}}>Planejamento — Daniela Coelho 31/dez/2026</div>
{plano.length===0&&<div style={{fontSize:12,color:'#333'}}>Carregando...</div>}
{plano.map((p,i)=>(
<div key={i} style={{display:'flex',gap:12,padding:'8px 0',borderBottom:'1px solid #111',alignItems:'flex-start'}}>
<div style={{fontSize:16,fontWeight:700,color:p.executado?'#4ade80':'#333',minWidth:44,textAlign:'center'}}>
{p.executado?'OK':'O'}<div style={{fontSize:10,color:'#333',fontWeight:400}}>Dia {p.dia}</div>
</div>
<div>
<div style={{fontSize:11,color:p.fase==='revelacao'?'#f59e0b':'#7c3aed',fontWeight:600,marginBottom:1}}>{p.fase}</div>
<div style={{fontSize:12,color:'#bbb'}}>{p.acao}</div>
</div>
</div>
))}
</div>
)}
{aba==='log'&&(
<div style={card}>
<div style={{fontSize:12,color:'#555',marginBottom:8}}>Log automatico</div>
{log.length===0&&<div style={{fontSize:12,color:'#222'}}>Aguardando eventos...</div>}
{log.map((l,i)=>(
<div key={i} style={{fontSize:11,padding:'3px 0',borderBottom:'1px solid #0a0a0a',display:'flex',gap:8}}>
<span style={{color:'#333',flexShrink:0,fontFamily:'monospace'}}>{l.h}</span>
<span style={{color:'#888'}}>{l.m}</span>
</div>
))}
</div>
)}
</div>
</div>
)
}