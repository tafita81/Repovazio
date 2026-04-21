'use client';
import {useState,useEffect,useRef} from 'react';

const TOPICS=["Ansiedade & Burnout","Apego Ansioso","Narcisismo & Manipulacao","Trauma de Infancia","Autossabotagem","Relacionamentos Toxicos","Inteligencia Emocional","Depressao & Tristeza","Limites Saudaveis","Gaslighting","Autoestima","Sindrome do Impostor","Dependencia Emocional","Luto & Perda","Ansiedade Social","Psicologia do Dinheiro","Lideranca Toxica","Vicio em Validacao"];

const SERIES={apego:{nome:'A Ciencia do Apego',icon:'\u{1F4CE}',sub:'Por que voce ama quem te faz sofrer',eps:[{n:1,t:'O que e apego ansioso'},{n:2,t:'Por que escolhemos quem nos machuca'},{n:3,t:'O ciclo de abandono e reconexao'},{n:4,t:'Padroes da infancia'},{n:5,t:'Como sair do loop'},{n:6,t:'Construindo apego seguro'},{n:7,t:'Reconhecendo red flags'},{n:8,t:'O amor saudavel existe'}]},narcisismo:{nome:'Narcisismo Documentado',icon:'\u{1FA9E}',sub:'O que ninguem conta sobre manipulacao',eps:[{n:1,t:'O que e narcisismo real'},{n:2,t:'Love bombing - a isca perfeita'},{n:3,t:'Gaslighting na pratica'},{n:4,t:'O descarte'},{n:5,t:'Trauma bond - por que voce volta'},{n:6,t:'Hoovering - a volta do narcisista'},{n:7,t:'No contact - unica saida'},{n:8,t:'Recuperacao pos-narcisista'}]},ansiedade:{nome:'Ansiedade Documentada',icon:'\u26A1',sub:'Sua mente acelerada tem um motivo',eps:[{n:1,t:'O que e ansiedade'},{n:2,t:'Sintomas fisicos'},{n:3,t:'Respiracao 4-7-8'},{n:4,t:'Exposicao gradual'},{n:5,t:'Pensamentos catastroficos'},{n:6,t:'Mindfulness pratico'},{n:7,t:'Sono e ansiedade'},{n:8,t:'Protocolo completo'}]},trauma:{nome:'Trauma Invisivel',icon:'\u{1F513}',sub:'O que seu corpo carrega sem voce saber',eps:[{n:1,t:'O que e trauma'},{n:2,t:'Trauma esta no corpo'},{n:3,t:'Triggers - o que sao'},{n:4,t:'Freeze - paralisacao'},{n:5,t:'Somatizacao'},{n:6,t:'Exercicio de grounding'},{n:7,t:'EMDR basico'},{n:8,t:'Integracao'}]},burnout:{nome:'Burnout Documentado',icon:'\u{1F525}',sub:'Voce nao e preguicoso — esta esgotado',eps:[{n:1,t:'O que e burnout'},{n:2,t:'3 fases do esgotamento'},{n:3,t:'Semana 1-2: parar'},{n:4,t:'Semana 3-4: descanso ativo'},{n:5,t:'Semana 5-6: limites'},{n:6,t:'Semana 7: retorno gradual'},{n:7,t:'Semana 8: novo ritmo'},{n:8,t:'Prevencao'}]}};

