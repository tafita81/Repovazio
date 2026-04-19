export const dynamic='force-dynamic';
export const maxDuration=60;
const GK=process.env.GROQ_API_KEY;
const GMK=process.env.GEMINI_API_KEY;
const OAK=process.env.OPENAI_API_KEY;
const PGH=process.env.GITHUB_PAT||'';
const REPO='tafita81/Repovazio';
const SU=process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK=process.env.SUPABASE_SERVICE_KEY;
async function db(p:string,m='GET',b?:object){
  if(!SU||!SK)return null;
  try{const r=await fetch(`${SU}/rest/v1/${p}`,{method:m,headers:{'Content-Type':'application/json',apikey:SK,Authorization:`Bearer ${SK}`,Prefer:m==='POST'?'return=representation':''},body:b?JSON.stringify(b):undefined});return r.ok?r.json():null;}catch{return null;}
}
async function lerGH(p:string){
  if(!PGH)return 'GITHUB_PAT nao configurada';
  try{const r=await fetch(`https://api.github.com/repos/${REPO}/contents/${p}`,{headers:{Authorization:`token ${PGH}`}});const d=await r.json();if(!r.ok)return 'Nao encontrado: '+p;return new TextDecoder().decode(Uint8Array.from(atob(d.content.replace(/\n/g,'')),c=>c.charCodeAt(0)));
  }catch(e:any){return 'Erro: '+e.message;}
}
async function editGH(p:string,content:string,msg:string){
  if(!PGH)return 'GITHUB_PAT nao configurada';
  try{
    const cr=await fetch(`https://api.github.com/repos/${REPO}/contents/${p}`,{headers:{Authorization:`token ${PGH}`}});
    const cd=await cr.json();if(!cr.ok)return 'Nao encontrado: '+p;
    const enc=new TextEncoder();const bytes=enc.encode(content);
    let bin='';for(let i=0;i<bytes.length;i+=8192)bin+=String.fromCharCode(...bytes.subarray(i,i+8192));
    const b64=btoa(bin);
    const r=await fetch(`https://api.github.com/repos/${REPO}/contents/${p}`,{method:'PUT',headers:{Authorization:`token ${PGH}`,'Content-Type':'application/json'},body:JSON.stringify({message:msg||'edit Executor IA',content:b64,sha:cd.sha})});
    return r.ok?'Editado: '+p:'Erro ao editar: '+p;
  }catch(e:any){return 'Erro: '+e.message;}
}
async function deployGH(){
  if(!PGH)return 'GITHUB_PAT nao configurada';
  try{
    const ref=await(await fetch(`https://api.github.com/repos/${REPO}/git/ref/heads/main`,{headers:{Authorization:`token ${PGH}`}})).json();
    const cm=await(await fetch(`https://api.github.com/repos/${REPO}/git/commits/${ref.object.sha}`,{headers:{Authorization:`token ${PGH}`}})).json();
    const nc=await(await fetch(`https://api.github.com/repos/${REPO}/git/commits`,{method:'POST',headers:{Authorization:`token ${PGH}`,'Content-Type':'application/json'},body:JSON.stringify({message:'chore: deploy Executor IA',tree:cm.tree.sha,parents:[ref.object.sha]})})).json();
    await fetch(`https://api.github.com/repos/${REPO}/git/refs/heads/main`,{method:'PATCH',headers:{Authorization:`token ${PGH}`,'Content-Type':'application/json'},body:JSON.stringify({sha:nc.sha})});
    return 'Deploy iniciado: '+nc.sha.slice(0,7);
  }catch(e:any){return 'Deploy falhou: '+e.message;}
}
async function callAI(msgs:any[],sys:string,maxTok=3000):Promise<{text:string,model:string}>{
  try{if(GK){const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${GK}`},body:JSON.stringify({model:'llama-3.3-70b-versatile',max_tokens:maxTok,temperature:0.7,messages:[{role:'system',content:sys},...msgs]})});const d=await r.json();if(r.ok&&d.choices?.[0]?.message?.content)return{text:d.choices[0].message.content,model:'groq-llama-3.3-70b'};}}catch(e){}
  try{if(GMK){const ct=msgs.map((m:any)=>({role:m.role==='assistant'?'model':'user',parts:[{text:m.content}]}));const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GMK}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({system_instruction:{parts:[{text:sys}]},contents:ct,generationConfig:{maxOutputTokens:Math.min(maxTok,2048),temperature:0.7}})});const d=await r.json();if(r.ok&&d.candidates?.[0]?.content?.parts?.[0]?.text)return{text:d.candidates[0].content.parts[0].text,model:'gemini-2.0-flash'};}}catch(e){}
  try{if(OAK){const r=await fetch('https://api.openai.com/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:`Bearer ${OAK}`},body:JSON.stringify({model:'gpt-4o-mini',max_tokens:maxTok,temperature:0.7,messages:[{role:'system',content:sys},...msgs]})});const d=await r.json();if(r.ok&&d.choices?.[0]?.message?.content)return{text:d.choices[0].message.content,model:'openai-gpt4o-mini'};}}catch(e){}
  return{text:'Nenhuma IA disponivel.',model:'none'};
}
export async function POST(req:Request){
  try{
    const body=await req.json();
    const pergunta:string=body.pergunta||'';
    const historico:any[]=body.historico||[];
    if(!pergunta)return Response.json({erro:'Pergunta vazia'},{status:400});
    const horaSP=new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});
    let execResult='';let ctx='';
    const pl=pergunta.toLowerCase();
    if(pl.includes('ler ')||pl.includes('ver arquivo')){const m=pergunta.match(/(?:ler|ver)\s+(?:arquivo\s+)?([a-zA-Z0-9\/._-]+\.[a-zA-Z]{1,5})/i);if(m){ctx='ARQUIVO '+m[1]+':\n'+(await lerGH(m[1]));}}
    if(pl.includes('metricas')||pl.includes('score')||pl.includes('roteiro')||pl.includes('producao')){const[r1,r2]=await Promise.all([db('registros?order=created_at.desc&limit=10&select=topic,score,modelo,inovacao'),db('cerebro_memoria?order=score.desc&limit=10&select=topic,score,vezes_gerado')]);ctx='METRICAS:\n'+JSON.stringify({regs:r1,mem:r2},null,1).slice(0,2000);}
    if(pl.includes('deploy')||pl.includes('subir')){execResult=await deployGH();}
    const[rr,mm]=await Promise.all([db('registros?order=created_at.desc&limit=5&select=topic,score,modelo'),db('cerebro_memoria?order=score.desc&limit=5&select=topic,score')]);
    const sys=[
      'Voce e o Executor IA do psicologia.doc v7 — agente autonomo CTO+CMO+Estrategista.',
      'Voce PODE: editar arquivos GitHub respondendo com EDITAR_ARQUIVO: caminho/arquivo\n[codigo completo]\nFIM_ARQUIVO',
      'Voce PODE: analisar metricas, criar rotas, fazer deploy respondendo com a palavra deploy.',
      `Stack: Next.js 14+Supabase+Groq(14400req/dia)+Gemini+OpenAI GPT-4o-mini fallback pago.`,
      `Repo: ${REPO} | Deploy: repovazio.vercel.app | Canal: @psicologiadoc`,
      'Missao: canal dark YouTube PT-BR psicologia. Revelar Daniela Coelho psicologa Dia 261 ~31/dez/2026.',
      'WhatsApp grupo max 1024 membros — agente humanizado autonomo — viram clientes Daniela dez/2026.',
      'PRODUCOES: '+((rr as any[])||[]).map((r:any)=>r.topic+'('+r.score+')').join(', '),
      'TOP MEM: '+((mm as any[])||[]).slice(0,5).map((m:any)=>m.topic+':'+m.score).join(', '),
      'PENDENCIAS: 1.ElevenLabs 2.HeyGen 3.YouTube OAuth 4.Instagram 5.TikTok 6.Pinterest 7.PublicarDia1 8.AdSense',
      `Hora SP: ${horaSP}`,
      ctx?('CONTEXTO:\n'+ctx):'',
    ].filter(Boolean).join('\n');
    const msgs=[...historico.slice(-10).map((h:any)=>({role:h.role==='model'?'assistant':'user',content:h.text})),{role:'user',content:pergunta}];
    const{text:resposta,model}=await callAI(msgs,sys,3000);
    const mEdit=resposta.match(/EDITAR_ARQUIVO:\s*([^\n]+)\n([\s\S]+?)FIM_ARQUIVO/);
    if(mEdit&&!execResult){execResult=await editGH(mEdit[1].trim(),mEdit[2].trim(),'feat: Executor IA');}
    return Response.json({resposta,model,execResult:execResult||undefined,timestamp:new Date().toISOString()});
  }catch(e:any){return Response.json({erro:e.message},{status:500});}
}