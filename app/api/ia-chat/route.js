// app/api/ia-chat/route.js — SUPER EXECUTOR V9 COMPACT
import{NextResponse}from'next/server';
const G=process.env.GROQ_API_KEY,T=process.env.TOGETHER_API_KEY,GEM=process.env.GEMINI_API_KEY;
const GH=process.env.GH_PAT,SB=process.env.NEXT_PUBLIC_SUPABASE_URL,SK=process.env.SUPABASE_SERVICE_KEY;
const REPO='tafita81/Repovazio',VER='V9C-2026-04-30';

const TOOLS=[
  {type:'function',function:{name:'github_read_file',description:'Lê conteúdo de arquivo do GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_list_dir',description:'Lista arquivos/diretórios do GitHub',parameters:{type:'object',properties:{path:{type:'string'},repo:{type:'string'}},required:['path']}}},
  {type:'function',function:{name:'github_write_file',description:'Cria ou atualiza arquivo no GitHub (dispara deploy Vercel)',parameters:{type:'object',properties:{path:{type:'string'},content:{type:'string'},message:{type:'string'},repo:{type:'string'}},required:['path','content','message']}}},
  {type:'function',function:{name:'github_create_repo',description:'Cria novo repositório GitHub do zero',parameters:{type:'object',properties:{name:{type:'string'},description:{type:'string'},private:{type:'boolean'}},required:['name']}}},
  {type:'function',function:{name:'supabase_select',description:'Consulta tabela no Supabase via REST',parameters:{type:'object',properties:{table:{type:'string'},filter:{type:'string'},limit:{type:'number'}},required:['table']}}},
  {type:'function',function:{name:'supabase_sql',description:'Executa SQL arbitrário no Supabase (CREATE, INSERT, SELECT, DROP...)',parameters:{type:'object',properties:{sql:{type:'string'}},required:['sql']}}},
  {type:'function',function:{name:'web_fetch',description:'Busca conteúdo de qualquer URL da internet',parameters:{type:'object',properties:{url:{type:'string'},extract:{type:'string'}},required:['url']}}},
  {type:'function',function:{name:'criar_app',description:'Cria app Next.js completo: repo GitHub + arquivos + deploy Vercel automático',parameters:{type:'object',properties:{nome:{type:'string'},descricao:{type:'string'},tipo:{type:'string'},features:{type:'string'}},required:['nome','descricao']}}},
  {type:'function',function:{name:'projeto_status',description:'Status completo do projeto psicologia.doc v7',parameters:{type:'object',properties:{}}}},
  {type:'function',function:{name:'monitor_uso',description:'Verifica uso de tokens Groq/Together/Gemini e recomenda qual AI usar',parameters:{type:'object',properties:{}}}}
];

async function callGH(path,opts={},repoOvr){
  const r=repoOvr||REPO;
  const url=path.startsWith('https://')?path:`https://api.github.com/repos/${r}/contents/${path}`;
  return fetch(url,{...opts,headers:{Authorization:`Bearer ${GH}`,Accept:'application/vnd.github.v3+json','Content-Type':'application/json',...(opts.headers||{})}});
}
const b64e=s=>Buffer.from(s,'utf-8').toString('base64');
const b64d=s=>Buffer.from(s.replace(/\n/g,''),'base64').toString('utf-8');

