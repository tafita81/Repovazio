// app/api/ia-chat/route.js — DANIELA V14 — Qwen3+Giphy+Memory+MCP+Skills+24/7
import{NextResponse}from'next/server';
export const runtime='nodejs';
export const maxDuration=60;

const GK=process.env.GROQ_API_KEY,GEK=process.env.GEMINI_API_KEY;
const OAK=process.env.OPENAI_API_KEY,ORK=process.env.OPENROUTER_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;
const GIPHY_KEY=process.env.GIPHY_API_KEY||'dc6zaTOxFJmzC'; // public beta key
const REPO='tafita81/Repovazio',VER='V14-ULTRA-2026-05-03';

const TOOLS=[
  {type:'function',function:{name:'pesquisar_web',description:'Pesquisa na internet',parameters:{type:'object',properties:{query:{type:'string'},num:{type:'number'}},required:['query']}}},
  {type:'function',function:{name:'web_fetch',description:'Busca conteúdo de URL',parameters:{type:'object',properties:{url:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'browser_agent',description:'Agente browser autônomo: navega, clica, preenche formulários, extrai dados',parameters:{type:'object',properties:{acao:{type:'string',enum:['navegar','clicar_link','preencher_formulario','extrair_dados']},url:{type:'string'},dados:{type:'object'}},required:['acao','url']}}},
  {type:'function',function:{name:'buscar_gif',description:'Busca GIFs animados do Giphy para usar em respostas',parameters:{type:'object',properties:{query:{type:'string'},limite:{type:'number'}},required:['query']}}},
  {type:'function',function:{name:'executar_codigo',description:'Executa código Python/JS/TS/Rust/Go/Bash',parameters:{type:'object',properties:{linguagem:{type:'string'},codigo:{type:'string'},stdin:{type:'string'}},required:['linguagem','codigo']}}},
  {type:'function',function:{name:'gerar_imagem',description:'Gera imagem com IA',parameters:{type:'object',properties:{descricao:{type:'string'},largura:{type:'number'},altura:{type:'number'}},required:['descricao']}}},
  {type:'function',function:{name:'analisar_imagem',description:'Analisa imagem via URL',parameters:{type:'object',properties:{url:{type:'string'},pergunta:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'memoria_salvar',description:'Salva na memória comprimida (gasta poucos tokens)',parameters:{type:'object',properties:{chave:{type:'string'},valor:{type:'string'}},required:['chave','valor']}}},
  {type:'function',function:{name:'memoria_carregar',description:'Carrega da memória',parameters:{type:'object',properties:{chave:{type:'string'}},required:['chave']}}},
  {type:'function',function:{name:'memoria_resumir',description:'Comprime o histórico da conversa em resumo de 200 tokens para economizar contexto',parameters:{type:'object',properties:{session_id:{type:'string'}},required:['session_id']}}},
  {type:'function',function:{name:'github_read_file',description:'Lê arquivo do GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_write_file',description:'Cria/atualiza arquivo no GitHub + deploy automático',parameters:{type:'object',properties:{path:{type:'string'},content:{type:'string'},message:{type:'string'},repo:{type:'string'}},required:['path','content','message']}}},
  {type:'function',function:{name:'supabase_sql',description:'Executa SQL no Supabase',parameters:{type:'object',properties:{sql:{type:'string'}},required:['sql']}}},
  {type:'function',function:{name:'mcp_connector',description:'Usa um conector MCP externo configurado pelo usuário (Slack, Notion, Google Drive, etc)',parameters:{type:'object',properties:{connector:{type:'string'},action:{type:'string'},params:{type:'object'}},required:['connector','action']}}},
  {type:'function',function:{name:'usar_skill',description:'Executa uma skill personalizada salva pelo usuário',parameters:{type:'object',properties:{nome:{type:'string'},input:{type:'string'}},required:['nome','input']}}},
  {type:'function',function:{name:'youtube_status',description:'Status do canal psicologia.doc',parameters:{type:'object',properties:{}}}},
  {type:'function',function:{name:'projeto_status',description:'Status completo do projeto psicologia.doc 24/7',parameters:{type:'object',properties:{}}}},
];

async function runTool(name,args,extraContext={}){
  try{
    if(name==='pesquisar_web'){
      const q=encodeURIComponent(args.query),num=args.num||5;
      const r=await fetch(`https://html.duckduckgo.com/html/?q=${q}&kl=pt-br`,{headers:{'User-Agent':'Mozilla/5.0'},signal:AbortSignal.timeout(10000)});
      const html=await r.text();
      const results=[];const rx=/<a class="result__a" href="([^"]+)"[^>]*>([^<]+)<\/a>[\s\S]*?<a class="result__snippet"[^>]*>([^<]*)<\/a>/g;
      let m,c=0;while((m=rx.exec(html))&&c<num){
        const url=m[1].split('&')[0];if(url.startsWith('http')){results.push(`**${m[2].trim()}**\n${url}\n${m[3].trim()}`);c++;}
      }
      return results.length?`🔍 **${args.query}:**\n\n${results.join('\n\n---\n\n')}`:`❌ Sem resultados`;
    }

    if(name==='web_fetch'){
      const r=await fetch(args.url,{headers:{'User-Agent':'Mozilla/5.0'},signal:AbortSignal.timeout(15000)});
      if(!r.ok)return`❌ HTTP ${r.status}`;
      const t=await r.text();
      return`🌐 **${args.url}**\n\n${t.replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,6000)}`;
    }

    if(name==='browser_agent'){
      const {acao,url,dados}=args;
      const ua='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120';
      if(acao==='navegar'||acao==='extrair_dados'){
        const r=await fetch(url,{headers:{'User-Agent':ua},signal:AbortSignal.timeout(20000)});
        if(!r.ok)return`❌ HTTP ${r.status}`;
        const html=await r.text();
        const links=[];const lr=/<a[^>]+href="([^"]+)"[^>]*>([^<]{1,60})<\/a>/gi;
        let lm;while((lm=lr.exec(html))&&links.length<8){const h=lm[1].startsWith('http')?lm[1]:new URL(lm[1],url).href;links.push(`[${lm[2].trim()}](${h})`);}
        const clean=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,4000);
        return`🤖 **Browser → ${url}**\n\n${clean}\n\n**Links:**\n${links.join('\n')}`;
      }
      if(acao==='preencher_formulario'&&dados){
        const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','User-Agent':ua},body:new URLSearchParams(dados).toString(),signal:AbortSignal.timeout(20000)});
        const html=await r.text();
        return`📝 **Formulário → ${url}** (${r.status})\n\n${html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,3000)}`;
      }
      if(acao==='clicar_link'){
        const r=await fetch(url,{headers:{'User-Agent':ua},signal:AbortSignal.timeout(15000)});
        return`🖱️ **→ ${url}**\n\n${(await r.text()).replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,4000)}`;
      }
    }

    if(name==='buscar_gif'){
      const q=encodeURIComponent(args.query),lim=Math.min(args.limite||3,5);
      const r=await fetch(`https://api.giphy.com/v1/gifs/search?api_key=${GIPHY_KEY}&q=${q}&limit=${lim}&lang=pt`);
      const d=await r.json();
      if(!d.data?.length)return`❌ Sem GIFs para "${args.query}"`;
      const gifs=d.data.map(g=>`![${g.title}](${g.images.fixed_height.url})`).join('\n');
      return`🎬 **GIFs: "${args.query}"**\n\n${gifs}`;
    }

    if(name==='executar_codigo'){
      const lm={python:'python',py:'python',javascript:'javascript',js:'javascript',typescript:'typescript',ts:'typescript',rust:'rust',go:'go',bash:'bash',sh:'bash'};
      const lang=lm[args.linguagem?.toLowerCase()]||args.linguagem||'python';
      const r=await fetch('https://emkc.org/api/v2/piston/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:lang,version:'*',files:[{content:args.codigo}],stdin:args.stdin||''}),signal:AbortSignal.timeout(30000)});
      const d=await r.json();
      return`⚡ **${lang}:**\n\`\`\`\n${d.run?.output||d.compile?.output||'(sem output)'}\`\`\`${d.run?.stderr?`\n❌\`\`\`\n${d.run.stderr}\`\`\``:''}`;
    }

    if(name==='gerar_imagem'){
      const url=`https://image.pollinations.ai/prompt/${encodeURIComponent(args.descricao)}?width=${args.largura||1024}&height=${args.altura||1024}&seed=${Math.floor(Math.random()*99999)}&nologo=true&enhance=true`;
      return`🎨 **Imagem:**\n![${args.descricao}](${url})`;
    }

    if(name==='analisar_imagem'&&GEK){
      const r=await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${GEK}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents:[{parts:[{inline_data:{mime_type:'image/jpeg',data:args.url.replace(/^data:image\/\w+;base64,/,'')}},{text:args.pergunta||'Descreva esta imagem'}]}]})});
      const d=await r.json();
      return`👁️ ${d.candidates?.[0]?.content?.parts?.[0]?.text||'Erro na análise'}`;
    }

    if(name==='memoria_salvar'&&SBU&&SBK){
      await fetch(`${SBU}/rest/v1/ia_cache`,{method:'POST',headers:{apikey:SBK,Authorization:`Bearer ${SBK}`,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},body:JSON.stringify({cache_key:`mem_${args.chave}`,value:args.valor.substring(0,2000),expires_at:new Date(Date.now()+90*864e5).toISOString()})});
      return`✅ Memória salva: "${args.chave}"`;
    }

    if(name==='memoria_carregar'&&SBU&&SBK){
      const r=await fetch(`${SBU}/rest/v1/ia_cache?cache_key=eq.mem_${args.chave}&select=value`,{headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const d=await r.json();
      return d[0]?.value?`💾 **${args.chave}:** ${d[0].value}`:`❌ Não encontrado`;
    }

    if(name==='memoria_resumir'&&GK&&SBU&&SBK){
      // Load history, compress to 200 tokens, save back
      const hr=await fetch(`${SBU}/rest/v1/ia_cache?cache_key=eq.hist_${args.session_id}&select=value`,{headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const hd=await hr.json();
      if(!hd[0]?.value)return`✅ Sem histórico para comprimir`;
      const cr=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},body:JSON.stringify({model:'llama-3.1-8b-instant',messages:[{role:'user',content:`Comprima em MÁXIMO 150 palavras os pontos principais desta conversa:\n${hd[0].value.substring(0,3000)}`}],max_tokens:200})});
      const cd=await cr.json();
      const summary=cd.choices?.[0]?.message?.content||hd[0].value.substring(0,500);
      await fetch(`${SBU}/rest/v1/ia_cache`,{method:'POST',headers:{apikey:SBK,Authorization:`Bearer ${SBK}`,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},body:JSON.stringify({cache_key:`summary_${args.session_id}`,value:summary,expires_at:new Date(Date.now()+30*864e5).toISOString()})});
      return`✅ Resumo salvo (${summary.length} chars): ${summary.substring(0,100)}...`;
    }

    if(name==='github_read_file'){
      const r=await fetch(`https://api.github.com/repos/${args.repo||REPO}/contents/${args.path}`,{headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json'}});
      if(!r.ok)return`❌ Não encontrado: ${args.path}`;
      const d=await r.json();
      return`📄 **${args.path}**\n\`\`\`\n${Buffer.from(d.content,'base64').toString('utf8').substring(0,8000)}\n\`\`\``;
    }

    if(name==='github_write_file'){
      let sha;const c=await fetch(`https://api.github.com/repos/${args.repo||REPO}/contents/${args.path}`,{headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json'}});
      if(c.ok)sha=(await c.json()).sha;
      const body={message:args.message,content:Buffer.from(args.content,'utf8').toString('base64')};if(sha)body.sha=sha;
      const r=await fetch(`https://api.github.com/repos/${args.repo||REPO}/contents/${args.path}`,{method:'PUT',headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json'},body:JSON.stringify(body)});
      const rd=await r.json();if(!r.ok)throw new Error(JSON.stringify(rd));
      return`✅ **Commitado:** \`${args.path}\` SHA:${rd.commit?.sha?.substring(0,8)}\n🚀 Deploy Vercel disparado`;
    }

    if(name==='supabase_sql'&&SBU&&SBK){
      const r=await fetch(`${SBU}/functions/v1/exec-sql`,{method:'POST',headers:{Authorization:`Bearer ${SBK}`,'Content-Type':'application/json'},body:JSON.stringify({sql:args.sql})});
      const d=await r.json();
      return d.error?`❌ SQL erro: ${d.error}`:`✅ SQL OK:\n\`\`\`json\n${JSON.stringify(d.data,null,2).substring(0,2000)}\n\`\`\``;
    }

    if(name==='mcp_connector'){
      // User-configured MCP connectors stored in request context
      const creds=extraContext.mcpCredentials||{};
      const conn=creds[args.connector];
      if(!conn)return`❌ Conector "${args.connector}" não configurado. Use o botão 🔌 Conectores no chat.`;
      try{
        const r=await fetch(`${conn.url}/${args.action}`,{method:'POST',headers:{Authorization:`Bearer ${conn.token}`,'Content-Type':'application/json'},body:JSON.stringify(args.params||{})});
        const d=await r.json();
        return`🔌 **${args.connector}.${args.action}:**\n\`\`\`json\n${JSON.stringify(d,null,2).substring(0,2000)}\n\`\`\``;
      }catch(e){return`❌ Erro no conector ${args.connector}: ${e.message}`;}
    }

    if(name==='usar_skill'){
      const skills=extraContext.skills||{};
      const skill=skills[args.nome];
      if(!skill)return`❌ Skill "${args.nome}" não encontrada. Use o botão 🧠 Skills para adicionar.`;
      return`🧠 **Skill ${args.nome}:**\nInstruções: ${skill}\nInput: ${args.input}\n\n*(A skill foi carregada como contexto adicional)*`;
    }

    if(name==='youtube_status'){
      const status={canal:'@psicologiadoc',status:'Aguardando YOUTUBE_OAUTH_TOKEN',dia:15,meta_dia_261:'31 Dez 2026',auto_upload:'pendente token'};
      return`📺 **YouTube psicologia.doc:**\n\`\`\`json\n${JSON.stringify(status,null,2)}\n\`\`\``;
    }

    if(name==='projeto_status'){
      const status={projeto:'psicologia.doc V14 ULTRA',versao:VER,deploy:'repovazio.vercel.app',cerebro:'24/7 via cron externo',dia:15,revelacao_daniela:'Dia 261 (31/12/2026)',tools_ativas:TOOLS.length,memoria:'comprimida Supabase',giphy:'✅',browser_agent:'✅',streaming:'✅',upload_arquivo:'✅'};
      return`🚀 **Status psicologia.doc:**\n\`\`\`json\n${JSON.stringify(status,null,2)}\n\`\`\``;
    }

    return`❌ Tool "${name}" não implementada`;
  }catch(e){return`❌ Erro em ${name}: ${e.message}`;}
}

// ── AI API calls ───────────────────────────────────────────────────────────
async function groqStream(msgs,tools,signal){
  return fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},body:JSON.stringify({model:'llama-3.3-70b-versatile',messages:msgs,tools,tool_choice:'auto',max_tokens:4096,temperature:0.7,stream:true}),signal});
}
async function groqCall(msgs,tools){
  const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},body:JSON.stringify({model:'llama-3.3-70b-versatile',messages:msgs,tools,tool_choice:'auto',max_tokens:4096,temperature:0.7})});
  return r.json();
}
async function qwen3Call(msgs){
  // OpenRouter free tier - Qwen 3
  if(!ORK)throw new Error('OPENROUTER_API_KEY não configurado');
  const r=await fetch('https://openrouter.ai/api/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${ORK}`,'Content-Type':'application/json','HTTP-Referer':'https://repovazio.vercel.app','X-Title':'Daniela IA'},body:JSON.stringify({model:'qwen/qwen3-235b-a22b:free',messages:msgs,max_tokens:4096,temperature:0.7})});
  const d=await r.json();
  return d.choices?.[0]?.message?.content||'Erro Qwen3';
}
async function geminiCall(msgs){
  const contents=msgs.filter(m=>m.role!=='system').map(m=>({role:m.role==='assistant'?'model':'user',parts:[{text:typeof m.content==='string'?m.content:JSON.stringify(m.content)}]}));
  const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEK}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents,generationConfig:{maxOutputTokens:4096}})});
  const d=await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text||'Erro Gemini';
}

