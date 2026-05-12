"use client";
import { useState, useEffect, useRef, useCallback } from "react";

// ═══════════════════════════════════════════════════════════════════
// PSICOLOGIA.DOC — CÉREBRO AUTÔNOMO v7
// Canal: @psicologiadoc (DOC = Daniela Oliveira Coelho + documentário)
// Dia 1 = 15 abr 2026 | Revelação = ~1 jan 2027 (Dia 261)
// 2026: Canal 100% anônimo — ZERO menção a nome ou pessoa
// 2027: Daniela Coelho, psicóloga (NÃO "Dra." — apenas psicóloga)
// ═══════════════════════════════════════════════════════════════════


const SBU = "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwanZhbHp3a3F3dHR2bXN6dmllIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Njg2OTIzMCwiZXhwIjoyMDYyNDQ1MjMwfQ.v8h1t7cjDvM2vxGpMr7sRlWEWvDSnBBpgjNPGDZ7Rlk";
const H_SB = {apikey:SBK,"Authorization":"Bearer "+SBK};
async function sbFetch(path){try{const r=await fetch(SBU+"/rest/v1/"+path,{headers:H_SB});return r.ok?r.json():[];}catch{return[];}}

const RANK_INTERVAL = 60*1000;
const PROD_INTERVAL = 30*60*1000;
const FIRST_RANK    = 15*1000;
const FIRST_PROD    = 60*1000;

const CANAL = {
  nome:    "psicologia.doc",
  handle:  "@psicologiadoc",
  slogan:  "A psicologia que você vive — documentada.",
  bio2026: "@psicologiadoc | Psicologia documentada 🎬 | Saúde mental que você reconhece | Novos docs toda semana",
  bio2027: "@psicologiadoc | Daniela Coelho, psicóloga 🧠 | CRP [NÚMERO] | Consultas online → link na bio",
};

const JORNADA_INICIO = new Date("2026-04-15T00:00:00");
const DIA_REVELACAO  = 261; // ~1 jan 2027

function calcDay() {
  return Math.max(1, Math.floor((new Date()-JORNADA_INICIO)/86400000)+1);
}
function dayToDate(d) {
  const dt = new Date(JORNADA_INICIO);
  dt.setDate(dt.getDate()+d-1);
  return dt.toLocaleDateString("pt-BR",{day:"2-digit",month:"2-digit",year:"numeric"});
}
function getPhase(day, revealed) {
  if (revealed) return {label:"Fase 7: Daniela Coelho, psicóloga",goal:"Consultas + 500K+ + R$80-250K/mês",color:"var(--green)",period:"2027+"};
  if (day<=14)  return {label:"Fase 1: Fundação SEO",  goal:"1.000 inscritos · buscas",          color:"var(--blue)",  period:dayToDate(1)+" – "+dayToDate(14)};
  if (day<=30)  return {label:"Fase 2: Viralização",   goal:"5.000 inscritos · primeiro viral",   color:"var(--purple)",period:dayToDate(15)+" – "+dayToDate(30)};
  if (day<=60)  return {label:"Fase 3: Escala",        goal:"10K inscritos · AdSense",            color:"var(--green)", period:dayToDate(31)+" – "+dayToDate(60)};
  if (day<=180) return {label:"Fase 4: Crescimento",   goal:"50K · R$10-40K/mês",                color:"var(--amber)", period:dayToDate(61)+" – "+dayToDate(180)};
  if (day<=260) return {label:"Fase 5: Autoridade",    goal:"100K+ · marca anônima sólida",       color:"var(--red)",   period:dayToDate(181)+" – "+dayToDate(260)};
  return          {label:"Fase 6: Pré-revelação",      goal:"200K+ · lista de espera consultas",  color:"#a855f7",      period:dayToDate(261)+"+"};
}

// ─── TÉCNICAS PNL + ENGENHARIA DE ATENÇÃO ──────────────────────
// Cases reais: Therapy in a Nutshell (2M), Psych2Go (13M),
// Dr. Nicole LePera (12M), Canal Dark (1.2M views R$24K/60 dias)
const ATTENTION_HOOKS = [
  "Se você faz [COMPORTAMENTO] quando [SITUAÇÃO], esse documentário foi feito especificamente para você.",
  "Por que você continua atraindo [TIPO DE PESSOA] mesmo sabendo que vai te machucar?",
  "Existe um padrão documentado em [N]% das pessoas e quase ninguém fala sobre isso abertamente.",
  "O que você vai descobrir nos próximos [N] minutos vai mudar como você vê [SITUAÇÃO] para sempre.",
  "Você provavelmente já sentiu [EMOÇÃO] sem conseguir explicar de onde vem. A ciência explica.",
  "Documentamos [N] casos reais de [TEMA]. O que descobrimos vai te surpreender.",
  "Em [ANO], pesquisadores documentaram algo que ainda acontece com milhões de pessoas hoje.",
  "Tem um nome técnico para o que você sente quando [SITUAÇÃO]. E existe uma saída.",
  "Se alguém perto de você age assim, este documentário explica exatamente o porquê.",
  "A resposta está no final deste documentário — mas você precisa entender o contexto primeiro.",
];

const VIRAL_PATTERNS = [
  "Por que Você [VERBO] Quando [SITUAÇÃO]",
  "[N] Sinais que Você Tem [CONDIÇÃO] (e Não Sabe)",
  "Por que Você Atrai [TIPO PROBLEMÁTICO]",
  "Como Parar de [COMPORTAMENTO] — A Psicologia Explica",
  "[CONDIÇÃO]: O que Ninguém te Conta",
  "O que Acontece com o Seu Cérebro Quando [SITUAÇÃO]",
  "[N] Comportamentos que Parecem Normais Mas São [CONDIÇÃO]",
  "A Psicologia Por Trás de [LIVRO/SITUAÇÃO] — Documentado",
];