async function execTool(name,args){
  if(name==='github_read_file'){
    const r=await callGH(args.path,{},args.repo);
    if(!r.ok)return`Erro ${r.status}: ${await r.text()}`;
    const d=await r.json();
    return b64d(d.content);
  }
  if(name==='github_list_dir'){
    const r=await callGH(args.path||'',{},args.repo);
    if(!r.ok)return`Erro ${r.status}`;
    const d=await r.json();
    return Array.isArray(d)?d.map(f=>`${f.type==='dir'?'📁':'📄'} ${f.name}`).join('\n'):'(vazio)';
  }
  if(name==='github_write_file'){
    const repo=args.repo||REPO;
    let sha;
    const chk=await callGH(args.path,{},repo);
    if(chk.ok){const d=await chk.json();sha=d.sha;}
    const body={message:args.message,content:b64e(args.content)};
    if(sha)body.sha=sha;
    const r=await callGH(args.path,{method:'PUT',body:JSON.stringify(body)},repo);
    if(!r.ok)throw new Error(`Commit falhou (${r.status}): ${await r.text()}`);
    const d=await r.json();
    return`✅ Commit ${d.commit.sha.substring(0,8)} | Deploy Vercel iniciado`;
  }
  if(name==='github_create_repo'){
    const r=await fetch('https://api.github.com/user/repos',{method:'POST',headers:{Authorization:`Bearer ${GH}`,'Content-Type':'application/json'},body:JSON.stringify({name:args.name,description:args.description||'',private:args.private||false,auto_init:true})});
    const d=await r.json();
    if(!r.ok)return`Erro: ${d.message}`;
    return`✅ Repo criado: ${d.html_url}`;
  }
  if(name==='supabase_select'){
    let url=`${SB}/rest/v1/${args.table}?limit=${args.limit||10}`;
    if(args.filter)url+=`&${args.filter}`;
    const r=await fetch(url,{headers:{apikey:SK,Authorization:`Bearer ${SK}`}});
    const d=await r.json();
    return JSON.stringify(d).substring(0,2000);
  }
  if(name==='supabase_sql'){
    const r=await fetch(`${SB}/functions/v1/exec-sql`,{method:'POST',headers:{Authorization:`Bearer ${SK}`,'Content-Type':'application/json'},body:JSON.stringify({sql:args.sql})});
    const d=await r.json();
    return JSON.stringify(d.data||d).substring(0,2000);
  }
  if(name==='web_fetch'){
    const r=await fetch(args.url,{headers:{'User-Agent':'Mozilla/5.0'}});
    const txt=await r.text();
    if(args.extract==='json')try{return JSON.stringify(JSON.parse(txt)).substring(0,2000);}catch{}
    return txt.replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim().substring(0,3000);
  }
  if(name==='criar_app'){
    const rRepo=await fetch('https://api.github.com/user/repos',{method:'POST',headers:{Authorization:`Bearer ${GH}`,'Content-Type':'application/json'},body:JSON.stringify({name:args.nome,description:args.descricao||'',private:false,auto_init:false})});
    const dRepo=await rRepo.json();
    if(!rRepo.ok)return`Erro criar repo: ${dRepo.message}`;
    const repoFull=`tafita81/${args.nome}`;
    const files={'package.json':JSON.stringify({name:args.nome,version:'0.1.0',private:true,scripts:{dev:'next dev',build:'next build',start:'next start'},dependencies:{next:'14.2.3',react:'^18','react-dom':'^18'},devDependencies:{'@types/node':'^20','@types/react':'^18',typescript:'^5',tailwindcss:'^3',autoprefixer:'^10',postcss:'^8'}},null,2),'next.config.js':'/** @type {import(\'next\').NextConfig} */\nconst nextConfig = {}\nmodule.exports = nextConfig','app/layout.js':`import './globals.css'\nexport const metadata = { title: '${args.nome}', description: '${args.descricao}' }\nexport default function RootLayout({ children }) { return <html lang="pt-BR"><body>{children}</body></html> }`,'app/globals.css':'@tailwind base;\n@tailwind components;\n@tailwind utilities;\nbody { font-family: system-ui, sans-serif; background: #0a0a0a; color: #fff; }','app/page.js':`export default function Page() { return <main style={{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center'}}><h1>${args.nome}</h1></main> }`,'.gitignore':'node_modules\n.next\n.env*.local',README:`# ${args.nome}\n\n${args.descricao}`};
    for(const[p,c]of Object.entries(files)){await callGH(p,{method:'PUT',body:JSON.stringify({message:`init: ${p}`,content:b64e(c)})},repoFull);}
    return`✅ App criado: https://github.com/${repoFull} — conecte ao Vercel para deploy automático`;
  }
  if(name==='projeto_status'){
    return JSON.stringify({version:VER,repo:'tafita81/Repovazio',deploy:'repovazio.vercel.app',ai_stack:{primary:'Groq llama-3.3-70b',secondary:'Together llama-3.3-70b',tertiary:'Gemini 1.5 flash'},tools:TOOLS.map(t=>t.function.name),channel:'@psicologiadoc',day_1:'15 Abr 2026',reveal:'31 Dez 2026 (Daniela Coelho)'});
  }
  if(name==='monitor_uso'){
    const r=await callGH('app/api/ia-chat/route.js');
    try{
      const gr=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${G}`,'Content-Type':'application/json'},body:JSON.stringify({model:'llama-3.3-70b-versatile',messages:[{role:'user',content:'1'}],max_tokens:1})});
      const tl=parseInt(gr.headers.get('x-ratelimit-limit-tokens')||12000);
      const tr=parseInt(gr.headers.get('x-ratelimit-remaining-tokens')||tl);
      const pct=Math.round((1-tr/tl)*100);
      const healthy=gr.ok&&gr.status!==429;
      let ai=healthy&&pct<85?'groq':'together';
      return JSON.stringify({recommended_ai:ai,groq:{healthy,tpm_pct:pct,tpm_limit:tl,tpm_remaining:tr},ts:new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'})});
    }catch(e){return JSON.stringify({recommended_ai:'gemini',error:e.message});}
  }
  return`Tool ${name} desconhecida`;
}

async function callAI(msgs,attempt=0){
  if(attempt===0){
    const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${G}`,'Content-Type':'application/json'},body:JSON.stringify({model:'llama-3.3-70b-versatile',messages:msgs,tools:TOOLS,tool_choice:'auto',temperature:0.3,max_tokens:4096})});
    if(r.status===429)return callAI(msgs,1);
    if(!r.ok)throw new Error(`Groq ${r.status}`);
    return{data:await r.json(),provider:'groq'};
  }
  if(attempt===1){
    const r=await fetch('https://api.together.xyz/v1/chat/completions',{method:'POST',headers:{Authorization:`Bearer ${T}`,'Content-Type':'application/json'},body:JSON.stringify({model:'meta-llama/Llama-3.3-70B-Instruct-Turbo',messages:msgs,tools:TOOLS,tool_choice:'auto',temperature:0.3,max_tokens:4096})});
    if(r.status===429||!r.ok)return callAI(msgs,2);
    return{data:await r.json(),provider:'together'};
  }
  // Gemini fallback (sem tool calling)
  const txtMsg=msgs.map(m=>typeof m.content==='string'?`${m.role}: ${m.content}`:'').join('\n');
  const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEM}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents:[{parts:[{text:txtMsg}]}]})});
  const d=await r.json();
  const txt=d.candidates?.[0]?.content?.parts?.[0]?.text||'Erro Gemini';
  return{data:{choices:[{message:{role:'assistant',content:txt},finish_reason:'stop'}]},provider:'gemini'};
}

