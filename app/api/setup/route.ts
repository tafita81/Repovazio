export const dynamic='force-dynamic';
import{createClient}from'@supabase/supabase-js';
export async function GET(){
  const sb=createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!,process.env.SUPABASE_SERVICE_KEY!);
  const sqls=[
    `CREATE TABLE IF NOT EXISTS whatsapp_mensagens(id BIGSERIAL PRIMARY KEY,timestamp TIMESTAMPTZ DEFAULT now(),remetente TEXT,remetente_nome TEXT,conteudo TEXT,tipo TEXT DEFAULT 'texto',grupo_id TEXT,respondido BOOLEAN DEFAULT false,sentimento TEXT,topico_detectado TEXT)`,
    `CREATE TABLE IF NOT EXISTS whatsapp_respostas(id BIGSERIAL PRIMARY KEY,timestamp TIMESTAMPTZ DEFAULT now(),mensagem_id BIGINT,resposta TEXT NOT NULL,modelo_ia TEXT,enviado BOOLEAN DEFAULT false,horario_programado TIMESTAMPTZ,motivo TEXT)`,
    `CREATE TABLE IF NOT EXISTS whatsapp_membros(id BIGSERIAL PRIMARY KEY,phone TEXT UNIQUE,nome TEXT,entrada TIMESTAMPTZ DEFAULT now(),engajamento INT DEFAULT 0,ultima_mensagem TIMESTAMPTZ,perfil_psicologico TEXT,nivel_interesse INT DEFAULT 1)`,
    `CREATE TABLE IF NOT EXISTS planejamento_revelacao(id BIGSERIAL PRIMARY KEY,dia INT NOT NULL,data_prevista DATE,fase TEXT,acao TEXT,executado BOOLEAN DEFAULT false,resultado TEXT,criado_em TIMESTAMPTZ DEFAULT now())`,
    `INSERT INTO planejamento_revelacao(dia,fase,acao) VALUES(1,'lancamento','Publicar 1o video YouTube — ativa Dia 1'),(30,'crescimento','Meta 500 subs — WhatsApp grupo ativo'),(60,'engajamento','Meta 1000 subs — solicitar AdSense'),(90,'monetizacao','Primeiros ganhos AdSense — afiliados'),(120,'expansao','Meta 5000 subs — TikTok Instagram ativos'),(180,'consolidacao','Meta 10000 subs — curso gratuito lead magnet'),(240,'pre-revelacao','Hints sobre Daniela Coelho nos videos'),(261,'revelacao','REVELAR Daniela Coelho Psicologa — agenda consultas online'),(270,'pos-revelacao','Converter WhatsApp em clientes consulta'),(365,'escala','Meta 100000 subs — canal EUA ingles') ON CONFLICT DO NOTHING`,
  ];
  const results=[];
  for(const sql of sqls){
    const{error}=await sb.rpc('exec_sql',{sql}).single().catch(()=>({error:'rpc_unavailable'}));
    // fallback: tentar direto
    if(error){
      // usar fetch direto
      const r=await fetch(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest/v1/rpc/exec_sql`,{method:'POST',headers:{'Content-Type':'application/json',apikey:process.env.SUPABASE_SERVICE_KEY!,Authorization:`Bearer ${process.env.SUPABASE_SERVICE_KEY}`},body:JSON.stringify({query:sql})});
      results.push({sql:sql.slice(0,50),status:r.status});
    } else {results.push({sql:sql.slice(0,50),ok:true});}
  }
  return Response.json({setup_done:true,results});
}