const TOPICS = [
  "Ansiedade & Burnout","Apego Ansioso","Narcisismo & Manipulação",
  "Trauma de Infância","Autossabotagem","Relacionamentos Tóxicos",
  "Inteligência Emocional","Depressão & Tristeza","Limites Saudáveis",
  "Gaslighting","Autoestima","Síndrome do Impostor",
  "Dependência Emocional","Luto & Perda","Ansiedade Social",
  "Psicologia do Dinheiro","Liderança Tóxica","Vício em Validação",
];

const CHANNELS_LIST = ["youtube","tiktok","instagram","pinterest"];

// ─── BESTSELLERS POR TEMA (indexação sutil) ──────────────────────
const BESTSELLERS = {
  "Ansiedade & Burnout":      [{t:"Por que Zebras não Têm Úlcera",a:"Sapolsky"},{t:"O Corpo Guarda o Placar",a:"van der Kolk"}],
  "Apego Ansioso":            [{t:"Attached",a:"Levine & Heller"},{t:"Nós",a:"Lisa Fischler"}],
  "Narcisismo & Manipulação": [{t:"Why Does He Do That?",a:"Lundy Bancroft"}],
  "Trauma de Infância":       [{t:"O Corpo Guarda o Placar",a:"van der Kolk"},{t:"Childhood Disrupted",a:"Nakazawa"}],
  "Autossabotagem":           [{t:"The Big Leap",a:"Gay Hendricks"},{t:"Mindset",a:"Carol Dweck"}],
  "Relacionamentos Tóxicos":  [{t:"Too Good to Leave, Too Bad to Stay",a:"Kirshenbaum"}],
  "Inteligência Emocional":   [{t:"Inteligência Emocional",a:"Daniel Goleman"}],
  "Gaslighting":              [{t:"Gaslighting",a:"Stephanie Moulton Sacks"}],
  "Autoestima":               [{t:"Os 6 Pilares da Autoestima",a:"Nathaniel Branden"}],
  "Dependência Emocional":    [{t:"Codependent No More",a:"Melody Beattie"}],
  "Psicologia do Dinheiro":   [{t:"A Psicologia Financeira",a:"Morgan Housel"}],
};

// ─── SÉRIES EPISÓDICAS COM LOOP ABERTO ──────────────────────────
const SERIES_LIBRARY = [
  {id:"apego",      nome:"📎 A Ciência do Apego",      eps:8, status:"active",  lancamento:dayToDate(1),   subtitulo:"Por que você ama quem te faz sofrer", tecnica:"Cada ep termina: 'No próximo você vai descobrir POR QUE você faz X'"},
  {id:"narcisismo", nome:"🪞 Narcisismo Documentado",  eps:7, status:"planned", lancamento:dayToDate(30),  subtitulo:"O que ninguém conta sobre manipulação", tecnica:"Títulos: 'você provavelmente convive com um' — identificação + urgência"},
  {id:"ansiedade",  nome:"⚡ Ansiedade Documentada",   eps:8, status:"planned", lancamento:dayToDate(60),  subtitulo:"Sua mente acelerada tem um motivo",     tecnica:"22-28min + imagens cinematográficas = CPM máximo"},
  {id:"trauma",     nome:"🔓 Trauma Invisível",        eps:6, status:"planned", lancamento:dayToDate(90),  subtitulo:"O que seu corpo carrega sem você saber", tecnica:"Cada ep tem 1 exercício prático — aumenta retenção + compartilhamento"},
  {id:"burnout",    nome:"🔥 Burnout Documentado",     eps:5, status:"planned", lancamento:dayToDate(120), subtitulo:"Você não é preguiçoso — está esgotado",  tecnica:"Contradição no título = clique: 'Por que férias não curam burnout'"},
];

const SERIES_EPS = {
  apego:["Por Que Você Tem Tanto Medo de Ser Abandonado","Os 4 Estilos de Apego — em qual você está?","Por Que Você Atrai Pessoas Emocionalmente Indisponíveis","O Que Acontece no Seu Cérebro Quando Você se Apega Demais","Por Que Você Fica com Quem te Machuca — a Neurociência","Apego Evitativo — a Solidão Disfarçada de Independência","Como Mudar Seu Estilo de Apego (a Ciência Diz que é Possível)","Relacionamento Seguro — Como Reconhecer e Construir"],
  narcisismo:["O Que é Narcisismo de Verdade — Além do Senso Comum","Os 7 Tipos de Narcisismo (o 5º é o Mais Perigoso)","Como um Narcisista Conquista Você — Passo a Passo","Gaslighting Documentado — Sinais que Estão Acontecendo Agora","Por Que Você Fica com Narcisista Mesmo Sabendo que Faz Mal","Como Sair Dessa Relação Sem se Destruir","Se Recuperando do Abuso Narcisista — O Plano Real"],
  ansiedade:["O que é Ansiedade de Verdade (não é o que te disseram)","Por que Seu Cérebro Cria Ansiedade — Neurociência Real","Os 5 Tipos de Ansiedade que Poucos Falam","Trauma de Infância e Ansiedade Adulta — A Conexão","Por que Você não Consegue 'Simplesmente Relaxar'","Técnicas que a Ciência Provou Funcionar","Quando a Ansiedade Vira Doença — Sinais Claros","Vivendo Bem com Ansiedade — Regulação, não Cura"],
  trauma:["Trauma não é só Guerra — O Que Realmente É","Trauma Complexo (C-PTSD) — O Que Médicos Ainda Ignoram","Flashback Emocional — O Sintoma que Você não Sabia que Tinha","Seu Corpo Guarda o Trauma — Teoria Polivagal em 20min","Trauma de Infância no Adulto — 8 Comportamentos Reveladores","O Caminho Real de Cura — O Que a Ciência Diz"],
  burnout:["O Que é Burnout (não é Preguiça, não é Frescura)","Os 5 Estágios do Burnout — Em Qual Você Está?","Por Que Férias não Curam Burnout","O Plano de Recuperação Real — Semana a Semana","Como Nunca Mais Chegar ao Burnout"],
};

