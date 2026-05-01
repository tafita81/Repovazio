// app/api/cron/auto/route.js - CORRIGIDO v2
// Remove o bug que envenenava cerebro_memoria com ciclo_TIMESTAMP
export const dynamic='force-dynamic';
export const maxDuration=60;

const SU=process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK=process.env.SUPABASE_SERVICE_KEY;

async function db(p,m,b){
  if(!SU||!SK)return null;
  try{
    const r=await fetch(SU+'/rest/v1/'+p,{
      method:m||'GET',
      headers:{'Content-Type':'application/json',apikey:SK,Authorization:'Bearer '+SK,
        Prefer:m==='POST'?'return=representation':'''},
      body:b?JSON.stringify(b):undefined
    });
    return r.ok?r.json():null;
  }catch{return null}
}

export async function GET(){
  const ini=Date.now();
  const horaSP=new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});
  const res={iniciado_em:new Date().toISOString(),hora_sp:horaSP,acoes:[]};
  const base='https://repovazio.vercel.app';

  try{
    const r=await fetch(base+'/api/cerebro',{signal:AbortSignal.timeout(50000)});
    const d=await r.json();
    res.acoes.push({nome:'cerebro',status:r.ok?'ok':'falha',score:d.score,topic:d.topic,model:d.model});
  }catch(e){
    res.acoes.push({nome:'cerebro',status:'erro',erro:e.message});
  }

  try{
    const r=await fetch(base+'/api/cerebro/aprender',{signal:AbortSignal.timeout(15000)});
    res.acoes.push({nome:'aprender',status:r.ok?'ok':'falha'});
  }catch{
    res.acoes.push({nome:'aprender',status:'erro'});
  }

  const h=parseInt(new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo',hour:'2-digit'}).slice(0,2));
  if(h>=8&&h<22){
    try{
      const r=await fetch(base+'/api/ranking',{signal:AbortSignal.timeout(15000)});
      const d=await r.json();
      res.acoes.push({nome:'ranking',status:r.ok?'ok':'falha',total:d.total});
    }catch{
      res.acoes.push({nome:'ranking',status:'erro'});
    }
  }

  const ok=res.acoes.filter(a=>a.status==='ok').length;
  await db('ia_cache','POST',{
    cache_key:'cron_log_'+Date.now(),
    value:JSON.stringify({...res,ok_count:ok}),
    expires_at:new Date(Date.now()+7*24*60*60*1000).toISOString()
  });

  res.duracao_ms=Date.now()-ini;
  res.ok_count=ok;
  return Response.json(res);
}