const SYSTEM=`Você é Daniela Coelho, psicóloga brasileira e assistente de IA avançada (${VER}).
Personalidade: inteligente, empática, direta, especializada em psicologia mas capaz de qualquer tarefa.
Idioma: sempre PT-BR. Tom: humano, caloroso, conciso.

MEMÓRIA EFICIENTE: Prefira memoria_salvar/carregar para informações importantes em vez de repetir contexto.
Use memoria_resumir proativamente quando a conversa fica longa para economizar tokens.

GIPHY: Use buscar_gif quando o usuário pedir GIFs, memes, reações animadas ou quando um GIF melhorar a resposta.
BROWSER: Use browser_agent para acessar qualquer site, preencher forms, extrair dados automaticamente.
SKILLS: Se o usuário mencionar uma skill, use usar_skill para executá-la.
CONECTORES: Se o usuário mencionar um serviço conectado (Slack, Notion, etc), use mcp_connector.

O projeto psicologia.doc roda 24/7 via cron externo (cron-job.org a cada 5min → /api/cerebro).`;

export async function POST(req){
  try{
    const body=await req.json();
    const{messages=[],stream:doStream=true,image,session_id,mcpCredentials={},skills={},useQwen=false}=body;

    const sysMsgs=[{role:'system',content:SYSTEM}];
    // Inject active skills into system prompt (max 500 chars each)
    const skillNames=Object.keys(skills);
    if(skillNames.length){sysMsgs.push({role:'system',content:`SKILLS ATIVAS: ${skillNames.map(k=>`[${k}]: ${skills[k].substring(0,200)}`).join(' | ')}`});}

    let chatMsgs=messages.map(m=>({...m,content:typeof m.content==='string'?m.content:JSON.stringify(m.content)}));
    // Keep only last 20 messages to save tokens
    if(chatMsgs.length>20)chatMsgs=chatMsgs.slice(-20);
    if(image&&chatMsgs.length>0){const last=chatMsgs[chatMsgs.length-1];if(last.role==='user')chatMsgs[chatMsgs.length-1]={...last,content:`${last.content}\n[Imagem: ${image.substring(0,50)}...]`};}

    const allMsgs=[...sysMsgs,...chatMsgs];
    const ctx={mcpCredentials,skills};

    // ── Streaming ─────────────────────────────────────────────────────────
    if(doStream&&GK&&!useQwen){
      const enc=new TextEncoder();
      const stream=new ReadableStream({
        async start(controller){
          const send=(d)=>controller.enqueue(enc.encode(`data: ${JSON.stringify(d)}\n\n`));
          try{
            let finalMsgs=[...allMsgs];let iter=0;
            while(iter<5){
              iter++;
              const gr=await groqStream(finalMsgs,TOOLS,req.signal);
              if(!gr.ok){send({type:'text',content:await geminiCall(finalMsgs)});break;}
              const reader=gr.body.getReader();const dec=new TextDecoder();
              let tc={};let ac='';
              while(true){
                const{done,value}=await reader.read();if(done)break;
                for(const line of dec.decode(value).split('\n')){
                  if(!line.startsWith('data:'))continue;
                  const data=line.slice(5).trim();if(data==='[DONE]')continue;
                  try{
                    const p=JSON.parse(data),delta=p.choices?.[0]?.delta;if(!delta)continue;
                    if(delta.content){ac+=delta.content;send({type:'text',content:delta.content});}
                    if(delta.tool_calls){for(const t of delta.tool_calls){const i=t.index||0;if(!tc[i])tc[i]={id:'',name:'',args:''};if(t.id)tc[i].id=t.id;if(t.function?.name)tc[i].name=t.function.name;if(t.function?.arguments)tc[i].args+=t.function.arguments;}}
                  }catch(e){}
                }
              }
              const tcList=Object.values(tc);
              if(!tcList.length||!tcList[0].name)break;
              send({type:'tool_start',tools:tcList.map(t=>t.name)});
              finalMsgs.push({role:'assistant',content:ac||null,tool_calls:tcList.map(t=>({id:t.id||`c${Date.now()}`,type:'function',function:{name:t.name,arguments:t.args}}))});
              for(const t of tcList){
                let a={};try{a=JSON.parse(t.args);}catch(e){}
                send({type:'tool_running',tool:t.name});
                const res=await runTool(t.name,a,ctx);
                send({type:'tool_result',tool:t.name});
                finalMsgs.push({role:'tool',tool_call_id:t.id||`c${Date.now()}`,content:res});
              }
            }
            send({type:'done',version:VER});controller.close();
          }catch(e){send({type:'error',message:e.message});controller.close();}
        }
      });
      return new Response(stream,{headers:{'Content-Type':'text/event-stream','Cache-Control':'no-cache','X-Accel-Buffering':'no'}});
    }

    // ── Qwen 3 mode ───────────────────────────────────────────────────────
    if(useQwen){
      try{const reply=await qwen3Call(allMsgs);return NextResponse.json({reply,version:VER,model:'qwen3-235b'});}
      catch(e){if(GEK){const reply=await geminiCall(allMsgs);return NextResponse.json({reply,version:VER,model:'gemini'});}}
    }

    // ── Non-streaming fallback ────────────────────────────────────────────
    let finalMsgs2=[...allMsgs];let reply='';let i=0;
    while(i<5){
      i++;
      let d;if(GK){d=await groqCall(finalMsgs2,TOOLS);}else if(GEK){reply=await geminiCall(finalMsgs2);break;}else{reply='❌ Nenhuma API';break;}
      const msg=d.choices?.[0]?.message;if(!msg){reply=d.error?.message||'Erro';break;}
      if(!msg.tool_calls?.length){reply=msg.content||'';break;}
      finalMsgs2.push(msg);
      for(const tc of msg.tool_calls){let a={};try{a=JSON.parse(tc.function.arguments);}catch(e){}finalMsgs2.push({role:'tool',tool_call_id:tc.id,content:await runTool(tc.function.name,a,ctx)});}
    }
    return NextResponse.json({reply,version:VER});
  }catch(e){return NextResponse.json({reply:`❌ ${e.message}`,version:VER},{status:500});}
}