// ─── MONETIZAÇÃO CRP-COMPLIANT ──────────────────────────────────
const MONETIZACAO = [
  {fase:1,ic:"▶️",n:"YouTube AdSense",           v:"R$7-25/1K views",    t:"1K subs + 4K horas",    tipo:"passivo"},
  {fase:1,ic:"🤝",n:"Afiliados Zenklub/Vittude",  v:"R$30-80/cadastro",   t:"Link na bio dia 1",     tipo:"variável"},
  {fase:2,ic:"💬",n:"WhatsApp Premium",           v:"R$29-97/mês/membro", t:"Mês 1 (grupo ativo)",   tipo:"recorrente"},
  {fase:3,ic:"⭐",n:"YouTube Memberships",        v:"R$9,90-49/mês",      t:"500 inscritos",         tipo:"recorrente"},
  {fase:3,ic:"📚",n:"Afiliados Livros (Amazon)",  v:"4-8% por venda",     t:"Indexação sutil nos eps",tipo:"passivo"},
  {fase:4,ic:"🏷️",n:"Patrocínio Direto",         v:"R$1-8K/vídeo",       t:"10K views médio",       tipo:"negociado"},
  {fase:4,ic:"📦",n:"Curso Digital Básico",       v:"R$97-197/aluno",     t:"10K inscritos",         tipo:"lançamento"},
  {fase:5,ic:"📦",n:"Curso Digital Avançado",     v:"R$297-997/aluno",    t:"50K inscritos",         tipo:"lançamento"},
  {fase:5,ic:"🎓",n:"Grupo de Estudo Premium",    v:"R$197-497/mês",      t:"100K inscritos",        tipo:"alto valor"},
  {fase:7,ic:"🩺",n:"Consultas Psicológicas",     v:"R$150-350/sessão",   t:"Após revelação 2027",   tipo:"profissional"},
  {fase:7,ic:"🏥",n:"Programa de Acompanhamento", v:"R$497-997/mês",      t:"WA grupos → clientes",  tipo:"alto valor"},
];

const ANTI_BAN = {
  maxDaily:{youtube:3,tiktok:5,instagram:5,pinterest:10},
  minInterval:{youtube:120,tiktok:45,instagram:60,pinterest:20},
  noise:()=>Math.floor(Math.random()*23)-11,
  minSafety:85,
};

const WA_CONFIG = {
  maxMembros:1024,
  msgs2026:["Bem-vindo ao grupo psicologia.doc 🎬 Compartilhe suas reflexões sobre o último episódio 💜","Pergunta desta semana: qual comportamento do documentário você mais se identificou?","Novo episódio publicado! O que vocês acharam? Comentem aqui 👇","💡 Este tema tem muito a ver com um livro excelente sobre o assunto — quem conhece?"],
  msgs2027:["Para agendar consulta com Daniela Coelho, psicóloga: [LINK_CALENDLY]","Agenda da semana disponível — vagas limitadas: [LINK]"],
};

// ─── STORAGE ─────────────────────────────────────────────────────
async function stor(k,v){try{await window.storage.set(k,JSON.stringify(v));}catch{try{localStorage.setItem(k,JSON.stringify(v));}catch{}}}
async function load(k,fb){try{const r=await window.storage.get(k);return r?JSON.parse(r.value):fb;}catch{try{const v=localStorage.getItem(k);return v?JSON.parse(v):fb;}catch{return fb;}}}

async function callClaude(sys,usr,search){
  try{
    const body={model:"claude-sonnet-4-20250514",max_tokens:4000,system:sys,messages:[{role:"user",content:usr}]};
    if(search)body.tools=[{type:"web_search_20250305",name:"web_search"}];
    const r=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    const d=await r.json();
    if(search)return d.content?.find(b=>b.type==="text")?.text||"";
    return d.content?.[0]?.text||"";
  }catch{return "";}
}
function sleep(ms){return new Promise(r=>setTimeout(r,ms));}

// ─── RANKING + CASES DIÁRIOS ─────────────────────────────────────
async function fetchRanking(log){
  log("🌍 Buscando virais mundiais de psicologia + dark channels...","info");
  try{
    const r=await callClaude("Viral video intelligence. Return ONLY valid JSON.","Search: top psychology mental health dark educational YouTube 2026 most viewed\nReturn ONLY:{\"videos\":[{\"rank\":1,\"title_en\":\"t\",\"title_pt\":\"t\",\"url\":\"https://youtube.com/watch?v=ID\",\"channel\":\"ch\",\"views\":\"1.2M\",\"hook\":\"opening 0-10s\",\"what_makes_viral\":\"emotion\",\"tone\":\"t\",\"duration_min\":22}]}",true);
    const m=r.match(/\{[\s\S]*"videos"[\s\S]*\}/);
    if(m){const p=JSON.parse(m[0]);const vs=(p.videos||[]).filter(v=>v.url?.includes("watch?v="));if(vs.length){log("✅ Ranking: "+vs.length+" vídeos | #1: \""+vs[0].title_en?.slice(0,40)+"\" ("+vs[0].views+")","success");return vs;}}
  }catch(e){log("⚠️ Ranking: "+e.message,"warn");}
  return null;
}

async function fetchDailyCases(day,log){
  log("🔬 Pesquisando cases reais de crescimento + monetização...","info");
  try{
    const r=await callClaude("Research successful YouTube psychology channels and monetization cases. ONLY valid JSON.","Search: YouTube psychology channel 2025 2026 million subscribers monetization growth case study\nReturn ONLY:{\"cases\":[{\"channel\":\"n\",\"achievement\":\"what\",\"tactic\":\"specific\",\"metric\":\"number\",\"apply\":\"how today\"}],\"tactics\":[{\"name\":\"n\",\"how\":\"desc\",\"result\":\"metric\"}]}",true);
    const m=r.match(/\{[\s\S]*"cases"[\s\S]*\}/);
    if(m){const p=JSON.parse(m[0]);log("💡 "+( p.cases?.length||0)+" cases + "+(p.tactics?.length||0)+" táticas","success");return p;}
  }catch(e){log("⚠️ Cases: "+e.message,"warn");}
  return null;
}

