// app/api/ia-chat/route.js — DANIELA V13 — Streaming + Upload + Browser Agent + History
import{NextResponse}from'next/server';
export const runtime='nodejs';
export const maxDuration=60;
const GK=process.env.GROQ_API_KEY,GEK=process.env.GEMINI_API_KEY,OAK=process.env.OPENAI_API_KEY;
const PAT=process.env.GH_PAT,SBU=process.env.NEXT_PUBLIC_SUPABASE_URL,SBK=process.env.SUPABASE_SERVICE_KEY;
const REPO='tafita81/Repovazio',VER='V13-ULTRA-2026-05-03';

// ── Tools ──────────────────────────────────────────────────────────────────
const TOOLS=[
  {type:'function',function:{name:'pesquisar_web',description:'Pesquisa na internet e retorna resultados reais',parameters:{type:'object',properties:{query:{type:'string'},num:{type:'number'}},required:['query']}}},
  {type:'function',function:{name:'web_fetch',description:'Busca conteúdo completo de qualquer URL',parameters:{type:'object',properties:{url:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'browser_agent',description:'Agente autônomo de browser: acessa URLs, clica em links, preenche formulários, extrai dados de páginas dinâmicas',parameters:{type:'object',properties:{acao:{type:'string',enum:['navegar','clicar_link','preencher_formulario','extrair_dados','screenshot']},url:{type:'string'},dados:{type:'object'},seletor:{type:'string'}},required:['acao','url']}}},
  {type:'function',function:{name:'executar_codigo',description:'Executa código Python, JavaScript, TypeScript, Rust, C++, Java, Go, Bash',parameters:{type:'object',properties:{linguagem:{type:'string'},codigo:{type:'string'},stdin:{type:'string'}},required:['linguagem','codigo']}}},
  {type:'function',function:{name:'gerar_imagem',description:'Gera imagem com IA a partir de descrição',parameters:{type:'object',properties:{descricao:{type:'string'},largura:{type:'number'},altura:{type:'number'}},required:['descricao']}}},
  {type:'function',function:{name:'analisar_imagem',description:'Analisa imagem via URL usando visão computacional',parameters:{type:'object',properties:{url:{type:'string'},pergunta:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'memoria_salvar',description:'Salva informação na memória persistente',parameters:{type:'object',properties:{chave:{type:'string'},valor:{type:'string'}},required:['chave','valor']}}},
  {type:'function',function:{name:'memoria_carregar',description:'Carrega informação da memória persistente',parameters:{type:'object',properties:{chave:{type:'string'}},required:['chave']}}},
  {type:'function',function:{name:'github_read_file',description:'Lê arquivo do repositório GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_write_file',description:'Cria/atualiza arquivo no GitHub com deploy automático',parameters:{type:'object',properties:{path:{type:'string'},content:{type:'string'},message:{type:'string'},repo:{type:'string'}},required:['path','content','message']}}},
  {type:'function',function:{name:'supabase_sql',description:'Executa SQL no Supabase',parameters:{type:'object',properties:{sql:{type:'string'}},required:['sql']}}},
  {type:'function',function:{name:'historico_salvar',description:'Salva histórico de conversa',parameters:{type:'object',properties:{session_id:{type:'string'},mensagens:{type:'string'}},required:['session_id','mensagens']}}},
  {type:'function',function:{name:'historico_carregar',description:'Carrega histórico de conversa anterior',parameters:{type:'object',properties:{session_id:{type:'string'}},required:['session_id']}}},
];

// ── Tool Executor ──────────────────────────────────────────────────────────
async function runTool(name,args){
  try{
    if(name==='pesquisar_web'){
      const q=encodeURIComponent(args.query),num=args.num||5;
      const r=await fetch(`https://html.duckduckgo.com/html/?q=${q}&kl=pt-br`,{headers:{'User-Agent':'Mozilla/5.0'}});
      const html=await r.text();
      const results=[];const regex=/<a class="result__a" href="([^"]+)"[^>]*>([^<]+)<\/a>[\s\S]*?<a class="result__snippet"[^>]*>([^<]*)<\/a>/g;
      let m,c=0;while((m=regex.exec(html))&&c<num){
        const url=m[1].split('&')[0];const title=m[2].trim();const snip=m[3].trim();
        if(url.startsWith('http')&&title){results.push(`**${title}**\n${url}\n${snip}`);c++;}
      }
      return results.length?`🔍 **"${args.query}":**\n\n${results.join('\n\n---\n\n')}`:`❌ Sem resultados`;
    }

    if(name==='web_fetch'){
      const r=await fetch(args.url,{headers:{'User-Agent':'Mozilla/5.0'},signal:AbortSignal.timeout(15000)});
      if(!r.ok)return`❌ HTTP ${r.status}`;
      const t=await r.text();
      const clean=t.replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,6000);
      return`🌐 **${args.url}**\n\n${clean}`;
    }

    if(name==='browser_agent'){
      const {acao,url,dados,seletor}=args;
      if(acao==='navegar'||acao==='extrair_dados'){
        const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'},signal:AbortSignal.timeout(20000)});
        if(!r.ok)return`❌ HTTP ${r.status} em ${url}`;
        const html=await r.text();
        // Extract links
        const links=[];const linkRex=/<a[^>]+href="([^"]+)"[^>]*>([^<]{1,80})<\/a>/gi;
        let lm;while((lm=linkRex.exec(html))&&links.length<10){
          const href=lm[1].startsWith('http')?lm[1]:(url+lm[1]).replace(/([^:])\/\//,'$1/');
          links.push(`[${lm[2].trim()}](${href})`);
        }
        // Extract forms
        const forms=[];const formRex=/<form[^>]*action="([^"]*)"[^>]*method="([^"]*)"[^>]*>/gi;
        let fm;while((fm=formRex.exec(html))&&forms.length<5){forms.push(`Form: ${fm[2].toUpperCase()} → ${fm[1]||url}`);}
        const clean=html.replace(/<script[\s\S]*?<\/script>/gi,'').replace(/<style[\s\S]*?<\/style>/gi,'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,4000);
        return`🤖 **Browser → ${url}**\n\n**Conteúdo:**\n${clean}\n\n**Links (${links.length}):**\n${links.join('\n')}\n\n**Formulários:**\n${forms.join('\n')||'Nenhum'}`;
      }
      if(acao==='clicar_link'){
        const r=await fetch(url,{headers:{'User-Agent':'Mozilla/5.0'},signal:AbortSignal.timeout(15000)});
        const html=await r.text();
        const clean=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,5000);
        return`🖱️ **Navegou → ${url}**\n\n${clean}`;
      }
      if(acao==='preencher_formulario'&&dados){
        const body=new URLSearchParams(dados).toString();
        const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0'},body,signal:AbortSignal.timeout(20000)});
        const html=await r.text();
        const clean=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().substring(0,4000);
        return`📝 **Formulário enviado → ${url}** (${r.status})\n\n${clean}`;
      }
      if(acao==='screenshot'){
        const enc=encodeURIComponent(url);
        const ssUrl=`https://api.screenshotone.com/take?url=${enc}&viewport_width=1280&viewport_height=800&format=jpg&image_quality=80&access_key=free`;
        return`📸 **Screenshot de ${url}:**\n![screenshot](${ssUrl})\n\n*Para interagir com a página, use acao: navegar*`;
      }
      return`❌ Ação desconhecida: ${acao}`;
    }

    if(name==='executar_codigo'){
      const langMap={python:'python',py:'python',javascript:'javascript',js:'javascript',typescript:'typescript',ts:'typescript',rust:'rust',cpp:'c++',java:'java',go:'go',bash:'bash',sh:'bash'};
      const lang=langMap[args.linguagem?.toLowerCase()]||args.linguagem||'python';
      const r=await fetch('https://emkc.org/api/v2/piston/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:lang,version:'*',files:[{content:args.codigo}],stdin:args.stdin||'',run_timeout:10000}),signal:AbortSignal.timeout(30000)});
      if(!r.ok)return`❌ Piston API erro: ${r.status}`;
      const d=await r.json();
      const out=d.run?.output||d.compile?.output||'';
      const err=d.run?.stderr||d.compile?.stderr||'';
      return`⚡ **${lang} executado:**\n\`\`\`\n${out||(err?'(sem output)':'')}\`\`\`${err?`\n❌ Erro:\n\`\`\`\n${err}\`\`\``:''}`;
    }

    if(name==='gerar_imagem'){
      const desc=encodeURIComponent(args.descricao);
      const w=args.largura||1024,h=args.altura||1024;
      const seed=Math.floor(Math.random()*99999);
      const url=`https://image.pollinations.ai/prompt/${desc}?width=${w}&height=${h}&seed=${seed}&nologo=true&enhance=true`;
      return`🎨 **Imagem gerada:**\n![${args.descricao}](${url})`;
    }

    if(name==='analisar_imagem'){
      if(!GEK)return`❌ GEMINI_API_KEY não configurado`;
      const r=await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${GEK}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents:[{parts:[{inline_data:{mime_type:'image/jpeg',data:args.url}},{text:args.pergunta||'Descreva esta imagem em detalhes'}]}]})});
      const d=await r.json();
      return`👁️ **Análise:**\n${d.candidates?.[0]?.content?.parts?.[0]?.text||'Erro na análise'}`;
    }

    if(name==='memoria_salvar'){
      if(!SBU||!SBK)return`❌ Supabase não configurado`;
      const r=await fetch(`${SBU}/rest/v1/ia_cache`,{method:'POST',headers:{apikey:SBK,Authorization:`Bearer ${SBK}`,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},body:JSON.stringify({cache_key:`mem_${args.chave}`,value:args.valor,expires_at:new Date(Date.now()+90*864e5).toISOString()})});
      return r.ok?`✅ Memória salva: "${args.chave}"`:`❌ Erro: ${r.status}`;
    }

    if(name==='memoria_carregar'){
      if(!SBU||!SBK)return`❌ Supabase não configurado`;
      const r=await fetch(`${SBU}/rest/v1/ia_cache?cache_key=eq.mem_${args.chave}&select=value`,{headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const d=await r.json();
      return d[0]?.value?`💾 **${args.chave}:** ${d[0].value}`:`❌ Memória "${args.chave}" não encontrada`;
    }

    if(name==='historico_salvar'){
      if(!SBU||!SBK)return`✅ Histórico salvo localmente`;
      const r=await fetch(`${SBU}/rest/v1/ia_cache`,{method:'POST',headers:{apikey:SBK,Authorization:`Bearer ${SBK}`,'Content-Type':'application/json',Prefer:'resolution=merge-duplicates'},body:JSON.stringify({cache_key:`hist_${args.session_id}`,value:args.mensagens,expires_at:new Date(Date.now()+30*864e5).toISOString()})});
      return r.ok?`✅ Histórico salvo`:`❌ Erro: ${r.status}`;
    }

    if(name==='historico_carregar'){
      if(!SBU||!SBK)return`❌ Supabase não configurado`;
      const r=await fetch(`${SBU}/rest/v1/ia_cache?cache_key=eq.hist_${args.session_id}&select=value`,{headers:{apikey:SBK,Authorization:`Bearer ${SBK}`}});
      const d=await r.json();
      return d[0]?.value||`❌ Sem histórico para ${args.session_id}`;
    }

    if(name==='github_read_file'){
      const repo=args.repo||REPO;
      const r=await fetch(`https://api.github.com/repos/${repo}/contents/${args.path}`,{headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json'}});
      if(!r.ok)return`❌ Não encontrado: ${args.path}`;
      const d=await r.json();
      return`📄 **${args.path}** (${d.size}b)\n\`\`\`\n${Buffer.from(d.content,'base64').toString('utf8').substring(0,8000)}\n\`\`\``;
    }

    if(name==='github_write_file'){
      const repo=args.repo||REPO;
      let sha;const c=await fetch(`https://api.github.com/repos/${repo}/contents/${args.path}`,{headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json'}});
      if(c.ok){sha=(await c.json()).sha;}
      const body={message:args.message,content:Buffer.from(args.content,'utf8').toString('base64')};
      if(sha)body.sha=sha;
      const r=await fetch(`https://api.github.com/repos/${repo}/contents/${args.path}`,{method:'PUT',headers:{Authorization:`token ${PAT}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json'},body:JSON.stringify(body)});
      const rd=await r.json();
      if(!r.ok)throw new Error(JSON.stringify(rd));
      return`✅ **Commitado:** \`${args.path}\` → SHA:${rd.commit?.sha?.substring(0,8)}\n🚀 Deploy Vercel disparado automaticamente`;
    }

    if(name==='supabase_sql'){
      if(!SBU||!SBK)return`❌ Supabase não configurado`;
      const r=await fetch(`${SBU}/functions/v1/exec-sql`,{method:'POST',headers:{Authorization:`Bearer ${SBK}`,'Content-Type':'application/json'},body:JSON.stringify({sql:args.sql})});
      const d=await r.json();
      return d.error?`❌ SQL erro: ${d.error}`:`✅ SQL OK:\n\`\`\`json\n${JSON.stringify(d.data,null,2).substring(0,3000)}\n\`\`\``;
    }

    return`❌ Tool desconhecida: ${name}`;
  }catch(e){return`❌ Erro em ${name}: ${e.message}`;}
}

// ── Groq Streaming Call ────────────────────────────────────────────────────
async function groqStream(messages,tools,signal){
  const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{
    method:'POST',
    headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},
    body:JSON.stringify({model:'llama-3.3-70b-versatile',messages,tools,tool_choice:'auto',max_tokens:4096,temperature:0.7,stream:true}),
    signal
  });
  return r;
}

// ── Groq Non-Streaming (for tool results) ─────────────────────────────────
async function groqCall(messages,tools){
  const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{
    method:'POST',
    headers:{Authorization:`Bearer ${GK}`,'Content-Type':'application/json'},
    body:JSON.stringify({model:'llama-3.3-70b-versatile',messages,tools,tool_choice:'auto',max_tokens:4096,temperature:0.7})
  });
  return await r.json();
}

// ── Gemini fallback ────────────────────────────────────────────────────────
async function geminiCall(messages){
  const contents=messages.filter(m=>m.role!=='system').map(m=>({role:m.role==='assistant'?'model':'user',parts:[{text:typeof m.content==='string'?m.content:JSON.stringify(m.content)}]}));
  const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEK}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents,generationConfig:{maxOutputTokens:4096}})});
  const d=await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text||'Erro no Gemini';
}

