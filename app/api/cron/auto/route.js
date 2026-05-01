import{NextResponse}from'next/server';
const SBU=process.env.NEXT_PUBLIC_SUPABASE_URL;
const SBK=process.env.SUPABASE_SERVICE_KEY;
const GK=process.env.GROQ_API_KEY;
export const maxDuration=60;
export const dynamic='force-dynamic';
export async function GET(){
  const inicio=new Date().toISOString();
  const acoes=[];
  try{
    if(!GK||!SBU||!SBK){
      return NextResponse.json({ok:false,erro:'Env vars nao configuradas'},{status:500});
    }
    // Buscar topico com maior score da cerebro_memoria
    let topico='Psicologia e autoconhecimento';
    try{
      const r=await fetch(SBU+'/rest/v1/cerebro_memoria?select=topic,score&order=score.desc&limit=1',{
        headers:{apikey:SBK,Authorization:'Bearer '+SBK}
      });
      if(r.ok){
        const d=await r.json();
        if(d[0]&&d[0].topic&&!d[0].topic.match(/^d{13}$/)&&!d[0].topic.startsWith('ciclo_')){
          topico=d[0].topic;
        }
      }
    }catch(e){acoes.push({nome:'buscar_topico',status:'erro'});}
    // Gerar roteiro via Groq
    let roteiro=null;
    try{
      const prompt='Crie um roteiro PT-BR para video YouTube sobre: '+topico+'. Titulo, 3 pontos principais, conclusao. Maximo 300 palavras.';
      const gr=await fetch('https://api.groq.com/openai/v1/chat/completions',{
        method:'POST',
        headers:{Authorization:'Bearer '+GK,'Content-Type':'application/json'},
        body:JSON.stringify({model:'llama-3.3-70b-versatile',messages:[{role:'user',content:prompt}],max_tokens:400,temperature:0.7})
      });
      if(gr.ok){
        const gd=await gr.json();
        roteiro=gd.choices?.[0]?.message?.content||null;
        acoes.push({nome:'gerar_roteiro',status:'ok'});
      }else{
        acoes.push({nome:'gerar_roteiro',status:'erro_'+gr.status});
      }
    }catch(e){acoes.push({nome:'gerar_roteiro',status:'excecao'});}
    // Salvar na tabela registros
    if(roteiro){
      try{
        const ir=await fetch(SBU+'/rest/v1/registros',{
          method:'POST',
          headers:{apikey:SBK,Authorization:'Bearer '+SBK,'Content-Type':'application/json',Prefer:'return=minimal'},
          body:JSON.stringify({topic:topico,script:roteiro,score:75,status:'gerado'})
        });
        acoes.push({nome:'salvar_registro',status:ir.ok?'ok':'erro_'+ir.status});
      }catch(e){acoes.push({nome:'salvar_registro',status:'excecao'});}
    }
    // Log na ia_cache
    const logKey='cron_log_'+new Date().toISOString().slice(0,13).replace(':','').replace('T','_');
    try{
      await fetch(SBU+'/rest/v1/ia_cache',{
        method:'POST',
        headers:{apikey:SBK,Authorization:'Bearer '+SBK,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},
        body:JSON.stringify({cache_key:logKey,value:JSON.stringify({iniciado_em:inicio,topico,acoes,roteiro_len:roteiro?.length||0}),expires_at:new Date(Date.now()+7*24*3600000).toISOString()})
      });
    }catch(e){}
    return NextResponse.json({ok:true,topico,acoes,roteiro_len:roteiro?.length||0});
  }catch(e){
    return NextResponse.json({ok:false,erro:e.message},{status:500});
  }
}