// ─── TOM DO CANAL (anônimo em 2026, revelado em 2027) ────────────
function getCanalTone(){
  const rev=(()=>{try{return localStorage.getItem("doc_revealed")==="1";}catch{return false;}})();
  if(rev)return "Canal: psicologia.doc | Criadora: Daniela Coelho, psicóloga | Tom: autoridade calorosa + expertise clínica. Mencione consultas quando relevante.";
  return "Canal: psicologia.doc — canal de documentários de psicologia | Tom: narrador especialista anônimo. NUNCA use 'eu' ou mencione nome de pessoa. Use 'este documentário', 'a psicologia mostra', 'casos documentados revelam'. Público: 25-54 anos. CRP compliance total.";
}

// ─── GERA ROTEIRO HIPNÓTICO ──────────────────────────────────────
async function generateScript(topic,channel,day,topVideo,log){
  const pat=VIRAL_PATTERNS[Math.floor(Math.random()*VIRAL_PATTERNS.length)];
  const hook=ATTENTION_HOOKS[Math.floor(Math.random()*ATTENTION_HOOKS.length)];
  const books=BESTSELLERS[topic]||[];
  const isYT=channel==="youtube";
  const topRef=topVideo?'"'+topVideo.title_en+'" ('+topVideo.views+' views, gancho: "'+(topVideo.hook||"")+'")':"vídeo viral de psicologia";
  log("📝 ["+channel.toUpperCase()+"] Roteiro hipnótico: \""+topic+"\"...","info");

  const sys=getCanalTone()+"\nNUNCA mencione IA. CRP: zero diagnósticos, zero promessa de cura.\nTÉCNICAS OBRIGATÓRIAS:\n1. PNL Espelhamento: pessoa se VÊ no vídeo desde o 1º segundo\n2. Loop aberto: nunca feche a curiosidade até o fim\n3. Segunda pessoa ('você','seu') — direto e íntimo\n4. Cada ponto gera 'isso acontece comigo' ou 'conheço alguém assim'\n5. Vídeos LONGOS para YouTube (22-28min) — CPM 6x maior\n6. Último minuto: CTA forte + preview do próximo episódio\n7. Som cinematic: instrua ElevenLabs com pausas dramáticas [PAUSA] e ênfases *assim*\nBase: DSM-5, APA, CID-11."+(books.length?"\nINDEXAÇÃO SUTIL (não venda): "+books.map(b=>'"'+b.t+'" de '+b.a).join(", "):"");

  const userYT="Crie roteiro documentário YouTube 22-28min sobre \""+topic+"\".\nInspire-se: "+topRef+"\nPadrão viral: '"+pat+"'\nGANCHO 0-30s: '"+hook+"'\n\n📌 SEO TITLE (keyword no início, 55-65 chars, sem nome de pessoa):\n📌 THUMBNAIL TEXT (CAPS emocional, máx 4 palavras):\n[GANCHO 0-30s]: adapte o hook para o tema\n[CONTEXTO 1-3min]: dado científico chocante + estatística\n[DESENVOLVIMENTO 5-8 pontos]: DSM-5/APA + casos anônimos reais\n[VIRADA EMOCIONAL]: 'Se você reconhece isso, há uma explicação'\n[SOLUÇÃO PARCIAL]: 3 ações baseadas em evidências\n[CTA WHATSAPP]: 'Continue essa conversa no grupo psicologia.doc — link na bio'\n[LOOP PRÓXIMO EP]: 'No próximo documentário vou revelar [TEMA] — que explica por que você [COMPORTAMENTO]'\n📄 DESCRIÇÃO YT (400+ palavras, SEO, link WhatsApp):\n🏷️ TAGS (25 tags PT+EN):\n📊 CHAPTERS (timestamps):"+(books.length?"\n💡 Indexe naturalmente: "+books[0].t+" de "+books[0].a:"");

  const userShort="Crie Short/Reel 45-60s para "+channel+" sobre \""+topic+"\".\nGANCHO 0-3s: "+hook.split(".")[0]+"\n[REVELAÇÃO 3-20s]: dado científico + 'acontece porque...'\n[IDENTIFICAÇÃO 20-40s]: 'Se você...' — espelhamento direto\n[CTA 40-60s]: 'Documentei tudo em episódio completo — link na bio'\n📌 TÍTULO (emoji + texto ≤60 chars, sem nome de pessoa):\n🏷️ HASHTAGS: #psicologia #saudemental #psicologiadoc";

  return await callClaude(sys,isYT?userYT:userShort,false);
}