// 18 CATEGORIAS COM EPISÓDIOS (6 cada)
const CATS_EPS={
  "Ansiedade & Burnout":[{n:1,t:'Sintomas ocultos'},{n:2,t:'Ciclo do estresse'},{n:3,t:'Recuperacao ativa'},{n:4,t:'Limites no trabalho'},{n:5,t:'Tecnicas 5min'},{n:6,t:'Prevencao'}],
  "Apego Ansioso":[{n:1,t:'O que e apego'},{n:2,t:'Padroes tóxicos'},{n:3,t:'Medo abandono'},{n:4,t:'Infancia e apego'},{n:5,t:'Apego seguro'},{n:6,t:'Novo padrao'}],
  "Narcisismo & Manipulacao":[{n:1,t:'Sinais narcisista'},{n:2,t:'Love bombing'},{n:3,t:'Gaslighting'},{n:4,t:'Descarte'},{n:5,t:'Trauma bond'},{n:6,t:'No contact'}],
  "Trauma de Infancia":[{n:1,t:'Trauma escondido'},{n:2,t:'Corpo guarda'},{n:3,t:'Triggers'},{n:4,t:'Congelar'},{n:5,t:'Liberar'},{n:6,t:'Integrar'}],
  "Autossabotagem":[{n:1,t:'O que e'},{n:2,t:'Padroes'},{n:3,t:'Medo sucesso'},{n:4,t:'Quebrar ciclo'},{n:5,t:'Autoconfianca'},{n:6,t:'Novo eu'}],
  "Relacionamentos Toxicos":[{n:1,t:'Red flags'},{n:2,t:'Ciclo toxico'},{n:3,t:'Dependencia'},{n:4,t:'Sair'},{n:5,t:'Cura'},{n:6,t:'Saudavel'}],
  "Inteligencia Emocional":[{n:1,t:'O que e'},{n:2,t:'Autoconhecimento'},{n:3,t:'Regular emocoes'},{n:4,t:'Empatia'},{n:5,t:'Relacionar'},{n:6,t:'Praticar'}],
  "Depressao & Tristeza":[{n:1,t:'Diferenca'},{n:2,t:'Sinais'},{n:3,t:'Buscar ajuda'},{n:4,t:'Rotina'},{n:5,t:'Conexao'},{n:6,t:'Esperanca'}],
  "Limites Saudaveis":[{n:1,t:'O que sao'},{n:2,t:'Por que dificil'},{n:3,t:'Dizer nao'},{n:4,t:'Familia'},{n:5,t:'Trabalho'},{n:6,t:'Manter'}],
  "Gaslighting":[{n:1,t:'O que e'},{n:2,t:'Taticas'},{n:3,t:'Duvidar si'},{n:4,t:'Reconhecer'},{n:5,t:'Documentar'},{n:6,t:'Sair'}],
  "Autoestima":[{n:1,t:'O que e'},{n:2,t:'Criticas internas'},{n:3,t:'Padroes irreais'},{n:4,t:'Construir'},{n:5,t:'Autocompaixao'},{n:6,t:'Manter'}],
  "Sindrome do Impostor":[{n:1,t:'O que e'},{n:2,t:'Quem tem'},{n:3,t:'Voz interna'},{n:4,t:'Evidencias'},{n:5,t:'Compartilhar'},{n:6,t:'Superar'}],
  "Dependencia Emocional":[{n:1,t:'O que e'},{n:2,t:'Sinais'},{n:3,t:'Raiz'},{n:4,t:'Autonomia'},{n:5,t:'Sozinho OK'},{n:6,t:'Equilibrio'}],
  "Luto & Perda":[{n:1,t:'Estagios'},{n:2,t:'Nao linear'},{n:3,t:'Corpo sente'},{n:4,t:'Permitir'},{n:5,t:'Apoio'},{n:6,t:'Seguir'}],
  "Ansiedade Social":[{n:1,t:'O que e'},{n:2,t:'Sintomas'},{n:3,t:'Evitacao'},{n:4,t:'Exposicao'},{n:5,t:'Pratica'},{n:6,t:'Viver'}],
  "Psicologia do Dinheiro":[{n:1,t:'Crencas'},{n:2,t:'Infancia'},{n:3,t:'Escassez'},{n:4,t:'Autopunicao'},{n:5,t:'Abundancia'},{n:6,t:'Saudavel'}],
  "Lideranca Toxica":[{n:1,t:'Sinais'},{n:2,t:'Microgerencia'},{n:3,t:'Manipulacao'},{n:4,t:'Proteger'},{n:5,t:'Sair ou ficar'},{n:6,t:'Recuperar'}],
  "Vicio em Validacao":[{n:1,t:'O que e'},{n:2,t:'Redes sociais'},{n:3,t:'Autovalor'},{n:4,t:'Interno'},{n:5,t:'Praticar'},{n:6,t:'Liberdade'}]
};

