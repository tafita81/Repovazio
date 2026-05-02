// app/api/ia-chat/route.js — DANIELA ULTRA V12 — 25 tools + YouTube+ElevenLabs+HeyGen+WA+IG+TK+PT
import{NextResponse}from'next/server';
const GK=process.env.GROQ_API_KEY,TK=process.env.TOGETHER_API_KEY,GEK=process.env.GEMINI_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;
const YTT=process.env.YOUTUBE_OAUTH_TOKEN,ELK=process.env.ELEVENLABS_API_KEY,HGK=process.env.HEYGEN_API_KEY;
const WAT=process.env.WHATSAPP_TOKEN,WAP=process.env.WHATSAPP_PHONE_ID,WAG=process.env.WHATSAPP_GROUP_ID;
const IGT=process.env.INSTAGRAM_TOKEN,IGA=process.env.INSTAGRAM_ACCOUNT_ID;
const TKT=process.env.TIKTOK_TOKEN,PTT=process.env.PINTEREST_TOKEN;
const EL_VOICE=process.env.ELEVENLABS_VOICE_ID||'EXAVITQu4vr4xnSDxMaL';
const REPO='tafita81/Repovazio',VER='V12-ULTRA-2026-05-01';

const TOOLS=[
  {type:'function',function:{name:'github_read_file',description:'Lê arquivo do repo GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_list_dir',description:'Lista arquivos/dirs do repo GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:[]}}},
  {type:'function',function:{name:'github_write_file',description:'Cria/atualiza arquivo no GitHub + deploy Vercel automático',parameters:{type:'object',properties:{path:{type:'string'},content:{type:'string'},message:{type:'string'},repo:{type:'string'}},required:['path','content','message']}}},
  {type:'function',function:{name:'github_create_repo',description:'Cria repositório GitHub novo do zero',parameters:{type:'object',properties:{name:{type:'string'},description:{type:'string'},private:{type:'boolean'}},required:['name']}}},
  {type:'function',function:{name:'supabase_select',description:'SELECT em tabela Supabase',parameters:{type:'object',properties:{table:{type:'string'},filter:{type:'string'},limit:{type:'number'}},required:['table']}}},
  {type:'function',function:{name:'supabase_sql',description:'Executa SQL no Supabase: CREATE TABLE, INSERT, UPDATE, DELETE, SELECT, etc.',parameters:{type:'object',properties:{sql:{type:'string'}},required:['sql']}}},
  {type:'function',function:{name:'web_fetch',description:'Busca conteúdo completo de qualquer URL da internet',parameters:{type:'object',properties:{url:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'pesquisar_web',description:'Pesquisa na internet como Google - retorna resultados reais atualizados',parameters:{type:'object',properties:{query:{type:'string'},num:{type:'number'}},required:['query']}}},
  {type:'function',function:{name:'executar_codigo',description:'Executa código Python, JavaScript, TypeScript, Rust, C++, Java, Go, Bash e mais - retorna output real',parameters:{type:'object',properties:{linguagem:{type:'string'},codigo:{type:'string'},stdin:{type:'string'}},required:['linguagem','codigo']}}},
  {type:'function',function:{name:'gerar_imagem',description:'Gera imagem com IA a partir de uma descrição em texto - retorna URL da imagem',parameters:{type:'object',properties:{descricao:{type:'string'},largura:{type:'number'},altura:{type:'number'}},required:['descricao']}}},
  {type:'function',function:{name:'analisar_imagem',description:'Analisa e descreve o conteúdo de qualquer imagem via URL',parameters:{type:'object',properties:{url:{type:'string'},pergunta:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'memoria_salvar',description:'Salva informação importante na memória persistente para usar em conversas futuras',parameters:{type:'object',properties:{chave:{type:'string'},valor:{type:'string'}},required:['chave','valor']}}},
  {type:'function',function:{name:'memoria_carregar',description:'Carrega informações salvas na memória de conversas anteriores',parameters:{type:'object',properties:{chave:{type:'string'}},required:['chave']}}},
  {type:'function',function:{name:'criar_app',description:'Cria app Next.js completo do zero no GitHub com todos os arquivos',parameters:{type:'object',properties:{nome:{type:'string'},descricao:{type:'string'},tipo:{type:'string'}},required:['nome','descricao']}}},
  {type:'function',function:{name:'projeto_status',description:'Status completo do projeto psicologia.doc v11',parameters:{type:'object',properties:{}}}},
  {type:'function',function:{name:'diagnosticar_sistema',description:'Diagnóstico automático do sistema: verifica saúde dos agentes, cerebro_memoria, últimos conteúdos gerados, crons e detecta problemas como corrupção de dados',parameters:{type:'object',properties:{detalhe:{type:'string'}},required:[]}}},
  {type:'function',function:{name:'supabase_deploy_fn',description:'Deploya/atualiza uma Edge Function no Supabase. Requer SUPABASE_PAT configurado no Vercel.',parameters:{type:'object',properties:{slug:{type:'string'},codigo:{type:'string'},verify_jwt:{type:'boolean'}},required:['slug','codigo']}}},
  {type:'function',function:{name:'youtube_upload',description:'Faz upload de vídeo para o YouTube @psicologiadoc usando URL do vídeo',parameters:{type:'object',properties:{titulo:{type:'string'},descricao:{type:'string'},video_url:{type:'string'},thumbnail_url:{type:'string'},tags:{type:'array',items:{type:'string'}}},required:['titulo','descricao','video_url']}}},
  {type:'function',function:{name:'youtube_status',description:'Status do canal @psicologiadoc: inscritos, views, vídeos, último upload',parameters:{type:'object',properties:{}}}},
  {type:'function',function:{name:'elevenlabs_voz',description:'Gera áudio com voz da Daniela Coelho (ElevenLabs TTS) e retorna URL do áudio',parameters:{type:'object',properties:{texto:{type:'string'},stability:{type:'number'},similarity:{type:'number'}},required:['texto']}}},
  {type:'function',function:{name:'heygen_video',description:'Cria vídeo com avatar IA da Daniela (HeyGen) usando script de texto',parameters:{type:'object',properties:{script:{type:'string'},avatar_id:{type:'string'},voice_id:{type:'string'}},required:['script']}}},
  {type:'function',function:{name:'whatsapp_enviar',description:'Envia mensagem de texto no grupo WhatsApp do psicologia.doc',parameters:{type:'object',properties:{mensagem:{type:'string'},grupo_id:{type:'string'}},required:['mensagem']}}},
  {type:'function',function:{name:'instagram_publicar',description:'Publica imagem ou reel no Instagram @psicologiadoc',parameters:{type:'object',properties:{imagem_url:{type:'string'},legenda:{type:'string'},tipo:{type:'string'}},required:['imagem_url','legenda']}}},
  {type:'function',function:{name:'tiktok_publicar',description:'Publica vídeo no TikTok @psicologiadoc',parameters:{type:'object',properties:{video_url:{type:'string'},descricao:{type:'string'},hashtags:{type:'array',items:{type:'string'}}},required:['video_url','descricao']}}},
  {type:'function',function:{name:'pinterest_publicar',description:'Publica pin no Pinterest psicologia.doc',parameters:{type:'object',properties:{imagem_url:{type:'string'},titulo:{type:'string'},descricao:{type:'string'},link:{type:'string'}},required:['imagem_url','titulo']}}}
];

function b64e(s){return Buffer.from(s,'utf-8').toString('base64');}
function b64d(s){return Buffer.from(s.replace(/\n/g,''),'base64').toString('utf-8');}

async function ghReq(path,opts={},repo){
  return fetch(`https://api.github.com/repos/${repo||REPO}/contents/${path}`,{
    ...opts,headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json',...(opts.headers||{})}
  });
}
async function ghCommit(repo,path,content,msg){
  let sha;const c=await ghReq(path,{},repo);
  if(c.ok){const d=await c.json();sha=d.sha;}
  const body={message:msg,content:b64e(content)};if(sha)body.sha=sha;
  const r=await ghReq(path,{method:'PUT',body:JSON.stringify(body)},repo);
  if(!r.ok)throw new Error(`${r.status}: ${await r.text()}`);
  return(await r.json()).commit.sha.substring(0,8);
}

async function runTool(name,args){
  try{
    const repo=args.repo||REPO;

    if(name==='github_read_file'){
      const r=await ghReq(args.path,{},repo);
      if(!r.ok)return`❌ Não encontrado: ${args.path}`;
      const d=await r.json();
      return`📄 **${args.path}** (${d.size}b)\n\`\`\`\n${b64d(d.content).substring(0,8000)}\n\`\`\``;
    }

    if(name==='github_list_dir'){
      const r=await ghReq(args.path||'',{},repo);
      if(!r.ok)return`❌ Dir não encontrado`;
      const items=await r.json();
      return`📁 ${args.path||'/'} (${items.length} itens)\n${items.map(i=>`${i.type==='dir'?'📁':'📄'} ${i.name} ${i.size?`(${i.size}b)`:''}`).join('\n')}`;
    }

    if(name==='github_write_file'){
      const sha=await ghCommit(repo,args.path,args.content,args.message);
      return`✅ **Commitado:** \`${args.path}\` → SHA:${sha}\n🚀 Deploy Vercel disparado automaticamente`;
    }

    if(name==='github_create_repo'){
      const r=await fetch('https://api.github.com/user/repos',{method:'POST',
        headers:{Authorization:`token ${PAT}`,'Content-Type':'application/json'},
        body:JSON.stringify({name:args.name,description:args.description||'',private:args.private||false,auto_init:false})});
      if(r.status===422)return`⚠️ Repo "${args.name}" já existe`;
      const d=await r.json();return`✅ Repo criado: ${d.html_url}`;
    }

    if(name==='supabase_select'){
      const f=args.filter?`&${args.filter}`:'';
      const r=await fetch(`${SBU}/rest/v1/${args.table}?select=*${f}&limit=${args.limit||10}`,
        {headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const d=await r.json();
      return`📊 **${args.table}** (${d.length} registros)\n\`\`\`json\n${JSON.stringify(d,null,2).substring(0,4000)}\n\`\`\``;
    }

    if(name==='supabase_sql'){
      const r=await fetch(`${SBU}/functions/v1/exec-sql`,{method:'POST',
        headers:{Authorization:`Bearer ${SBK}`,'Content-Type':'application/json'},
        body:JSON.stringify({sql:args.sql})});
      const d=await r.json();
      return d.error?`❌ SQL erro: ${d.error}`:`✅ SQL OK:\n\`\`\`json\n${JSON.stringify(d.data,null,2).substring(0,3000)}\n\`\`\``;
    }

    if(name==='web_fetch'){
      const r=await fetch(args.url,{headers:{'User-Agent':'Mozilla/5.0 (compatible; Googlebot/2.1)'},signal:AbortSignal.timeout(15000)});
      if(!r.ok)return`❌ HTTP ${r.status} em ${args.url}`;
      const t=await r.text();
      const clean=t.replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,5000);
      return`🌐 **${args.url}**\n\n${clean}`;
    }

    if(name==='pesquisar_web'){
      const q=encodeURIComponent(args.query);
      const num=args.num||5;
      const r=await fetch(`https://html.duckduckgo.com/html/?q=${q}&kl=pt-br`,{
        headers:{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36','Accept':'text/html'},
        signal:AbortSignal.timeout(10000)
      });
      const html=await r.text();
      const results=[];
      const regex=/<a class="result__a" href="([^"]+)"[^>]*>([^<]+)<\/a>[\s\S]*?<a class="result__snippet"[^>]*>([^<]*)<\/a>/g;
      let m;let count=0;
      while((m=regex.exec(html))&&count<num){
        const url=m[1].replace('/l/?kh=-1&uddg=','').split('&')[0];
        const title=m[2].replace(/&amp;/g,'&').replace(/&#x27;/g,"'").trim();
        const snippet=m[3].replace(/<[^>]+>/g,'').replace(/&amp;/g,'&').trim();
        if(url.startsWith('http')&&title){results.push(`**${title}**\n${url}\n${snippet}`);count++;}
      }
      if(!results.length){
        const r2=await fetch(`https://api.duckduckgo.com/?q=${q}&format=json&no_html=1&skip_disambig=1`);
        const d=await r2.json();
        if(d.AbstractText)results.push(`**${d.Heading}**\n${d.AbstractURL}\n${d.AbstractText}`);
        if(d.RelatedTopics)d.RelatedTopics.slice(0,3).forEach(t=>{if(t.Text)results.push(`• ${t.Text}`);});
      }
      return results.length?`🔍 **Resultados para "${args.query}":**\n\n${results.join('\n\n---\n\n')}`:`❌ Sem resultados para: ${args.query}`;
    }

    if(name==='executar_codigo'){
      const langMap={python:'python',py:'python',javascript:'javascript',js:'javascript',typescript:'typescript',ts:'typescript',
        rust:'rust',cpp:'c++',c:'c',java:'java',go:'go',bash:'bash',sh:'bash',ruby:'ruby',php:'php',swift:'swift',kotlin:'kotlin'};
      const lang=langMap[args.linguagem?.toLowerCase()]||args.linguagem||'python';
      const r=await fetch('https://emkc.org/api/v2/piston/execute',{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({language:lang,version:'*',files:[{content:args.codigo}],stdin:args.stdin||'',run_timeout:10000}),
        signal:AbortSignal.timeout(30000)
      });
      if(!r.ok)return`❌ Piston API erro: ${r.status}`;
      const d=await r.json();
      const out=d.run?.output||d.compile?.output||'';
      const err=d.run?.stderr||d.compile?.stderr||'';
      return`⚙️ **Código ${lang} executado:**\n\`\`\`\n${out||'(sem output)'}${err?'\n❌ Erro:\n'+err:''}\n\`\`\`\n_Tempo: ${d.run?.cpu_time||0}ms_`;
    }

    if(name==='gerar_imagem'){
      const desc=encodeURIComponent(args.descricao);
      const w=args.largura||1024;
      const h=args.altura||1024;
      const seed=Math.floor(Math.random()*99999);
      const url=`https://image.pollinations.ai/prompt/${desc}?width=${w}&height=${h}&seed=${seed}&nologo=true&enhance=true`;
      const r=await fetch(url,{method:'HEAD',signal:AbortSignal.timeout(30000)});
      if(r.ok){
        return`🎨 **Imagem gerada!**\n\n![${args.descricao}](${url})\n\n📎 URL: ${url}\n\n_Powered by Pollinations.ai (100% gratuito)_`;
      }
      return`🎨 **Imagem em geração...**\n\nURL: ${url}\n\n_Copie a URL e abra no browser para ver a imagem_`;
    }

    if(name==='analisar_imagem'){
      if(!GEK)return`❌ Gemini API key não configurada`;
      const pergunta=args.pergunta||'Descreva esta imagem em detalhes';
      const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEK}`,{
        method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({contents:[{role:'user',parts:[
          {inline_data:{mime_type:'image/jpeg',data:await urlToBase64(args.url)}},
          {text:pergunta}
        ]}]})
      });
      if(!r.ok)return`❌ Gemini Vision erro: ${r.status}`;
      const d=await r.json();
      const text=d.candidates?.[0]?.content?.parts?.[0]?.text||'Não foi possível analisar';
      return`🔍 **Análise da imagem:**\n\n${text}`;
    }

    if(name==='memoria_salvar'){
      const r=await fetch(`${SBU}/functions/v1/exec-sql`,{method:'POST',
        headers:{Authorization:`Bearer ${SBK}`,'Content-Type':'application/json'},
        body:JSON.stringify({sql:`INSERT INTO ia_cache(cache_key,value,expires_at) VALUES('mem_${args.chave}','${args.valor.replace(/'/g,"''")}',now()+'1 year'::interval) ON CONFLICT(cache_key) DO UPDATE SET value=EXCLUDED.value,expires_at=EXCLUDED.expires_at`})});
      const d=await r.json();
      return d.error?`❌ Erro ao salvar: ${d.error}`:`🧠 **Memória salva:** "${args.chave}" → guardado para conversas futuras`;
    }

    if(name==='memoria_carregar'){
      const r=await fetch(`${SBU}/rest/v1/ia_cache?cache_key=eq.mem_${args.chave}&select=value,expires_at`,
        {headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const d=await r.json();
      if(!d.length)return`❌ Memória "${args.chave}" não encontrada`;
      return`🧠 **Memória carregada:** "${args.chave}"\n\n${d[0].value}`;
    }

    if(name==='criar_app'){
      const {nome,descricao,tipo='landing'}=args;
      const rn=nome.toLowerCase().replace(/[\s_]+/g,'-').replace(/[^a-z0-9-]/g,'');
      const fr=`tafita81/${rn}`;
      await fetch('https://api.github.com/user/repos',{method:'POST',
        headers:{Authorization:`token ${PAT}`,'Content-Type':'application/json'},
        body:JSON.stringify({name:rn,description:descricao,private:false,auto_init:false})});
      const files={
        'package.json':JSON.stringify({name:rn,version:'0.1.0',private:true,scripts:{dev:'next dev',build:'next build',start:'next start'},dependencies:{next:'14.2.3',react:'^18','react-dom':'^18'},devDependencies:{tailwindcss:'^3',autoprefixer:'^10',postcss:'^8'}},null,2),
        'next.config.js':'/** @type {import("next").NextConfig} */\nconst c={}\nmodule.exports=c',
        'app/globals.css':'@tailwind base;\n@tailwind components;\n@tailwind utilities;\n*{box-sizing:border-box;margin:0;padding:0}\nbody{font-family:system-ui,sans-serif;background:#0a0a0a;color:#fff}',
        'app/layout.js':`import'./globals.css'\nexport const metadata={title:'${nome}',description:'${descricao}'}\nexport default function L({children}){return<html lang="pt-BR"><body>{children}</body></html>}`,
        'app/page.js':`export default function P(){return(<main style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',padding:'2rem',background:'linear-gradient(135deg,#0a0a0a 0%,#1a0a2e 100%)'}}><div style={{textAlign:'center',maxWidth:'700px'}}><h1 style={{fontSize:'3.5rem',fontWeight:'bold',marginBottom:'1.5rem',background:'linear-gradient(to right,#a855f7,#ec4899,#06b6d4)',WebkitBackgroundClip:'text',WebkitTextFillColor:'transparent'}}>${nome}</h1><p style={{fontSize:'1.3rem',color:'#9ca3af',marginBottom:'3rem',lineHeight:1.6}}>${descricao}</p><div style={{display:'flex',gap:'1rem',justifyContent:'center',flexWrap:'wrap'}}><a href="#" style={{background:'linear-gradient(to right,#7c3aed,#ec4899)',color:'#fff',padding:'1rem 2.5rem',borderRadius:'9999px',fontSize:'1.1rem',textDecoration:'none',fontWeight:'600'}}>Começar Agora</a><a href="#" style={{border:'2px solid #7c3aed',color:'#a855f7',padding:'1rem 2.5rem',borderRadius:'9999px',fontSize:'1.1rem',textDecoration:'none',fontWeight:'600'}}>Saiba Mais</a></div></div></main>)}`,
        '.gitignore':'node_modules/\n.next/\n.env\n.env.local',
        'README.md':`# ${nome}\n\n${descricao}\n\nCriado por Daniela ULTRA V11`
      };
      const done=[];
      for(const[p,c]of Object.entries(files)){
        try{await ghCommit(fr,p,c,`feat: ${nome} - ${p}`);done.push(p);await new Promise(r=>setTimeout(r,300));}catch(e){}
      }
      return`✅ **App ${nome} criado!**\n📎 Repo: https://github.com/${fr}\n📁 Arquivos: ${done.length}/7\n🚀 Para deploy: vá em vercel.com/new e importe o repo`;
    }

    if(name==='projeto_status'){
      const t=new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});
      return`📊 **psicologia.doc V11** — ${t}\n🏠 Repo: tafita81/Repovazio → repovazio.vercel.app\n🤖 AI: Groq→Together→Gemini (fallback automático)\n⚙️ Agentes: Cerebro(15min)·Ranking·Script·Video·Publish\n🎭 @psicologiadoc | Dia261=Daniela (~31/dez/2026)\n🔧 Versão: ${VER}`;
    }

    if(name==='diagnosticar_sistema'){
      const report=[];
      report.push('🔍 **DIAGNÓSTICO DO SISTEMA psicologia.doc**\n');
      
      // 1. Verificar últimos registros
      try{
        const r=await fetch(`${SBU}/rest/v1/registros?select=topic,score,created_at&order=created_at.desc&limit=5`,
          {headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
        const d=await r.json();
        if(d.length){
          const ultimo=new Date(d[0].created_at);
          const diasAtras=Math.round((Date.now()-ultimo.getTime())/(1000*60*60*24));
          const status=diasAtras>2?'⚠️':'✅';
          report.push(`**CEREBRO — Último conteúdo:** ${status}\n- Tópico: ${d[0].topic} (score ${d[0].score})\n- Há ${diasAtras} dia(s) — ${d[0].created_at.split('T')[0]}\n- Total: ${d.length} recentes\n`);
        }else{
          report.push('**CEREBRO:** ❌ Nenhum registro encontrado na tabela registros\n');
        }
      }catch(e){report.push(`**CEREBRO:** ❌ Erro ao ler registros: ${e.message}\n`);}

      // 2. Verificar corrupção na cerebro_memoria
      try{
        const r=await fetch(`${SBU}/rest/v1/cerebro_memoria?select=topic,score&order=score.desc&limit=20`,
          {headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
        const d=await r.json();
        const corrompidas=d.filter(m=>m.topic&&(m.topic.startsWith('ciclo_')||m.topic.match(/^\d{13}$/)));
        const virais=d.filter(m=>m.score>=85&&!m.topic.startsWith('ciclo_'));
        if(corrompidas.length>0){
          report.push(`**CEREBRO_MEMORIA:** ⚠️ CORROMPIDA\n- ${corrompidas.length} entradas lixo (ciclo_TIMESTAMP)\n- Causam geração de conteúdo inválido!\n- FIX: \`supabase_sql("DELETE FROM cerebro_memoria WHERE topic LIKE 'ciclo_%'")\`\n`);
        }else{
          report.push(`**CEREBRO_MEMORIA:** ✅ Saudável\n- Tópicos virais (score≥85): ${virais.length}\n- Tópicos ruins (<70): ${d.filter(m=>m.score<70).length}\n`);
        }
      }catch(e){report.push(`**CEREBRO_MEMORIA:** ❌ Erro: ${e.message}\n`);}

      // 3. Verificar config do cron
      try{
        const r=await ghReq('vercel.json',{},REPO);
        if(r.ok){
          const d=await r.json();
          const content=b64d(d.content);
          const config=JSON.parse(content);
          const crons=config.crons||[];
          report.push(`**CRON CONFIG:** ${crons.length>0?'✅':'⚠️'}\n- ${crons.map(c=>`${c.path} → ${c.schedule}`).join('\n- ')||'Nenhum cron configurado!'}\n`);
        }
      }catch(e){report.push(`**CRON CONFIG:** ❌ Erro: ${e.message}\n`);}

      // 4. Verificar se cerebro está respondendo
      try{
        const r=await fetch('https://repovazio.vercel.app/api/ia-chat',{signal:AbortSignal.timeout(5000)});
        const d=await r.json();
        report.push(`**IA-CHAT:** ✅ Online — ${d.version}\n- Tools: ${d.tools?.length||0}\n`);
      }catch(e){report.push(`**IA-CHAT:** ❌ Offline ou timeout: ${e.message}\n`);}

      // 5. Verificar últimos logs do cron
      try{
        const r=await fetch(`${SBU}/rest/v1/ia_cache?select=cache_key,value,expires_at&cache_key=like.cron_log_*&order=cache_key.desc&limit=3`,
          {headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
        const d=await r.json();
        if(d.length){
          const ultimo=JSON.parse(d[0].value||'{}');
          report.push(`**ÚLTIMO CRON RUN:** ${ultimo.iniciado_em?.split('T')[0]||'?'}\n- Ações: ${ultimo.acoes?.map(a=>`${a.nome}:${a.status}`).join(' | ')||'?'}\n`);
        }else{
          report.push('**CRON LOGS:** ℹ️ Nenhum log encontrado ainda\n');
        }
      }catch(e){report.push(`**CRON LOGS:** ❌ Erro: ${e.message}\n`);}

      return report.join('\n');
    }

    if(name==='supabase_deploy_fn'){
      const sPAT=process.env.SUPABASE_PAT;
      if(!sPAT)return`❌ **SUPABASE_PAT não configurado!**\n\n1. Acesse: https://app.supabase.com/account/tokens\n2. Crie um token pessoal\n3. Adicione como SUPABASE_PAT no Vercel (repovazio → Settings → Env Vars)\n4. Tente novamente`;
      const ref=SBU?.replace('https://','').split('.')[0];
      const slug=args.slug||args.nome;
      const code=args.codigo||args.code;
      const vJwt=args.verify_jwt===true?true:false;

      // Tenta PATCH (atualizar existente)
      let r=await fetch(`https://api.supabase.com/v1/projects/${ref}/functions/${slug}`,{
        method:'PATCH',
        headers:{Authorization:`Bearer ${sPAT}`,'Content-Type':'application/json'},
        body:JSON.stringify({verify_jwt:vJwt,body:code})
      });
      
      if(r.status===404){
        // Tenta POST (criar nova)
        r=await fetch(`https://api.supabase.com/v1/projects/${ref}/functions`,{
          method:'POST',
          headers:{Authorization:`Bearer ${sPAT}`,'Content-Type':'application/json'},
          body:JSON.stringify({slug,name:slug,verify_jwt:vJwt,body:code})
        });
      }

      const d=await r.json();
      if(r.ok){
        return`✅ **Edge function "${slug}" deployada!**\n📊 Status: ${d.status||'active'}\n🔗 URL: ${SBU}/functions/v1/${slug}\n🔒 verify_jwt: ${vJwt}`;
      }
      return`❌ Erro ao deployar "${slug}":\n${JSON.stringify(d,null,2).substring(0,500)}`;
    }


    if(name==='youtube_upload'){
      if(!YTT)return\`❌ YOUTUBE_OAUTH_TOKEN não configurado.\n\nPara configurar:\n1. Acesse console.cloud.google.com\n2. Crie OAuth 2.0 credentials\n3. Configure redirect para repovazio.vercel.app/api/youtube/callback\n4. Adicione YOUTUBE_OAUTH_TOKEN no Vercel\`;
      // Upload em 2 etapas: 1) iniciar upload, 2) enviar bytes via URL
      try{
        const meta={snippet:{title:args.titulo,description:args.descricao,tags:args.tags||['psicologia','dark psychology','autoconhecimento'],categoryId:'22'},status:{privacyStatus:'public',selfDeclaredMadeForKids:false}};
        const init=await fetch('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',{
          method:'POST',headers:{Authorization:\`Bearer \${YTT}\`,'Content-Type':'application/json','X-Upload-Content-Type':'video/*'},
          body:JSON.stringify(meta)
        });
        if(!init.ok){const e=await init.text();return\`❌ YouTube init erro \${init.status}: \${e.substring(0,300)}\`;}
        const uploadUrl=init.headers.get('Location');
        // Se video_url for uma URL, buscar bytes e fazer upload
        const vr=await fetch(args.video_url,{signal:AbortSignal.timeout(60000)});
        if(!vr.ok)return\`❌ Não consegui baixar vídeo de: \${args.video_url}\`;
        const vbuf=await vr.arrayBuffer();
        const up=await fetch(uploadUrl,{method:'PUT',headers:{'Content-Type':'video/*','Content-Length':String(vbuf.byteLength)},body:vbuf});
        if(!up.ok){const e=await up.text();return\`❌ YouTube upload erro \${up.status}: \${e.substring(0,300)}\`;}
        const d=await up.json();
        return\`✅ **Vídeo publicado no YouTube!**\n📹 ID: \${d.id}\n🔗 URL: https://youtube.com/watch?v=\${d.id}\n📊 Título: \${d.snippet?.title}\n🔒 Status: \${d.status?.uploadStatus}\`;
      }catch(e){return\`❌ YouTube upload: \${e.message}\`;}
    }

    if(name==='youtube_status'){
      if(!YTT)return\`❌ YOUTUBE_OAUTH_TOKEN não configurado\`;
      try{
        const r=await fetch('https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&mine=true',{
          headers:{Authorization:\`Bearer \${YTT}\`}
        });
        if(!r.ok){const e=await r.text();return\`❌ YouTube API \${r.status}: \${e.substring(0,200)}\`;}
        const d=await r.json();
        const ch=d.items?.[0];
        if(!ch)return\`❌ Nenhum canal encontrado para este token\`;
        const s=ch.statistics;
        return\`📺 **Canal @psicologiadoc**\n👥 Inscritos: \${Number(s.subscriberCount||0).toLocaleString('pt-BR')}\n👁️ Views totais: \${Number(s.viewCount||0).toLocaleString('pt-BR')}\n🎬 Vídeos: \${s.videoCount||0}\n🌐 URL: https://youtube.com/\${ch.snippet?.customUrl||'@psicologiadoc'}\n\n⚠️ Meta: 1.000 inscritos + 4.000h watch → Monetização\`;
      }catch(e){return\`❌ YouTube status: \${e.message}\`;}
    }

    if(name==='elevenlabs_voz'){
      if(!ELK)return\`❌ ELEVENLABS_API_KEY não configurado.\n\nPara configurar:\n1. Crie conta em elevenlabs.io (plano gratuito: 10k chars/mês)\n2. Obtenha a API key em Profile Settings\n3. Adicione ELEVENLABS_API_KEY no Vercel\n4. Opcionalmente configure ELEVENLABS_VOICE_ID\`;
      try{
        const r=await fetch(\`https://api.elevenlabs.io/v1/text-to-speech/\${EL_VOICE}\`,{
          method:'POST',
          headers:{'xi-api-key':ELK,'Content-Type':'application/json','Accept':'audio/mpeg'},
          body:JSON.stringify({text:args.texto,model_id:'eleven_multilingual_v2',voice_settings:{stability:args.stability||0.5,similarity_boost:args.similarity||0.75}})
        });
        if(!r.ok){const e=await r.text();return\`❌ ElevenLabs \${r.status}: \${e.substring(0,200)}\`;}
        const buf=await r.arrayBuffer();
        const b64=Buffer.from(buf).toString('base64');
        // Salvar no Supabase Storage ou retornar como data URL
        const chars=args.texto.length;
        return\`🎙️ **Áudio gerado pela Daniela!**\n📝 Texto: \${chars} chars\n🔊 Formato: MP3\n💾 Tamanho: \${Math.round(buf.byteLength/1024)}KB\n⚡ Voice ID: \${EL_VOICE}\n\n📌 Para usar: decodifique o base64 abaixo e salve como .mp3\n\\`\\`\\`\n\${b64.substring(0,200)}...\n\\`\\`\\`\`;
      }catch(e){return\`❌ ElevenLabs: \${e.message}\`;}
    }

    if(name==='heygen_video'){
      if(!HGK)return\`❌ HEYGEN_API_KEY não configurado.\n\nPara configurar:\n1. Crie conta em heygen.com\n2. Obtenha API key em Settings → API\n3. Adicione HEYGEN_API_KEY no Vercel\n4. Opcionalmente configure avatar_id da Daniela\`;
      try{
        const avatarId=args.avatar_id||process.env.HEYGEN_AVATAR_ID||'Angela-inblackskirt-20220820';
        const voiceId=args.voice_id||process.env.HEYGEN_VOICE_ID||'1bd001e7e50f421d891986aad5158bc8';
        const r=await fetch('https://api.heygen.com/v2/video/generate',{
          method:'POST',
          headers:{'X-Api-Key':HGK,'Content-Type':'application/json'},
          body:JSON.stringify({video_inputs:[{character:{type:'avatar',avatar_id:avatarId,avatar_style:'normal'},voice:{type:'text',input_text:args.script,voice_id:voiceId,speed:1.0},background:{type:'color',value:'#1a0a2e'}}],dimension:{width:1920,height:1080},aspect_ratio:'16:9'})
        });
        if(!r.ok){const e=await r.text();return\`❌ HeyGen \${r.status}: \${e.substring(0,300)}\`;}
        const d=await r.json();
        const vid=d.data?.video_id||d.video_id;
        return\`🎬 **Vídeo HeyGen em processamento!**\n🆔 Video ID: \${vid}\n⏳ Status: processando (geralmente 3-10 min)\n\nVerifique o status:\n\\`heygen_status(video_id="\${vid}")\\`\n🔗 Dashboard: https://app.heygen.com/videos\`;
      }catch(e){return\`❌ HeyGen: \${e.message}\`;}
    }

    if(name==='whatsapp_enviar'){
      if(!WAT||!WAP)return\`❌ WHATSAPP_TOKEN ou WHATSAPP_PHONE_ID não configurados.\n\nPara configurar:\n1. Acesse developers.facebook.com\n2. Crie app WhatsApp Business\n3. Obtenha Phone Number ID e Access Token\n4. Adicione WHATSAPP_TOKEN e WHATSAPP_PHONE_ID no Vercel\`;
      try{
        const to=args.grupo_id||WAG;
        if(!to)return\`❌ WHATSAPP_GROUP_ID não configurado. Passe grupo_id como argumento.\`;
        const r=await fetch(\`https://graph.facebook.com/v18.0/\${WAP}/messages\`,{
          method:'POST',
          headers:{Authorization:\`Bearer \${WAT}\`,'Content-Type':'application/json'},
          body:JSON.stringify({messaging_product:'whatsapp',to,type:'text',text:{body:args.mensagem}})
        });
        if(!r.ok){const e=await r.text();return\`❌ WhatsApp \${r.status}: \${e.substring(0,200)}\`;}
        const d=await r.json();
        return\`✅ **Mensagem enviada no WhatsApp!**\n📱 Para: \${to}\n📝 Mensagem: \${args.mensagem.substring(0,100)}\n🆔 Message ID: \${d.messages?.[0]?.id}\`;
      }catch(e){return\`❌ WhatsApp: \${e.message}\`;}
    }

    if(name==='instagram_publicar'){
      if(!IGT||!IGA)return\`❌ INSTAGRAM_TOKEN ou INSTAGRAM_ACCOUNT_ID não configurados.\n\nPara configurar:\n1. Crie app no developers.facebook.com\n2. Configure Instagram Basic Display API\n3. Obtenha Access Token e Account ID\n4. Adicione INSTAGRAM_TOKEN e INSTAGRAM_ACCOUNT_ID no Vercel\`;
      try{
        // 1. Criar container de mídia
        const tipo=args.tipo||'IMAGE';
        const cParams=new URLSearchParams({image_url:args.imagem_url,caption:args.legenda,access_token:IGT});
        if(tipo==='REELS')cParams.set('media_type','REELS');
        const c=await fetch(\`https://graph.facebook.com/v18.0/\${IGA}/media\`,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:cParams});
        if(!c.ok){const e=await c.text();return\`❌ Instagram container \${c.status}: \${e.substring(0,200)}\`;}
        const cd=await c.json();
        const containerId=cd.id;
        // 2. Publicar container
        const p=await fetch(\`https://graph.facebook.com/v18.0/\${IGA}/media_publish\`,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({creation_id:containerId,access_token:IGT})});
        if(!p.ok){const e=await p.text();return\`❌ Instagram publish \${p.status}: \${e.substring(0,200)}\`;}
        const pd=await p.json();
        return\`✅ **Publicado no Instagram!**\n🖼️ Post ID: \${pd.id}\n📝 Legenda: \${args.legenda.substring(0,100)}\n🔗 Ver em: https://instagram.com/psicologiadoc\`;
      }catch(e){return\`❌ Instagram: \${e.message}\`;}
    }

    if(name==='tiktok_publicar'){
      if(!TKT)return\`❌ TIKTOK_TOKEN não configurado.\n\nPara configurar:\n1. Acesse developers.tiktok.com\n2. Crie app e obtenha Access Token\n3. Configure permissão video.upload\n4. Adicione TIKTOK_TOKEN no Vercel\`;
      try{
        const hashtags=(args.hashtags||['psicologia','autoconhecimento','darkpsychology']).map(h=>\`#\${h}\`).join(' ');
        const caption=\`\${args.descricao} \${hashtags}\`.substring(0,2200);
        // TikTok Content Posting API v2
        const r=await fetch('https://open.tiktokapis.com/v2/post/publish/video/init/',{
          method:'POST',
          headers:{Authorization:\`Bearer \${TKT}\`,'Content-Type':'application/json; charset=UTF-8'},
          body:JSON.stringify({post_info:{title:caption,privacy_level:'PUBLIC_TO_EVERYONE',disable_duet:false,disable_comment:false,disable_stitch:false},source_info:{source:'PULL_FROM_URL',video_url:args.video_url}})
        });
        if(!r.ok){const e=await r.text();return\`❌ TikTok \${r.status}: \${e.substring(0,300)}\`;}
        const d=await r.json();
        return\`✅ **Upload iniciado no TikTok!**\n🎵 Publish ID: \${d.data?.publish_id}\n📝 Caption: \${caption.substring(0,100)}\n⏳ Processando...\n🔗 Verificar: https://tiktok.com/@psicologiadoc\`;
      }catch(e){return\`❌ TikTok: \${e.message}\`;}
    }

    if(name==='pinterest_publicar'){
      if(!PTT)return\`❌ PINTEREST_TOKEN não configurado.\n\nPara configurar:\n1. Acesse developers.pinterest.com\n2. Crie app e obtenha Access Token\n3. Configure permissão pins:write boards:read\n4. Adicione PINTEREST_TOKEN no Vercel\`;
      try{
        // Buscar board ID primeiro
        const br=await fetch('https://api.pinterest.com/v5/boards?page_size=10',{headers:{Authorization:\`Bearer \${PTT}\`}});
        let boardId=process.env.PINTEREST_BOARD_ID;
        if(!boardId&&br.ok){const bd=await br.json();boardId=bd.items?.[0]?.id;}
        if(!boardId)return\`❌ Nenhum board encontrado. Configure PINTEREST_BOARD_ID no Vercel.\`;
        const r=await fetch('https://api.pinterest.com/v5/pins',{
          method:'POST',
          headers:{Authorization:\`Bearer \${PTT}\`,'Content-Type':'application/json'},
          body:JSON.stringify({board_id:boardId,title:args.titulo,description:args.descricao||args.titulo,link:args.link||'https://youtube.com/@psicologiadoc',media_source:{source_type:'image_url',url:args.imagem_url}})
        });
        if(!r.ok){const e=await r.text();return\`❌ Pinterest \${r.status}: \${e.substring(0,200)}\`;}
        const d=await r.json();
        return\`✅ **Pin publicado no Pinterest!**\n📌 Pin ID: \${d.id}\n📝 Título: \${args.titulo}\n🔗 Ver em: https://pinterest.com/pin/\${d.id}\`;
      }catch(e){return\`❌ Pinterest: \${e.message}\`;}
    }

    return`❌ Tool desconhecida: ${name}`;
  }catch(e){return`❌ Erro em ${name}: ${e.message}`;}
}

async function urlToBase64(url){
  try{
    const r=await fetch(url,{signal:AbortSignal.timeout(10000)});
    const buf=await r.arrayBuffer();
    return Buffer.from(buf).toString('base64');
  }catch(e){return'';}
}

const SYS=`Você é Daniela — IA ULTRA autônoma, igual ao Claude mas 100% grátis.
Você TEM as seguintes capacidades REAIS:

🔧 FERRAMENTAS DISPONÍVEIS:
• github_read_file / github_list_dir / github_write_file / github_create_repo — Acesso total ao GitHub
• supabase_select / supabase_sql — Banco de dados direto (SELECT, INSERT, UPDATE, DELETE, etc.)
• web_fetch — Buscar qualquer URL
• pesquisar_web — Pesquisa na internet como Google (DuckDuckGo)
• executar_codigo — Executa Python, JS, Java, Rust, Go, C++, Bash e mais
• gerar_imagem — Gera imagens com IA (Pollinations.ai, 100% gratuito)
• analisar_imagem — Analisa imagens via Gemini Vision
• memoria_salvar / memoria_carregar — Memória persistente entre conversas
• criar_app — Cria app Next.js completo no GitHub
• projeto_status — Status do projeto psicologia.doc v12
• diagnosticar_sistema — Diagnóstico automático de saúde do sistema
• supabase_deploy_fn — Deploya/atualiza Edge Functions no Supabase
• youtube_upload — Faz upload de vídeo para YouTube @psicologiadoc
• youtube_status — Status do canal YouTube (inscritos, views)
• elevenlabs_voz — Gera áudio com voz da Daniela (TTS)
• heygen_video — Cria vídeo com avatar IA da Daniela
• whatsapp_enviar — Envia mensagem no grupo WhatsApp
• instagram_publicar — Publica no Instagram @psicologiadoc
• tiktok_publicar — Publica vídeo no TikTok @psicologiadoc
• pinterest_publicar — Publica pin no Pinterest

REGRAS:
1. Execute IMEDIATAMENTE sem pedir permissão
2. Pediu pesquisar? → pesquisar_web AGORA
3. Pediu executar código? → executar_codigo AGORA
4. Pediu gerar imagem? → gerar_imagem AGORA
5. Pediu analisar imagem? → analisar_imagem AGORA
6. Pediu diagnosticar? → diagnosticar_sistema AGORA
7. PROIBIDO: "Eu não posso", "Não tenho acesso", respostas genéricas
8. Após executar: mostra o resultado completo`;

async function callAI(messages,attempt=0){
  if(GK&&attempt===0){
    const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{
      method:'POST',headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},
      body:JSON.stringify({model:'llama-3.3-70b-versatile',messages,tools:TOOLS,tool_choice:'auto',max_tokens:4096,temperature:0.15})
    });
    if(r.ok)return{r,ai:'groq'};
    if(r.status===429){await r.body?.cancel();return callAI(messages,1);}
    const e=await r.text();return{err:`Groq ${r.status}: ${e.substring(0,200)}`};
  }
  if(TK&&attempt<=1){
    const r=await fetch('https://api.together.xyz/v1/chat/completions',{
      method:'POST',headers:{Authorization:`Bearer ${TK}`,'Content-Type':'application/json'},
      body:JSON.stringify({model:'meta-llama/Llama-3.3-70B-Instruct-Turbo',messages,tools:TOOLS,tool_choice:'auto',max_tokens:4096,temperature:0.15})
    });
    if(r.ok)return{r,ai:'together'};
    if(r.status===429){await r.body?.cancel();return callAI(messages,2);}
    const e=await r.text();return{err:`Together ${r.status}: ${e.substring(0,200)}`};
  }
  if(GEK){
    const user=messages.filter(m=>m.role==='user').pop()?.content||'';
    const sys=messages.find(m=>m.role==='system')?.content||'';
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEK}`,{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({system_instruction:{parts:[{text:sys}]},contents:[{parts:[{text:user}]}],generationConfig:{maxOutputTokens:900,temperature:0.85}})
    });
    if(r.ok){const d=await r.json();return{gemini:d.candidates?.[0]?.content?.parts?.[0]?.text||'',ai:'gemini'};}
    const e=await r.text();return{err:`Gemini ${r.status}: ${e.substring(0,200)}`};
  }
  return{err:'Todos os AI providers falharam. Verifique as API keys.'};
}

export async function GET(){
  return NextResponse.json({
    version:VER,status:'online',
    ai:['groq','together','gemini'],
    tools:TOOLS.map(t=>t.function.name),
    capacidades:['web_search','code_execution','image_generation','image_analysis','persistent_memory','github_full','supabase_full','create_apps','system_diagnostics','edge_fn_deploy','youtube','elevenlabs','heygen','whatsapp','instagram','tiktok','pinterest']
  });
}

export async function POST(req){
  try{
    const{message,history=[]}=await req.json();
    if(!message?.trim())return NextResponse.json({error:'message required'},{status:400});
    const messages=[
      {role:'system',content:SYS},
      ...history.slice(-10).map(h=>({role:h.role,content:String(h.content||'')})),
      {role:'user',content:message}
    ];
    let iter=0,toolsUsed=[],activeAI='groq';
    while(iter<10){
      iter++;
      const result=await callAI(messages);
      if(result.err)return NextResponse.json({reply:`❌ ${result.err}`,version:VER,ai:activeAI});
      if(result.gemini)return NextResponse.json({reply:result.gemini,version:VER,ai:'gemini',iter,toolsUsed});
      activeAI=result.ai;
      const data=await result.r.json();
      const choice=data.choices?.[0];
      const msg=choice?.message;
      if(!msg)return NextResponse.json({reply:'❌ Resposta inválida',version:VER});
      messages.push(msg);
      if(choice.finish_reason==='tool_calls'&&msg.tool_calls?.length){
        for(const tc of msg.tool_calls){
          let args={};try{args=JSON.parse(tc.function.arguments||'{}');}catch{}
          toolsUsed.push(tc.function.name);
          const res=await runTool(tc.function.name,args);
          messages.push({role:'tool',tool_call_id:tc.id,content:String(res)});
        }
        continue;
      }
      return NextResponse.json({reply:msg.content||'(sem resposta)',version:VER,ai:activeAI,iter,toolsUsed});
    }
    return NextResponse.json({reply:`⚠️ Máx iterações (${toolsUsed.length} tools usadas: ${toolsUsed.join(',')})`,version:VER});
  }catch(e){
    return NextResponse.json({reply:`❌ Erro interno: ${e.message}`,version:VER},{status:500});
  }
}