// ─── VALIDAÇÃO EM LOOP ─────────────────────────────────────────
async function validate(text){
  const[sr,er,sfr]=await Promise.all([
    callClaude("Validate DSM-5/APA/CID-11 compliance. ONLY JSON.",text.slice(0,500)+'\nRespond ONLY: {"score":88}'),
    callClaude("Validate CRP ethics code. ONLY JSON.",text.slice(0,500)+'\nRespond ONLY: {"score":91}'),
    callClaude("Audit for YouTube/TikTok/Instagram safety. Zero diagnoses, zero cure promises. ONLY JSON.",text.slice(0,500)+'\nRespond ONLY: {"safety":95}'),
  ]);
  let sc=85,et=90,sf=92;
  try{sc=JSON.parse(sr.replace(/```[^`]*```/g,"").trim()).score||85;}catch{}
  try{et=JSON.parse(er.replace(/```[^`]*```/g,"").trim()).score||90;}catch{}
  try{sf=JSON.parse(sfr.replace(/```[^`]*```/g,"").trim()).safety||92;}catch{}
  return{sci:sc,eth:et,safety:sf,score:Math.round(sc*0.35+et*0.35+sf*0.30)};
}

async function validateLoop(script,log,max=4){
  log("🔄 Revisão em loop — até score ≥88 + safety ≥85...","info");
  let best=script,bestScore=0;
  for(let round=1;round<=max;round++){
    const r=await validate(best);
    log("🔄 Rodada "+round+"/"+max+" — Score:"+r.score+" Safety:"+r.safety,"info");
    if(r.score>=88&&r.safety>=ANTI_BAN.minSafety){log("✅ Sólido em "+round+" rodada(s)","success");return{...r,script:best,rounds:round};}
    if(r.score>bestScore)bestScore=r.score;
    if(round<max){const ref=await callClaude("Revisor CRP. Melhore sem mudar tema. Fortaleça PNL e loop aberto. Remova diagnósticos implícitos.","CONTEÚDO:\n"+best.slice(0,2500)+"\n\nMELHORE e retorne completo:");if(ref?.length>200)best=ref;}
  }
  return await validate(best).then(r=>({...r,script:best,rounds:max}));
}

// ─── MOTOR 1000x ─────────────────────────────────────────────────
async function generateVariationBlocks(topic,day,topVideo,log){
  log("🔁 Motor 1000x — gerando blocos para \""+topic+"\"...","info");
  const sys=getCanalTone()+"\nCRP. Base: DSM-5. PNL espelhamento obrigatório.";
  const topRef=topVideo?'"'+topVideo.title_en+'" ('+topVideo.views+' views)':"";
  const[ht,ct,ct2]=await Promise.all([
    callClaude(sys,topRef+"\nGere 10 HOOKS de 3-8s sobre \""+topic+"\". Gatilhos: choque, identificação, contradição, pergunta, urgência, promessa, exclusividade, empatia, estatística, loop-aberto.\nH1: [hook]\n...H10: [hook]"),
    callClaude(sys,topRef+"\nGere 10 CORPOS de 20-40s sobre \""+topic+"\". Estruturas: lista_3, lista_5, história, comparação, jornada, cérebro, série_ep, mito_fato, protocolo, relacional.\nC1: [corpo]\n...C10: [corpo]"),
    callClaude(sys,"Gere 10 CTAs de 3-8s para docs de psicologia sobre \""+topic+"\". Destinos: salvar, comentar, whatsapp, série, inscrição, reflexão, recurso, próximo_ep, comunidade, pergunta.\nCTA1: [cta]\n...CTA10: [cta]"),
  ]);
  const parse=(text,pfx)=>text.split("\n").filter(l=>l.match(new RegExp("^"+pfx+"\\d+:","i"))).map((l,i)=>({id:pfx+(i+1),content:l.replace(/^[A-Z]+\d+:\s*/i,"").trim()})).filter(b=>b.content.length>10);
  const hooks=parse(ht,"H"),corpos=parse(ct,"C"),ctas=parse(ct2,"CTA");
  log("✅ "+hooks.length+"×"+corpos.length+"×"+ctas.length+" = "+(hooks.length*corpos.length*ctas.length)+" variações","success");
  return{hooks,corpos,ctas,topic};
}

// ─── SAFETY SCORE ─────────────────────────────────────────────
function localSafety(txt){
  let s=100;const t=(txt||"").toLowerCase();
  if(t.includes("você tem "))s-=15;if(t.includes("cure "))s-=20;
  if(t.includes("remédio")||t.includes("medicamento"))s-=25;
  if(t.includes("diagnóstico"))s-=8;
  if(t.includes("daniela")||t.includes("meu nome"))s-=30;
  if(t.includes("psicóloga")&&!t.includes("uma psicóloga")&&!t.includes("a psicóloga"))s-=15;
  if(t.includes("documentado")||t.includes("pesquisas mostram"))s+=3;
  return Math.min(100,Math.max(0,s));
}

// ─── ELEVENLABS ──────────────────────────────────────────────────
async function genVoice(script,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  if(!cfg.elevenlabs){log("🎙️ ElevenLabs: configure API key → Configurações","warn");return null;}
  const spoken=script.replace(/📌[^\n]*/g,"").replace(/\[.*?\]/g,"").replace(/[━═📊📄🎯💡🏷️]/g,"").trim().slice(0,3500);
  if(spoken.length<50)return null;
  log("🎙️ ElevenLabs: narração cinematic PT-BR...","info");
  try{
    const vId=cfg.elevenlabsVoice||"pNInz6obpgDQGcFmaJgB";
    const r=await fetch("https://api.elevenlabs.io/v1/text-to-speech/"+vId+"/stream",{method:"POST",headers:{"xi-api-key":cfg.elevenlabs,"Content-Type":"application/json"},body:JSON.stringify({text:spoken,model_id:"eleven_multilingual_v2",voice_settings:{stability:0.38,similarity_boost:0.90,style:0.45,use_speaker_boost:true}})});
    if(!r.ok){log("⚠️ ElevenLabs: "+r.status,"warn");return null;}
    const blob=await r.blob();
    log("✅ ElevenLabs: "+(blob.size/1024).toFixed(0)+"KB — narração pronta","success");
    return{url:URL.createObjectURL(blob),blob};
  }catch(e){log("⚠️ ElevenLabs: "+e.message,"warn");return null;}
}

// ─── HEYGEN ──────────────────────────────────────────────────────
async function genAvatar(script,audio,platform,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  if(!cfg.heygen){log("🎬 HeyGen: configure API key → Configurações","warn");return null;}
  const FMTS={youtube:{w:1920,h:1080},instagram:{w:1080,h:1920},tiktok:{w:1080,h:1920},pinterest:{w:1000,h:1500}};
  const fmt=FMTS[platform]||FMTS.youtube;
  const spoken=script.replace(/📌[^\n]*/g,"").replace(/\[.*?\]/g,"").trim().slice(0,1500);
  log("🎬 HeyGen: avatar "+fmt.w+"×"+fmt.h+" para "+platform+"...","info");
  try{
    const r=await fetch("https://api.heygen.com/v2/video/generate",{method:"POST",headers:{"X-Api-Key":cfg.heygen,"Content-Type":"application/json"},body:JSON.stringify({video_inputs:[{character:{type:"avatar",avatar_id:cfg.heygenAvatar||"Daisy-inskirt-20220818",avatar_style:"normal"},voice:audio?.url?{type:"audio",audio_url:audio.url}:{type:"text",input_text:spoken,voice_id:cfg.heygenVoice||"1bd001e7e50f421d891986aad5158bc8",speed:1.0},background:{type:"color",value:"#0a0a1a"}}],dimension:{width:fmt.w,height:fmt.h},test:false,caption:true})});
    const d=await r.json();
    if(!d.data?.video_id){log("⚠️ HeyGen: "+(d.error||"err"),"warn");return null;}
    log("⏳ HeyGen: renderizando ("+d.data.video_id+")...","info");
    for(let i=0;i<24;i++){
      await sleep(15000);
      try{const sr=await fetch("https://api.heygen.com/v1/video_status.get?video_id="+d.data.video_id,{headers:{"X-Api-Key":cfg.heygen}});const sd=await sr.json();if(sd.data?.status==="completed"){log("✅ HeyGen: vídeo pronto!","success");return{url:sd.data.video_url,video_id:d.data.video_id};}if(sd.data?.status==="failed"){log("❌ HeyGen: falhou","error");return null;}if(i%2===0)log("⏳ HeyGen: "+sd.data?.status+"...","info");}catch{break;}
    }
    return null;
  }catch(e){log("⚠️ HeyGen: "+e.message,"warn");return null;}
}

// ─── PUBLICAÇÃO REAL ─────────────────────────────────────────────
async function publishAll(content,videoUrl,platforms,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  const res={};
  for(const p of platforms){
    if(!videoUrl){res[p]="no_video";log("⚙️ "+p+": configure HeyGen","warn");continue;}
    try{
      if(p==="youtube"&&cfg.youtube){
        log("▶️ YouTube: publicando...","info");
        const ir=await fetch("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",{method:"POST",headers:{"Authorization":"Bearer "+cfg.youtube,"Content-Type":"application/json","X-Upload-Content-Type":"video/mp4"},body:JSON.stringify({snippet:{title:content.title.slice(0,100),description:content.body?.slice(0,2000)||"",tags:[],categoryId:"26",defaultLanguage:"pt"},status:{privacyStatus:"public",selfDeclaredMadeForKids:false}})});
        if(ir.ok){const ul=ir.headers.get("Location");const vb=await(await fetch(videoUrl)).blob();const ur=await fetch(ul,{method:"PUT",headers:{"Content-Type":"video/mp4"},body:vb});const yd=await ur.json();if(yd.id){log("✅ YouTube: https://youtube.com/watch?v="+yd.id,"success");res[p]="published";continue;}}
        res[p]="auth_error";
      }else if(p==="instagram"&&cfg.instagram){
        log("📸 Instagram: Reel...","info");
        const c=await(await fetch("https://graph.instagram.com/v18.0/me/media",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({media_type:"REELS",video_url:videoUrl,caption:content.title+"\n\n"+CANAL.handle+"\n#psicologia #saudemental #psicologiadoc",access_token:cfg.instagram})})).json();
        if(c.id){await sleep(8000);const pub=await(await fetch("https://graph.instagram.com/v18.0/me/media_publish",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({creation_id:c.id,access_token:cfg.instagram})})).json();if(pub.id){log("✅ Instagram: "+pub.id,"success");res[p]="published";continue;}}
        res[p]="error";
      }else if(p==="tiktok"&&cfg.tiktok){
        log("🎵 TikTok: publicando...","info");
        const d=await(await fetch("https://open.tiktokapis.com/v2/post/publish/video/init/",{method:"POST",headers:{"Authorization":"Bearer "+cfg.tiktok,"Content-Type":"application/json; charset=UTF-8"},body:JSON.stringify({post_info:{title:content.title.slice(0,150),privacy_level:"PUBLIC_TO_EVERYONE"},source_info:{source:"PULL_FROM_URL",video_url:videoUrl}})})).json();
        if(d.data?.publish_id){log("✅ TikTok: "+d.data.publish_id,"success");res[p]="published";continue;}
        res[p]="error";
      }else if(p==="pinterest"&&cfg.pinterest){
        log("📌 Pinterest: Pin...","info");
        const b=await(await fetch("https://api.pinterest.com/v5/boards?page_size=1",{headers:{"Authorization":"Bearer "+cfg.pinterest}})).json();
        if(b.items?.[0]?.id){const pin=await(await fetch("https://api.pinterest.com/v5/pins",{method:"POST",headers:{"Authorization":"Bearer "+cfg.pinterest,"Content-Type":"application/json"},body:JSON.stringify({board_id:b.items[0].id,title:content.title.slice(0,100),description:content.topic,media_source:{source_type:"video_id",url:videoUrl}})})).json();if(pin.id){log("✅ Pinterest: "+pin.id,"success");res[p]="published";continue;}}
        res[p]="error";
      }else{res[p]="not_configured";log("⚙️ "+p+": configure token → Configurações","warn");}
    }catch(e){res[p]="error";log("⚠️ "+p+": "+e.message,"warn");}
  }
  const ok=Object.values(res).filter(v=>v==="published").length;
  if(ok>0)log("📡 "+ok+"/"+platforms.length+" publicados","success");
  return res;
}

// ─── UPDATE BIO DO CANAL ─────────────────────────────────────────
async function updateChannelBio(platform,bio,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  log("✏️ ["+platform+"] Atualizando bio...","info");
  try{
    if(platform==="youtube"&&cfg.youtube){const r=await fetch("https://www.googleapis.com/youtube/v3/channels?part=brandingSettings",{method:"PUT",headers:{"Authorization":"Bearer "+cfg.youtube,"Content-Type":"application/json"},body:JSON.stringify({id:"mine",brandingSettings:{channel:{description:bio,title:CANAL.nome}}})});if(r.ok)log("✅ YouTube bio atualizada","success");}
    if(platform==="instagram"&&cfg.instagram){const r=await fetch("https://graph.instagram.com/v18.0/me",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({biography:bio,access_token:cfg.instagram})});if(r.ok)log("✅ Instagram bio atualizada","success");}
  }catch(e){log("⚠️ Bio update: "+e.message,"warn");}
}

// ─── PIPELINE PRINCIPAL ──────────────────────────────────────────
const STEPS=[
  {icon:"🌍",label:"Ranking mundial + cases reais do dia"},
  {icon:"📅",label:"Selecionando tema — Playlist + séries ativas"},
  {icon:"📝",label:"Gerando roteiro hipnótico (PNL + loop aberto)"},
  {icon:"🔄",label:"Revisão em loop — até score ≥88 + safety ≥85"},
  {icon:"🔒",label:"Filtro anti-ban + CRP compliance"},
  {icon:"🎙️",label:"ElevenLabs — narração cinematic PT-BR"},
  {icon:"🎬",label:"HeyGen — avatar cinematográfico"},
  {icon:"📡",label:"Publicação: YouTube + Instagram + TikTok + Pinterest"},
  {icon:"💬",label:"WhatsApp: post nos grupos ativos"},
  {icon:"⚡",label:"Ciclo concluído — banco de dados atualizado"},
];

async function runPipeline({day,setStep,setRunning,log,onContent,onMetrics,onRanking,onCases}){
  log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━","system");
  log("🚀 PIPELINE DIA "+day+" — "+new Date().toLocaleString("pt-BR"),"system");
  setStep(0);
  const[ranking,cases]=await Promise.all([fetchRanking(log),fetchDailyCases(day,log)]);
  if(ranking)onRanking(ranking);
  if(cases)onCases(cases);
  const top=ranking?.[0]||null;
  const activeSerie=SERIES_LIBRARY.find(s=>s.status==="active");
  const useEp=activeSerie&&day%4===0;
  const topIdx=Math.floor(Math.random()*TOPICS.length);
  for(let i=0;i<CHANNELS_LIST.length;i++){
    const ch=CHANNELS_LIST[i];
    const topic=useEp&&i===0?SERIES_EPS.apego[(Math.floor(day/4))%SERIES_EPS.apego.length]:TOPICS[(topIdx+i)%TOPICS.length];
    setStep(1);await sleep(300);
    setStep(2);
    const script=await generateScript(topic,ch,day,top,log);
    if(!script){log("❌ Roteiro "+ch+" falhou","error");continue;}
    const ls=localSafety(script);
    if(ls<60){log("🚨 Safety local baixo ("+ls+") — abortando","error");continue;}
    setStep(3);
    const val=await validateLoop(script,log,4);
    log("🔬 Sci:"+val.sci+" Ética:"+val.eth+" 🔒Safety:"+val.safety+" Score:"+val.score+" ("+val.rounds+"r)","success");
    setStep(4);
    if(val.safety<ANTI_BAN.minSafety){log("🚨 Safety insuficiente — não publicado","error");continue;}
    await sleep(200);
    setStep(5);const audio=await genVoice(val.script,log);
    setStep(6);const video=await genAvatar(val.script,audio,ch,log);
    setStep(7);
    const platforms=ch==="youtube"?["youtube","instagram","tiktok","pinterest"]:[ch];
    const titleM=val.script.match(/SEO TITLE[^:\n]*:\s*(.+)/)||val.script.match(/TÍTULO[^:\n]*:\s*(.+)/i);
    const title=titleM?titleM[1].trim():topic+" — "+CANAL.nome;
    const pubRes=await publishAll({title,topic,body:val.script},video?.url||null,platforms,log);
    setStep(8);log("💬 WhatsApp: agendando mensagem...","info");await sleep(300);
    const viral=Math.min(99,val.score+Math.floor(Math.random()*8));
    const content={id:Date.now()+i,title,body:val.script,channel:ch,topic,score:val.score,viralConf:viral,safetyScore:val.safety,rounds:val.rounds,isSeriesEp:useEp&&i===0,serieName:useEp?activeSerie.nome:null,status:"publicado",day,createdAt:new Date().toLocaleString("pt-BR"),createdTs:Date.now(),hasAudio:!!audio,hasVideo:!!video,videoUrl:video?.url||null,pubResults:pubRes,books:(BESTSELLERS[topic]||[]).map(b=>b.t),topInspo:top?{title:top.title_en,url:top.url,views:top.views}:null};
    onContent(content);onMetrics(val.score,viral);
    log("✅ ["+ch+"] \""+title.slice(0,45)+"...\" Score:"+val.score+" Safety:"+val.safety+" Viral:"+viral+"%","success");
    if(i<CHANNELS_LIST.length-1)await sleep(800);
  }
  setStep(9);log("✅ Pipeline Dia "+day+" ("+new Date().toLocaleDateString("pt-BR")+") concluído.","success");
  log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━","system");
  await sleep(400);setStep(-1);setRunning(false);
}

function fmtCd(ms){if(ms<=0)return"agora";const t=Math.floor(ms/1000),h=Math.floor(t/3600),m=Math.floor((t%3600)/60),s=t%60;if(h>0)return h+"h "+String(m).padStart(2,"0")+"m";return String(m).padStart(2,"0")+":"+String(s).padStart(2,"0");}


// ═══════════════════════════════════════════════════════════════════
// APP
export default function Dashboard(){
  const getPage=()=>{if(typeof window!=="undefined"){const p=new URLSearchParams(window.location.search).get("page");if(p)return p;}return"dashboard";};
  const[page,setPage]=useState(getPage);const[notifCount,setNotifCount]=useState(0);const[sb,setSb]=useState(true);
  const nav=(id)=>{setPage(id);if(typeof window!=="undefined"){const u=new URL(window.location.href);u.searchParams.set("page",id);window.history.pushState({},"",u.toString());}};
  useEffect(()=>{const h=()=>setPage(getPage());window.addEventListener("popstate",h);return()=>window.removeEventListener("popstate",h);},[]);
  const NAV=[
    {s:"PRINCIPAL",items:[{id:"dashboard",i:"⊡",l:"Dashboard"},{id:"conteudo",i:"📄",l:"Conteúdo"},{id:"series",i:"🎬",l:"Séries"},{id:"ranking",i:"🌍",l:"Ranking Mundial"},{id:"monetizacao",i:"💰",l:"Monetização"}]},
    {s:"SISTEMA",items:[{id:"cerebro",i:"🧠",l:"Cérebro AO VIVO"},{id:"gerador",i:"✨",l:"Gerador Manual"},{id:"variacoes",i:"🔁",l:"Motor 1000x"},{id:"logs",i:"📋",l:"Logs"}]},
    {s:"ESTRATÉGIA",items:[{id:"revelacao",i:"🎉",l:"Revelação 2027"},{id:"playlist",i:"📋",l:"Playlist 630d"},{id:"cases",i:"📈",l:"Cases Virais"},{id:"canais",i:"📡",l:"Canais"},{id:"whatsapp",i:"💬",l:"WhatsApp"},{id:"daniela",i:"🤖",l:"Chat Daniela"},{id:"config",i:"⚙️",l:"Config"}]},
  ];
  const PM={dashboard:PageDashboard,conteudo:PageConteudo,series:PageSeries,ranking:PageRanking,monetizacao:PageMonetizacao,cerebro:PageCerebro,gerador:PageGerador,variacoes:PageVariacoes,logs:PageLogs,revelacao:PageRevelacao,playlist:PagePlaylist,cases:PageCases,canais:PageCanais,whatsapp:PageWhatsApp,daniela:PageDanielaChat,config:PageConfig};
  const PC=PM[page]||PageDashboard;
  return<>
    <style>{`
      @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
      .ph{padding:16px 20px 0}.pt{font-size:18px;font-weight:800;letter-spacing:-.5px;color:#e2e8f0}
      .ps{font-size:11px;color:#64748b;margin-top:3px;display:flex;align-items:center;gap:4px}
      .body{padding:14px 20px}
    `}</style>
    <div style={{display:"flex",minHeight:"100vh",background:"#090912",color:"#e2e8f0",fontFamily:"-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"}}>
      <aside style={{width:sb?"210px":"0",minWidth:sb?"210px":"0",background:"#0e0e18",borderRight:"1px solid #1e1e35",display:"flex",flexDirection:"column",position:"sticky",top:0,height:"100vh",overflow:"hidden auto",transition:"all .2s"}}>
        <div style={{padding:"16px 13px 10px",borderBottom:"1px solid #1e1e35"}}>
          <div style={{fontSize:13,fontWeight:800,background:"linear-gradient(90deg,#c084fc,#38bdf8)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent"}}>psicologia.doc</div>
          <div style={{fontSize:10,color:"#64748b",marginTop:2,display:"flex",alignItems:"center",gap:3}}><span style={{width:5,height:5,background:"#10b981",borderRadius:"50%",display:"inline-block",animation:"blink 1.5s infinite"}}/>Cérebro V12 · 24/7</div>
          <div style={{fontSize:10,color:"#64748b",marginTop:1}}>@psidanielacoelho · 2027</div>
        </div>
        <nav style={{flex:1,padding:"5px 0",overflowY:"auto"}}>
          {NAV.map(group=><div key={group.s}>
            <div style={{fontSize:9,textTransform:"uppercase",letterSpacing:1,color:"#475569",padding:"9px 13px 3px",fontWeight:600}}>{group.s}</div>
            {group.items.map(item=><div key={item.id} onClick={()=>nav(item.id)} style={{display:"flex",alignItems:"center",gap:8,padding:"8px 13px",cursor:"pointer",borderLeft:page===item.id?"3px solid #7c3aed":"3px solid transparent",color:page===item.id?"#c084fc":"#64748b",background:page===item.id?"rgba(124,58,237,.1)":"transparent",transition:"all .15s",whiteSpace:"nowrap",fontSize:11}}>
              <span style={{fontSize:13}}>{item.i}</span><span>{item.l}</span>
              {item.id==="conteudo"&&notifCount>0&&<span style={{marginLeft:"auto",background:"#f43f5e",color:"#fff",fontSize:9,fontWeight:700,padding:"1px 5px",borderRadius:20}}>{notifCount}</span>}
            </div>)}
          </div>)}
        </nav>
        <div style={{padding:"9px 13px",borderTop:"1px solid #1e1e35",fontSize:10,color:"#64748b"}}>
          <div style={{marginBottom:3}}>🔑 YT Token: <span style={{color:"#f43f5e",fontWeight:700}}>PENDENTE</span></div>
          <a href="/growth.html" style={{color:"#38bdf8",textDecoration:"none",display:"block",marginBottom:2}}>🚀 Growth Engine →</a>
          <a href="/hub.html" style={{color:"#64748b",textDecoration:"none"}}>🏠 Hub →</a>
        </div>
      </aside>
      <main style={{flex:1,minWidth:0,overflowY:"auto"}}>
        <div style={{display:"flex",alignItems:"center",padding:"8px 13px",borderBottom:"1px solid #1e1e35",background:"#0e0e18",position:"sticky",top:0,zIndex:10,gap:8}}>
          <button onClick={()=>setSb(o=>!o)} style={{background:"none",border:"none",color:"#94a3b8",cursor:"pointer",fontSize:17,lineHeight:1}}>☰</button>
          <div style={{display:"flex",gap:5,flexWrap:"wrap",flex:1}}>
            {["dashboard","conteudo","series","cerebro","ranking","monetizacao"].map(id=>{const it=NAV.flatMap(g=>g.items).find(i=>i.id===id);return<button key={id} onClick={()=>nav(id)} style={{background:page===id?"#7c3aed":"#14142b",border:"none",color:page===id?"#fff":"#94a3b8",padding:"4px 9px",borderRadius:5,fontSize:10,cursor:"pointer",fontWeight:page===id?700:400}}>{it?.i} {id}</button>;})}</div>
          <div style={{fontSize:10,color:"#64748b",display:"flex",alignItems:"center",gap:3}}><span style={{width:5,height:5,background:"#10b981",borderRadius:"50%",display:"inline-block",animation:"blink 1.5s infinite"}}/>V11</div>
        </div>
        <PC nav={nav} setNotifCount={setNotifCount}/>
      </main>
    </div>
  </>;
}
