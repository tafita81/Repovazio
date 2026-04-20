'use client';
import {useState, useEffect, useRef} from 'react';

export default function D() {
  const [tab, setTab] = useState('dashboard');
  const [cerebro, setCerebro] = useState({});
  const [estado, setEstado] = useState({});
  const [plano, setPlano] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [logs, setLogs] = useState([]);
  const [ciclos, setCiclos] = useState(0);
  const logRef = useRef(null);

  useEffect(() => {
    loadAll();
    triggerCron();
    // Refresh dados a cada 3s
    const intData = setInterval(loadAll, 3000);
    // Executar cron auto a cada 60s (contorna limite Hobby)
    const intCron = setInterval(triggerCron, 60000);
    return () => { clearInterval(intData); clearInterval(intCron); };
  }, []);

  async function triggerCron() {
    try {
      const r = await fetch('/api/cron/auto');
      const d = await r.json();
      setCiclos(c => c + 1);
      setLogs(p => [{t: new Date().toLocaleTimeString('pt-BR'), m: 'CRON #' + (ciclos+1) + ' | ' + (d.acoes?.map(a => a.nome + ':' + a.status).join(', ') || 'erro') + ' | ' + (d.duracao_ms || '?') + 'ms'}, ...p].slice(0,100));
    } catch (e) {
      setLogs(p => [{t: new Date().toLocaleTimeString('pt-BR'), m: 'CRON erro: ' + e.message}, ...p].slice(0,100));
    }
  }

  async function loadAll() {
    const r = await Promise.allSettled([
      fetch('/api/cerebro/status').then(x => x.json()),
      fetch('/api/state').then(x => x.json()),
      fetch('/api/ranking').then(x => x.json()),
    ]);
    if (r[0].status === 'fulfilled') setCerebro(r[0].value);
    if (r[1].status === 'fulfilled') {
      setEstado(r[1].value);
      setPlano((r[1].value.plano || []).filter((p,i,a) => a.findIndex(x => x.dia === p.dia) === i).sort((a,b) => a.dia - b.dia));
    }
    if (r[2].status === 'fulfilled') setRanking(r[2].value.ranking || []);
  }

  const tabs = [
    {id:'dashboard',l:'⊡Dashboard'},{id:'cerebro',l:'🧠Cérebro AO VIVO'},{id:'gerador',l:'✨Gerador Manual'},
    {id:'motor',l:'🔁Motor 1000x'},{id:'series',l:'🎬Séries Episódicas'},{id:'revelacao',l:'🎉Revelação 2027'},
    {id:'canais',l:'📡Gestão de Canais'},{id:'whatsapp',l:'💬WhatsApp Grupos'},{id:'ranking',l:'🌍Ranking Mundial'},
    {id:'cases',l:'📈Cases do Dia'},{id:'playlist',l:'📋Playlist 630 dias'},{id:'conteudo',l:'📄Conteúdo'},
    {id:'monetizacao',l:'💰Monetização'},{id:'config',l:'⚙️Configurações'},{id:'logs',l:'📋Logs'}
  ];

  const c = {minHeight:'100vh', background:'linear-gradient(135deg,#0a0118,#1a0b2e 50%,#2d1b4e)', color:'#e0d4f7', fontFamily:'system-ui'};
  const hd = {background:'rgba(0,0,0,0.5)', borderBottom:'2px solid rgba(124,58,237,0.5)', padding:'1rem', position:'sticky', top:0, zIndex:10};
  const tt = {margin:0, fontSize:'1.5rem', fontWeight:800, background:'linear-gradient(90deg,#a78bfa,#7c3aed)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent'};
  const tb = (a) => ({background:a?'linear-gradient(135deg,#7c3aed,#6d28d9)':'transparent', border:'none', borderRadius:'0.5rem', padding:'0.65rem 1.25rem', color:a?'#fff':'#a78bfa', cursor:'pointer', fontSize:'0.85rem', fontWeight:a?600:500, whiteSpace:'nowrap'});
  const card = {background:'rgba(0,0,0,0.4)', borderRadius:'1rem', padding:'1.5rem', border:'1px solid rgba(124,58,237,0.3)', marginBottom:'1rem'};
  const grid = {display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(250px,1fr))', gap:'1rem'};
  const mtr = {background:'rgba(124,58,237,0.1)', borderRadius:'0.75rem', padding:'1.25rem', border:'1px solid rgba(124,58,237,0.3)'};
  const ml = {fontSize:'0.75rem', color:'#a78bfa', marginBottom:'0.5rem', textTransform:'uppercase', letterSpacing:'0.1em', fontWeight:600};
  const mv = {fontSize:'2.25rem', fontWeight:800, color:'#fff', lineHeight:1};
  const ms = {fontSize:'0.8rem', color:'#a78bfa', marginTop:'0.5rem'};
  const auto = {display:'inline-block', padding:'0.2rem 0.6rem', background:'rgba(16,185,129,0.2)', color:'#10b981', borderRadius:'0.3rem', fontSize:'0.7rem', fontWeight:700, marginLeft:'0.5rem'};

  return (
    <div style={c}>
      <style>{"@keyframes pulse {0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.6;transform:scale(1.2)}}"}</style>
      <div style={hd}>
        <div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',justifyContent:'space-between',alignItems:'center'}}>
          <h1 style={tt}><span style={{display:'inline-block',width:'0.6rem',height:'0.6rem',background:'#10b981',borderRadius:'50%',marginRight:'0.5rem',animation:'pulse 1.5s infinite'}}></span>psicologia.doc — Sistema Autônomo v7</h1>
          <div style={{display:'flex',gap:'1rem',alignItems:'center',fontSize:'0.85rem'}}>
            <span style={{color:'#10b981'}}>● Ciclos: {ciclos}</span>
            <span style={{color:'#a78bfa'}}>Dia {estado.dia_atual || '—'}</span>
          </div>
        </div>
      </div>
      <div style={{background:'rgba(0,0,0,0.3)',borderBottom:'1px solid rgba(124,58,237,0.3)',overflowX:'auto'}}>
        <div style={{maxWidth:'1400px',margin:'0 auto',display:'flex',gap:'0.25rem',padding:'0.5rem 1rem'}}>
          {tabs.map(t => <button key={t.id} onClick={()=>setTab(t.id)} style={tb(tab===t.id)}>{t.l}</button>)}
        </div>
      </div>
      <div style={{maxWidth:'1400px',margin:'1.5rem auto',padding:'0 1rem'}}>

        {tab==='dashboard' && <div>
          <div style={{marginBottom:'1.5rem',padding:'1rem 1.5rem',background:'rgba(16,185,129,0.1)',borderLeft:'4px solid #10b981',borderRadius:'0.5rem'}}>
            <strong style={{color:'#10b981'}}>✓ Sistema 100% Automático — {ciclos} ciclos executados</strong>
            <p style={{margin:'0.5rem 0 0',color:'#a78bfa',fontSize:'0.9rem'}}>Cérebro controla tudo. Trigger a cada 60s no frontend. Evolução infinita em cerebro_memoria.</p>
          </div>
          <div style={grid}>
            <div style={mtr}><div style={ml}>Dia Atual<span style={auto}>AUTO</span></div><div style={mv}>{estado.dia_atual || '—'}</div><div style={ms}>Revelação: Dia 261</div></div>
            <div style={mtr}><div style={ml}>Score<span style={auto}>LIVE</span></div><div style={mv}>{cerebro.score_medio_recente || cerebro.score || '—'}</div><div style={ms}>{cerebro.ultimo_topic?.slice(0,30) || 'Calculando...'}</div></div>
            <div style={mtr}><div style={ml}>Ciclos Hoje<span style={auto}>FRONTEND</span></div><div style={mv}>{ciclos}</div><div style={ms}>A cada 60s</div></div>
            <div style={mtr}><div style={ml}>Membros WA<span style={auto}>AUTO</span></div><div style={mv}>{estado.membros_wa || 0}</div><div style={ms}>Max: 1.024</div></div>
          </div>
        </div>}

        {tab==='cerebro' && <div style={card}>
          <h2 style={{marginTop:0}}>🧠 Cérebro AO VIVO<span style={auto}>24/7</span></h2>
          <p style={{color:'#a78bfa'}}>Aprendendo continuamente. Memoriza tudo em cerebro_memoria. Evolui infinitamente.</p>
          <div style={grid}>
            <div style={mtr}><div style={ml}>Status</div><div style={{fontSize:'1.5rem',fontWeight:700,color:'#10b981'}}>● {cerebro.status || 'ONLINE'}</div></div>
            <div style={mtr}><div style={ml}>Último Ciclo</div><div style={{fontSize:'1rem',fontWeight:600}}>{cerebro.ultimo_ciclo ? new Date(cerebro.ultimo_ciclo).toLocaleTimeString('pt-BR') : '—'}</div></div>
            <div style={mtr}><div style={ml}>Score Médio</div><div style={mv}>{cerebro.score_medio_recente || '—'}</div></div>
            <div style={mtr}><div style={ml}>Total Memória</div><div style={mv}>{cerebro.total_memoria || 0}</div></div>
          </div>
        </div>}

        {tab==='gerador' && <div style={card}><h2 style={{marginTop:0}}>✨ Gerador Automático<span style={auto}>AUTO</span></h2><p style={{color:'#a78bfa'}}>Roteiros gerados pelo cérebro. Zero ação manual necessária.</p></div>}

        {tab==='motor' && <div style={card}><h2 style={{marginTop:0}}>🔁 Motor 1000x — Ciclos: {ciclos}</h2><div style={grid}>{['Cérebro','Aprendizado','WhatsApp','Ranking'].map(n => <div key={n} style={mtr}><div style={ml}>{n}</div><div style={{fontSize:'1.2rem',fontWeight:700,color:'#10b981'}}>● ATIVO</div><div style={ms}>A cada 60s (frontend)</div></div>)}</div></div>}

        {tab==='series' && <div style={card}><h2 style={{marginTop:0}}>🎬 Séries Episódicas<span style={auto}>AUTO</span></h2></div>}

        {tab==='revelacao' && <div style={card}><h2 style={{marginTop:0}}>🎉 Revelação Daniela Coelho — Dia 261</h2><div style={{paddingLeft:'2rem',marginTop:'1.5rem'}}>{plano.slice(0,10).map(p => { const r = p.dia===261; return <div key={p.dia} style={{position:'relative',paddingBottom:'1.25rem',borderLeft:r?'3px solid #7c3aed':'3px solid rgba(124,58,237,0.3)',paddingLeft:'1.5rem'}}><div style={{position:'absolute',left:'-0.65rem',top:'0.1rem',width:'1.2rem',height:'1.2rem',borderRadius:'50%',background:r?'#7c3aed':'rgba(124,58,237,0.5)',border:'3px solid #1a0b2e'}}/><div style={{fontWeight:700,color:r?'#7c3aed':'#fff'}}>Dia {p.dia} · [{p.fase}]</div><div style={{color:'#a78bfa',fontSize:'0.9rem',marginTop:'0.25rem'}}>{p.acao}</div></div>})}</div></div>}

        {tab==='canais' && <div style={card}><h2 style={{marginTop:0}}>📡 Gestão Multi-Canais</h2><div style={grid}>{[['YouTube','@psicologiadoc','#10b981'],['Instagram','Pendente','#a78bfa'],['TikTok','Pendente','#a78bfa'],['Pinterest','Pendente','#a78bfa']].map(([n,v,cor]) => <div key={n} style={mtr}><div style={ml}>{n}</div><div style={{fontSize:'1.2rem',fontWeight:700,color:cor}}>{v}</div></div>)}</div></div>}

        {tab==='whatsapp' && <div style={card}><h2 style={{marginTop:0}}>💬 WhatsApp Grupos<span style={auto}>AUTO</span></h2><p style={{color:'#a78bfa'}}>Humanizado 8h-22h SP. Delay 2-45min.</p><div style={grid}><div style={mtr}><div style={ml}>Status</div><div style={{fontSize:'1.5rem',fontWeight:700,color:'#10b981'}}>● ATIVO</div></div><div style={mtr}><div style={ml}>Membros</div><div style={mv}>{estado.membros_wa || 0}/1024</div></div></div></div>}

        {tab==='ranking' && <div style={card}><h2 style={{marginTop:0}}>🌍 Ranking Mundial<span style={auto}>LIVE</span></h2>{ranking.length===0 ? <p style={{color:'#a78bfa'}}>Cérebro coletando dados... Aparecerá aqui nos próximos ciclos.</p> : ranking.slice(0,10).map((r,i) => <div key={i} style={{padding:'0.85rem 1rem',background:i<3?'rgba(124,58,237,0.2)':'rgba(0,0,0,0.2)',borderRadius:'0.5rem',marginBottom:'0.5rem',display:'flex',justifyContent:'space-between',alignItems:'center',borderLeft:i<3?'4px solid #7c3aed':'4px solid transparent'}}><span><strong style={{color:'#7c3aed'}}>#{i+1}</strong> · {r.topic}</span><span style={{color:'#fff',fontWeight:700,background:'rgba(124,58,237,0.3)',padding:'0.3rem 0.7rem',borderRadius:'0.3rem'}}>{r.score}/100</span></div>)}</div>}

        {tab==='cases' && <div style={card}><h2 style={{marginTop:0}}>📈 Cases do Dia</h2><div style={grid}><div style={mtr}><div style={ml}>Melhor Score</div><div style={mv}>{ranking[0]?.score || '—'}</div></div><div style={mtr}><div style={ml}>Total</div><div style={mv}>{ranking.length}</div></div><div style={mtr}><div style={ml}>Média</div><div style={mv}>{ranking.length ? Math.round(ranking.reduce((a,b)=>a+(b.score||0),0)/ranking.length) : '—'}</div></div></div></div>}

        {tab==='playlist' && <div style={card}><h2 style={{marginTop:0}}>📋 Playlist 630 dias</h2><div style={{marginTop:'1rem'}}>{plano.map((p,i) => <div key={i} style={{padding:'0.6rem 0.75rem',borderBottom:'1px solid rgba(124,58,237,0.2)',display:'flex',justifyContent:'space-between'}}><span><strong>Dia {p.dia}</strong> — {p.acao}</span><span style={{color:'#a78bfa',fontSize:'0.85rem'}}>{p.fase}</span></div>)}</div></div>}

        {tab==='conteudo' && <div style={card}><h2 style={{marginTop:0}}>📄 Biblioteca</h2></div>}

        {tab==='monetizacao' && <div style={card}><h2 style={{marginTop:0}}>💰 Monetização</h2><div style={grid}><div style={mtr}><div style={ml}>AdSense</div><div style={{fontSize:'1.3rem',fontWeight:700,color:'#a78bfa'}}>Pendente</div><div style={ms}>1K subs + 4K horas</div></div><div style={mtr}><div style={ml}>Afiliados</div><div style={mv}>R$ 0</div></div><div style={mtr}><div style={ml}>Consultas</div><div style={{fontSize:'1.3rem',fontWeight:700,color:'#a78bfa'}}>Dia 261+</div></div></div></div>}

        {tab==='config' && <div style={card}><h2 style={{marginTop:0}}>⚙️ Configurações</h2><div style={{color:'#a78bfa',lineHeight:1.8}}><p><strong>Stack:</strong> Next.js 14 + Supabase + Groq 14.400 req/dia</p><p><strong>Deploy:</strong> repovazio.vercel.app (Hobby)</p><p><strong>Crons:</strong> Vercel 1x/dia + Frontend 60s</p><p><strong>Auto-evolução:</strong> Ativa em cerebro_memoria</p></div></div>}

        {tab==='logs' && <div style={card}><h2 style={{marginTop:0}}>📋 Logs em Tempo Real<span style={auto}>AUTO</span></h2><div ref={logRef} style={{background:'rgba(0,0,0,0.5)',borderRadius:'0.5rem',padding:'1rem',maxHeight:'500px',overflowY:'auto',fontFamily:'ui-monospace,monospace',fontSize:'0.8rem'}}>{logs.length===0 ? <div style={{color:'#a78bfa'}}>Aguardando primeiro ciclo (60s)...</div> : logs.map((l,i) => <div key={i} style={{marginBottom:'0.3rem',color:'#10b981'}}><span style={{color:'#a78bfa'}}>[{l.t}]</span> {l.m}</div>)}</div></div>}

      </div>
    </div>
  );
}