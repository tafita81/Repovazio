'use client';
import{useState,useEffect,useRef,useCallback}from'react';

// Tempos otimizados para máximo views/monetização (sem exposição ao usuário)
const STATUS_INTERVAL=30*1000;      // status a cada 30s
const WA_CHECK_INTERVAL=8*60*1000; // checar WA a cada 8min (fica dentro do free)

export default function IAPage(){
  const[aba,setAba]=useState('executor');
  const[msgs,setMsgs]=useState([{role:'model',text:'🧠 Executor IA ativo. Posso editar código em produção, analisar métricas, criar agentes, otimizar o sistema. O que fazer agora?'}]);
  const[input,setInput]=useState('');
  const[loading,setLoading]=useState(false);
  const[status,setStatus]=useState<any>(null);
  const[waStatus,setWaStatus]=useState<any>(null);
  const[plano,setPlano]=useState<any[]>([]);
  const[autoLog,setAutoLog]=useState<any[]>([]);
  const[membrosWA,setMembrosWA]=useState(0);
  const chatRef=useRef<any>(null);

  const log=useCallback((msg:string)=>{
    const hora=new Date().toLocaleTimeString('pt-BR',{timeZone:'America/Sao_Paulo'});
    setAutoLog(prev=>[{hora,msg},...prev].slice(0,100));
  },[]);

  const fetchStatus=useCallback(async()=>{
    try{const r=await fetch('/api/cerebro/status');const d=await r.json();setStatus(d);}catch{}
  },[]);

  const fetchPlano=useCallback(async()=>{
    try{const r=await fetch('/api/state');const d=await r.json();if(d.plano)setPlano(d.plano);if(d.membros_wa)setMembrosWA(d.membros_wa);}catch{}
  },[]);

  const checkWA=useCallback(async()=>{
    try{const r=await fetch('/api/whatsapp');const d=await r.json();
      if(d.status==='ok'&&d.mensagem){log('💬 WA: "'+d.mensagem.slice(0,60)+'"');setWaStatus(d);}
    }catch{}
  },[log]);

  useEffect(()=>{
    fetchStatus();fetchPlano();
    const sId=setInterval(fetchStatus,STATUS_INTERVAL);
    const wId=setInterval(checkWA,WA_CHECK_INTERVAL);
    return()=>{clearInterval(sId);clearInterval(wId);};
  },[fetchStatus,fetchPlano,checkWA]);

  useEffect(()=>{if(chatRef.current)chatRef.current.scrollTop=chatRef.current.scrollHeight;},[msgs]);

  const enviar=async()=>{
    if(!input.trim()||loading)return;
    const pergunta=input.trim();setInput('');
    setMsgs(prev=>[...prev,{role:'user',text:pergunta}]);
    setLoading(true);
    try{
      const r=await fetch('/api/assistente',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pergunta,historico:msgs.slice(-10)})});
      const d=await r.json();
      const resp=d.resposta||d.erro||'Sem resposta';
      setMsgs(prev=>[...prev,{role:'model',text:resp,model:d.model,execResult:d.execResult}]);
      if(d.execResult)log('🔧 Executado: '+d.execResult.slice(0,80));
      if(d.deployUrl)log('🚀 Deploy: '+d.deployUrl);
    }catch(e:any){setMsgs(prev=>[...prev,{role:'model',text:'Erro: '+e.message}]);}
    finally{setLoading(false);}
  };

  const s:any={background:'#080810',color:'#e0e0f0',minHeight:'100vh',fontFamily:"'Inter',sans-serif",display:'flex',flexDirection:'column'};
  const btnAba=(a:string)=>({padding:'8px 18px',borderRadius:8,border:'none',cursor:'pointer',fontWeight:600,fontSize:12,
    background:aba===a?'#7c3aed':'#111',color:aba===a?'#fff':'#555',transition:'all .2s',letterSpacing:.3});
  const card:any={background:'#0f0f1a',border:'1px solid #1a1a2e',borderRadius:14,padding:18,marginBottom:14};
  const metric:any={background:'#080810',borderRadius:10,padding:'12px 14px',border:'1px solid #151530',textAlign:'center'};

  // Bio multi-rede otimizada
  const BIO=`🧠 psicologia.doc
Documentários anônimos de psicologia

📺 @psicologiadoc no YouTube
📸 Instagram: @psicologiadoc
🎵 TikTok: @psicologiadoc
📌 Pinterest: psicologiadoc

💬 Grupo VIP (apenas 1.024 vagas):
wa.me/[WHATSAPP_GROUP_LINK]
👆 Entre antes de fechar`;

  return(
    <div style={s}>
      {/* Header */}
      <div style={{background:'#0d0d1a',borderBottom:'1px solid #1a1a2e',padding:'12px 20px',display:'flex',alignItems:'center',justifyContent:'space-between',flexWrap:'wrap',gap:10}}>
        <div>
          <span style={{fontSize:17,fontWeight:700,color:'#7c3aed'}}>🧠 psicologia.doc</span>
          <span style={{fontSize:11,color:'#444',marginLeft:8}}>Cérebro Autônomo v7 • Daniela Coelho ~Dia 261</span>
        </div>
        <div style={{display:'flex',gap:8,alignItems:'center'}}>
          <span style={{fontSize:11,color:'#4ade80',background:'#051a0d',padding:'2px 10px',borderRadius:20,border:'1px solid #0a3a1a'}}>● ATIVO</span>
          <span style={{fontSize:11,color:'#7c3aed',background:'#150a2e',padding:'2px 10px',borderRadius:20,border:'1px solid #2a1a4e'}}>Groq→Gemini→GPT-4o-mini</span>
          {status&&<span style={{fontSize:11,color:'#666'}}>{status.total_producoes||0} roteiros</span>}
        </div>
      </div>

      {/* Métricas topo — compacto, só o essencial */}
      <div style={{background:'#0a0a16',borderBottom:'1px solid #141428',padding:'8px 20px',display:'flex',gap:24,flexWrap:'wrap',fontSize:11,color:'#444'}}>
        <span>📊 Score médio: <b style={{color:'#4ade80'}}>{status?.score_medio||'—'}</b></span>
        <span>💬 WA membros: <b style={{color:'#06b6d4'}}>{membrosWA||'—'}/1024</b></span>
        <span>🗓 Dia atual: <b style={{color:'#f59e0b'}}>{status?.dia_atual||1}</b></span>
        <span>📅 Revelação Daniela: <b style={{color:'#a78bfa'}}>Dia 261 ~31/dez/2026</b></span>
      </div>

      {/* Abas */}
      <div style={{padding:'12px 20px 0',display:'flex',gap:6,borderBottom:'1px solid #111',flexWrap:'wrap'}}>
        {[['executor','🧠 Executor IA'],['status','📊 Status'],['whatsapp','💬 WhatsApp'],['plano','🗓 Plano'],['log','📋 Log'],['bios','📣 Bios']].map(([a,l])=>(
          <button key={a} style={btnAba(a)} onClick={()=>setAba(a)}>{l}</button>
        ))}
      </div>

      <div style={{flex:1,overflow:'auto',padding:20}}>

        {/* EXECUTOR IA */}
        {aba==='executor'&&(
          <div style={{display:'flex',flexDirection:'column',height:'72vh'}}>
            <div style={{marginBottom:10,fontSize:12,color:'#444',lineHeight:1.6}}>
              ⚡ Executor IA — pode editar código no GitHub, analisar métricas, criar rotas, otimizar deploys, planejar estratégias. Fale como CTO.
            </div>
            <div ref={chatRef} style={{flex:1,overflow:'auto',display:'flex',flexDirection:'column',gap:10,paddingBottom:10}}>
              {msgs.map((m,i)=>(
                <div key={i} style={{display:'flex',justifyContent:m.role==='user'?'flex-end':'flex-start'}}>
                  <div style={{maxWidth:'88%',background:m.role==='user'?'#2a0d6e':'#0f0f1e',border:'1px solid '+(m.role==='user'?'#4a1da4':'#1a1a2e'),borderRadius:12,padding:'10px 14px'}}>
                    <div style={{fontSize:13,lineHeight:1.65,whiteSpace:'pre-wrap'}}>{m.text}</div>
                    {(m as any).model&&<div style={{fontSize:10,color:'#333',marginTop:4}}>{(m as any).model}</div>}
                    {(m as any).execResult&&<div style={{fontSize:11,color:'#4ade80',marginTop:6,padding:'4px 8px',background:'#030f03',borderRadius:6}}>✅ {(m as any).execResult}</div>}
                  </div>
                </div>
              ))}
              {loading&&<div style={{color:'#333',fontSize:13,textAlign:'center'}}>⟳ executando...</div>}
            </div>
            <div style={{display:'flex',gap:8,paddingTop:10,borderTop:'1px solid #111'}}>
              <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>e.key==='Enter'&&!e.shiftKey&&enviar()}
                placeholder="Ex: analise os roteiros com maior score e diga o padrão, ou: otimize o vercel.json para mais crons..."
                style={{flex:1,background:'#0f0f1a',border:'1px solid #1a1a2e',borderRadius:10,padding:'10px 14px',color:'#e0e0f0',fontSize:13,outline:'none'}}/>
              <button onClick={enviar} disabled={loading}
                style={{background:loading?'#2a1a4e':'#7c3aed',border:'none',borderRadius:10,padding:'10px 22px',color:'#fff',cursor:loading?'not-allowed':'pointer',fontWeight:700,fontSize:13}}>
                {loading?'...':'▶'}
              </button>
            </div>
          </div>
        )}

        {/* STATUS */}
        {aba==='status'&&(
          <div>
            <div style={card}>
              <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill,minmax(130px,1fr))',gap:10}}>
                {[['Roteiros',status?.total_producoes],['Score Médio',status?.score_medio],['Memória',status?.topicos_em_memoria],['WA Membros',membrosWA+'/1024']].map(([k,v])=>(
                  <div key={k} style={metric}><div style={{fontSize:10,color:'#444',marginBottom:4}}>{k}</div><div style={{fontSize:22,fontWeight:700,color:'#7c3aed'}}>{v??'—'}</div></div>
                ))}
              </div>
            </div>
            {status?.ultimas_producoes?.length>0&&(
              <div style={card}>
                <div style={{fontSize:12,color:'#555',marginBottom:10}}>Últimas produções</div>
                {status.ultimas_producoes.map((p:any,i:number)=>(
                  <div key={i} style={{display:'flex',justifyContent:'space-between',padding:'6px 0',borderBottom:'1px solid #111',fontSize:12}}>
                    <span style={{color:'#bbb'}}>{p.topic}</span>
                    <div style={{display:'flex',gap:10,fontSize:11}}>
                      <span style={{color:p.score>=90?'#4ade80':p.score>=80?'#f59e0b':'#f87171'}}>{p.score} pts</span>
                      <span style={{color:'#333'}}>{p.modelo||'groq'}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* WHATSAPP */}
        {aba==='whatsapp'&&(
          <div>
            <div style={card}>
              <div style={{fontSize:13,color:'#555',marginBottom:12}}>Agente WhatsApp Autônomo</div>
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:12,marginBottom:14}}>
                <div style={metric}><div style={{fontSize:10,color:'#444'}}>Membros</div><div style={{fontSize:24,fontWeight:700,color:'#06b6d4'}}>{membrosWA}/1024</div></div>
                <div style={metric}><div style={{fontSize:10,color:'#444'}}>Revelação</div><div style={{fontSize:16,fontWeight:700,color:'#f59e0b'}}>Dia 261</div></div>
              </div>
              <div style={{fontSize:12,color:'#444',lineHeight:2}}>
                <div>✅ <b style={{color:'#4ade80'}}>Agente ativo</b> — mensagens humanizadas em horários aleatórios (8h-22h SP)</div>
                <div>🎭 Persona: membro anônimo empático 28-35 anos, sem revelar IA</div>
                <div>⏰ Delay aleatório: 2-45 min por mensagem (humanização)</div>
                <div>🔍 Lê e responde mensagens do grupo quando detecta angústia/tristeza</div>
                <div>🎯 Meta: 1.024 membros engajados até Dia 261</div>
                <div>🗓 <b style={{color:'#a78bfa'}}>31/dez/2026</b>: revela Daniela Coelho psicóloga → agenda consultas</div>
              </div>
              {waStatus&&(
                <div style={{marginTop:14,background:'#030f03',borderRadius:8,padding:12,fontSize:12,border:'1px solid #0a2a0a'}}>
                  <div style={{color:'#4ade80',marginBottom:4}}>Última mensagem do agente:</div>
                  <div style={{color:'#ccc',fontStyle:'italic'}}>"{waStatus.mensagem}"</div>
                  <div style={{color:'#333',fontSize:10,marginTop:4}}>modelo: {waStatus.modelo} • delay: {waStatus.delay_min}min</div>
                </div>
              )}
            </div>
            <div style={card}>
              <div style={{fontSize:12,color:'#555',marginBottom:10}}>Configurar para ativar envio real</div>
              <div style={{fontSize:11,color:'#333',lineHeight:2}}>
                <div>1. Crie conta Meta Business → WhatsApp Business API</div>
                <div>2. Adicione no Vercel: <code style={{color:'#7c3aed'}}>WHATSAPP_TOKEN</code>, <code style={{color:'#7c3aed'}}>WHATSAPP_PHONE_ID</code>, <code style={{color:'#7c3aed'}}>WHATSAPP_GROUP_ID</code></div>
                <div>3. Configure webhook: <code style={{color:'#06b6d4'}}>repovazio.vercel.app/api/whatsapp</code></div>
                <div>4. Token de verificação: <code style={{color:'#4ade80'}}>psicologiadoc_webhook</code></div>
              </div>
            </div>
          </div>
        )}

        {/* PLANO */}
        {aba==='plano'&&(
          <div>
            <div style={card}>
              <div style={{fontSize:13,color:'#555',marginBottom:14}}>Planejamento — Revelação Daniela Coelho 31/dez/2026</div>
              {plano.length===0&&(
                <div style={{fontSize:12,color:'#333'}}>Carregando plano...</div>
              )}
              {plano.map((p:any,i:number)=>(
                <div key={i} style={{display:'flex',gap:14,padding:'10px 0',borderBottom:'1px solid #111',alignItems:'flex-start'}}>
                  <div style={{fontSize:20,fontWeight:700,color:p.executado?'#4ade80':'#333',minWidth:50,textAlign:'center'}}>
                    {p.executado?'✅':'◯'}<div style={{fontSize:10,color:'#333',fontWeight:400}}>Dia {p.dia}</div>
                  </div>
                  <div>
                    <div style={{fontSize:12,color:p.fase==='revelacao'?'#f59e0b':'#7c3aed',fontWeight:600,marginBottom:2}}>{p.fase}</div>
                    <div style={{fontSize:13,color:'#bbb'}}>{p.acao}</div>
                    {p.resultado&&<div style={{fontSize:11,color:'#4ade80',marginTop:2}}>↳ {p.resultado}</div>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* LOG */}
        {aba==='log'&&(
          <div style={card}>
            <div style={{fontSize:12,color:'#555',marginBottom:10}}>Log automático em tempo real</div>
            {autoLog.length===0&&<div style={{fontSize:12,color:'#222'}}>Aguardando eventos...</div>}
            {autoLog.map((l:any,i:number)=>(
              <div key={i} style={{fontSize:11,padding:'4px 0',borderBottom:'1px solid #0a0a0a',display:'flex',gap:10}}>
                <span style={{color:'#333',flexShrink:0,fontFamily:'monospace'}}>{l.hora}</span>
                <span style={{color:'#888'}}>{l.msg}</span>
              </div>
            ))}
          </div>
        )}

        {/* BIOS */}
        {aba==='bios'&&(
          <div>
            <div style={card}>
              <div style={{fontSize:13,color:'#555',marginBottom:12}}>Bio Universal — copiar para todas as redes</div>
              <pre style={{fontSize:12,background:'#080810',borderRadius:8,padding:14,color:'#aaa',lineHeight:1.9,border:'1px solid #111',whiteSpace:'pre-wrap',wordBreak:'break-word'}}>{BIO}</pre>
              <div style={{fontSize:11,color:'#333',marginTop:10,lineHeight:1.8}}>
                ✅ Colocar esta bio em: YouTube | Instagram | TikTok | Pinterest<br/>
                ✅ Substituir [WHATSAPP_GROUP_LINK] pelo link real do grupo<br/>
                ✅ Cada plataforma deve linkar para as demais + WhatsApp<br/>
                ✅ Limite de 1.024 membros cria urgência e exclusividade
              </div>
            </div>
            <div style={card}>
              <div style={{fontSize:12,color:'#555',marginBottom:10}}>Estratégia de crescimento cross-platform</div>
              <div style={{fontSize:12,color:'#444',lineHeight:2.1}}>
                <div>📺 <b style={{color:'#aaa'}}>YouTube</b>: vídeos 22-28min + Shorts (extraídos do roteiro) → bio com link WA</div>
                <div>📸 <b style={{color:'#aaa'}}>Instagram</b>: Reels (Shorts) + Stories com "entre no grupo" → link na bio</div>
                <div>🎵 <b style={{color:'#aaa'}}>TikTok</b>: clips 60-90s + CTA para WA no comentário fixado</div>
                <div>📌 <b style={{color:'#aaa'}}>Pinterest</b>: frases visuais de psicologia → tráfego passivo para YouTube</div>
                <div>💬 <b style={{color:'#aaa'}}>WhatsApp</b>: grupo fecha em 1.024 → membros viram clientes da Daniela em dez/2026</div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}