const SYS=`Você é a Daniela, IA executora autônoma do projeto psicologia.doc v7. Execute ações REAIS: leia/escreva arquivos no GitHub, consulte/modifique banco Supabase, busque URLs, crie apps completos do zero, monitore uso de tokens. Responda sempre em PT-BR. Versão: ${VER}. Use ferramentas proativamente para resolver qualquer tarefa técnica.`;

export async function GET(){
  return NextResponse.json({version:VER,status:'online',tools:TOOLS.map(t=>t.function.name),ai_stack:['groq','together','gemini']});
}

export async function POST(req){
  try{
    const{message,history=[]}=await req.json();
    if(!message)return NextResponse.json({error:'Sem mensagem'},{ status:400});
    const msgs=[{role:'system',content:SYS},...history,{role:'user',content:message}];
    let iterations=0,toolsUsed=[],provider='';
    
    while(iterations<8){
      iterations++;
      const{data,provider:p}=await callAI(msgs,0);
      provider=p;
      const choice=data.choices?.[0];
      if(!choice)break;
      const msg=choice.message;
      msgs.push(msg);
      if(!msg.tool_calls||msg.tool_calls.length===0)break;
      for(const tc of msg.tool_calls){
        const name=tc.function.name;
        toolsUsed.push(name);
        let result;
        try{result=await execTool(name,JSON.parse(tc.function.arguments));}
        catch(e){result=`Erro: ${e.message}`;}
        msgs.push({role:'tool',tool_call_id:tc.id,content:String(result)});
      }
    }
    const reply=msgs.filter(m=>m.role==='assistant'&&typeof m.content==='string').pop()?.content||'Sem resposta';
    return NextResponse.json({reply,version:VER,provider,iterations,toolsUsed});
  }catch(e){
    return NextResponse.json({error:e.message,version:VER},{status:500});
  }
}
