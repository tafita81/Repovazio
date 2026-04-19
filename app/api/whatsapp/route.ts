export const dynamic='force-dynamic';
export const maxDuration=60;
const GK=process.env.GROQ_API_KEY;
const GMK=process.env.GEMINI_API_KEY;
const OAK=process.env.OPENAI_API_KEY;
const WA_TOKEN=process.env.WHATSAPP_TOKEN;
const WA_PHONE=process.env.WHATSAPP_PHONE_ID;
const WA_GROUP=process.env.WHATSAPP_GROUP_ID;
const SU=process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK=process.env.SUPABASE_SERVICE_KEY;
const POOL=["alguem mais sente que a ansiedade aparece quando as coisas estao indo bem? tipo sabotagem automatica","tava pensando hoje... quanto tempo a gente gasta fingindo estar bem pra nao preocupar as pessoas","sei la se e so comigo mas o silencio de certas pessoas diz muito mais que qualquer palavra","as vezes a gente precisa de um tempo sozinho nao porque quer mas porque e a unica forma de processar tudo","alguem aqui tambem teve que aprender a colocar limites com pessoas que ama? como foi isso?","o corpo avisa antes da mente. dor nas costas, aperto no peito, cansaco sem razao... sinais que a gente ignora","crescer significa perceber que algumas pessoas nao vao mudar e tudo bem. a mudanca que importa e a nossa","quem aqui passou por um relacionamento que parecia amor mas era dependencia emocional? como saiu disso?","nao e fraqueza chorar. e o corpo liberando o que a mente nao consegue mais segurar","ja repararam como a gente naturaliza o estresse como se fosse normal viver no limite todo dia?"];
async function ai(prompt:string,sys:string,tok=200):Promise<{text:string,model:string}>{
  try{if(GK){const r=await fetch('https://api.groq.com/openai/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+GK},body:JSON.stringify({model:'llama-3.3-70b-versatile',max_tokens:tok,temperature:0.92,messages:[{role:'system',content:sys},{role:'user',content:prompt}]})});const d=await r.json();if(r.ok&&d.choices?.[0]?.message?.content)return{text:d.choices[0].message.content,model:'groq'};}}catch{}
  try{if(GMK){const r=await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key='+GMK,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({system_instruction:{parts:[{text:sys}]},contents:[{parts:[{text:prompt}]}],generationConfig:{maxOutputTokens:tok,temperature:0.92}})});const d=await r.json();if(r.ok&&d.candidates?.[0]?.content?.parts?.[0]?.text)return{text:d.candidates[0].content.parts[0].text,model:'gemini'};}}catch{}
  try{if(OAK){const r=await fetch('https://api.openai.com/v1/chat/completions',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+OAK},body:JSON.stringify({model:'gpt-4o-mini',max_tokens:tok,temperature:0.92,messages:[{role:'system',content:sys},{role:'user',content:prompt}]})});const d=await r.json();if(r.ok&&d.choices?.[0]?.message?.content)return{text:d.choices[0].message.content,model:'openai'};}}catch{}
  return{text:'',model:'none'};
}
async function db(path:string,method='GET',body?:object){
  if(!SU||!SK)return null;
  try{const r=await fetch(SU+'/rest/v1/'+path,{method,headers:{'Content-Type':'application/json',apikey:SK,Authorization:'Bearer '+SK,Prefer:method==='POST'?'return=representation':''},body:body?JSON.stringify(body):undefined});return r.ok?r.json():null;}catch{return null;}
}
async function enviarWA(texto:string):Promise<boolean>{
  if(!WA_TOKEN||!WA_PHONE||!WA_GROUP)return false;
  try{const r=await fetch('https://graph.facebook.com/v19.0/'+WA_PHONE+'/messages',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+WA_TOKEN},body:JSON.stringify({messaging_product:'whatsapp',to:WA_GROUP,type:'text',text:{body:texto}})});return r.ok;}catch{return false;}
}
export async function GET(req:Request){
  const horaSP=new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'});
  const hora=parseInt(horaSP.split(', ')[1]?.split(':')[0]||'12');
  if(hora<8||hora>=22)return Response.json({status:'silencio_noturno',hora:horaSP});
  const recentes=(await db('whatsapp_mensagens?order=timestamp.desc&limit=20'))||[];
  const naoRespondida=(recentes as any[]).find((m:any)=>!m.respondido&&(m.sentimento==='angustia'||m.sentimento==='tristeza'));
  const sys='Voce e um membro anonimo de um grupo de psicologia no WhatsApp. Brasileiro, 28-35 anos, interessado em saude mental. NUNCA revele que e IA. Tom humano informal, ocasionalmente com erros de digitacao naturais. Maximo 2 frases. Sem emojis em excesso. Hora: '+horaSP;
  let mensagem='';let modelo='none';let motivo='';
  if(naoRespondida&&Math.random()<0.4){
    const{text,model}=await ai('Alguem disse no grupo: "'+naoRespondida.conteudo+'". Responda de forma humana empatica curta (1-2 frases). Nao use emojis. Nao seja obvio. Seja natural.',sys,120);
    mensagem=text;modelo=model;motivo='resposta_mensagem_'+naoRespondida.id;
    if(naoRespondida.id)await db('whatsapp_mensagens?id=eq.'+naoRespondida.id,'PATCH',{respondido:true});
  } else {
    const base=POOL[Math.floor(Math.random()*POOL.length)];
    const{text,model}=await ai('Baseado nessa ideia: "'+base+'", escreva UMA mensagem para grupo de psicologia. Tom humano informal 1-2 frases sem emojis como pensamento espontaneo.',sys,120);
    mensagem=text||base;modelo=model;motivo='iniciativa';
  }
  if(!mensagem)return Response.json({status:'sem_mensagem'});
  const delayMin=Math.floor(Math.random()*43)+2;
  const horarioEnvio=new Date(Date.now()+delayMin*60000);
  await db('whatsapp_respostas','POST',{resposta:mensagem,modelo_ia:modelo,enviado:false,horario_programado:horarioEnvio.toISOString(),motivo});
  const enviado=await enviarWA(mensagem);
  return Response.json({status:'ok',mensagem,modelo,delay_min:delayMin,enviado,motivo,hora_sp:horaSP});
}
export async function POST(req:Request){
  try{
    const body=await req.json();
    if(body['hub.verify_token']==='psicologiadoc_webhook')return new Response(body['hub.challenge'],{status:200});
    const messages=body.entry?.[0]?.changes?.[0]?.value?.messages;
    if(!messages?.length)return Response.json({ok:true});
    const sysAnalise='Classifique o sentimento em uma palavra: alegria, tristeza, ansiedade, angustia, neutro, duvida, encorajamento. Responda APENAS com uma palavra.';
    for(const msg of messages){
      const conteudo=msg.text?.body||'';
      const remetente=msg.from;
      const nome=body.entry?.[0]?.changes?.[0]?.value?.contacts?.find((c:any)=>c.wa_id===remetente)?.profile?.name||'Membro';
      if(!conteudo)continue;
      const{text:sent}=await ai(conteudo,sysAnalise,10);
      await db('whatsapp_mensagens','POST',{remetente,remetente_nome:nome,conteudo,tipo:'texto',grupo_id:WA_GROUP||'principal',sentimento:sent?.trim().toLowerCase()||'neutro'});
    }
    return Response.json({ok:true});
  }catch(e:any){return Response.json({erro:e.message},{status:500});}
}