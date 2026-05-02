// app/api/ia-chat/route.js — DANIELA ULTRA V11 — Igual ao Claude
import{NextResponse}from'next/server';
const GK=process.env.GROQ_API_KEY,TK=process.env.TOGETHER_API_KEY,GEK=process.env.GEMINI_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;
const REPO='tafita81/Repovazio',VER='V11-ULTRA-2026-05-01';

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
  {type:'function',function:{name:'supabase_deploy_fn',description:'Deploya/atualiza uma Edge Function no Supabase. Requer SUPABASE_PAT configurado no Vercel.',parameters:{type:'object',properties:{slug:{type:'string'},codigo:{type:'string'},verify_jwt:{type:'boolean'}},required:['slug','codigo']}}}
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
• projeto_status — Status do projeto
• diagnosticar_sistema — Diagnóstico automático de saúde do sistema
• supabase_deploy_fn — Deploya/atualiza Edge Functions no Supabase

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
    if(r.status===429||r.status===402){await r.body?.cancel();return callAI(messages,2);}
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
    capacidades:['web_search','code_execution','image_generation','image_analysis','persistent_memory','github_full','supabase_full','create_apps','system_diagnostics','edge_fn_deploy']
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