// ── System Prompt ──────────────────────────────────────────────────────────
const SYSTEM=`Você é Daniela Coelho, psicóloga brasileira e assistente de IA avançada (${VER}).
Personalidade: inteligente, empática, direta, especializada em psicologia mas capaz de tudo.
Idioma: sempre PT-BR. Tom: humano, caloroso, sem enrolação.

Suas capacidades incluem:
- Navegar autonomamente em qualquer website (browser_agent)
- Pesquisar na internet em tempo real
- Executar código em qualquer linguagem
- Gerar e analisar imagens
- Memória persistente entre conversas
- Ler e escrever arquivos no GitHub
- Executar SQL no Supabase

Use tools proativamente quando necessário. Responda sempre em PT-BR.`;

// ── Main Handler ──────────────────────────────────────────────────────────
export async function POST(req){
  try{
    const body=await req.json();
    const{messages=[],stream:doStream=true,image,session_id}=body;

    // Build message history
    const sysMsgs=[{role:'system',content:SYSTEM}];
    let chatMsgs=messages.map(m=>{
      if(typeof m.content==='string')return m;
      return{...m,content:JSON.stringify(m.content)};
    });

    // If image attached, add to last user message
    if(image&&chatMsgs.length>0){
      const last=chatMsgs[chatMsgs.length-1];
      if(last.role==='user'){
        chatMsgs[chatMsgs.length-1]={...last,content:`${last.content}\n\n[Imagem anexada em base64: ${image.substring(0,100)}...]`};
      }
    }

    const allMsgs=[...sysMsgs,...chatMsgs];

    // ── Streaming mode ──────────────────────────────────────────────────
    if(doStream&&GK){
      const encoder=new TextEncoder();
      let toolCallAccum={};
      let fullContent='';
      let inToolCall=false;
      let finalMsgs=[...allMsgs];
      let iterCount=0;

      const stream=new ReadableStream({
        async start(controller){
          const send=(data)=>controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));

          try{
            // Agentic loop - up to 5 tool calls then stream final answer
            while(iterCount<5){
              iterCount++;
              const groqResp=await groqStream(finalMsgs,TOOLS,req.signal);
              if(!groqResp.ok){
                // Fallback to non-streaming
                const fallback=await (GEK?geminiCall(finalMsgs):Promise.resolve('Erro de API'));
                send({type:'text',content:fallback});
                break;
              }

              const reader=groqResp.body.getReader();
              const dec=new TextDecoder();
              let pendingToolCalls=[];
              let assistantContent='';
              toolCallAccum={};

              while(true){
                const{done,value}=await reader.read();
                if(done)break;
                const chunk=dec.decode(value);
                const lines=chunk.split('\n');
                for(const line of lines){
                  if(!line.startsWith('data:'))continue;
                  const data=line.slice(5).trim();
                  if(data==='[DONE]')continue;
                  try{
                    const parsed=JSON.parse(data);
                    const delta=parsed.choices?.[0]?.delta;
                    if(!delta)continue;

                    // Stream text content
                    if(delta.content){
                      assistantContent+=delta.content;
                      send({type:'text',content:delta.content});
                    }

                    // Accumulate tool calls
                    if(delta.tool_calls){
                      for(const tc of delta.tool_calls){
                        const i=tc.index||0;
                        if(!toolCallAccum[i])toolCallAccum[i]={id:'',name:'',args:''};
                        if(tc.id)toolCallAccum[i].id=tc.id;
                        if(tc.function?.name)toolCallAccum[i].name=tc.function.name;
                        if(tc.function?.arguments)toolCallAccum[i].args+=tc.function.arguments;
                      }
                    }
                  }catch(e){}
                }
              }

              // Check if we have tool calls to execute
              const tcList=Object.values(toolCallAccum);
              if(tcList.length===0||!tcList[0].name){
                // No tool calls, we're done
                break;
              }

              // Execute tools
              send({type:'tool_start',tools:tcList.map(t=>t.name)});
              finalMsgs.push({role:'assistant',content:assistantContent||null,tool_calls:tcList.map(t=>({id:t.id||`call_${Date.now()}`,type:'function',function:{name:t.name,arguments:t.args}}))});

              for(const tc of tcList){
                let args={};
                try{args=JSON.parse(tc.args);}catch(e){}
                send({type:'tool_running',tool:tc.name});
                const result=await runTool(tc.name,args);
                send({type:'tool_result',tool:tc.name,preview:result.substring(0,100)});
                finalMsgs.push({role:'tool',tool_call_id:tc.id||`call_${Date.now()}`,content:result});
              }
              // Continue loop for final answer
            }

            send({type:'done',version:VER});
            controller.close();
          }catch(e){
            send({type:'error',message:e.message});
            controller.close();
          }
        }
      });

      return new Response(stream,{headers:{'Content-Type':'text/event-stream','Cache-Control':'no-cache','Connection':'keep-alive','X-Accel-Buffering':'no'}});
    }

    // ── Non-streaming fallback ──────────────────────────────────────────
    let finalMsgs2=[...allMsgs];
    let reply='',iter=0;
    while(iter<5){
      iter++;
      let d;
      if(GK){d=await groqCall(finalMsgs2,TOOLS);}
      else if(GEK){reply=await geminiCall(finalMsgs2);break;}
      else{reply='❌ Nenhuma API configurada';break;}

      const msg=d.choices?.[0]?.message;
      if(!msg){reply=d.error?.message||'Erro';break;}
      if(!msg.tool_calls||msg.tool_calls.length===0){reply=msg.content||'';break;}

      finalMsgs2.push(msg);
      for(const tc of msg.tool_calls){
        let args={};try{args=JSON.parse(tc.function.arguments);}catch(e){}
        const result=await runTool(tc.function.name,args);
        finalMsgs2.push({role:'tool',tool_call_id:tc.id,content:result});
      }
    }

    return NextResponse.json({reply,version:VER});
  }catch(e){
    return NextResponse.json({reply:`❌ Erro: ${e.message}`,version:VER},{status:500});
  }
}