export default function Dashboard(){
const[tab,sT]=useState('dashboard');
const[cb,sCb]=useState({});
const[st,sSt]=useState({});
const[pl,sPl]=useState([]);
const[rk,sRk]=useState([]);
const[lg,sLg]=useState([]);
const[cy,sCy]=useState(0);
const[q,sQ]=useState('');
const[resp,sResp]=useState('');
const[loading,setLoading]=useState(false);
const[selSerie,setSelSerie]=useState('apego');
const[showAllEps,setShowAllEps]=useState(false);
const[selCat,setSelCat]=useState(TOPICS[0]);
const[showCatEps,setShowCatEps]=useState(false);
const inputRef=useRef(null);
const lr=useRef(null);

useEffect(()=>{
  la();
  triggerCron();
  const i1=setInterval(la,3000);
  const i2=setInterval(triggerCron,60000);
  return()=>{clearInterval(i1);clearInterval(i2)}
},[]);

// AUTOFOCUS CORRIGIDO
useEffect(()=>{
  if(tab==='dashboard'&&inputRef.current){
    inputRef.current.focus();
  }
},[tab]);

async function triggerCron(){
  try{
    const r=await fetch('/api/cron/auto');
    const d=await r.json();
    sCy(c=>c+1);
    sLg(p=>[{t:new Date().toLocaleTimeString('pt-BR'),m:'CRON | '+(d.acoes?.map(a=>a.nome+':'+a.status).join(', ')||'erro')+' | '+d.duracao_ms+'ms'},...p].slice(0,100))
  }catch(e){
    sLg(p=>[{t:new Date().toLocaleTimeString('pt-BR'),m:'CRON erro: '+e.message},...p].slice(0,100))
  }
}

async function la(){
  const r=await Promise.allSettled([
    fetch('/api/cerebro/status').then(x=>x.json()),
    fetch('/api/state').then(x=>x.json()),
    fetch('/api/ranking').then(x=>x.json())
  ]);
  if(r[0].status==='fulfilled')sCb(r[0].value);
  if(r[1].status==='fulfilled'){
    sSt(r[1].value);
    sPl((r[1].value.plano||[]).filter((p,i,a)=>a.findIndex(x=>x.dia===p.dia)===i).sort((a,b)=>a.dia-b.dia))
  }
  if(r[2].status==='fulfilled')sRk(r[2].value.ranking||[])
}

async function askIA(){
  if(!q.trim())return;
  setLoading(true);
  try{
    const r=await fetch('/api/assistente',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pergunta:q,historico:[]})
    });
    const d=await r.json();
    sResp(d.resposta||d.erro||'Sem resposta');
    sQ('')
  }catch(e){
    sResp('Erro: '+e.message)
  }finally{
    setLoading(false)
  }
}

const tabs=[{id:'dashboard',l:'\u229EDashboard'},{id:'cerebro',l:'\u{1F9E0}Cerebro'},{id:'gerador',l:'\u2728Gerador'},{id:'motor',l:'\u{1F501}Motor 1000x'},{id:'series',l:'\u{1F3AC}Series'},{id:'categorias',l:'\u{1F4DA}Categorias'},{id:'revelacao',l:'\u{1F389}Revelacao'},{id:'canais',l:'\u{1F4E1}Canais'},{id:'whatsapp',l:'\u{1F4AC}WhatsApp'},{id:'ranking',l:'\u{1F30D}Ranking'},{id:'cases',l:'\u{1F4C8}Cases'},{id:'playlist',l:'\u{1F4CB}Playlist'},{id:'conteudo',l:'\u{1F4C4}Conteudo'},{id:'monetizacao',l:'\u{1F4B0}Monetizacao'},{id:'config',l:'\u2699Config'},{id:'logs',l:'\u{1F4CB}Logs'}];

const pur='#7c3aed',lp='#a78bfa',gn='#10b981';
const C=({children})=><div style={{background:'rgba(0,0,0,0.4)',borderRadius:'1rem',padding:'1.5rem',border:'1px solid rgba(124,58,237,0.3)',marginBottom:'1rem'}}>{children}</div>;
const M=({l,v,s,t})=><div style={{background:'rgba(124,58,237,0.1)',borderRadius:'0.75rem',padding:'1.25rem',border:'1px solid rgba(124,58,237,0.3)'}}><div style={{fontSize:'0.75rem',color:lp,marginBottom:'0.5rem',textTransform:'uppercase',letterSpacing:'0.1em',fontWeight:600}}>{l}{t&&<span style={{display:'inline-block',padding:'0.2rem 0.6rem',background:'rgba(16,185,129,0.2)',color:gn,borderRadius:'0.3rem',fontSize:'0.7rem',fontWeight:700,marginLeft:'0.5rem'}}>{t}</span>}</div><div style={{fontSize:'2rem',fontWeight:800,color:'#fff',lineHeight:1}}>{v}</div>{s&&<div style={{fontSize:'0.8rem',color:lp,marginTop:'0.5rem'}}>{s}</div>}</div>;
const G=({children})=><div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))',gap:'1rem'}}>{children}</div>;

