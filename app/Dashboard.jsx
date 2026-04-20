'use client';
import {useState,useEffect,useRef} from 'react';
export default function Dashboard(){
const[tab,sT]=useState('dashboard');
const[cb,sCb]=useState({});
const[st,sSt]=useState({});
const[pl,sPl]=useState([]);
const[rk,sRk]=useState([]);
const[lg,sLg]=useState([]);
const[cy,sCy]=useState(0);
const lr=useRef(null);
useEffect(()=>{
la();triggerCron();
const i1=setInterval(la,3000);
const i2=setInterval(triggerCron,60000);
return()=>{clearInterval(i1);clearInterval(i2)};
},[]);
async function triggerCron(){
try{const r=await fetch('/api/cron/auto');const d=await r.json();sCy(c=>c+1);
sLg(p=>[{t:new Date().toLocaleTimeString('pt-BR'),m:'CRON #'+(cy+1)+' '+JSON.stringify(d.acoes?.map(a=>a.nome+':'+a.status)||[]).slice(0,80)+' '+d.duracao_ms+'ms'},...p].slice(0,100));
}catch(e){sLg(p=>[{t:new Date().toLocaleTimeString('pt-BR'),m:'CRON erro: '+e.message},...p].slice(0,100))}}
async function la(){
const r=await Promise.allSettled([fetch('/api/cerebro/status').then(x=>x.json()),fetch('/api/state').then(x=>x.json()),fetch('/api/ranking').then(x=>x.json())]);
if(r[0].status==='fulfilled')sCb(r[0].value);
if(r[1].status==='fulfilled'){sSt(r[1].value);sPl((r[1].value.plano||[]).filter((p,i,a)=>a.findIndex(x=>x.dia===p.dia)===i).sort((a,b)=>a.dia-b.dia))}
if(r[2].status==='fulfilled')sRk(r[2].value.ranking||[])}
const tabs=[{id:'dashboard',l:'⊡Dashboard'},{id:'cerebro',l:'\u{1F9E0}Cérebro AO VIVO'},{id:'gerador',l:'\u2728Gerador Manual'},{id:'motor',l:'\u{1F501}Motor 1000x'},{id:'series',l:'\u{1F3AC}Séries Episódicas'},{id:'revelacao',l:'\u{1F389}Revelação 2027'},{id:'canais',l:'\u{1F4E1}Gestão de Canais'},{id:'whatsapp',l:'\u{1F4AC}WhatsApp Grupos'},{id:'ranking',l:'\u{1F30D}Ranking Mundial'},{id:'cases',l:'\u{1F4C8}Cases do Dia'},{id:'playlist',l:'\u{1F4CB}Playlist 630 dias'},{id:'conteudo',l:'\u{1F4C4}Conteúdo'},{id:'monetizacao',l:'\u{1F4B0}Monetização'},{id:'config',l:'\u2699\uFE0FConfigurações'},{id:'logs',l:'\u{1F4CB}Logs'}];
const bg='linear-gradient(135deg,#0a0118,#1a0b2e 50%,#2d1b4e)';
const pur='#7c3aed';const lpur='#a78bfa';const grn='#10b981';
const C=({children,...p})=><div style={{background:'rgba(0,0,0,0.4)',borderRadius:'1rem',padding:'1.5rem',border:'1px solid rgba(124,58,237,0.3)',marginBottom:'1rem',...(p.style||{})}}>{children}</div>;
const M=({label,value,sub,tag})=><div style={{background:'rgba(124,58,237,0.1)',borderRadius:'0.75rem',padding:'1.25rem',border:'1px solid rgba(124,58,237,0.3)'}}><div style={{fontSize:'0.75rem',color:lpur,marginBottom:'0.5rem',textTransform:'uppercase',letterSpacing:'0.1em',fontWeight:600}}>{label}{tag&&<span style={{display:'inline-block',padding:'0.2rem 0.6rem',background:'rgba(16,185,129,0.2)',color:grn,borderRadius:'0.3rem',fontSize:'0.7rem',fontWeight:700,marginLeft:'0.5rem'}}>{tag}</span>}</div><div style={{fontSize:'2.25rem',fontWeight:800,color:'#fff',lineHeight:1}}>{value}</div>{sub&&<div style={{fontSize:'0.8rem',color:lpur,marginTop:'0.5rem'}}>{sub}</div>}</div>;
const G=({children})=><div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))',gap:'1rem'}}>{children}</div>;
return(<div style={{minHeight:'100vh',background:bg,color:'#e0d4f7',fontFamily:'system-ui'}}>
<style>{'@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.2)}}'}</style>
<div style={{background:'rgba(0,0,0,0.5)',borderBottom:'2px solid rgba(124,58,237,0.5)',padding:'1rem',position:'sticky',top:0,zIndex:10}}>
<div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
<h1 style={{margin:0,fontSize:'1.5rem',fontWeight:800,background:'linear-gradient(90deg,'+lpur+','+pur+')',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}><span style={{display:'inline-block',width:'0.6rem',height:'0.6rem',background:grn,borderRadius:'50%',marginRight:'0.5rem',animation:'pulse 1.5s infinite'}}/>psicologia.doc — Sistema Autônomo v7</h1>
<div style={{display:'flex',gap:'1rem',alignItems:'center',fontSize:'0.85rem'}}><span style={{color:grn}}>Ciclos: {cy}</span><span style={{color:lpur}}>Dia {st.dia_atual||'—'}</span></div>
</div></div>
<div style={{background:'rgba(0,0,0,0.3)',borderBottom:'1px solid rgba(124,58,237,0.3)',overflowX:'auto'}}>
<div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',gap:'0.25rem',padding:'0.5rem 1rem'}}>
{tabs.map(t=><button key={t.id} onClick={()=>sT(t.id)} style={{background:tab===t.id?'linear-gradient(135deg,'+pur+',#6d28d9)':'transparent',border:'none',borderRadius:'0.5rem',padding:'0.65rem 1.25rem',color:tab===t.id?'#fff':lpur,cursor:'pointer',fontSize:'0.85rem',fontWeight:tab===t.id?600:500,whiteSpace:'nowrap'}}>{t.l}</button>)}
</div></div>
<div style={{maxWidth:'1400px',margin:'1.5rem auto',padding:'0 1rem'}}>

{tab==='dashboard'&&<div>
<div style={{marginBottom:'1.5rem',padding:'1rem 1.5rem',background:'rgba(16,185,129,0.1)',borderLeft:'4px solid '+grn,borderRadius:'0.5rem'}}>
<strong style={{color:grn}}>\u2713 Sistema 100% Automático — {cy} ciclos executados</strong>
<p style={{margin:'0.5rem 0 0',color:lpur,fontSize:'0.9rem'}}>Cérebro autônomo rodando a cada 60s via cron-job.org. Zero intervenção manual. Memória infinita em cerebro_memoria.</p></div>
<G><M label="Dia Atual" value={st.dia_atual||'—'} sub="Revelação: Dia 261" tag="AUTO"/><M label="Score Cérebro" value={cb.score_medio_recente||cb.score||'—'} sub={cb.ultimo_topic?.slice(0,30)||'Calculando...'} tag="LIVE"/><M label="Ciclos" value={cy} sub="A cada 60s" tag="CRON"/><M label="Membros WA" value={st.membros_wa||0} sub="Max: 1.024" tag="AUTO"/></G></div>}

{tab==='cerebro'&&<C><h2 style={{marginTop:0}}>\u{1F9E0} Cérebro AO VIVO <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>24/7</span></h2><p style={{color:lpur}}>Aprendendo continuamente. Cada ciclo salva tópico+score em cerebro_memoria. Evolui infinitamente.</p><G><M label="Status" value={cb.status==='online'?'\u25CF ONLINE':'\u25CF '+( cb.status||'ONLINE')} tag=""/><M label="Último Ciclo" value={cb.ultimo_ciclo?new Date(cb.ultimo_ciclo).toLocaleTimeString('pt-BR'):'—'}/><M label="Score Médio" value={cb.score_medio_recente||'—'}/><M label="Total Memória" value={cb.total_memoria||0}/></G></C>}

{tab==='gerador'&&<C><h2 style={{marginTop:0}}>\u2728 Gerador Automático <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>AUTO</span></h2><p style={{color:lpur}}>Roteiros de 22-28 min gerados automaticamente pelo cérebro. A cada ciclo, o melhor tópico é transformado em roteiro via /api/video/script. Zero ação manual.</p></C>}

{tab==='motor'&&<C><h2 style={{marginTop:0}}>\u{1F501} Motor 1000x — {cy} ciclos</h2><p style={{color:lpur}}>Vercel Hobby (1x/dia) + cron-job.org (1x/min) + frontend trigger (60s). Cérebro auto-ajusta.</p><G>{['Cérebro Principal','Aprendizado IA','WhatsApp Agente','Ranking Mundial'].map(n=><M key={n} label={n} value="\u25CF ATIVO" sub="60s via cron externo"/>)}</G></C>}

{tab==='series'&&<C><h2 style={{marginTop:0}}>\u{1F3AC} Séries Episódicas <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>AUTO</span></h2><p style={{color:lpur}}>Cérebro cria séries temáticas com episódios conectados. Cada série gera 8-12 episódios automaticamente.</p><G><M label="Séries Ativas" value="—"/><M label="Episódios" value="—"/></G></C>}

{tab==='revelacao'&&<C><h2 style={{marginTop:0}}>\u{1F389} Revelação Daniela Coelho — Dia 261</h2><div style={{paddingLeft:'2rem',marginTop:'1.5rem'}}>{pl.slice(0,10).map(p=>{const isR=p.dia===261;return <div key={p.dia} style={{position:'relative',paddingBottom:'1.25rem',borderLeft:isR?'3px solid '+pur:'3px solid rgba(124,58,237,0.3)',paddingLeft:'1.5rem'}}><div style={{position:'absolute',left:'-0.65rem',top:'0.1rem',width:'1.2rem',height:'1.2rem',borderRadius:'50%',background:isR?pur:'rgba(124,58,237,0.5)',border:'3px solid #1a0b2e'}}/><div style={{fontWeight:700,color:isR?pur:'#fff'}}>Dia {p.dia} [{p.fase}]</div><div style={{color:lpur,fontSize:'0.9rem',marginTop:'0.25rem'}}>{p.acao}</div></div>})}</div></C>}

{tab==='canais'&&<C><h2 style={{marginTop:0}}>\u{1F4E1} Gestão Multi-Canais</h2><G>{[['YouTube','@psicologiadoc',grn],['Instagram','Pendente',lpur],['TikTok','Pendente',lpur],['Pinterest','Pendente',lpur]].map(([n,v,cor])=><M key={n} label={n} value={v}/>)}</G></C>}

{tab==='whatsapp'&&<C><h2 style={{marginTop:0}}>\u{1F4AC} WhatsApp Grupos <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>AUTÔNOMO</span></h2><p style={{color:lpur}}>Agente humanizado 8h-22h SP. Delay 2-45min. Persona: membro anônimo 28-35 anos. Modelo: Groq → Gemini → OpenAI.</p><G><M label="Status" value="\u25CF ATIVO" tag="AUTO"/><M label="Membros" value={(st.membros_wa||0)+'/1024'}/><M label="Horário" value="8h-22h SP"/></G></C>}

{tab==='ranking'&&<C><h2 style={{marginTop:0}}>\u{1F30D} Ranking Mundial <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>LIVE</span></h2>{rk.length===0?<p style={{color:lpur}}>Cérebro coletando dados... Ranking aparecerá nos próximos ciclos.</p>:rk.slice(0,10).map((r,i)=><div key={i} style={{padding:'0.85rem 1rem',background:i<3?'rgba(124,58,237,0.2)':'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',display:'flex',justifyContent:'space-between',alignItems:'center',borderLeft:i<3?'4px solid '+pur:'4px solid transparent'}}><span><strong style={{color:pur}}>#{i+1}</strong> {r.topic}</span><span style={{color:'#fff',fontWeight:700,background:'rgba(124,58,237,0.3)',padding:'0.3rem 0.7rem',borderRadius:'0.3rem'}}>{r.score}/100</span></div>)}</C>}

{tab==='cases'&&<C><h2 style={{marginTop:0}}>\u{1F4C8} Cases do Dia</h2><p style={{color:lpur}}>Top vídeos analisados automaticamente</p><G><M label="Melhor Score" value={rk[0]?.score||'—'}/><M label="Total Analisado" value={rk.length}/><M label="Score Médio" value={rk.length?Math.round(rk.reduce((a,b)=>a+(b.score||0),0)/rk.length):'—'}/></G></C>}

{tab==='playlist'&&<C><h2 style={{marginTop:0}}>\u{1F4CB} Playlist 630 dias</h2><div style={{marginTop:'1rem'}}>{pl.map((p,i)=><div key={i} style={{padding:'0.6rem 0.75rem',borderBottom:'1px solid rgba(124,58,237,0.2)',display:'flex',justifyContent:'space-between'}}><span><strong>Dia {p.dia}</strong> — {p.acao}</span><span style={{color:lpur,fontSize:'0.85rem'}}>{p.fase}</span></div>)}</div></C>}

{tab==='conteudo'&&<C><h2 style={{marginTop:0}}>\u{1F4C4} Biblioteca de Conteúdo</h2><p style={{color:lpur}}>Roteiros e vídeos gerados automaticamente pelo cérebro</p><G><M label="Roteiros Gerados" value="—"/><M label="Vídeos Publicados" value="—"/></G></C>}

{tab==='monetizacao'&&<C><h2 style={{marginTop:0}}>\u{1F4B0} Monetização</h2><G><M label="AdSense" value="Pendente" sub="Meta: 1K subs + 4K horas"/><M label="Afiliados" value="R$ 0"/><M label="Consultas" value="Dia 261+" sub="Pós-revelação Daniela"/></G></C>}

{tab==='config'&&<C><h2 style={{marginTop:0}}>\u2699\uFE0F Configurações</h2><div style={{color:lpur,lineHeight:1.8}}><p><strong>Stack:</strong> Next.js 14 + Supabase + Groq 14.400 req/dia</p><p><strong>Deploy:</strong> repovazio.vercel.app (Hobby)</p><p><strong>Crons:</strong> Vercel 1x/dia + cron-job.org 1x/min</p><p><strong>Auto-evolução:</strong> Ativa em cerebro_memoria</p><p><strong>Repo:</strong> tafita81/Repovazio</p></div></C>}

{tab==='logs'&&<C><h2 style={{marginTop:0}}>\u{1F4CB} Logs em Tempo Real <span style={{fontSize:'0.7rem',background:'rgba(16,185,129,0.2)',color:grn,padding:'0.2rem 0.6rem',borderRadius:'0.3rem'}}>AUTO</span></h2><div ref={lr} style={{background:'rgba(0,0,0,0.5)',borderRadius:'0.5rem',padding:'1rem',maxHeight:'500px',overflowY:'auto',fontFamily:'ui-monospace,monospace',fontSize:'0.8rem'}}>{lg.length===0?<div style={{color:lpur}}>Aguardando primeiro ciclo...</div>:lg.map((l,i)=><div key={i} style={{marginBottom:'0.3rem',color:grn}}><span style={{color:lpur}}>[{l.t}]</span> {l.m}</div>)}</div></C>}

</div></div>)}