return(<div style={{minHeight:'100vh',background:'linear-gradient(135deg,#0a0118,#1a0b2e 50%,#2d1b4e)',color:'#e0d4f7',fontFamily:'system-ui'}}>
<style>{'@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(1.2)}}'}</style>

<div style={{background:'rgba(0,0,0,0.5)',borderBottom:'2px solid rgba(124,58,237,0.5)',padding:'1rem',position:'sticky',top:0,zIndex:10}}>
  <div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
    <h1 style={{margin:0,fontSize:'1.4rem',fontWeight:800,background:'linear-gradient(90deg,'+lp+','+pur+')',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>
      <span style={{display:'inline-block',width:'0.6rem',height:'0.6rem',background:gn,borderRadius:'50%',marginRight:'0.5rem',animation:'pulse 1.5s infinite'}}/>
      psicologia.doc v7
    </h1>
    <div style={{display:'flex',gap:'1rem',alignItems:'center',fontSize:'0.85rem'}}>
      <span style={{color:gn}}>Ciclos: {cy}</span>
      <span style={{color:lp}}>Dia {st.dia_atual||'--'}</span>
    </div>
  </div>
</div>

<div style={{background:'rgba(0,0,0,0.3)',borderBottom:'1px solid rgba(124,58,237,0.3)',overflowX:'auto'}}>
  <div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',gap:'0.25rem',padding:'0.5rem 1rem'}}>
    {tabs.map(t=><button key={t.id} onClick={()=>sT(t.id)} style={{background:tab===t.id?'linear-gradient(135deg,'+pur+',#6d28d9)':'transparent',border:'none',borderRadius:'0.5rem',padding:'0.6rem 1.1rem',color:tab===t.id?'#fff':lp,cursor:'pointer',fontSize:'0.85rem',fontWeight:tab===t.id?600:500,whiteSpace:'nowrap'}}>{t.l}</button>)}
  </div>
</div>

<div style={{maxWidth:'1400px',margin:'1.5rem auto',padding:'0 1rem'}}>

{tab==='dashboard'&&<div>
  <div style={{marginBottom:'1.5rem',padding:'1rem',background:'rgba(16,185,129,0.1)',borderLeft:'4px solid '+gn,borderRadius:'0.5rem'}}>
    <strong style={{color:gn}}>Sistema 100% Autonomo -- {cy} ciclos -- cron-job.org 5min</strong>
    <p style={{margin:'0.5rem 0 0',color:lp,fontSize:'0.9rem'}}>Cerebro roda 24/7. Zero intervencao manual.</p>
  </div>
  <G><M l="Dia" v={st.dia_atual||'--'} s="Revelacao: 261" t="AUTO"/><M l="Score" v={cb.score_medio_recente||cb.score||'--'} t="LIVE"/><M l="Ciclos" v={cy} s="5min cron externo" t="CRON"/><M l="WA" v={st.membros_wa||0} s="Max: 1024" t="AUTO"/></G>
  
  <C>
    <h3 style={{margin:'0 0 1rem',color:'#fff'}}>🤖 Chat Executor IA (Agente Completo)</h3>
    <p style={{margin:'0 0 1rem',color:lp,fontSize:'0.9rem'}}>Esse agente pode fazer commits GitHub, deploys Vercel, queries Supabase, postar redes sociais e TUDO mais. Use linguagem natural.</p>
    <div style={{marginBottom:'1rem'}}>
      <input 
        ref={inputRef}
        value={q} 
        onChange={e=>sQ(e.target.value)} 
        onKeyDown={e=>e.key==='Enter'&&!loading&&askIA()} 
        placeholder="Ex: Criar nova rota API, fazer deploy, atualizar dashboard, postar no Instagram..." 
        autoFocus
        style={{width:'100%',padding:'0.75rem',background:'rgba(0,0,0,0.3)',border:'1px solid rgba(124,58,237,0.4)',borderRadius:'0.5rem',color:'#fff',fontSize:'0.9rem',outline:'none'}}
      />
    </div>
    <button onClick={askIA} disabled={loading||!q.trim()} style={{padding:'0.6rem 1.5rem',background:loading||!q.trim()?'rgba(124,58,237,0.3)':'linear-gradient(135deg,'+pur+',#6d28d9)',border:'none',borderRadius:'0.5rem',color:'#fff',fontWeight:600,cursor:loading||!q.trim()?'not-allowed':'pointer',marginBottom:'1rem',fontSize:'0.9rem'}}>
      {loading?'🔄 Executando...':'🚀 Executar'}
    </button>
    {resp&&<div style={{background:'rgba(0,0,0,0.4)',borderRadius:'0.5rem',padding:'1rem',border:'1px solid rgba(124,58,237,0.3)',maxHeight:'400px',overflowY:'auto'}}>
      <strong style={{color:lp,fontSize:'0.85rem'}}>Resposta do Executor:</strong>
      <pre style={{margin:'0.5rem 0 0',color:'#fff',lineHeight:1.6,whiteSpace:'pre-wrap',fontFamily:'inherit'}}>{resp}</pre>
    </div>}
  </C>
</div>}

{tab==='cerebro'&&<C><h2 style={{marginTop:0}}>Cerebro AO VIVO</h2><p style={{color:lp}}>Autoaprendizado continuo. Memoria infinita.</p><G><M l="Status" v={(cb.status||'online').toUpperCase()}/><M l="Ultimo Ciclo" v={cb.ultimo_ciclo?new Date(cb.ultimo_ciclo).toLocaleTimeString('pt-BR'):'--'}/><M l="Score Medio" v={cb.score_medio_recente||'--'}/><M l="Memoria" v={cb.total_memoria||0}/></G></C>}

{tab==='gerador'&&<C><h2 style={{marginTop:0}}>Gerador Automatico</h2><p style={{color:lp}}>Roteiros 22-28min gerados automaticamente via /api/video/script</p><h3 style={{color:lp}}>18 Categorias:</h3><div style={{display:'flex',flexWrap:'wrap',gap:'0.5rem'}}>{TOPICS.map(t=><span key={t} style={{background:'rgba(124,58,237,0.2)',border:'1px solid rgba(124,58,237,0.4)',borderRadius:'0.5rem',padding:'0.4rem 0.8rem',fontSize:'0.85rem',color:'#fff'}}>{t}</span>)}</div></C>}

{tab==='motor'&&<C><h2 style={{marginTop:0}}>Motor 1000x -- {cy} ciclos</h2><p style={{color:lp}}>cron-job.org (5min) + Vercel (1x/dia)</p><G>{['Cerebro','Aprendizado','WhatsApp','Ranking'].map(n=><M key={n} l={n} v="ATIVO" s="5min cron"/>)}</G></C>}

{tab==='series'&&<C><h2 style={{marginTop:0}}>Series Episodicas</h2><p style={{color:lp}}>5 series, 8 episodios cada (40 total)</p><div style={{marginBottom:'1rem',display:'flex',gap:'0.5rem',flexWrap:'wrap'}}>{Object.keys(SERIES).map(k=><button key={k} onClick={()=>{setSelSerie(k);setShowAllEps(false)}} style={{padding:'0.5rem 1rem',background:selSerie===k?'linear-gradient(135deg,'+pur+',#6d28d9)':'rgba(124,58,237,0.2)',border:'none',borderRadius:'0.5rem',color:'#fff',cursor:'pointer',fontWeight:selSerie===k?600:400}}>{SERIES[k].icon} {SERIES[k].nome}</button>)}</div>{selSerie&&<div style={{background:'rgba(0,0,0,0.3)',borderRadius:'0.75rem',padding:'1.5rem',borderLeft:'4px solid '+pur}}><h3 style={{margin:0,color:'#fff'}}>{SERIES[selSerie].icon} {SERIES[selSerie].nome}</h3><p style={{margin:'0.5rem 0',color:lp,fontSize:'0.95rem'}}>{SERIES[selSerie].sub}</p><button onClick={()=>setShowAllEps(!showAllEps)} style={{marginTop:'0.75rem',padding:'0.5rem 1.2rem',background:'rgba(124,58,237,0.3)',border:'1px solid rgba(124,58,237,0.5)',borderRadius:'0.5rem',color:'#fff',cursor:'pointer',fontWeight:600,fontSize:'0.85rem'}}>{showAllEps?'Ocultar episodios':'Ver todos os '+SERIES[selSerie].eps.length+' episodios'}</button>{showAllEps&&<div style={{marginTop:'1rem'}}>{SERIES[selSerie].eps.map(ep=><div key={ep.n} style={{padding:'0.75rem',background:'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',display:'flex',justifyContent:'space-between',alignItems:'center'}}><div><strong style={{color:pur}}>Ep. {ep.n}</strong> <span style={{color:'#fff'}}>{ep.t}</span></div><button style={{padding:'0.4rem 1rem',background:'linear-gradient(135deg,'+gn+',#059669)',border:'none',borderRadius:'0.4rem',color:'#fff',fontSize:'0.8rem',fontWeight:600,cursor:'pointer'}} onClick={()=>alert('Video sera criado automaticamente pelo cerebro')}>Ver video</button></div>)}</div>}</div>}</C>}

{tab==='categorias'&&<C><h2 style={{marginTop:0}}>18 Categorias com Episodios</h2><p style={{color:lp}}>Cada categoria tem 6 episodios (108 total)</p><div style={{marginBottom:'1rem',display:'flex',gap:'0.5rem',flexWrap:'wrap'}}>{TOPICS.map(t=><button key={t} onClick={()=>{setSelCat(t);setShowCatEps(false)}} style={{padding:'0.5rem 1rem',background:selCat===t?'linear-gradient(135deg,'+pur+',#6d28d9)':'rgba(124,58,237,0.2)',border:'none',borderRadius:'0.5rem',color:'#fff',cursor:'pointer',fontWeight:selCat===t?600:400,fontSize:'0.85rem'}}>{t}</button>)}</div>{selCat&&CATS_EPS[selCat]&&<div style={{background:'rgba(0,0,0,0.3)',borderRadius:'0.75rem',padding:'1.5rem',borderLeft:'4px solid '+pur}}><h3 style={{margin:0,color:'#fff'}}>{selCat}</h3><button onClick={()=>setShowCatEps(!showCatEps)} style={{marginTop:'0.75rem',padding:'0.5rem 1.2rem',background:'rgba(124,58,237,0.3)',border:'1px solid rgba(124,58,237,0.5)',borderRadius:'0.5rem',color:'#fff',cursor:'pointer',fontWeight:600,fontSize:'0.85rem'}}>{showCatEps?'Ocultar episodios':'Ver todos os '+CATS_EPS[selCat].length+' episodios'}</button>{showCatEps&&<div style={{marginTop:'1rem'}}>{CATS_EPS[selCat].map(ep=><div key={ep.n} style={{padding:'0.75rem',background:'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',display:'flex',justifyContent:'space-between',alignItems:'center'}}><div><strong style={{color:pur}}>Ep. {ep.n}</strong> <span style={{color:'#fff'}}>{ep.t}</span></div><button style={{padding:'0.4rem 1rem',background:'linear-gradient(135deg,'+gn+',#059669)',border:'none',borderRadius:'0.4rem',color:'#fff',fontSize:'0.8rem',fontWeight:600,cursor:'pointer'}} onClick={()=>alert('Video sera criado automaticamente')}>Ver video</button></div>)}</div>}</div>}</C>}

{tab==='revelacao'&&<C><h2 style={{marginTop:0}}>Revelacao Daniela Coelho -- Dia 261</h2><div style={{paddingLeft:'2rem',marginTop:'1.5rem'}}>{pl.slice(0,10).map(p=>{const isR=p.dia===261;return <div key={p.dia} style={{position:'relative',paddingBottom:'1.25rem',borderLeft:isR?'3px solid '+pur:'3px solid rgba(124,58,237,0.3)',paddingLeft:'1.5rem'}}><div style={{position:'absolute',left:'-0.65rem',top:'0.1rem',width:'1.2rem',height:'1.2rem',borderRadius:'50%',background:isR?pur:'rgba(124,58,237,0.5)',border:'3px solid #1a0b2e'}}/><div style={{fontWeight:700,color:isR?pur:'#fff'}}>Dia {p.dia} [{p.fase}]</div><div style={{color:lp,fontSize:'0.9rem',marginTop:'0.25rem'}}>{p.acao}</div></div>})}</div></C>}

{tab==='canais'&&<C><h2 style={{marginTop:0}}>Multi-Canais</h2><G>{[['YouTube','@psicologiadoc',gn],['Instagram','Pendente',lp],['TikTok','Pendente',lp],['Pinterest','Pendente',lp]].map(([n,v,c])=><M key={n} l={n} v={v}/>)}</G></C>}

{tab==='whatsapp'&&<C><h2 style={{marginTop:0}}>WhatsApp Autonomo</h2><p style={{color:lp}}>Agente 8h-22h SP (BRT). Delay 2-45min. Mensagens humanizadas.</p><G><M l="Status" v="PENDENTE" s="Aguardando tokens" t="CONF"/><M l="Membros" v={(st.membros_wa||0)+'/1024'}/><M l="Horario" v="8h-22h SP"/><M l="Delay" v="2-45min" s="Humanizado"/></G><div style={{marginTop:'1.5rem',padding:'1rem',background:'rgba(124,58,237,0.1)',borderRadius:'0.5rem'}}><strong style={{color:pur}}>Configuracao necessaria:</strong><p style={{margin:'0.5rem 0 0',color:lp,fontSize:'0.9rem'}}>Adicionar no Vercel env: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, WHATSAPP_GROUP_ID</p></div></C>}

{tab==='ranking'&&<C><h2 style={{marginTop:0}}>Ranking Mundial</h2>{rk.length===0?<p style={{color:lp}}>Coletando dados...</p>:rk.slice(0,10).map((r,i)=><div key={i} style={{padding:'0.85rem',background:i<3?'rgba(124,58,237,0.2)':'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',display:'flex',justifyContent:'space-between',borderLeft:i<3?'4px solid '+pur:'none'}}><span><strong style={{color:pur}}>#{i+1}</strong> {r.topic}</span><span style={{fontWeight:700,background:'rgba(124,58,237,0.3)',padding:'0.3rem 0.7rem',borderRadius:'0.3rem'}}>{r.score}/100</span></div>)}</C>}

{tab==='cases'&&<C><h2 style={{marginTop:0}}>Cases do Dia</h2><G><M l="Melhor" v={rk[0]?.score||'--'}/><M l="Total" v={rk.length}/><M l="Media" v={rk.length?Math.round(rk.reduce((a,b)=>a+(b.score||0),0)/rk.length):'--'}/></G></C>}

{tab==='playlist'&&<C><h2 style={{marginTop:0}}>Playlist 630 dias</h2>{pl.map((p,i)=><div key={i} style={{padding:'0.6rem',borderBottom:'1px solid rgba(124,58,237,0.2)',display:'flex',justifyContent:'space-between'}}><span><strong>Dia {p.dia}</strong> -- {p.acao}</span><span style={{color:lp,fontSize:'0.85rem'}}>{p.fase}</span></div>)}</C>}

{tab==='conteudo'&&<C><h2 style={{marginTop:0}}>Biblioteca Completa</h2><p style={{color:lp}}>18 categorias (108 eps) + 5 series (40 eps) = 148 episodios total</p><h3 style={{color:lp,marginBottom:'0.75rem'}}>Categorias ({TOPICS.length}):</h3><div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))',gap:'0.75rem',marginBottom:'1.5rem'}}>{TOPICS.map((t,i)=><div key={t} style={{background:'rgba(124,58,237,0.15)',border:'1px solid rgba(124,58,237,0.3)',borderRadius:'0.5rem',padding:'0.6rem',fontSize:'0.85rem'}}><strong style={{color:pur}}>{i+1}.</strong> {t} <span style={{color:lp,fontSize:'0.75rem'}}>(6 eps)</span></div>)}</div><h3 style={{color:lp,marginBottom:'0.75rem'}}>Series ({Object.keys(SERIES).length}):</h3>{Object.values(SERIES).map((s,i)=><div key={i} style={{padding:'0.75rem',borderBottom:'1px solid rgba(124,58,237,0.2)',display:'flex',justifyContent:'space-between',alignItems:'center'}}><div><strong style={{color:'#fff'}}>{s.icon} {s.nome}</strong><p style={{margin:'0.25rem 0 0',color:lp,fontSize:'0.8rem'}}>{s.sub}</p></div><span style={{background:'rgba(124,58,237,0.2)',padding:'0.3rem 0.7rem',borderRadius:'0.3rem',fontSize:'0.8rem',fontWeight:600}}>{s.eps.length} eps</span></div>)}</C>}

{tab==='monetizacao'&&<C><h2 style={{marginTop:0}}>Monetizacao</h2><G><M l="AdSense" v="Pendente" s="1K subs + 4K horas"/><M l="Afiliados" v="R$ 0"/><M l="Consultas" v="Dia 261+" s="Pos-revelacao"/><M l="Cursos" v="Planejado" s="Apego, Narcisismo"/></G></C>}

{tab==='config'&&<C><h2 style={{marginTop:0}}>Configuracoes</h2><div style={{color:lp,lineHeight:1.8}}><p><strong>Stack:</strong> Next.js 14 + Supabase + Groq Llama 3.3 70B</p><p><strong>Cron:</strong> cron-job.org 5min + Vercel 1x/dia</p><p><strong>Categorias:</strong> {TOPICS.length} ({TOPICS.length*6} eps)</p><p><strong>Series:</strong> {Object.keys(SERIES).length} ({Object.values(SERIES).reduce((a,s)=>a+s.eps.length,0)} eps)</p><p><strong>Total episodios:</strong> {TOPICS.length*6 + Object.values(SERIES).reduce((a,s)=>a+s.eps.length,0)}</p><p><strong>GitHub:</strong> tafita81/Repovazio</p><p><strong>Vercel:</strong> repovazio.vercel.app</p><p><strong>Supabase:</strong> tpjvalzwkqwttvmszvie</p></div><h3 style={{color:pur,marginTop:'1.5rem'}}>Conexoes Pendentes:</h3><div style={{marginTop:'1rem'}}>{[
  {n:'ElevenLabs',s:'ELEVENLABS_API_KEY',d:'Voz PT-BR feminina'},
  {n:'HeyGen',s:'HEYGEN_API_KEY',d:'Avatar 4K Daniela'},
  {n:'YouTube OAuth',s:'YT_CLIENT_ID + YT_CLIENT_SECRET',d:'Publicacao automatica'},
  {n:'WhatsApp Business',s:'WHATSAPP_TOKEN + PHONE_ID',d:'Agente grupos'},
  {n:'Instagram Graph',s:'IG_ACCESS_TOKEN',d:'Posts automaticos'},
  {n:'TikTok API',s:'TIKTOK_ACCESS_TOKEN',d:'Videos automaticos'},
  {n:'Pinterest API',s:'PINTEREST_ACCESS_TOKEN',d:'Pins automaticos'}
].map(c=><div key={c.n} style={{padding:'0.75rem',background:'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',borderLeft:'3px solid rgba(124,58,237,0.5)'}}><strong style={{color:'#fff'}}>{c.n}</strong><div style={{color:lp,fontSize:'0.85rem',marginTop:'0.25rem'}}>Env: {c.s}</div><div style={{color:'#888',fontSize:'0.8rem',marginTop:'0.25rem'}}>{c.d}</div></div>)}</div></C>}

{tab==='logs'&&<C><h2 style={{marginTop:0}}>Logs</h2><div ref={lr} style={{background:'rgba(0,0,0,0.5)',borderRadius:'0.5rem',padding:'1rem',maxHeight:'500px',overflowY:'auto',fontFamily:'ui-monospace,monospace',fontSize:'0.8rem'}}>{lg.length===0?<div style={{color:lp}}>Aguardando...</div>:lg.map((l,i)=><div key={i} style={{marginBottom:'0.3rem',color:gn}}><span style={{color:lp}}>[{l.t}]</span> {l.m}</div>)}</div></C>}

</div>
</div>)}