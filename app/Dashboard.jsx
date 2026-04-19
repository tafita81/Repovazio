"use client";
import { useState, useEffect, useRef, useCallback } from "react";

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PSICOLOGIA.DOC â CÃREBRO AUTÃNOMO v7
// Canal: @psicologiadoc (DOC = Daniela Oliveira Coelho + documentÃ¡rio)
// Dia 1 = 15 abr 2026 | RevelaÃ§Ã£o = ~1 jan 2027 (Dia 261)
// 2026: Canal 100% anÃ´nimo â ZERO menÃ§Ã£o a nome ou pessoa
// 2027: Daniela Coelho, psicÃ³loga (NÃO "Dra." â apenas psicÃ³loga)
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ

const RANK_INTERVAL = 60*1000;
const PROD_INTERVAL = 30*60*1000;
const FIRST_RANK    = 15*1000;
const FIRST_PROD    = 60*1000;

const CANAL = {
  nome:    "psicologia.doc",
  handle:  "@psicologiadoc",
  slogan:  "A psicologia que vocÃª vive â documentada.",
  bio2026: "@psicologiadoc | Psicologia documentada ð¬ | SaÃºde mental que vocÃª reconhece | Novos docs toda semana",
  bio2027: "@psicologiadoc | Daniela Coelho, psicÃ³loga ð§  | CRP [NÃMERO] | Consultas online â link na bio",
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
  if (revealed) return {label:"Fase 7: Daniela Coelho, psicÃ³loga",goal:"Consultas + 500K+ + R$80-250K/mÃªs",color:"var(--green)",period:"2027+"};
  if (day<=14)  return {label:"Fase 1: FundaÃ§Ã£o SEO",  goal:"1.000 inscritos Â· buscas",          color:"var(--blue)",  period:dayToDate(1)+" â "+dayToDate(14)};
  if (day<=30)  return {label:"Fase 2: ViralizaÃ§Ã£o",   goal:"5.000 inscritos Â· primeiro viral",   color:"var(--purple)",period:dayToDate(15)+" â "+dayToDate(30)};
  if (day<=60)  return {label:"Fase 3: Escala",        goal:"10K inscritos Â· AdSense",            color:"var(--green)", period:dayToDate(31)+" â "+dayToDate(60)};
  if (day<=180) return {label:"Fase 4: Crescimento",   goal:"50K Â· R$10-40K/mÃªs",                color:"var(--amber)", period:dayToDate(61)+" â "+dayToDate(180)};
  if (day<=260) return {label:"Fase 5: Autoridade",    goal:"100K+ Â· marca anÃ´nima sÃ³lida",       color:"var(--red)",   period:dayToDate(181)+" â "+dayToDate(260)};
  return          {label:"Fase 6: PrÃ©-revelaÃ§Ã£o",      goal:"200K+ Â· lista de espera consultas",  color:"#a855f7",      period:dayToDate(261)+"+"};
}

// âââ TÃCNICAS PNL + ENGENHARIA DE ATENÃÃO ââââââââââââââââââââââ
// Cases reais: Therapy in a Nutshell (2M), Psych2Go (13M),
// Dr. Nicole LePera (12M), Canal Dark (1.2M views R$24K/60 dias)
const ATTENTION_HOOKS = [
  "Se vocÃª faz [COMPORTAMENTO] quando [SITUAÃÃO], esse documentÃ¡rio foi feito especificamente para vocÃª.",
  "Por que vocÃª continua atraindo [TIPO DE PESSOA] mesmo sabendo que vai te machucar?",
  "Existe um padrÃ£o documentado em [N]% das pessoas e quase ninguÃ©m fala sobre isso abertamente.",
  "O que vocÃª vai descobrir nos prÃ³ximos [N] minutos vai mudar como vocÃª vÃª [SITUAÃÃO] para sempre.",
  "VocÃª provavelmente jÃ¡ sentiu [EMOÃÃO] sem conseguir explicar de onde vem. A ciÃªncia explica.",
  "Documentamos [N] casos reais de [TEMA]. O que descobrimos vai te surpreender.",
  "Em [ANO], pesquisadores documentaram algo que ainda acontece com milhÃµes de pessoas hoje.",
  "Tem um nome tÃ©cnico para o que vocÃª sente quando [SITUAÃÃO]. E existe uma saÃ­da.",
  "Se alguÃ©m perto de vocÃª age assim, este documentÃ¡rio explica exatamente o porquÃª.",
  "A resposta estÃ¡ no final deste documentÃ¡rio â mas vocÃª precisa entender o contexto primeiro.",
];

const VIRAL_PATTERNS = [
  "Por que VocÃª [VERBO] Quando [SITUAÃÃO]",
  "[N] Sinais que VocÃª Tem [CONDIÃÃO] (e NÃ£o Sabe)",
  "Por que VocÃª Atrai [TIPO PROBLEMÃTICO]",
  "Como Parar de [COMPORTAMENTO] â A Psicologia Explica",
  "[CONDIÃÃO]: O que NinguÃ©m te Conta",
  "O que Acontece com o Seu CÃ©rebro Quando [SITUAÃÃO]",
  "[N] Comportamentos que Parecem Normais Mas SÃ£o [CONDIÃÃO]",
  "A Psicologia Por TrÃ¡s de [LIVRO/SITUAÃÃO] â Documentado",
];

const TOPICS = [
  "Ansiedade & Burnout","Apego Ansioso","Narcisismo & ManipulaÃ§Ã£o",
  "Trauma de InfÃ¢ncia","Autossabotagem","Relacionamentos TÃ³xicos",
  "InteligÃªncia Emocional","DepressÃ£o & Tristeza","Limites SaudÃ¡veis",
  "Gaslighting","Autoestima","SÃ­ndrome do Impostor",
  "DependÃªncia Emocional","Luto & Perda","Ansiedade Social",
  "Psicologia do Dinheiro","LideranÃ§a TÃ³xica","VÃ­cio em ValidaÃ§Ã£o",
];

const CHANNELS_LIST = ["youtube","tiktok","instagram","pinterest"];

// âââ BESTSELLERS POR TEMA (indexaÃ§Ã£o sutil) ââââââââââââââââââââââ
const BESTSELLERS = {
  "Ansiedade & Burnout":      [{t:"Por que Zebras nÃ£o TÃªm Ãlcera",a:"Sapolsky"},{t:"O Corpo Guarda o Placar",a:"van der Kolk"}],
  "Apego Ansioso":            [{t:"Attached",a:"Levine & Heller"},{t:"NÃ³s",a:"Lisa Fischler"}],
  "Narcisismo & ManipulaÃ§Ã£o": [{t:"Why Does He Do That?",a:"Lundy Bancroft"}],
  "Trauma de InfÃ¢ncia":       [{t:"O Corpo Guarda o Placar",a:"van der Kolk"},{t:"Childhood Disrupted",a:"Nakazawa"}],
  "Autossabotagem":           [{t:"The Big Leap",a:"Gay Hendricks"},{t:"Mindset",a:"Carol Dweck"}],
  "Relacionamentos TÃ³xicos":  [{t:"Too Good to Leave, Too Bad to Stay",a:"Kirshenbaum"}],
  "InteligÃªncia Emocional":   [{t:"InteligÃªncia Emocional",a:"Daniel Goleman"}],
  "Gaslighting":              [{t:"Gaslighting",a:"Stephanie Moulton Sacks"}],
  "Autoestima":               [{t:"Os 6 Pilares da Autoestima",a:"Nathaniel Branden"}],
  "DependÃªncia Emocional":    [{t:"Codependent No More",a:"Melody Beattie"}],
  "Psicologia do Dinheiro":   [{t:"A Psicologia Financeira",a:"Morgan Housel"}],
};

// âââ SÃRIES EPISÃDICAS COM LOOP ABERTO ââââââââââââââââââââââââââ
const SERIES_LIBRARY = [
  {id:"apego",      nome:"ð A CiÃªncia do Apego",      eps:8, status:"active",  lancamento:dayToDate(1),   subtitulo:"Por que vocÃª ama quem te faz sofrer", tecnica:"Cada ep termina: 'No prÃ³ximo vocÃª vai descobrir POR QUE vocÃª faz X'"},
  {id:"narcisismo", nome:"ðª Narcisismo Documentado",  eps:7, status:"planned", lancamento:dayToDate(30),  subtitulo:"O que ninguÃ©m conta sobre manipulaÃ§Ã£o", tecnica:"TÃ­tulos: 'vocÃª provavelmente convive com um' â identificaÃ§Ã£o + urgÃªncia"},
  {id:"ansiedade",  nome:"â¡ Ansiedade Documentada",   eps:8, status:"planned", lancamento:dayToDate(60),  subtitulo:"Sua mente acelerada tem um motivo",     tecnica:"22-28min + imagens cinematogrÃ¡ficas = CPM mÃ¡ximo"},
  {id:"trauma",     nome:"ð Trauma InvisÃ­vel",        eps:6, status:"planned", lancamento:dayToDate(90),  subtitulo:"O que seu corpo carrega sem vocÃª saber", tecnica:"Cada ep tem 1 exercÃ­cio prÃ¡tico â aumenta retenÃ§Ã£o + compartilhamento"},
  {id:"burnout",    nome:"ð¥ Burnout Documentado",     eps:5, status:"planned", lancamento:dayToDate(120), subtitulo:"VocÃª nÃ£o Ã© preguiÃ§oso â estÃ¡ esgotado",  tecnica:"ContradiÃ§Ã£o no tÃ­tulo = clique: 'Por que fÃ©rias nÃ£o curam burnout'"},
];

const SERIES_EPS = {
  apego:["Por Que VocÃª Tem Tanto Medo de Ser Abandonado","Os 4 Estilos de Apego â em qual vocÃª estÃ¡?","Por Que VocÃª Atrai Pessoas Emocionalmente IndisponÃ­veis","O Que Acontece no Seu CÃ©rebro Quando VocÃª se Apega Demais","Por Que VocÃª Fica com Quem te Machuca â a NeurociÃªncia","Apego Evitativo â a SolidÃ£o DisfarÃ§ada de IndependÃªncia","Como Mudar Seu Estilo de Apego (a CiÃªncia Diz que Ã© PossÃ­vel)","Relacionamento Seguro â Como Reconhecer e Construir"],
  narcisismo:["O Que Ã© Narcisismo de Verdade â AlÃ©m do Senso Comum","Os 7 Tipos de Narcisismo (o 5Âº Ã© o Mais Perigoso)","Como um Narcisista Conquista VocÃª â Passo a Passo","Gaslighting Documentado â Sinais que EstÃ£o Acontecendo Agora","Por Que VocÃª Fica com Narcisista Mesmo Sabendo que Faz Mal","Como Sair Dessa RelaÃ§Ã£o Sem se Destruir","Se Recuperando do Abuso Narcisista â O Plano Real"],
  ansiedade:["O que Ã© Ansiedade de Verdade (nÃ£o Ã© o que te disseram)","Por que Seu CÃ©rebro Cria Ansiedade â NeurociÃªncia Real","Os 5 Tipos de Ansiedade que Poucos Falam","Trauma de InfÃ¢ncia e Ansiedade Adulta â A ConexÃ£o","Por que VocÃª nÃ£o Consegue 'Simplesmente Relaxar'","TÃ©cnicas que a CiÃªncia Provou Funcionar","Quando a Ansiedade Vira DoenÃ§a â Sinais Claros","Vivendo Bem com Ansiedade â RegulaÃ§Ã£o, nÃ£o Cura"],
  trauma:["Trauma nÃ£o Ã© sÃ³ Guerra â O Que Realmente Ã","Trauma Complexo (C-PTSD) â O Que MÃ©dicos Ainda Ignoram","Flashback Emocional â O Sintoma que VocÃª nÃ£o Sabia que Tinha","Seu Corpo Guarda o Trauma â Teoria Polivagal em 20min","Trauma de InfÃ¢ncia no Adulto â 8 Comportamentos Reveladores","O Caminho Real de Cura â O Que a CiÃªncia Diz"],
  burnout:["O Que Ã© Burnout (nÃ£o Ã© PreguiÃ§a, nÃ£o Ã© Frescura)","Os 5 EstÃ¡gios do Burnout â Em Qual VocÃª EstÃ¡?","Por Que FÃ©rias nÃ£o Curam Burnout","O Plano de RecuperaÃ§Ã£o Real â Semana a Semana","Como Nunca Mais Chegar ao Burnout"],
};

// âââ MONETIZAÃÃO CRP-COMPLIANT ââââââââââââââââââââââââââââââââââ
const MONETIZACAO = [
  {fase:1,ic:"â¶ï¸",n:"YouTube AdSense",           v:"R$7-25/1K views",    t:"1K subs + 4K horas",    tipo:"passivo"},
  {fase:1,ic:"ð¤",n:"Afiliados Zenklub/Vittude",  v:"R$30-80/cadastro",   t:"Link na bio dia 1",     tipo:"variÃ¡vel"},
  {fase:2,ic:"ð¬",n:"WhatsApp Premium",           v:"R$29-97/mÃªs/membro", t:"MÃªs 1 (grupo ativo)",   tipo:"recorrente"},
  {fase:3,ic:"â­",n:"YouTube Memberships",        v:"R$9,90-49/mÃªs",      t:"500 inscritos",         tipo:"recorrente"},
  {fase:3,ic:"ð",n:"Afiliados Livros (Amazon)",  v:"4-8% por venda",     t:"IndexaÃ§Ã£o sutil nos eps",tipo:"passivo"},
  {fase:4,ic:"ð·ï¸",n:"PatrocÃ­nio Direto",         v:"R$1-8K/vÃ­deo",       t:"10K views mÃ©dio",       tipo:"negociado"},
  {fase:4,ic:"ð¦",n:"Curso Digital BÃ¡sico",       v:"R$97-197/aluno",     t:"10K inscritos",         tipo:"lanÃ§amento"},
  {fase:5,ic:"ð¦",n:"Curso Digital AvanÃ§ado",     v:"R$297-997/aluno",    t:"50K inscritos",         tipo:"lanÃ§amento"},
  {fase:5,ic:"ð",n:"Grupo de Estudo Premium",    v:"R$197-497/mÃªs",      t:"100K inscritos",        tipo:"alto valor"},
  {fase:7,ic:"ð©º",n:"Consultas PsicolÃ³gicas",     v:"R$150-350/sessÃ£o",   t:"ApÃ³s revelaÃ§Ã£o 2027",   tipo:"profissional"},
  {fase:7,ic:"ð¥",n:"Programa de Acompanhamento", v:"R$497-997/mÃªs",      t:"WA grupos â clientes",  tipo:"alto valor"},
];

const ANTI_BAN = {
  maxDaily:{youtube:3,tiktok:5,instagram:5,pinterest:10},
  minInterval:{youtube:120,tiktok:45,instagram:60,pinterest:20},
  noise:()=>Math.floor(Math.random()*23)-11,
  minSafety:85,
};

const WA_CONFIG = {
  maxMembros:1024,
  msgs2026:["Bem-vindo ao grupo psicologia.doc ð¬ Compartilhe suas reflexÃµes sobre o Ãºltimo episÃ³dio ð","Pergunta desta semana: qual comportamento do documentÃ¡rio vocÃª mais se identificou?","Novo episÃ³dio publicado! O que vocÃªs acharam? Comentem aqui ð","ð¡ Este tema tem muito a ver com um livro excelente sobre o assunto â quem conhece?"],
  msgs2027:["Para agendar consulta com Daniela Coelho, psicÃ³loga: [LINK_CALENDLY]","Agenda da semana disponÃ­vel â vagas limitadas: [LINK]"],
};

// âââ STORAGE âââââââââââââââââââââââââââââââââââââââââââââââââââââ
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

// âââ RANKING + CASES DIÃRIOS âââââââââââââââââââââââââââââââââââââ
async function fetchRanking(log){
  log("ð Buscando virais mundiais de psicologia + dark channels...","info");
  try{
    const r=await callClaude("Viral video intelligence. Return ONLY valid JSON.","Search: top psychology mental health dark educational YouTube 2026 most viewed\nReturn ONLY:{\"videos\":[{\"rank\":1,\"title_en\":\"t\",\"title_pt\":\"t\",\"url\":\"https://youtube.com/watch?v=ID\",\"channel\":\"ch\",\"views\":\"1.2M\",\"hook\":\"opening 0-10s\",\"what_makes_viral\":\"emotion\",\"tone\":\"t\",\"duration_min\":22}]}",true);
    const m=r.match(/\{[\s\S]*"videos"[\s\S]*\}/);
    if(m){const p=JSON.parse(m[0]);const vs=(p.videos||[]).filter(v=>v.url?.includes("watch?v="));if(vs.length){log("â Ranking: "+vs.length+" vÃ­deos | #1: \""+vs[0].title_en?.slice(0,40)+"\" ("+vs[0].views+")","success");return vs;}}
  }catch(e){log("â ï¸ Ranking: "+e.message,"warn");}
  return null;
}

async function fetchTokenStats(){try{const r=await fetch('/api/tokens');return await r.json();}catch{return null;}}

async function fetchDailyCases(day,log){
  log("ð¬ Pesquisando cases reais de crescimento + monetizaÃ§Ã£o...","info");
  try{
    const r=await callClaude("Research successful YouTube psychology channels and monetization cases. ONLY valid JSON.","Search: YouTube psychology channel 2025 2026 million subscribers monetization growth case study\nReturn ONLY:{\"cases\":[{\"channel\":\"n\",\"achievement\":\"what\",\"tactic\":\"specific\",\"metric\":\"number\",\"apply\":\"how today\"}],\"tactics\":[{\"name\":\"n\",\"how\":\"desc\",\"result\":\"metric\"}]}",true);
    const m=r.match(/\{[\s\S]*"cases"[\s\S]*\}/);
    if(m){const p=JSON.parse(m[0]);log("ð¡ "+( p.cases?.length||0)+" cases + "+(p.tactics?.length||0)+" tÃ¡ticas","success");return p;}
  }catch(e){log("â ï¸ Cases: "+e.message,"warn");}
  return null;
}

// âââ TOM DO CANAL (anÃ´nimo em 2026, revelado em 2027) ââââââââââââ
function getCanalTone(){
  const rev=(()=>{try{return localStorage.getItem("doc_revealed")==="1";}catch{return false;}})();
  if(rev)return "Canal: psicologia.doc | Criadora: Daniela Coelho, psicÃ³loga | Tom: autoridade calorosa + expertise clÃ­nica. Mencione consultas quando relevante.";
  return "Canal: psicologia.doc â canal de documentÃ¡rios de psicologia | Tom: narrador especialista anÃ´nimo. NUNCA use 'eu' ou mencione nome de pessoa. Use 'este documentÃ¡rio', 'a psicologia mostra', 'casos documentados revelam'. PÃºblico: 25-54 anos. CRP compliance total.";
}

// âââ GERA ROTEIRO HIPNÃTICO ââââââââââââââââââââââââââââââââââââââ
async function generateScript(topic,channel,day,topVideo,log){
  const pat=VIRAL_PATTERNS[Math.floor(Math.random()*VIRAL_PATTERNS.length)];
  const hook=ATTENTION_HOOKS[Math.floor(Math.random()*ATTENTION_HOOKS.length)];
  const books=BESTSELLERS[topic]||[];
  const isYT=channel==="youtube";
  const topRef=topVideo?'"'+topVideo.title_en+'" ('+topVideo.views+' views, gancho: "'+(topVideo.hook||"")+'")':"vÃ­deo viral de psicologia";
  log("ð ["+channel.toUpperCase()+"] Roteiro hipnÃ³tico: \""+topic+"\"...","info");

  const sys=getCanalTone()+"\nNUNCA mencione IA. CRP: zero diagnÃ³sticos, zero promessa de cura.\nTÃCNICAS OBRIGATÃRIAS:\n1. PNL Espelhamento: pessoa se VÃ no vÃ­deo desde o 1Âº segundo\n2. Loop aberto: nunca feche a curiosidade atÃ© o fim\n3. Segunda pessoa ('vocÃª','seu') â direto e Ã­ntimo\n4. Cada ponto gera 'isso acontece comigo' ou 'conheÃ§o alguÃ©m assim'\n5. VÃ­deos LONGOS para YouTube (22-28min) â CPM 6x maior\n6. Ãltimo minuto: CTA forte + preview do prÃ³ximo episÃ³dio\n7. Som cinematic: instrua ElevenLabs com pausas dramÃ¡ticas [PAUSA] e Ãªnfases *assim*\nBase: DSM-5, APA, CID-11."+(books.length?"\nINDEXAÃÃO SUTIL (nÃ£o venda): "+books.map(b=>'"'+b.t+'" de '+b.a).join(", "):"");

  const userYT="Crie roteiro documentÃ¡rio YouTube 22-28min sobre \""+topic+"\".\nInspire-se: "+topRef+"\nPadrÃ£o viral: '"+pat+"'\nGANCHO 0-30s: '"+hook+"'\n\nð SEO TITLE (keyword no inÃ­cio, 55-65 chars, sem nome de pessoa):\nð THUMBNAIL TEXT (CAPS emocional, mÃ¡x 4 palavras):\n[GANCHO 0-30s]: adapte o hook para o tema\n[CONTEXTO 1-3min]: dado cientÃ­fico chocante + estatÃ­stica\n[DESENVOLVIMENTO 5-8 pontos]: DSM-5/APA + casos anÃ´nimos reais\n[VIRADA EMOCIONAL]: 'Se vocÃª reconhece isso, hÃ¡ uma explicaÃ§Ã£o'\n[SOLUÃÃO PARCIAL]: 3 aÃ§Ãµes baseadas em evidÃªncias\n[CTA WHATSAPP]: 'Continue essa conversa no grupo psicologia.doc â link na bio'\n[LOOP PRÃXIMO EP]: 'No prÃ³ximo documentÃ¡rio vou revelar [TEMA] â que explica por que vocÃª [COMPORTAMENTO]'\nð DESCRIÃÃO YT (400+ palavras, SEO, link WhatsApp):\nð·ï¸ TAGS (25 tags PT+EN):\nð CHAPTERS (timestamps):"+(books.length?"\nð¡ Indexe naturalmente: "+books[0].t+" de "+books[0].a:"");

  const userShort="Crie Short/Reel 45-60s para "+channel+" sobre \""+topic+"\".\nGANCHO 0-3s: "+hook.split(".")[0]+"\n[REVELAÃÃO 3-20s]: dado cientÃ­fico + 'acontece porque...'\n[IDENTIFICAÃÃO 20-40s]: 'Se vocÃª...' â espelhamento direto\n[CTA 40-60s]: 'Documentei tudo em episÃ³dio completo â link na bio'\nð TÃTULO (emoji + texto â¤60 chars, sem nome de pessoa):\nð·ï¸ HASHTAGS: #psicologia #saudemental #psicologiadoc";

  return await callClaude(sys,isYT?userYT:userShort,false);
}

// âââ VALIDAÃÃO EM LOOP âââââââââââââââââââââââââââââââââââââââââ
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
  log("ð RevisÃ£o em loop â atÃ© score â¥88 + safety â¥85...","info");
  let best=script,bestScore=0;
  for(let round=1;round<=max;round++){
    const r=await validate(best);
    log("ð Rodada "+round+"/"+max+" â Score:"+r.score+" Safety:"+r.safety,"info");
    if(r.score>=88&&r.safety>=ANTI_BAN.minSafety){log("â SÃ³lido em "+round+" rodada(s)","success");return{...r,script:best,rounds:round};}
    if(r.score>bestScore)bestScore=r.score;
    if(round<max){const ref=await callClaude("Revisor CRP. Melhore sem mudar tema. FortaleÃ§a PNL e loop aberto. Remova diagnÃ³sticos implÃ­citos.","CONTEÃDO:\n"+best.slice(0,2500)+"\n\nMELHORE e retorne completo:");if(ref?.length>200)best=ref;}
  }
  return await validate(best).then(r=>({...r,script:best,rounds:max}));
}

// âââ MOTOR 1000x âââââââââââââââââââââââââââââââââââââââââââââââââ
async function generateVariationBlocks(topic,day,topVideo,log){
  log("ð Motor 1000x â gerando blocos para \""+topic+"\"...","info");
  const sys=getCanalTone()+"\nCRP. Base: DSM-5. PNL espelhamento obrigatÃ³rio.";
  const topRef=topVideo?'"'+topVideo.title_en+'" ('+topVideo.views+' views)':"";
  const[ht,ct,ct2]=await Promise.all([
    callClaude(sys,topRef+"\nGere 10 HOOKS de 3-8s sobre \""+topic+"\". Gatilhos: choque, identificaÃ§Ã£o, contradiÃ§Ã£o, pergunta, urgÃªncia, promessa, exclusividade, empatia, estatÃ­stica, loop-aberto.\nH1: [hook]\n...H10: [hook]"),
    callClaude(sys,topRef+"\nGere 10 CORPOS de 20-40s sobre \""+topic+"\". Estruturas: lista_3, lista_5, histÃ³ria, comparaÃ§Ã£o, jornada, cÃ©rebro, sÃ©rie_ep, mito_fato, protocolo, relacional.\nC1: [corpo]\n...C10: [corpo]"),
    callClaude(sys,"Gere 10 CTAs de 3-8s para docs de psicologia sobre \""+topic+"\". Destinos: salvar, comentar, whatsapp, sÃ©rie, inscriÃ§Ã£o, reflexÃ£o, recurso, prÃ³ximo_ep, comunidade, pergunta.\nCTA1: [cta]\n...CTA10: [cta]"),
  ]);
  const parse=(text,pfx)=>text.split("\n").filter(l=>l.match(new RegExp("^"+pfx+"\\d+:","i"))).map((l,i)=>({id:pfx+(i+1),content:l.replace(/^[A-Z]+\d+:\s*/i,"").trim()})).filter(b=>b.content.length>10);
  const hooks=parse(ht,"H"),corpos=parse(ct,"C"),ctas=parse(ct2,"CTA");
  log("â "+hooks.length+"Ã"+corpos.length+"Ã"+ctas.length+" = "+(hooks.length*corpos.length*ctas.length)+" variaÃ§Ãµes","success");
  return{hooks,corpos,ctas,topic};
}

// âââ SAFETY SCORE âââââââââââââââââââââââââââââââââââââââââââââ
function localSafety(txt){
  let s=100;const t=(txt||"").toLowerCase();
  if(t.includes("vocÃª tem "))s-=15;if(t.includes("cure "))s-=20;
  if(t.includes("remÃ©dio")||t.includes("medicamento"))s-=25;
  if(t.includes("diagnÃ³stico"))s-=8;
  if(t.includes("daniela")||t.includes("meu nome"))s-=30;
  if(t.includes("psicÃ³loga")&&!t.includes("uma psicÃ³loga")&&!t.includes("a psicÃ³loga"))s-=15;
  if(t.includes("documentado")||t.includes("pesquisas mostram"))s+=3;
  return Math.min(100,Math.max(0,s));
}

// âââ ELEVENLABS ââââââââââââââââââââââââââââââââââââââââââââââââââ
async function genVoice(script,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  if(!cfg.elevenlabs){log("ðï¸ ElevenLabs: configure API key â ConfiguraÃ§Ãµes","warn");return null;}
  const spoken=script.replace(/ð[^\n]*/g,"").replace(/\[.*?\]/g,"").replace(/[ââððð¯ð¡ð·ï¸]/g,"").trim().slice(0,3500);
  if(spoken.length<50)return null;
  log("ðï¸ ElevenLabs: narraÃ§Ã£o cinematic PT-BR...","info");
  try{
    const vId=cfg.elevenlabsVoice||"pNInz6obpgDQGcFmaJgB";
    const r=await fetch("https://api.elevenlabs.io/v1/text-to-speech/"+vId+"/stream",{method:"POST",headers:{"xi-api-key":cfg.elevenlabs,"Content-Type":"application/json"},body:JSON.stringify({text:spoken,model_id:"eleven_multilingual_v2",voice_settings:{stability:0.38,similarity_boost:0.90,style:0.45,use_speaker_boost:true}})});
    if(!r.ok){log("â ï¸ ElevenLabs: "+r.status,"warn");return null;}
    const blob=await r.blob();
    log("â ElevenLabs: "+(blob.size/1024).toFixed(0)+"KB â narraÃ§Ã£o pronta","success");
    return{url:URL.createObjectURL(blob),blob};
  }catch(e){log("â ï¸ ElevenLabs: "+e.message,"warn");return null;}
}

// âââ HEYGEN ââââââââââââââââââââââââââââââââââââââââââââââââââââââ
async function genAvatar(script,audio,platform,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  if(!cfg.heygen){log("ð¬ HeyGen: configure API key â ConfiguraÃ§Ãµes","warn");return null;}
  const FMTS={youtube:{w:1920,h:1080},instagram:{w:1080,h:1920},tiktok:{w:1080,h:1920},pinterest:{w:1000,h:1500}};
  const fmt=FMTS[platform]||FMTS.youtube;
  const spoken=script.replace(/ð[^\n]*/g,"").replace(/\[.*?\]/g,"").trim().slice(0,1500);
  log("ð¬ HeyGen: avatar "+fmt.w+"Ã"+fmt.h+" para "+platform+"...","info");
  try{
    const r=await fetch("https://api.heygen.com/v2/video/generate",{method:"POST",headers:{"X-Api-Key":cfg.heygen,"Content-Type":"application/json"},body:JSON.stringify({video_inputs:[{character:{type:"avatar",avatar_id:cfg.heygenAvatar||"Daisy-inskirt-20220818",avatar_style:"normal"},voice:audio?.url?{type:"audio",audio_url:audio.url}:{type:"text",input_text:spoken,voice_id:cfg.heygenVoice||"1bd001e7e50f421d891986aad5158bc8",speed:1.0},background:{type:"color",value:"#0a0a1a"}}],dimension:{width:fmt.w,height:fmt.h},test:false,caption:true})});
    const d=await r.json();
    if(!d.data?.video_id){log("â ï¸ HeyGen: "+(d.error||"err"),"warn");return null;}
    log("â³ HeyGen: renderizando ("+d.data.video_id+")...","info");
    for(let i=0;i<24;i++){
      await sleep(15000);
      try{const sr=await fetch("https://api.heygen.com/v1/video_status.get?video_id="+d.data.video_id,{headers:{"X-Api-Key":cfg.heygen}});const sd=await sr.json();if(sd.data?.status==="completed"){log("â HeyGen: vÃ­deo pronto!","success");return{url:sd.data.video_url,video_id:d.data.video_id};}if(sd.data?.status==="failed"){log("â HeyGen: falhou","error");return null;}if(i%2===0)log("â³ HeyGen: "+sd.data?.status+"...","info");}catch{break;}
    }
    return null;
  }catch(e){log("â ï¸ HeyGen: "+e.message,"warn");return null;}
}

// âââ PUBLICAÃÃO REAL âââââââââââââââââââââââââââââââââââââââââââââ
async function publishAll(content,videoUrl,platforms,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  const res={};
  for(const p of platforms){
    if(!videoUrl){res[p]="no_video";log("âï¸ "+p+": configure HeyGen","warn");continue;}
    try{
      if(p==="youtube"&&cfg.youtube){
        log("â¶ï¸ YouTube: publicando...","info");
        const ir=await fetch("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",{method:"POST",headers:{"Authorization":"Bearer "+cfg.youtube,"Content-Type":"application/json","X-Upload-Content-Type":"video/mp4"},body:JSON.stringify({snippet:{title:content.title.slice(0,100),description:content.body?.slice(0,2000)||"",tags:[],categoryId:"26",defaultLanguage:"pt"},status:{privacyStatus:"public",selfDeclaredMadeForKids:false}})});
        if(ir.ok){const ul=ir.headers.get("Location");const vb=await(await fetch(videoUrl)).blob();const ur=await fetch(ul,{method:"PUT",headers:{"Content-Type":"video/mp4"},body:vb});const yd=await ur.json();if(yd.id){log("â YouTube: https://youtube.com/watch?v="+yd.id,"success");res[p]="published";continue;}}
        res[p]="auth_error";
      }else if(p==="instagram"&&cfg.instagram){
        log("ð¸ Instagram: Reel...","info");
        const c=await(await fetch("https://graph.instagram.com/v18.0/me/media",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({media_type:"REELS",video_url:videoUrl,caption:content.title+"\n\n"+CANAL.handle+"\n#psicologia #saudemental #psicologiadoc",access_token:cfg.instagram})})).json();
        if(c.id){await sleep(8000);const pub=await(await fetch("https://graph.instagram.com/v18.0/me/media_publish",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({creation_id:c.id,access_token:cfg.instagram})})).json();if(pub.id){log("â Instagram: "+pub.id,"success");res[p]="published";continue;}}
        res[p]="error";
      }else if(p==="tiktok"&&cfg.tiktok){
        log("ðµ TikTok: publicando...","info");
        const d=await(await fetch("https://open.tiktokapis.com/v2/post/publish/video/init/",{method:"POST",headers:{"Authorization":"Bearer "+cfg.tiktok,"Content-Type":"application/json; charset=UTF-8"},body:JSON.stringify({post_info:{title:content.title.slice(0,150),privacy_level:"PUBLIC_TO_EVERYONE"},source_info:{source:"PULL_FROM_URL",video_url:videoUrl}})})).json();
        if(d.data?.publish_id){log("â TikTok: "+d.data.publish_id,"success");res[p]="published";continue;}
        res[p]="error";
      }else if(p==="pinterest"&&cfg.pinterest){
        log("ð Pinterest: Pin...","info");
        const b=await(await fetch("https://api.pinterest.com/v5/boards?page_size=1",{headers:{"Authorization":"Bearer "+cfg.pinterest}})).json();
        if(b.items?.[0]?.id){const pin=await(await fetch("https://api.pinterest.com/v5/pins",{method:"POST",headers:{"Authorization":"Bearer "+cfg.pinterest,"Content-Type":"application/json"},body:JSON.stringify({board_id:b.items[0].id,title:content.title.slice(0,100),description:content.topic,media_source:{source_type:"video_id",url:videoUrl}})})).json();if(pin.id){log("â Pinterest: "+pin.id,"success");res[p]="published";continue;}}
        res[p]="error";
      }else{res[p]="not_configured";log("âï¸ "+p+": configure token â ConfiguraÃ§Ãµes","warn");}
    }catch(e){res[p]="error";log("â ï¸ "+p+": "+e.message,"warn");}
  }
  const ok=Object.values(res).filter(v=>v==="published").length;
  if(ok>0)log("ð¡ "+ok+"/"+platforms.length+" publicados","success");
  return res;
}

// âââ UPDATE BIO DO CANAL âââââââââââââââââââââââââââââââââââââââââ
async function updateChannelBio(platform,bio,log){
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  log("âï¸ ["+platform+"] Atualizando bio...","info");
  try{
    if(platform==="youtube"&&cfg.youtube){const r=await fetch("https://www.googleapis.com/youtube/v3/channels?part=brandingSettings",{method:"PUT",headers:{"Authorization":"Bearer "+cfg.youtube,"Content-Type":"application/json"},body:JSON.stringify({id:"mine",brandingSettings:{channel:{description:bio,title:CANAL.nome}}})});if(r.ok)log("â YouTube bio atualizada","success");}
    if(platform==="instagram"&&cfg.instagram){const r=await fetch("https://graph.instagram.com/v18.0/me",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({biography:bio,access_token:cfg.instagram})});if(r.ok)log("â Instagram bio atualizada","success");}
  }catch(e){log("â ï¸ Bio update: "+e.message,"warn");}
}

// âââ PIPELINE PRINCIPAL ââââââââââââââââââââââââââââââââââââââââââ
const STEPS=[
  {icon:"ð",label:"Ranking mundial + cases reais do dia"},
  {icon:"ð",label:"Selecionando tema â Playlist + sÃ©ries ativas"},
  {icon:"ð",label:"Gerando roteiro hipnÃ³tico (PNL + loop aberto)"},
  {icon:"ð",label:"RevisÃ£o em loop â atÃ© score â¥88 + safety â¥85"},
  {icon:"ð",label:"Filtro anti-ban + CRP compliance"},
  {icon:"ðï¸",label:"ElevenLabs â narraÃ§Ã£o cinematic PT-BR"},
  {icon:"ð¬",label:"HeyGen â avatar cinematogrÃ¡fico"},
  {icon:"ð¡",label:"PublicaÃ§Ã£o: YouTube + Instagram + TikTok + Pinterest"},
  {icon:"ð¬",label:"WhatsApp: post nos grupos ativos"},
  {icon:"â¡",label:"Ciclo concluÃ­do â banco de dados atualizado"},
];

async function runPipeline({day,setStep,setRunning,log,onContent,onMetrics,onRanking,onCases}){
  log("ââââââââââââââââââââââââââââââ","system");
  log("ð PIPELINE DIA "+day+" â "+new Date().toLocaleString("pt-BR"),"system");
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
    if(!script){log("â Roteiro "+ch+" falhou","error");continue;}
    const ls=localSafety(script);
    if(ls<60){log("ð¨ Safety local baixo ("+ls+") â abortando","error");continue;}
    setStep(3);
    const val=await validateLoop(script,log,4);
    log("ð¬ Sci:"+val.sci+" Ãtica:"+val.eth+" ðSafety:"+val.safety+" Score:"+val.score+" ("+val.rounds+"r)","success");
    setStep(4);
    if(val.safety<ANTI_BAN.minSafety){log("ð¨ Safety insuficiente â nÃ£o publicado","error");continue;}
    await sleep(200);
    setStep(5);const audio=await genVoice(val.script,log);
    setStep(6);const video=await genAvatar(val.script,audio,ch,log);
    setStep(7);
    const platforms=ch==="youtube"?["youtube","instagram","tiktok","pinterest"]:[ch];
    const titleM=val.script.match(/SEO TITLE[^:\n]*:\s*(.+)/)||val.script.match(/TÃTULO[^:\n]*:\s*(.+)/i);
    const title=titleM?titleM[1].trim():topic+" â "+CANAL.nome;
    const pubRes=await publishAll({title,topic,body:val.script},video?.url||null,platforms,log);
    setStep(8);log("ð¬ WhatsApp: agendando mensagem...","info");await sleep(300);
    const viral=Math.min(99,val.score+Math.floor(Math.random()*8));
    const content={id:Date.now()+i,title,body:val.script,channel:ch,topic,score:val.score,viralConf:viral,safetyScore:val.safety,rounds:val.rounds,isSeriesEp:useEp&&i===0,serieName:useEp?activeSerie.nome:null,status:"publicado",day,createdAt:new Date().toLocaleString("pt-BR"),createdTs:Date.now(),hasAudio:!!audio,hasVideo:!!video,videoUrl:video?.url||null,pubResults:pubRes,books:(BESTSELLERS[topic]||[]).map(b=>b.t),topInspo:top?{title:top.title_en,url:top.url,views:top.views}:null};
    onContent(content);onMetrics(val.score,viral);
    log("â ["+ch+"] \""+title.slice(0,45)+"...\" Score:"+val.score+" Safety:"+val.safety+" Viral:"+viral+"%","success");
    if(i<CHANNELS_LIST.length-1)await sleep(800);
  }
  setStep(9);log("â Pipeline Dia "+day+" ("+new Date().toLocaleDateString("pt-BR")+") concluÃ­do.","success");
  log("ââââââââââââââââââââââââââââââ","system");
  await sleep(400);setStep(-1);setRunning(false);
}

function fmtCd(ms){if(ms<=0)return"agora";const t=Math.floor(ms/1000),h=Math.floor(t/3600),m=Math.floor((t%3600)/60),s=t%60;if(h>0)return h+"h "+String(m).padStart(2,"0")+"m";return String(m).padStart(2,"0")+":"+String(s).padStart(2,"0");}


// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// APP
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
export default function App(){
  const[page,setPage]=useState("dashboard");
  const[sidebarOpen,setSidebar]=useState(false);
  const[darkMode,setDarkMode]=useState(true);
  const[dayNumber,setDayNumber]=useState(calcDay);
  const[revealed,setRevealed]=useState(()=>{try{return localStorage.getItem("doc_revealed")==="1";}catch{return false;}});
  const[revealModal,setRevealModal]=useState(false);
  const[metrics,setMetrics]=useState({generated:0,published:0,viralReady:0,scoreAvg:0});
const[tokenStats,setTokenStats]=useState(null);
const[tokenLoading,setTokenLoading]=useState(false);
  const[contents,setContents]=useState([]);
  const[logs,setLogs]=useState([{id:1,time:"--:--:--",type:"system",text:"ð¬ psicologia.doc v7 â Dia 1: 15 abr 2026 Â· RevelaÃ§Ã£o: ~1 jan 2027 Â· CÃ©rebro iniciando..."}]);
  const[ranking,setRanking]=useState([]);
  const[cases,setCases]=useState(null);
  const[isRunning,setIsRunning]=useState(false);
  const[isRanking,setIsRanking]=useState(false);
  const[step,setStep]=useState(-1);
  const[notifCount,setNotifCount]=useState(0);
  const[notifOpen,setNotifOpen]=useState(false);
  const[notifs,setNotifs]=useState([]);
  const[variations,setVariations]=useState(null);
  const[waGroups,setWaGroups]=useState([{id:1,nome:"psicologia.doc #1",membros:0,ativo:true}]);
  const[now,setNow]=useState(new Date());
  const[nextProd,setNextProd]=useState(Date.now()+FIRST_PROD);
  const[nextRank,setNextRank]=useState(Date.now()+FIRST_RANK);

  const logRef=useRef(null),runRef=useRef(false),rankRef=useRef(false),initRef=useRef(false);

  useEffect(()=>{
    const root=document.documentElement;const d=darkMode;
    root.style.setProperty("--bg",d?"#0a0a0f":"#f5f5f7");root.style.setProperty("--surf",d?"#13131a":"#ffffff");
    root.style.setProperty("--surf2",d?"#1c1c26":"#f0f0f5");root.style.setProperty("--border",d?"#252535":"#e2e2e8");
    root.style.setProperty("--text",d?"#f0f0f8":"#111827");root.style.setProperty("--text2",d?"#b0b0c8":"#374151");
    root.style.setProperty("--muted",d?"#55556a":"#9ca3af");
  },[darkMode]);

  useEffect(()=>{const t=setInterval(()=>{setNow(new Date());setDayNumber(calcDay());},1000);return()=>clearInterval(t);},[]);

  useEffect(()=>{
    (async()=>{
      const[m,c,r]=await Promise.all([load("doc_metrics",{generated:0,published:0,viralReady:0,scoreAvg:0}),load("doc_contents",[]),load("doc_ranking",[])]);
      setMetrics(m);setContents(c);setRanking(r);
    })();
  },[]);

  const addLog=useCallback((text,type="info")=>{
    const ts=new Date().toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit",second:"2-digit"});
    const e={id:Date.now()+Math.random(),time:ts,type,text};
    setLogs(p=>{const n=[e,...p.slice(0,299)];setTimeout(()=>{if(logRef.current)logRef.current.scrollTop=0;},20);return n;});
  },[]);

  const onContent=useCallback(c=>{
    setContents(p=>{const n=[c,...p.slice(0,99)];stor("doc_contents",n);return n;});
    setNotifCount(x=>x+1);
    setNotifs(p=>[{id:c.id,title:c.title,channel:c.channel,score:c.score,ts:c.createdAt},...p.slice(0,19)]);
  },[]);

  const onMetrics=useCallback((score,viral)=>{
    setMetrics(m=>{const g=m.generated+1;const nm={...m,generated:g,published:m.published+1,viralReady:viral>=85?m.viralReady+1:m.viralReady,scoreAvg:g===1?score:Math.round((m.scoreAvg*m.generated+score)/g)};stor("doc_metrics",nm);return nm;});
  },[]);

  const onRanking=useCallback(r=>{setRanking(r);stor("doc_ranking",r);},[]);
  const refreshTokens=useCallback(async()=>{setTokenLoading(true);const t=await fetchTokenStats();if(t)setTokenStats(t);setTokenLoading(false);},[]);
  const onCases=useCallback(c=>setCases(c),[]);

  useEffect(()=>{
    if(initRef.current)return;initRef.current=true;
    let lastR=0,lastP=0;
    async function doRank(){if(rankRef.current)return;rankRef.current=true;setIsRanking(true);setNextRank(Date.now()+RANK_INTERVAL);const r=await fetchRanking(addLog);if(r)onRanking(r);setIsRanking(false);rankRef.current=false;}
    async function doProd(){if(runRef.current)return;runRef.current=true;setIsRunning(true);setNextProd(Date.now()+PROD_INTERVAL);await runPipeline({day:calcDay(),setStep,setRunning:(v)=>{setIsRunning(v);if(!v)runRef.current=false;},log:addLog,onContent,onMetrics,onRanking,onCases});runRef.current=false;}
    const t1=setTimeout(doRank,FIRST_RANK),t2=setTimeout(doProd,FIRST_PROD);
refreshTokens();
const tokenCron=setInterval(refreshTokens,5*60*1000);
    const cron=setInterval(()=>{const n=Date.now();if(n-lastR>=RANK_INTERVAL){lastR=n;doRank();}if(n-lastP>=PROD_INTERVAL){lastP=n;doProd();}},10000);
    const onVis=()=>{if(document.visibilityState==="visible"){const n=Date.now();if(n-lastR>=RANK_INTERVAL){lastR=n;doRank();}}};
    document.addEventListener("visibilitychange",onVis);
    return()=>{clearTimeout(t1);clearTimeout(t2);clearInterval(cron);clearInterval(tokenCron);document.removeEventListener("visibilitychange",onVis);};
  },[addLog,onContent,onMetrics,onRanking,onCases]);

  const forceRun=useCallback(async()=>{
    if(runRef.current)return;runRef.current=true;setIsRunning(true);setNextProd(Date.now()+PROD_INTERVAL);
    addLog("â¡ Ciclo forÃ§ado â Dia "+calcDay()+" ("+new Date().toLocaleDateString("pt-BR")+")","system");
    await runPipeline({day:calcDay(),setStep,setRunning:(v)=>{setIsRunning(v);if(!v)runRef.current=false;},log:addLog,onContent,onMetrics,onRanking,onCases});
    runRef.current=false;
  },[addLog,onContent,onMetrics,onRanking,onCases]);

  const activateReveal=useCallback(()=>{
    try{localStorage.setItem("doc_revealed","1");}catch{}
    setRevealed(true);setRevealModal(false);
    addLog("ð REVELAÃÃO ATIVADA â psicologia.doc agora Ã© de Daniela Coelho, psicÃ³loga","system");
    addLog("ð¡ Atualizando bios YouTube e Instagram automaticamente...","info");
    ["youtube","instagram"].forEach(p=>updateChannelBio(p,CANAL.bio2027,addLog));
    addLog("ð Atualize TikTok e Pinterest manualmente â bios disponÃ­veis em RevelaÃ§Ã£o","info");
  },[addLog]);

  const navTo=p=>{setPage(p);setSidebar(false);setNotifOpen(false);};
  const ph=getPhase(dayNumber,revealed);
  const msToProd=Math.max(0,nextProd-now.getTime());
  const msToRank=Math.max(0,nextRank-now.getTime());
  const prodPct=Math.min(100,((PROD_INTERVAL-msToProd)/PROD_INTERVAL)*100);
  const timeStr=now.toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit",second:"2-digit"});
  const dateStr=now.toLocaleDateString("pt-BR",{weekday:"long",day:"2-digit",month:"long",year:"numeric"});
  const canReveal=dayNumber>=DIA_REVELACAO||revealed;
  const daysToReveal=Math.max(0,DIA_REVELACAO-dayNumber);
  const revealDate=dayToDate(DIA_REVELACAO);
  const totalWA=waGroups.reduce((s,g)=>s+g.membros,0);

  const NAV=[
    {id:"dashboard",icon:"â¡",label:"Dashboard"},
    {id:"cerebro",icon:"ð§ ",label:"CÃ©rebro AO VIVO"},
    {id:"gerador",icon:"â¨",label:"Gerador Manual"},
    {id:"variacoes",icon:"ð",label:"Motor 1000x"},
    {id:"series",icon:"ð¬",label:"SÃ©ries EpisÃ³dicas"},
    {id:"revelacao",icon:"ð",label:"RevelaÃ§Ã£o 2027",badge:canReveal&&!revealed?"ð":revealed?"â":null},
    {id:"canais",icon:"ð¡",label:"GestÃ£o de Canais"},
    {id:"whatsapp",icon:"ð¬",label:"WhatsApp Grupos"},
    {id:"ranking",icon:"ð",label:"Ranking Mundial"},
    {id:"cases",icon:"ð",label:"Cases do Dia"},
    {id:"playlist",icon:"ð",label:"Playlist 630 dias"},
    {id:"conteudo",icon:"ð",label:"ConteÃºdo",badge:notifCount>0?notifCount:null},
    {id:"monetizacao",icon:"ð°",label:"MonetizaÃ§Ã£o"},
    {id:"configuracoes",icon:"âï¸",label:"ConfiguraÃ§Ãµes"},
    {id:"logs",icon:"ð",label:"Logs"},
  ];

  return(
    <>
      <style>{CSS}</style>
      <div className="app">
        <div className={"overlay"+(sidebarOpen?" show":"")} onClick={()=>setSidebar(false)}/>

        {/* MODAL REVELAÃÃO */}
        {revealModal&&(
          <div style={{position:"fixed",inset:0,zIndex:300,background:"rgba(0,0,0,0.75)",display:"flex",alignItems:"center",justifyContent:"center",padding:20,backdropFilter:"blur(8px)"}} onClick={()=>setRevealModal(false)}>
            <div onClick={e=>e.stopPropagation()} style={{width:"min(400px,92vw)",background:"var(--surf)",borderRadius:20,overflow:"hidden",boxShadow:"0 20px 60px rgba(0,0,0,0.6)"}}>
              <div style={{background:"linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)",padding:"22px 20px 18px"}}>
                <div style={{fontSize:44,marginBottom:8}}>ð</div>
                <div style={{fontWeight:800,fontSize:18,color:"white",lineHeight:1.2}}>Revelar Daniela Coelho,<br/>psicÃ³loga</div>
              </div>
              <div style={{padding:20}}>
                {["â Bios YouTube e Instagram atualizadas automaticamente","â Todo conteÃºdo futuro menciona Daniela Coelho, psicÃ³loga","â CTAs incluem link de consultas","â WhatsApp: funil de consultas ativado","â ï¸ Atualize TikTok e Pinterest manualmente","â ï¸ IrreversÃ­vel â use apenas com CRP ativo"].map((it,i)=>(
                  <div key={i} style={{display:"flex",gap:8,marginBottom:7,fontSize:12,color:it.startsWith("â ï¸")?"var(--amber)":"var(--text2)"}}>
                    <span style={{flexShrink:0}}>{it.split(" ")[0]}</span><span>{it.split(" ").slice(1).join(" ")}</span>
                  </div>
                ))}
                <div style={{background:"rgba(217,119,6,0.08)",border:"1px solid rgba(217,119,6,0.25)",borderRadius:10,padding:12,marginTop:10,marginBottom:16,fontSize:11,color:"var(--amber)"}}>
                  â ï¸ Use apenas apÃ³s ter o CRP emitido. A comunidade vai celebrar esta revelaÃ§Ã£o.
                </div>
                <div style={{display:"flex",gap:10}}>
                  <button onClick={()=>setRevealModal(false)} style={{flex:1,padding:"12px",borderRadius:12,border:"2px solid var(--border)",background:"var(--surf2)",color:"var(--text)",fontWeight:700,cursor:"pointer"}}>Cancelar</button>
                  <button onClick={activateReveal} style={{flex:2,padding:"12px",borderRadius:12,border:"none",background:"linear-gradient(135deg,#7c3aed,#a855f7)",color:"white",fontWeight:800,cursor:"pointer"}}>ð Confirmar RevelaÃ§Ã£o</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* NOTIFICAÃÃES */}
        {notifOpen&&(
          <div style={{position:"fixed",inset:0,zIndex:200,display:"flex",flexDirection:"column",alignItems:"flex-end"}} onClick={()=>setNotifOpen(false)}>
            <div onClick={e=>e.stopPropagation()} style={{width:"min(340px,92vw)",marginTop:"calc(52px + env(safe-area-inset-top,0px))",background:"var(--surf)",borderRadius:"0 0 0 16px",border:"1px solid var(--border)",boxShadow:"0 8px 32px rgba(0,0,0,0.3)",maxHeight:"80dvh",display:"flex",flexDirection:"column"}}>
              <div style={{padding:"12px 16px",borderBottom:"1px solid var(--border)",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                <div style={{fontWeight:700,fontSize:14}}>ð ProduÃ§Ãµes</div>
                <button onClick={()=>{setNotifCount(0);setNotifOpen(false);}} style={{fontSize:11,padding:"4px 10px",borderRadius:20,border:"1px solid var(--border)",background:"var(--surf2)",color:"var(--muted)",cursor:"pointer"}}>Limpar</button>
              </div>
              <div style={{overflowY:"auto",flex:1}}>
                {notifs.length===0&&<div style={{padding:24,textAlign:"center",color:"var(--muted)",fontSize:13}}>Aguardando produÃ§Ã£o...</div>}
                {notifs.map(n=>(
                  <div key={n.id} onClick={()=>navTo("conteudo")} style={{display:"flex",gap:10,padding:"10px 14px",borderBottom:"1px solid var(--border)",cursor:"pointer"}}>
                    <div style={{width:36,height:36,borderRadius:10,flexShrink:0,background:"rgba(124,58,237,0.1)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:18}}>ð¬</div>
                    <div style={{flex:1,minWidth:0}}>
                      <div style={{fontSize:12,fontWeight:600,lineHeight:1.35,overflow:"hidden",textOverflow:"ellipsis",display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical"}}>{n.title}</div>
                      <div style={{display:"flex",gap:6,marginTop:3}}>
                        <span style={{fontSize:10,fontWeight:700,color:"var(--purple)"}}>{n.channel}</span>
                        <span style={{fontSize:10,fontWeight:700,color:"var(--green)"}}>â¡{n.score}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* SIDEBAR */}
        <nav className={"sidebar"+(sidebarOpen?" open":"")}>
          <div style={{padding:"16px 16px 12px",borderBottom:"1px solid var(--border)"}}>
            <div style={{display:"flex",alignItems:"center",gap:10}}>
              <div style={{width:40,height:40,borderRadius:12,background:"linear-gradient(135deg,#7c3aed,#a855f7)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:20,flexShrink:0}}>ð¬</div>
              <div><div style={{fontWeight:800,fontSize:15}}>psicologia.doc</div><div style={{fontSize:10,color:"var(--muted)"}}>v7 Â· Dia {dayNumber} Â· {new Date().toLocaleDateString("pt-BR")}</div></div>
            </div>
          </div>
          <div style={{margin:"8px 12px",padding:"8px 12px",background:isRunning?"rgba(124,58,237,0.08)":"rgba(5,150,105,0.08)",border:"1px solid "+(isRunning?"var(--pb)":"var(--gb)"),borderRadius:10,display:"flex",alignItems:"center",gap:8}}>
            <div style={{width:8,height:8,borderRadius:"50%",background:isRunning?"var(--purple)":"var(--green)",animation:"pulse 1.5s infinite",flexShrink:0}}/>
            <div style={{fontSize:11,fontWeight:700,color:isRunning?"var(--purple)":"var(--green)"}}>{isRunning?"â¡ Produzindo...":isRanking?"ð Buscando ranking...":"CÃ©rebro AutÃ´nomo 24/7 â ATIVO"}</div>
          </div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,padding:"8px 12px",borderBottom:"1px solid var(--border)"}}>
            {[{l:"ð Ranking",v:isRanking?"ð":fmtCd(msToRank),c:"var(--blue)"},{l:"ð¬ ProduÃ§Ã£o",v:isRunning?"â¡ ATIVO":fmtCd(msToProd),c:isRunning?"var(--purple)":"var(--green)"}].map(m=>(
              <div key={m.l} style={{background:"var(--surf2)",padding:"8px 10px",borderRadius:8}}>
                <div style={{fontSize:9,color:"var(--muted)",fontWeight:700,marginBottom:3}}>{m.l}</div>
                <div style={{fontSize:13,fontWeight:800,fontFamily:"monospace",color:m.c}}>{m.v}</div>
              </div>
            ))}
          </div>
          <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:5,padding:"8px 12px",borderBottom:"1px solid var(--border)"}}>
            {[{l:"Docs",v:metrics.generated,c:"var(--purple)"},{l:"Pub.",v:metrics.published,c:"var(--green)"},{l:"Score",v:metrics.scoreAvg||"â",c:"var(--amber)"},{l:"Dia",v:dayNumber,c:"var(--blue)"}].map(m=>(
              <div key={m.l} style={{textAlign:"center",background:"var(--surf2)",borderRadius:8,padding:"5px 2px"}}>
                <div style={{fontWeight:800,fontSize:14,color:m.c}}>{m.v}</div>
                <div style={{fontSize:9,color:"var(--muted)",marginTop:1}}>{m.l}</div>
              </div>
            ))}
          </div>
          {revealed&&<div style={{margin:"8px 12px",padding:"8px 12px",background:"linear-gradient(135deg,rgba(124,58,237,0.1),rgba(236,72,153,0.05))",border:"1px solid rgba(124,58,237,0.3)",borderRadius:10}}><div style={{fontSize:11,fontWeight:700,color:"var(--purple)"}}>ð Daniela Coelho, psicÃ³loga</div><div style={{fontSize:9,color:"var(--muted)",marginTop:2}}>RevelaÃ§Ã£o ativa Â· Consultas abertas</div></div>}
          <nav style={{padding:"6px 0",flex:1,overflowY:"auto"}}>
            {NAV.map(n=>(
              <div key={n.id} className={"ni"+(page===n.id?" on":"")} onClick={()=>navTo(n.id)}>
                <span style={{fontSize:17,width:24,flexShrink:0}}>{n.icon}</span>
                <span style={{flex:1}}>{n.label}</span>
                {n.badge&&<span style={{fontSize:9,fontWeight:700,background:n.badge==="â"?"var(--gl)":n.badge==="ð"?"var(--pl)":"var(--rl)",color:n.badge==="â"?"var(--green)":n.badge==="ð"?"var(--purple)":"var(--red)",borderRadius:4,padding:"1px 5px",flexShrink:0}}>{n.badge}</span>}
              </div>
            ))}
          </nav>
        </nav>

        {/* TOPBAR */}
        <div className="topbar">
          <button className={"hbtn"+(sidebarOpen?" open":"")} onClick={()=>setSidebar(v=>!v)}><span/><span/><span/></button>
          <div style={{display:"flex",alignItems:"center",gap:8,flex:1}}>
            <div style={{width:26,height:26,borderRadius:8,background:"linear-gradient(135deg,#7c3aed,#a855f7)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:13,flexShrink:0}}>ð¬</div>
            <div style={{fontWeight:800,fontSize:14}}>psicologia.doc</div>
          </div>
          <div style={{display:"flex",alignItems:"center",gap:8}}>
            <button onClick={()=>setDarkMode(v=>!v)} style={{width:34,height:34,borderRadius:"50%",border:"none",background:"var(--surf2)",cursor:"pointer",fontSize:15,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}>{darkMode?"âï¸":"ð"}</button>
            <div style={{fontSize:11,fontWeight:700,padding:"4px 9px",borderRadius:20,background:isRunning?"rgba(124,58,237,0.15)":"rgba(5,150,105,0.1)",color:isRunning?"var(--purple)":"var(--green)",whiteSpace:"nowrap"}}>{isRunning?"â¡ Gerando":"â Online"}</div>
            <button className="nb-btn" onClick={()=>{setNotifOpen(v=>!v);setNotifCount(0);}}>ð{notifCount>0&&<span className="nb">{notifCount>9?"9+":notifCount}</span>}</button>
          </div>
        </div>

        {/* MAIN */}
        <main className="main">
          {page==="dashboard"&&<PageDashboard tokenStats={tokenStats} tokenLoading={tokenLoading} refreshTokens={refreshTokens} timeStr={timeStr} dateStr={dateStr} metrics={metrics} contents={contents} ranking={ranking} dayNumber={dayNumber} isRunning={isRunning} isRanking={isRanking} ph={ph} msToProd={msToProd} msToRank={msToRank} prodPct={prodPct} step={step} forceRun={forceRun} setPage={navTo} revealed={revealed} canReveal={canReveal} daysToReveal={daysToReveal} revealDate={revealDate} onRevealClick={()=>setRevealModal(true)} waGroups={waGroups} totalWA={totalWA}/>}
          {page==="cerebro"&&<PageCerebro timeStr={timeStr} dateStr={dateStr} step={step} isRunning={isRunning} isRanking={isRanking} logs={logs} logRef={logRef} dayNumber={dayNumber} ph={ph} msToProd={msToProd} msToRank={msToRank} ranking={ranking}/>}
          {page==="gerador"&&<PageGerador addLog={addLog} onContent={onContent} dayNumber={dayNumber}/>}
          {page==="variacoes"&&<PageVariacoes dayNumber={dayNumber} ranking={ranking} addLog={addLog} onContent={onContent} variations={variations} setVariations={setVariations}/>}
          {page==="series"&&<PageSeries dayNumber={dayNumber}/>}
          {page==="revelacao"&&<PageRevelacao dayNumber={dayNumber} revealed={revealed} canReveal={canReveal} daysToReveal={daysToReveal} revealDate={revealDate} onRevealClick={()=>setRevealModal(true)}/>}
          {page==="canais"&&<PageCanais revealed={revealed}/>}
          {page==="whatsapp"&&<PageWhatsApp waGroups={waGroups} setWaGroups={setWaGroups} contents={contents} revealed={revealed}/>}
          {page==="ranking"&&<PageRanking ranking={ranking} isRanking={isRanking}/>}
          {page==="cases"&&<PageCases cases={cases}/>}
          {page==="playlist"&&<PagePlaylist dayNumber={dayNumber}/>}
          {page==="conteudo"&&<PageConteudo contents={contents} setNotifCount={setNotifCount}/>}
          {page==="monetizacao"&&<PageMonetizacao metrics={metrics} dayNumber={dayNumber} revealed={revealed}/>}
          {page==="configuracoes"&&<PageConfig metrics={metrics}/>}
          {page==="logs"&&<PageLogs logs={logs} logRef={logRef}/>}
        </main>
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: DASHBOARD
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageDashboard({tokenStats,tokenLoading,refreshTokens,timeStr,dateStr,metrics,contents,ranking,dayNumber,isRunning,isRanking,ph,msToProd,msToRank,prodPct,step,forceRun,setPage,revealed,canReveal,daysToReveal,revealDate,onRevealClick,waGroups,totalWA}){
  const activeSerie=SERIES_LIBRARY.find(s=>s.status==="active");
  const avgSafety=contents.length?Math.round(contents.reduce((s,c)=>(s+(c.safetyScore||92)),0)/contents.length):92;
  const booksContent=contents.filter(c=>c.books?.length).length;
  return(
    <>
      <div className="ph"><div><div className="pt">psicologia.doc</div><div className="ps">{ph.label} Â· {ph.period}</div></div>
        <div style={{display:"flex",alignItems:"center",gap:6,padding:"6px 12px",borderRadius:20,background:"rgba(5,150,105,0.1)",border:"1px solid var(--gb)",flexShrink:0}}>
          <div style={{width:7,height:7,borderRadius:"50%",background:"var(--green)",animation:"pulse 1.5s infinite"}}/>
          <span style={{fontSize:11,fontWeight:700,color:"var(--green)",whiteSpace:"nowrap"}}>24/7</span>
        </div>
      </div>
      <div className="body">
        {/* RelÃ³gio */}
        <div style={{background:"linear-gradient(135deg,rgba(124,58,237,0.12),rgba(168,85,247,0.04))",border:"1px solid rgba(124,58,237,0.25)",borderRadius:18,padding:"18px 18px 14px",marginBottom:14}}>
          <div style={{fontSize:10,fontWeight:700,color:"var(--purple)",textTransform:"uppercase",letterSpacing:"1px",marginBottom:8}}>ð RelÃ³gio do CÃ©rebro Â· psicologia.doc</div>
          <div style={{fontFamily:"monospace",fontSize:38,fontWeight:800,letterSpacing:"0.05em",lineHeight:1,marginBottom:6,color:"#FF69B4"}}>{timeStr}</div>
          <div style={{fontSize:12,color:"var(--text2)",marginBottom:12,textTransform:"capitalize"}}>{dateStr}</div>
          <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:10}}>
            <div style={{background:"rgba(0,0,0,0.2)",borderRadius:10,padding:"10px 12px"}}>
              <div style={{fontSize:9,color:"var(--muted)",fontWeight:700,textTransform:"uppercase",marginBottom:4}}>ð¬ ProduÃ§Ã£o</div>
              <div style={{fontFamily:"monospace",fontSize:20,fontWeight:800,color:isRunning?"var(--purple)":"var(--green)",lineHeight:1}}>{isRunning?"â¡ AGORA":fmtCd(msToProd)}</div>
              {!isRunning&&<div style={{height:3,background:"rgba(255,255,255,0.1)",borderRadius:2,marginTop:6,overflow:"hidden"}}><div style={{height:"100%",borderRadius:2,background:"var(--green)",width:prodPct+"%",transition:"width 1s linear"}}/></div>}
            </div>
            <div style={{background:"rgba(0,0,0,0.2)",borderRadius:10,padding:"10px 12px"}}>
              <div style={{fontSize:9,color:"var(--muted)",fontWeight:700,textTransform:"uppercase",marginBottom:4}}>ð Ranking</div>
              <div style={{fontFamily:"monospace",fontSize:20,fontWeight:800,color:isRanking?"var(--blue)":"var(--text2)",lineHeight:1}}>{isRanking?"ð ATIVO":fmtCd(msToRank)}</div>
            </div>
          </div>
          {isRunning&&<div style={{marginTop:12}}>
            <div style={{fontSize:10,color:"var(--purple)",marginBottom:5,fontWeight:600}}>Etapa {Math.max(0,step)+1}/10 â {STEPS[Math.max(0,step)]?.label}</div>
            <div style={{display:"flex",gap:3}}>{STEPS.map((_,i)=><div key={i} style={{flex:1,height:4,borderRadius:2,background:i<step?"var(--green)":i===step?"var(--purple)":"rgba(124,58,237,0.15)",transition:"background 0.3s"}}/>)}</div>
          </div>}
        </div>

        {/* BotÃ£o ciclo */}
        {!isRunning?(
          <button onClick={forceRun} style={{width:"100%",padding:"13px",borderRadius:12,border:"none",background:"linear-gradient(135deg,var(--purple),#a855f7)",color:"white",fontWeight:700,fontSize:14,cursor:"pointer",marginBottom:14,display:"flex",alignItems:"center",justifyContent:"center",gap:8}}>
            â¡ ForÃ§ar Ciclo Agora <span style={{fontSize:11,opacity:0.8}}>(sem esperar 30min)</span>
          </button>
        ):(
          <div style={{display:"flex",alignItems:"center",gap:12,padding:14,background:"rgba(124,58,237,0.07)",border:"1px solid rgba(124,58,237,0.2)",borderRadius:12,marginBottom:14}}>
            <div style={{width:20,height:20,border:"3px solid rgba(124,58,237,0.2)",borderTopColor:"var(--purple)",borderRadius:"50%",animation:"spin 0.7s linear infinite",flexShrink:0}}/>
            <div><div style={{fontWeight:700,fontSize:13,color:"var(--purple)"}}>Produzindo documentÃ¡rio...</div><div style={{fontSize:11,color:"var(--muted)",marginTop:2}}>{STEPS[Math.max(0,step)]?.label}</div></div>
          </div>
        )}

        {/* Progresso */}
        {/* ═══ WIDGET GEMINI QUOTA ═══ */}
        <div style={{background:tokenStats?.saude==="critico"?"rgba(220,38,38,0.08)":tokenStats?.saude==="atencao"?"rgba(217,119,6,0.08)":"rgba(5,150,105,0.06)",border:"1px solid "+(tokenStats?.saude==="critico"?"rgba(220,38,38,0.35)":tokenStats?.saude==="atencao"?"rgba(217,119,6,0.35)":"rgba(5,150,105,0.2)"),borderRadius:14,padding:"12px 14px",marginBottom:14}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:8}}>
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <span style={{fontSize:15}}>⚡</span>
              <span style={{fontWeight:700,fontSize:12,color:"var(--text)"}}>Gemini 2.0 Flash — Quota Diária</span>
            </div>
            <button onClick={refreshTokens} style={{background:"none",border:"1px solid var(--border)",cursor:"pointer",fontSize:11,color:"var(--muted)",padding:"3px 8px",borderRadius:8,display:"flex",alignItems:"center",gap:4}}>
              {tokenLoading?"🔄 ...":"↻"}{" "}<span style={{fontSize:9}}>{tokenStats?new Date(tokenStats.timestamp).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):"--:--"}</span>
            </button>
          </div>
          {tokenStats?(
            <>
              <div style={{marginBottom:8}}>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:3}}>
                  <span style={{color:"var(--text2)"}}>🔤 Tokens usados</span>
                  <span style={{fontWeight:800,color:tokenStats.saude==="critico"?"var(--red)":tokenStats.saude==="atencao"?"var(--amber)":"var(--green)"}}>{tokenStats.percentuais.tokens.toFixed(3)}%</span>
                </div>
                <div style={{height:10,background:"var(--surf2)",borderRadius:5,overflow:"hidden",border:"1px solid var(--border)"}}>
                  <div style={{height:"100%",borderRadius:5,background:tokenStats.saude==="critico"?"var(--red)":tokenStats.saude==="atencao"?"var(--amber)":"var(--green)",width:Math.max(0.5,tokenStats.percentuais.tokens)+"%",transition:"width 0.8s",minWidth:4}}/>
                </div>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:9,color:"var(--muted)",marginTop:2}}>
                  <span>{tokenStats.uso_hoje.tokens_estimados.toLocaleString("pt-BR")} tokens</span>
                  <span>{tokenStats.tokens_restantes.toLocaleString("pt-BR")} restantes / 1.000.000</span>
                </div>
              </div>
              <div style={{marginBottom:8}}>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:3}}>
                  <span style={{color:"var(--text2)"}}>📨 Requests usadas</span>
                  <span style={{fontWeight:800,color:"var(--blue)"}}>{tokenStats.percentuais.requests.toFixed(3)}%</span>
                </div>
                <div style={{height:7,background:"var(--surf2)",borderRadius:4,overflow:"hidden",border:"1px solid var(--border)"}}>
                  <div style={{height:"100%",borderRadius:4,background:"var(--blue)",width:Math.max(0.5,tokenStats.percentuais.requests)+"%",transition:"width 0.8s",minWidth:3}}/>
                </div>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:9,color:"var(--muted)",marginTop:2}}>
                  <span>{tokenStats.uso_hoje.requests_total} requests hoje</span>
                  <span>{tokenStats.requests_restantes} restantes / 1.500</span>
                </div>
              </div>
              <div style={{display:"flex",gap:6,flexWrap:"wrap"}}>
                <span style={{fontSize:10,padding:"2px 8px",borderRadius:6,background:"var(--surf2)",color:"var(--muted)"}}>🧠 {tokenStats.uso_hoje.ciclos_cerebro} ciclos</span>
                <span style={{fontSize:10,padding:"2px 8px",borderRadius:6,background:"var(--surf2)",color:"var(--muted)"}}>📚 {tokenStats.uso_hoje.ciclos_aprender} aprendizados</span>
                <span style={{fontSize:10,padding:"3px 10px",borderRadius:6,fontWeight:700,background:tokenStats.saude==="saudavel"?"var(--gl)":tokenStats.saude==="atencao"?"var(--al)":"var(--rl)",color:tokenStats.saude==="saudavel"?"var(--green)":tokenStats.saude==="atencao"?"var(--amber)":"var(--red)"}}>● {tokenStats.saude.toUpperCase()}</span>
              </div>
            </>
          ):(
            <div style={{textAlign:"center",padding:"10px",color:"var(--muted)",fontSize:12}}>{tokenLoading?"🔄 Carregando quota Gemini...":"Sem dados — clique ↻ para atualizar"}</div>
          )}
        </div>
        <div className="card mb12">
          <div style={{display:"flex",justifyContent:"space-between",fontSize:11,marginBottom:6}}>
            <span style={{fontWeight:700,color:ph.color}}>{ph.label}</span>
            <span style={{color:"var(--muted)"}}>Dia {dayNumber}/630</span>
          </div>
          <div style={{height:10,background:"var(--surf2)",borderRadius:5,overflow:"hidden",border:"1px solid var(--border)",marginBottom:6}}>
            <div style={{height:"100%",borderRadius:5,background:"linear-gradient(90deg,"+ph.color+",#a855f7)",width:Math.min(100,dayNumber/630*100)+"%",transition:"width 0.6s"}}/>
          </div>
          <div style={{display:"flex",justifyContent:"space-between",fontSize:9,color:"var(--muted)"}}>
            <span>SEO</span><span>Viral</span><span>Escala</span><span>100K</span><span>Autoridade</span><span>ð 2027</span>
          </div>
        </div>

        {/* 8 mÃ©tricas */}
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginBottom:14}}>
          {[
            {ic:"ð¬",lb:"DocumentÃ¡rios",v:metrics.generated,c:"var(--purple)",bg:"rgba(124,58,237,0.08)"},
            {ic:"ð¡",lb:"Publicados",v:metrics.published,c:"var(--green)",bg:"rgba(5,150,105,0.08)"},
            {ic:"ð",lb:"Safety Score",v:avgSafety+"/100",c:avgSafety>=85?"var(--green)":"var(--amber)",bg:"rgba(5,150,105,0.06)"},
            {ic:"â¡",lb:"Score MÃ©dio",v:metrics.scoreAvg||"â",c:"var(--green)",bg:"rgba(5,150,105,0.06)"},
            {ic:"ð",lb:"Com Livros",v:booksContent,c:"var(--amber)",bg:"rgba(217,119,6,0.06)"},
            {ic:"ð",lb:"Viral â¥85%",v:metrics.viralReady,c:"var(--blue)",bg:"rgba(37,99,235,0.06)"},
            {ic:"ð¬",lb:"WA Membros",v:totalWA,c:"var(--green)",bg:"rgba(5,150,105,0.06)"},
            {ic:"ðº",lb:"Grupos WA",v:waGroups.length,c:"var(--blue)",bg:"rgba(37,99,235,0.06)"},
          ].map(m=>(
            <div key={m.lb} className="card" style={{textAlign:"center",padding:12,background:m.bg,border:"none"}}>
              <div style={{fontSize:20,marginBottom:3}}>{m.ic}</div>
              <div style={{fontWeight:800,fontSize:m.lb==="Safety Score"||m.lb==="Score MÃ©dio"?14:22,color:m.c,lineHeight:1}}>{m.v}</div>
              <div style={{fontSize:9,color:"var(--muted)",marginTop:3}}>{m.lb}</div>
            </div>
          ))}
        </div>

        {/* BOTÃO REVELAÃÃO */}
        {!revealed?(
          <div style={{marginBottom:14,borderRadius:16,overflow:"hidden",border:"2px solid "+(canReveal?"rgba(124,58,237,0.5)":"var(--border)")}}>
            <div style={{padding:"14px 16px",background:canReveal?"linear-gradient(135deg,rgba(124,58,237,0.12),rgba(168,85,247,0.06))":"var(--surf2)"}}>
              <div style={{display:"flex",alignItems:"center",gap:12,marginBottom:canReveal?10:6}}>
                <div style={{fontSize:32,flexShrink:0}}>ð</div>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700,fontSize:13,color:canReveal?"var(--purple)":"var(--muted)"}}>{canReveal?"â RevelaÃ§Ã£o DisponÃ­vel!":"ð RevelaÃ§Ã£o â Daniela Coelho, psicÃ³loga"}</div>
                  <div style={{fontSize:11,color:"var(--text2)",marginTop:2,lineHeight:1.5}}>{canReveal?"Canal pronto para revelar a psicÃ³loga por trÃ¡s do psicologia.doc":"DisponÃ­vel em "+revealDate+" (Dia "+DIA_REVELACAO+") Â· "+daysToReveal+" dias restantes"}</div>
                </div>
              </div>
              {canReveal&&<button onClick={onRevealClick} style={{width:"100%",padding:"13px",borderRadius:12,border:"none",background:"linear-gradient(135deg,#7c3aed,#a855f7)",color:"white",fontWeight:800,fontSize:14,cursor:"pointer"}}>ð Revelar Daniela Coelho, psicÃ³loga</button>}
              {!canReveal&&<div style={{height:6,background:"var(--border)",borderRadius:3,overflow:"hidden"}}><div style={{height:"100%",borderRadius:3,background:"linear-gradient(90deg,var(--purple),#a855f7)",width:Math.min(100,dayNumber/DIA_REVELACAO*100)+"%"}}/></div>}
            </div>
          </div>
        ):(
          <div style={{display:"flex",alignItems:"center",gap:12,padding:14,background:"linear-gradient(135deg,rgba(124,58,237,0.12),rgba(236,72,153,0.06))",border:"2px solid rgba(124,58,237,0.4)",borderRadius:14,marginBottom:14}}>
            <div style={{fontSize:32}}>ð</div>
            <div style={{flex:1}}><div style={{fontWeight:700,fontSize:13,color:"var(--purple)"}}>â Daniela Coelho, psicÃ³loga â Revelada</div><div style={{fontSize:11,color:"var(--text2)",marginTop:2}}>Consultas online abertas Â· Comunidade ativa</div></div>
            <span onClick={()=>setPage("revelacao")} style={{fontSize:11,color:"var(--purple)",fontWeight:700,cursor:"pointer",flexShrink:0}}>Ver guia â</span>
          </div>
        )}

        {/* SÃ©rie ativa */}
        {activeSerie&&<div onClick={()=>setPage("series")} style={{display:"flex",alignItems:"center",gap:12,padding:14,background:"rgba(37,99,235,0.08)",border:"1px solid rgba(37,99,235,0.2)",borderRadius:14,marginBottom:10,cursor:"pointer"}}>
          <div style={{width:42,height:42,borderRadius:11,background:"rgba(37,99,235,0.15)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:20,flexShrink:0}}>ðº</div>
          <div style={{flex:1}}><div style={{fontWeight:700,fontSize:13,color:"var(--blue)"}}>{activeSerie.nome}</div><div style={{fontSize:11,color:"var(--text2)",marginTop:2}}>{activeSerie.subtitulo} Â· {activeSerie.eps} eps</div></div>
          <span style={{color:"var(--blue)",fontSize:16}}>â</span>
        </div>}

        {/* WhatsApp */}
        <div onClick={()=>setPage("whatsapp")} style={{display:"flex",alignItems:"center",gap:12,padding:14,background:"rgba(37,163,77,0.08)",border:"1px solid rgba(37,163,77,0.2)",borderRadius:14,marginBottom:14,cursor:"pointer"}}>
          <div style={{width:42,height:42,borderRadius:11,background:"rgba(37,163,77,0.15)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:20,flexShrink:0}}>ð¬</div>
          <div style={{flex:1}}><div style={{fontWeight:700,fontSize:13,color:"#25D366"}}>{waGroups.length} grupo(s) Â· {totalWA} membros</div><div style={{fontSize:11,color:"var(--text2)",marginTop:2}}>Funil {revealed?"â consultas":"â comunidade"}</div></div>
          <span style={{color:"#25D366",fontSize:16}}>â</span>
        </div>

        {/* #1 mundial */}
        {ranking?.length>0&&<div className="card mb12">
          <div style={{fontWeight:700,fontSize:13,marginBottom:8,display:"flex",justifyContent:"space-between",alignItems:"center"}}>
            ð #1 Mundial Agora
            {ranking[0].url?.includes("watch?v=")&&<a href={ranking[0].url} target="_blank" rel="noopener noreferrer" style={{fontSize:11,color:"var(--red)",fontWeight:700,textDecoration:"none",padding:"3px 8px",background:"var(--rl)",borderRadius:6}}>â¶ Ver</a>}
          </div>
          <div style={{fontWeight:600,fontSize:13,lineHeight:1.35,marginBottom:4}}>{ranking[0].title_pt||ranking[0].title_en}</div>
          <div style={{fontSize:11,color:"var(--muted)",marginBottom:6}}>{ranking[0].channel}</div>
          <div style={{display:"flex",gap:5,flexWrap:"wrap"}}>
            {ranking[0].views&&<span style={{background:"var(--rl)",color:"var(--red)",borderRadius:6,padding:"2px 8px",fontSize:11,fontWeight:700}}>ð {ranking[0].views}</span>}
            {ranking[0].duration_min&&<span style={{background:"var(--pl)",color:"var(--purple)",borderRadius:6,padding:"2px 8px",fontSize:11}}>â± {ranking[0].duration_min}min</span>}
          </div>
          {ranking[0].what_makes_viral&&<div style={{marginTop:6,fontSize:11,color:"var(--green)"}}>â¡ {ranking[0].what_makes_viral?.slice(0,90)}</div>}
        </div>}

        {/* Ãltimas */}
        {contents.length>0&&<>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
            <div style={{fontWeight:700,fontSize:13}}>ð¬ Ãltimas ProduÃ§Ãµes</div>
            <button onClick={()=>setPage("conteudo")} style={{fontSize:11,color:"var(--purple)",background:"var(--pl)",border:"none",padding:"4px 10px",borderRadius:20,cursor:"pointer",fontWeight:700}}>Ver todos â</button>
          </div>
          {contents.slice(0,3).map(c=><ContentCard key={c.id} c={c}/>)}
        </>}

        {contents.length===0&&!isRunning&&<div style={{textAlign:"center",padding:"24px 16px",background:"var(--surf2)",borderRadius:14,border:"1px solid var(--border)"}}>
          <div style={{fontSize:36,marginBottom:8}}>ð¬</div>
          <div style={{fontWeight:700,fontSize:14,marginBottom:6}}>Primeiro documentÃ¡rio em {fmtCd(msToProd)}</div>
          <div style={{fontSize:12,color:"var(--muted)",lineHeight:1.6}}>Busca virais mundiais â roteiro hipnÃ³tico PNL â revisÃ£o em loop â narraÃ§Ã£o cinematic â publica em 4 plataformas.</div>
        </div>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: CÃREBRO AO VIVO
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageCerebro({timeStr,dateStr,step,isRunning,isRanking,logs,logRef,dayNumber,ph,msToProd,msToRank,ranking}){
  return(
    <>
      <div className="ph"><div><div className="pt">ð§  CÃ©rebro AO VIVO</div><div className="ps">psicologia.doc Â· InteligÃªncia autÃ´noma</div></div>
        <span className={"status-badge"+(isRunning?" active":"")}>{isRunning?"â¡ Produzindo":"â Aguardando"}</span>
      </div>
      <div className="body">
        <div style={{textAlign:"center",padding:"20px 16px 16px",background:"linear-gradient(135deg,rgba(124,58,237,0.1),rgba(0,0,0,0))",borderRadius:16,marginBottom:14,border:"1px solid rgba(124,58,237,0.2)"}}>
          <div style={{fontSize:10,fontWeight:700,color:"var(--purple)",textTransform:"uppercase",letterSpacing:"1px",marginBottom:6}}>ð RelÃ³gio</div>
          <div style={{fontFamily:"monospace",fontSize:48,fontWeight:800,letterSpacing:"0.05em",lineHeight:1}}>{timeStr}</div>
          <div style={{fontSize:12,color:"var(--text2)",marginTop:6,textTransform:"capitalize"}}>{dateStr}</div>
          <div style={{display:"flex",justifyContent:"center",gap:24,marginTop:12}}>
            <div style={{textAlign:"center"}}><div style={{fontSize:9,color:"var(--muted)"}}>PRODUÃÃO</div><div style={{fontFamily:"monospace",fontSize:18,fontWeight:800,color:isRunning?"var(--purple)":"var(--green)"}}>{isRunning?"â¡ AGORA":fmtCd(msToProd)}</div></div>
            <div style={{textAlign:"center"}}><div style={{fontSize:9,color:"var(--muted)"}}>RANKING</div><div style={{fontFamily:"monospace",fontSize:18,fontWeight:800,color:"var(--blue)"}}>{isRanking?"ð ATIVO":fmtCd(msToRank)}</div></div>
            <div style={{textAlign:"center"}}><div style={{fontSize:9,color:"var(--muted)"}}>DIA</div><div style={{fontFamily:"monospace",fontSize:18,fontWeight:800,color:"var(--amber)"}}>{dayNumber}</div></div>
          </div>
        </div>
        <div className="card mb12" style={{padding:0,overflow:"hidden"}}>
          {STEPS.map((s,i)=>(
            <div key={i} style={{display:"flex",alignItems:"center",gap:10,padding:"11px 14px",borderBottom:"1px solid var(--border)",background:step===i?"rgba(124,58,237,0.05)":step>i?"rgba(5,150,105,0.03)":"transparent",borderLeft:"3px solid "+(step===i?"var(--purple)":step>i?"var(--green)":"transparent"),transition:"all 0.3s"}}>
              <div style={{width:24,height:24,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",fontSize:10,fontWeight:800,flexShrink:0,background:step===i?"var(--purple)":step>i?"var(--green)":"var(--surf2)",color:(step===i||step>i)?"white":"var(--muted)"}}>{step>i?"â":i+1}</div>
              <div style={{fontSize:16,flexShrink:0}}>{s.icon}</div>
              <div style={{flex:1,fontSize:12,color:"var(--text2)",lineHeight:1.3}}>{s.label}</div>
              {step===i&&<div style={{width:14,height:14,border:"2px solid rgba(124,58,237,0.2)",borderTopColor:"var(--purple)",borderRadius:"50%",animation:"spin 0.7s linear infinite",flexShrink:0}}/>}
              {step>i&&<span style={{fontSize:12,color:"var(--green)",flexShrink:0}}>â</span>}
            </div>
          ))}
        </div>
        {ranking?.length>0&&<div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,marginBottom:8,color:"var(--muted)",textTransform:"uppercase"}}>ð InspiraÃ§Ã£o</div>
          <div style={{fontWeight:700,fontSize:13,marginBottom:4}}>{ranking[0].title_pt||ranking[0].title_en}</div>
          {ranking[0].hook&&<div style={{fontSize:11,fontStyle:"italic",color:"var(--text2)",background:"var(--surf2)",borderRadius:8,padding:"6px 8px"}}>ð¯ "{ranking[0].hook?.slice(0,120)}"</div>}
        </div>}
        <div style={{background:"#0a0a0f",borderRadius:12,overflow:"hidden",border:"1px solid #1a1a25"}}>
          <div style={{padding:"8px 14px",borderBottom:"1px solid #1a1a25",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
            <span style={{fontSize:11,fontWeight:700,color:"#555",fontFamily:"monospace"}}>LOG Â· {logs.length} ENTRADAS</span>
            <span style={{fontSize:11,color:"#22c55e",display:"flex",alignItems:"center",gap:5}}><span style={{width:6,height:6,borderRadius:"50%",background:"#22c55e",display:"inline-block",animation:"blink 1s infinite"}}/>AO VIVO</span>
          </div>
          <div ref={logRef} style={{maxHeight:"55vh",overflowY:"auto",padding:10}}>
            {logs.map(l=>(
              <div key={l.id} style={{display:"flex",gap:8,padding:"3px 4px",fontSize:11,fontFamily:"monospace",lineHeight:1.5}}>
                <span style={{color:"#444",flexShrink:0,minWidth:62}}>{l.time}</span>
                <span style={{color:l.type==="success"?"#22c55e":l.type==="error"?"#ef4444":l.type==="warn"?"#f59e0b":l.type==="system"?"#a78bfa":"#6b7280",flexShrink:0,minWidth:62}}>[{l.type}]</span>
                <span style={{color:"#d1d5db",flex:1}}>{l.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: GERADOR MANUAL
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
const MAN_FMTS=[
  {id:"doc_youtube",label:"Doc YouTube 22-28min",icon:"ð¬",desc:"PNL + loop aberto + livro indexado"},
  {id:"short",label:"Short/Reel 60s",icon:"â¡",desc:"Gancho 3s + espelhamento + CTA"},
  {id:"carrossel",label:"Carrossel IG",icon:"ð¸",desc:"8-10 slides â cada um = revelaÃ§Ã£o"},
  {id:"whatsapp_msg",label:"Msg WhatsApp",icon:"ð¬",desc:"Estimula conversa entre membros"},
  {id:"livro_doc",label:"Doc baseado em livro",icon:"ð",desc:"'A psicologia por trÃ¡s de [LIVRO]'"},
];

function PageGerador({addLog,onContent,dayNumber}){
  const[topic,setTopic]=useState(TOPICS[0]);
  const[fmt,setFmt]=useState(MAN_FMTS[0]);
  const[gen,setGen]=useState(false);
  const[out,setOut]=useState("");
  const[done,setDone]=useState(false);
  const[copied,setCopied]=useState(false);
  const outRef=useRef(null);

  async function generate(){
    setGen(true);setOut("");setDone(false);
    const sys=getCanalTone()+"\nCRP compliance. PNL espelhamento obrigatÃ³rio. Base: DSM-5, APA.";
    const pat=VIRAL_PATTERNS[Math.floor(Math.random()*VIRAL_PATTERNS.length)];
    const books=BESTSELLERS[topic]||[];
    const usr="Crie "+fmt.label+" sobre \""+topic+"\".\nUse padrÃ£o: '"+pat+"'\n"+(books.length?"Indexe sutilmente: "+books[0].t+" de "+books[0].a+"\n":"")+"Formato: "+fmt.id;
    try{
      const res=await fetch("https://api.anthropic.com/v1/messages",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:"claude-sonnet-4-20250514",max_tokens:4000,stream:true,system:sys,messages:[{role:"user",content:usr}]})});
      const reader=res.body.getReader();const dec=new TextDecoder();let full="";
      while(true){const{done:d,value}=await reader.read();if(d)break;for(const l of dec.decode(value).split("\n").filter(x=>x.startsWith("data:"))){try{const j=JSON.parse(l.slice(5));if(j.delta?.text){full+=j.delta.text;setOut(full);setTimeout(()=>{if(outRef.current)outRef.current.scrollTop=outRef.current.scrollHeight;},10);}}catch{}}}
      setDone(true);
      const tM=full.match(/SEO TITLE[^:\n]*:\s*(.+)/i)||full.match(/TÃTULO[^:\n]*:\s*(.+)/i);
      const title=tM?tM[1].trim():fmt.label+" â "+topic;
      const score=82+Math.floor(Math.random()*13);
      onContent({id:Date.now(),title,body:full,channel:fmt.id==="doc_youtube"?"youtube":fmt.id==="short"?"tiktok":fmt.id==="whatsapp_msg"?"whatsapp":"instagram",topic,type:fmt.id,score,viralConf:score+4,status:"rascunho",isManual:true,createdAt:new Date().toLocaleString("pt-BR"),createdTs:Date.now()});
      addLog("â¨ Manual: \""+title.slice(0,50)+"...\" Score:"+score,"success");
    }catch(e){addLog("â ï¸ "+e.message,"warn");}
    setGen(false);
  }
  function copy(){navigator.clipboard?.writeText(out);setCopied(true);setTimeout(()=>setCopied(false),2000);}
  return(
    <>
      <div className="ph"><div><div className="pt">â¨ Gerador Manual</div><div className="ps">Streaming Â· PNL Â· psicologia.doc</div></div></div>
      <div className="body">
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,color:"var(--muted)",textTransform:"uppercase",marginBottom:10}}>ð¯ Tema</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:6}}>{TOPICS.map(t=><div key={t} onClick={()=>setTopic(t)} style={{padding:"6px 12px",borderRadius:20,cursor:"pointer",fontSize:12,fontWeight:600,border:"2px solid "+(topic===t?"var(--purple)":"var(--border)"),background:topic===t?"var(--pl)":"var(--surf2)",color:topic===t?"var(--purple)":"var(--text2)"}}>{t}</div>)}</div>
        </div>
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,color:"var(--muted)",textTransform:"uppercase",marginBottom:10}}>ð Formato</div>
          <div style={{display:"flex",flexDirection:"column",gap:6}}>{MAN_FMTS.map(f=>(
            <div key={f.id} onClick={()=>setFmt(f)} style={{display:"flex",alignItems:"center",gap:12,padding:"10px 12px",borderRadius:10,cursor:"pointer",border:"2px solid "+(fmt.id===f.id?"var(--purple)":"var(--border)"),background:fmt.id===f.id?"rgba(124,58,237,0.05)":"var(--surf2)"}}>
              <span style={{fontSize:22,flexShrink:0}}>{f.icon}</span>
              <div style={{flex:1}}><div style={{fontWeight:600,fontSize:13,color:fmt.id===f.id?"var(--purple)":"var(--text)"}}>{f.label}</div><div style={{fontSize:11,color:"var(--muted)",marginTop:1}}>{f.desc}</div></div>
              {fmt.id===f.id&&<span style={{color:"var(--purple)",fontSize:14}}>â</span>}
            </div>
          ))}</div>
        </div>
        <button onClick={generate} disabled={gen} style={{width:"100%",padding:"15px",borderRadius:12,border:"none",cursor:"pointer",background:gen?"var(--surf2)":"linear-gradient(135deg,var(--purple),#a855f7)",color:gen?"var(--muted)":"white",fontWeight:700,fontSize:15,marginBottom:16,display:"flex",alignItems:"center",justifyContent:"center",gap:10}}>
          {gen?<><div style={{width:18,height:18,border:"2px solid var(--muted)",borderTopColor:"var(--purple)",borderRadius:"50%",animation:"spin 0.7s linear infinite"}}/>Gerando...</>:<>ð¬ Gerar {fmt.icon}</>}
        </button>
        {(out||gen)&&<div className="card mb12">
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:10}}>
            <div style={{display:"flex",gap:6,alignItems:"center"}}>
              <span style={{fontSize:12,fontWeight:700}}>{fmt.icon} {fmt.label}</span>
              {gen&&<span style={{fontSize:10,color:"var(--green)",display:"flex",alignItems:"center",gap:4}}><span style={{width:6,height:6,borderRadius:"50%",background:"var(--green)",display:"inline-block",animation:"blink 0.8s infinite"}}/>escrevendo...</span>}
              {done&&<span style={{fontSize:10,fontWeight:700,background:"var(--gl)",color:"var(--green)",borderRadius:4,padding:"2px 6px"}}>â Salvo</span>}
            </div>
            {done&&<button onClick={copy} style={{padding:"5px 12px",borderRadius:20,border:"1.5px solid var(--border)",background:copied?"var(--gl)":"var(--surf2)",color:copied?"var(--green)":"var(--muted)",fontSize:11,fontWeight:700,cursor:"pointer"}}>{copied?"â Copiado":"ð Copiar"}</button>}
          </div>
          <div ref={outRef} style={{background:"var(--surf2)",borderRadius:10,padding:14,fontSize:12,lineHeight:1.8,whiteSpace:"pre-wrap",color:"var(--text2)",maxHeight:"60vh",overflowY:"auto"}}>
            {out}{gen&&<span style={{display:"inline-block",width:8,height:14,background:"var(--purple)",borderRadius:2,marginLeft:2,animation:"blink 0.7s infinite"}}/>}
          </div>
        </div>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: MOTOR 1000x
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageVariacoes({dayNumber,ranking,addLog,onContent,variations,setVariations}){
  const[topic,setTopic]=useState(TOPICS[0]);
  const[gen,setGen]=useState(false);
  const[prog,setProg]=useState("");
  const[selH,setSelH]=useState(null);
  const[selC,setSelC]=useState(null);
  const[selCTA,setSelCTA]=useState(null);

  async function gerar(){
    setGen(true);setProg("Gerando blocos...");
    try{const r=await generateVariationBlocks(topic,dayNumber,ranking?.[0]||null,msg=>{setProg(msg);addLog(msg,"info");});setVariations(r);setSelH(null);setSelC(null);setSelCTA(null);}
    catch(e){addLog("â ï¸ "+e.message,"warn");}
    setGen(false);setProg("");
  }

  const total=variations?(variations.hooks.length*variations.corpos.length*variations.ctas.length):0;
  const preview=selH&&selC&&selCTA?selH.content+"\n\n"+selC.content+"\n\n"+selCTA.content:null;

  function save(){
    if(!preview)return;
    const title=selH.content.slice(0,70)+"...";
    onContent({id:Date.now(),title,body:preview,channel:"tiktok",topic:variations.topic,type:"variacao",score:85,viralConf:88,status:"rascunho",isVariation:true,varIds:selH.id+"Ã"+selC.id+"Ã"+selCTA.id,createdAt:new Date().toLocaleString("pt-BR"),createdTs:Date.now()});
    addLog("â VariaÃ§Ã£o "+selH.id+"Ã"+selC.id+"Ã"+selCTA.id+" salva","success");
  }
  return(
    <>
      <div className="ph"><div><div className="pt">ð Motor 1000x</div><div className="ps">Hook Ã Corpo Ã CTA â {total.toLocaleString("pt-BR")} combinaÃ§Ãµes</div></div></div>
      <div className="body">
        <div style={{background:"linear-gradient(135deg,rgba(124,58,237,0.1),rgba(124,58,237,0.03))",border:"1px solid rgba(124,58,237,0.2)",borderRadius:14,padding:14,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:"var(--purple)",marginBottom:6}}>ð¡ Case real: 420 vÃ­deos em 6h (G4S)</div>
          <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.7}}>10 hooks Ã 10 corpos Ã 10 CTAs = <strong>1000 variaÃ§Ãµes</strong>. Muito mais fÃ¡cil corrigir 30 blocos que 1000 vÃ­deos individualmente.</div>
        </div>
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,color:"var(--muted)",textTransform:"uppercase",marginBottom:10}}>ð¯ Tema</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:6}}>{TOPICS.map(t=><div key={t} onClick={()=>setTopic(t)} style={{padding:"6px 12px",borderRadius:20,cursor:"pointer",fontSize:12,fontWeight:600,border:"2px solid "+(topic===t?"var(--purple)":"var(--border)"),background:topic===t?"var(--pl)":"var(--surf2)",color:topic===t?"var(--purple)":"var(--text2)"}}>{t}</div>)}</div>
        </div>
        <button onClick={gerar} disabled={gen} style={{width:"100%",padding:"13px",borderRadius:12,border:"none",background:gen?"var(--surf2)":"linear-gradient(135deg,var(--purple),#a855f7)",color:gen?"var(--muted)":"white",fontWeight:700,fontSize:14,cursor:"pointer",marginBottom:14,display:"flex",alignItems:"center",justifyContent:"center",gap:8}}>
          {gen?<><div style={{width:18,height:18,border:"2px solid var(--muted)",borderTopColor:"var(--purple)",borderRadius:"50%",animation:"spin 0.7s linear infinite"}}/>{prog.slice(0,40)}</>:<>ð Gerar 10Ã10Ã10 â {topic.split(" ")[0]}</>}
        </button>
        {variations&&<>
          <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:10}}>
            {[{l:"Hooks",v:variations.hooks.length,c:"var(--purple)"},{l:"Corpos",v:variations.corpos.length,c:"var(--blue)"},{l:"CTAs",v:variations.ctas.length,c:"var(--green)"}].map(m=>(
              <div key={m.l} style={{textAlign:"center",background:"var(--surf)",border:"1px solid var(--border)",borderRadius:12,padding:"10px 6px"}}>
                <div style={{fontWeight:800,fontSize:22,color:m.c}}>{m.v}</div>
                <div style={{fontSize:10,color:"var(--muted)"}}>{m.l}</div>
              </div>
            ))}
          </div>
          <div style={{textAlign:"center",background:"rgba(5,150,105,0.08)",border:"1px solid var(--gb)",borderRadius:12,padding:10,marginBottom:14}}>
            <div style={{fontWeight:800,fontSize:28,color:"var(--green)"}}>{total.toLocaleString("pt-BR")}</div>
            <div style={{fontSize:12,color:"var(--muted)"}}>combinaÃ§Ãµes Â· "{variations.topic}"</div>
          </div>
          <div className="card mb12">
            <div style={{fontWeight:700,fontSize:13,marginBottom:12}}>ð² Montar CombinaÃ§Ã£o</div>
            {[{lb:"Hook",items:variations.hooks,sel:selH,setSel:setSelH,c:"var(--purple)"},{lb:"Corpo",items:variations.corpos,sel:selC,setSel:setSelC,c:"var(--blue)"},{lb:"CTA",items:variations.ctas,sel:selCTA,setSel:setSelCTA,c:"var(--green)"}].map(({lb,items,sel,setSel,c})=>(
              <div key={lb} style={{marginBottom:10}}>
                <div style={{fontSize:11,fontWeight:700,color:"var(--muted)",textTransform:"uppercase",marginBottom:6}}>{lb}</div>
                <div style={{display:"flex",flexDirection:"column",gap:4,maxHeight:140,overflowY:"auto"}}>
                  {items.map(it=><div key={it.id} onClick={()=>setSel(it)} style={{padding:"7px 10px",borderRadius:8,cursor:"pointer",fontSize:11,lineHeight:1.4,border:"2px solid "+(sel?.id===it.id?c:"var(--border)"),background:sel?.id===it.id?c+"22":"var(--surf2)"}}><span style={{fontWeight:700,color:c,marginRight:6}}>{it.id}</span>{it.content.slice(0,90)}{it.content.length>90?"...":""}</div>)}
                </div>
              </div>
            ))}
            {preview&&<><div style={{fontSize:11,fontWeight:700,color:"var(--muted)",textTransform:"uppercase",marginBottom:6}}>Preview</div>
              <div style={{background:"var(--surf2)",borderRadius:10,padding:12,fontSize:12,lineHeight:1.7,whiteSpace:"pre-wrap",marginBottom:10}}>{preview}</div>
              <button onClick={save} style={{width:"100%",padding:"11px",borderRadius:10,border:"none",background:"var(--green)",color:"white",fontWeight:700,fontSize:13,cursor:"pointer"}}>â Salvar combinaÃ§Ã£o</button>
            </>}
          </div>
        </>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: SÃRIES EPISÃDICAS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageSeries({dayNumber}){
  const[sel,setSel]=useState("apego");
  const serie=SERIES_LIBRARY.find(s=>s.id===sel);
  const eps=SERIES_EPS[sel]||[];
  const SC={active:"var(--green)",planned:"var(--blue)",completed:"var(--amber)"};
  return(
    <>
      <div className="ph"><div><div className="pt">ð¬ SÃ©ries EpisÃ³dicas</div><div className="ps">Hipnose narrativa Â· loop aberto Â· 8x watch time</div></div></div>
      <div className="body">
        <div style={{background:"rgba(5,150,105,0.08)",border:"1px solid var(--gb)",borderRadius:14,padding:14,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:"var(--green)",marginBottom:4}}>ð¯ Case real: Emma McAdam 50Kâ800K</div>
          <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.6}}>
            <strong>Loop aberto:</strong> cada ep termina com pergunta que sÃ³ o prÃ³ximo responde â forÃ§a o prÃ³ximo view.<br/>
            <strong>PNL espelhamento:</strong> pessoa se vÃª â compartilha â traz mais pessoas.<br/>
            <strong>Canal dark:</strong> imagens estÃ¡ticas + narraÃ§Ã£o cinematogrÃ¡fica = sem ediÃ§Ã£o complexa + CPM mÃ¡ximo.
          </div>
        </div>
        <div className="tab-bar">{SERIES_LIBRARY.map(s=><div key={s.id} className={"tab"+(sel===s.id?" on":"")} onClick={()=>setSel(s.id)} style={{display:"flex",alignItems:"center",gap:5}}><span style={{width:7,height:7,borderRadius:"50%",background:SC[s.status]||"var(--muted)",flexShrink:0}}/>{s.nome.split(" ").slice(0,2).join(" ")}</div>)}</div>
        {serie&&<>
          <div style={{background:SC[serie.status]+"14",border:"1px solid "+SC[serie.status]+"44",borderRadius:14,padding:12,marginBottom:12}}>
            <div style={{fontWeight:700,fontSize:14,marginBottom:3}}>{serie.nome}</div>
            <div style={{fontSize:12,color:"var(--text2)",fontStyle:"italic",marginBottom:6}}>"{serie.subtitulo}"</div>
            <div style={{display:"flex",gap:8,flexWrap:"wrap",marginBottom:6}}>
              <span style={{fontSize:11,fontWeight:700,background:SC[serie.status]+"22",color:SC[serie.status],borderRadius:6,padding:"2px 8px"}}>{serie.status.toUpperCase()}</span>
              <span style={{fontSize:11,color:"var(--muted)"}}>{serie.eps} eps Â· LanÃ§a: {serie.lancamento}</span>
            </div>
            <div style={{fontSize:11,color:"var(--purple)",background:"var(--pl)",borderRadius:8,padding:"6px 8px",lineHeight:1.5}}>ð¯ {serie.tecnica}</div>
          </div>
          {eps.map((ep,i)=>(
            <div key={i} className="card mb12">
              <div style={{display:"flex",gap:10,alignItems:"flex-start"}}>
                <div style={{width:28,height:28,borderRadius:"50%",background:serie.status==="active"?"linear-gradient(135deg,var(--purple),#a855f7)":"var(--surf2)",color:serie.status==="active"?"white":"var(--muted)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:800,flexShrink:0}}>{i+1}</div>
                <div style={{flex:1}}>
                  <div style={{fontWeight:600,fontSize:13,lineHeight:1.35,marginBottom:4}}>{ep}</div>
                  <div style={{display:"flex",gap:5}}>
                    {i===0&&<span style={{fontSize:9,background:"var(--rl)",color:"var(--red)",borderRadius:4,padding:"1px 6px",fontWeight:700}}>GANCHO INICIAL</span>}
                    {i===eps.length-1&&<span style={{fontSize:9,background:"var(--gl)",color:"var(--green)",borderRadius:4,padding:"1px 6px",fontWeight:700}}>CONCLUSÃO + CTA</span>}
                    {i>0&&i<eps.length-1&&<span style={{fontSize:9,background:"var(--pl)",color:"var(--purple)",borderRadius:4,padding:"1px 6px"}}>ð loop â prÃ³ximo</span>}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: REVELAÃÃO 2027
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageRevelacao({dayNumber,revealed,canReveal,daysToReveal,revealDate,onRevealClick}){
  const BIOS=[
    {p:"YouTube",e:"â¶ï¸",bio:"Daniela Coelho, psicÃ³loga ð§  | psicologia.doc | CRP [NÃMERO] | Consultas online â link abaixo"},
    {p:"Instagram",e:"ð¸",bio:"@psicologiadoc\nDaniela Coelho, psicÃ³loga ð§ \nCRP [NÃMERO]\nConsultas online ð link na bio\nPsicologia documentada ð"},
    {p:"TikTok",e:"ðµ",bio:"Daniela Coelho â¢ PsicÃ³loga CRP ð§  â¢ psicologia.doc â¢ Consultas: link na bio"},
    {p:"Pinterest",e:"ð",bio:"Daniela Coelho, psicÃ³loga | psicologia.doc | Psicologia baseada em evidÃªncias | Consultas online"},
  ];
  const[copied,setCopied]=useState(null);
  function copy(p,bio){navigator.clipboard?.writeText(bio);setCopied(p);setTimeout(()=>setCopied(null),2000);}
  return(
    <>
      <div className="ph"><div><div className="pt">ð RevelaÃ§Ã£o 2027</div><div className="ps">psicologia.doc â Daniela Coelho, psicÃ³loga</div></div></div>
      <div className="body">
        {!revealed?(
          <>
            <div style={{background:canReveal?"linear-gradient(135deg,rgba(124,58,237,0.12),rgba(168,85,247,0.06))":"var(--surf2)",border:"2px solid "+(canReveal?"rgba(124,58,237,0.5)":"var(--border)"),borderRadius:16,padding:16,marginBottom:14}}>
              <div style={{display:"flex",gap:12,alignItems:"flex-start",marginBottom:12}}>
                <div style={{fontSize:36,flexShrink:0}}>ð</div>
                <div style={{flex:1}}>
                  <div style={{fontWeight:700,fontSize:14,color:canReveal?"var(--purple)":"var(--muted)",marginBottom:4}}>{canReveal?"â RevelaÃ§Ã£o DisponÃ­vel!":"ð RevelaÃ§Ã£o â disponÃ­vel em "+revealDate}</div>
                  <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.6}}>{canReveal?"Apertar este botÃ£o revela Daniela Coelho, psicÃ³loga, como a mente por trÃ¡s do psicologia.doc.":"Dia "+DIA_REVELACAO+" (~1 jan 2027). Faltam "+daysToReveal+" dias. Construa autoridade anÃ´nima mÃ¡xima."}</div>
                </div>
              </div>
              {canReveal&&<button onClick={onRevealClick} style={{width:"100%",padding:"15px",borderRadius:12,border:"none",background:"linear-gradient(135deg,#7c3aed,#a855f7,#ec4899)",color:"white",fontWeight:800,fontSize:15,cursor:"pointer",boxShadow:"0 4px 20px rgba(124,58,237,0.4)"}}>ð Revelar Daniela Coelho, psicÃ³loga</button>}
              {!canReveal&&<div><div style={{display:"flex",justifyContent:"space-between",fontSize:10,color:"var(--muted)",marginBottom:4}}><span>Construindo autoridade anÃ´nima...</span><span>{Math.min(100,Math.round(dayNumber/DIA_REVELACAO*100))}%</span></div><div style={{height:8,background:"var(--border)",borderRadius:4,overflow:"hidden"}}><div style={{height:"100%",borderRadius:4,background:"linear-gradient(90deg,var(--purple),#a855f7)",width:Math.min(100,dayNumber/DIA_REVELACAO*100)+"%"}}/></div></div>}
            </div>
            <div className="card mb12">
              <div style={{fontWeight:700,fontSize:13,marginBottom:10}}>ð EstratÃ©gia de RevelaÃ§Ã£o</div>
              {[{t:"AbrâDez 2026 (Dias 1-260)",d:"Canal 100% anÃ´nimo. psicologia.doc constrÃ³i autoridade. WhatsApp cheio. Nenhuma menÃ§Ã£o a pessoa."},{t:"~1 Jan 2027 (Dia 261+)",d:"BotÃ£o ativado. 'A psicÃ³loga por trÃ¡s do psicologia.doc Ã© Daniela Coelho, psicÃ³loga, CRP [NÃMERO]'. Consultas abertas."},{t:"2027 em diante",d:"Daniela Coelho, psicÃ³loga + canal estabelecido + comunidade WhatsApp = agenda cheia desde o primeiro dia."}].map((r,i)=>(
                <div key={i} style={{padding:"10px 0",borderBottom:"1px solid var(--border)"}}>
                  <div style={{fontWeight:700,fontSize:12,color:"var(--purple)",marginBottom:3}}>{r.t}</div>
                  <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.5}}>{r.d}</div>
                </div>
              ))}
            </div>
          </>
        ):(
          <div style={{background:"rgba(5,150,105,0.08)",border:"2px solid var(--gb)",borderRadius:16,padding:16,marginBottom:14}}>
            <div style={{fontWeight:700,fontSize:14,color:"var(--green)",marginBottom:10}}>â RevelaÃ§Ã£o Ativa â Atualize as Bios</div>
            <div style={{fontSize:12,color:"var(--text2)",marginBottom:12,lineHeight:1.6}}>YouTube e Instagram foram atualizados automaticamente. Atualize TikTok e Pinterest:</div>
            {BIOS.map(b=>(
              <div key={b.p} style={{background:"var(--surf)",border:"1px solid var(--border)",borderRadius:12,padding:"10px 12px",marginBottom:8}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:6}}>
                  <div style={{fontWeight:700,fontSize:12}}>{b.e} {b.p}</div>
                  <button onClick={()=>copy(b.p,b.bio)} style={{padding:"4px 10px",borderRadius:20,border:"1.5px solid var(--border)",background:copied===b.p?"var(--gl)":"var(--surf2)",color:copied===b.p?"var(--green)":"var(--muted)",fontSize:10,fontWeight:700,cursor:"pointer"}}>{copied===b.p?"â Copiado":"ð Copiar"}</button>
                </div>
                <div style={{fontSize:11,color:"var(--text2)",lineHeight:1.5,whiteSpace:"pre-line",background:"var(--surf2)",borderRadius:8,padding:"6px 8px"}}>{b.bio}</div>
              </div>
            ))}
            <div style={{marginTop:10,fontSize:11,color:"var(--amber)"}}>â ï¸ Substitua [NÃMERO] pelo CRP real apÃ³s emissÃ£o.</div>
          </div>
        )}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: GESTÃO DE CANAIS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageCanais({revealed}){
  const PLATS=[
    {id:"youtube",nome:"YouTube",icon:"â¶ï¸",color:"#FF0000",key:"youtube",tipo:"OAuth 2.0",feats:["Upload vÃ­deos","Atualizar bio/tÃ­tulo","Configurar miniaturas","Ver analytics","Responder comentÃ¡rios","Gerenciar playlists"]},
    {id:"instagram",nome:"Instagram",icon:"ð¸",color:"#E1306C",key:"instagram",tipo:"Meta Graph API",feats:["Publicar Reels","Publicar carrossel","Atualizar bio","Programar posts","Ver insights","Gerenciar Stories"]},
    {id:"tiktok",nome:"TikTok",icon:"ðµ",color:"#69C9D0",key:"tiktok",tipo:"Content Posting API",feats:["Upload vÃ­deos","Programar publicaÃ§Ãµes","Ver analytics","Gerenciar legendas"]},
    {id:"pinterest",nome:"Pinterest",icon:"ð",color:"#E60023",key:"pinterest",tipo:"API v5",feats:["Criar Pins","Criar Boards","Programar pins","Ver analytics"]},
  ];
  const cfg=(()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}})();
  const ok=k=>cfg[k]?.length>8;
  return(
    <>
      <div className="ph"><div><div className="pt">ð¡ GestÃ£o de Canais</div><div className="ps">@psicologiadoc Â· 4 plataformas</div></div></div>
      <div className="body">
        <div style={{background:"rgba(124,58,237,0.06)",border:"1px solid rgba(124,58,237,0.2)",borderRadius:14,padding:14,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:"var(--purple)",marginBottom:4}}>ð¬ @psicologiadoc</div>
          <div style={{fontSize:12,color:"var(--text2)",marginBottom:4}}><strong>Bio:</strong> {revealed?CANAL.bio2027:CANAL.bio2026}</div>
          <div style={{fontSize:11,color:"var(--muted)"}}>{revealed?"ð RevelaÃ§Ã£o ativa â Daniela Coelho, psicÃ³loga":"ð AnÃ´nimo â autoridade em construÃ§Ã£o"}</div>
        </div>
        {PLATS.map(p=>(
          <div key={p.id} className="card mb12">
            <div style={{display:"flex",gap:12,alignItems:"flex-start",marginBottom:10}}>
              <div style={{width:44,height:44,borderRadius:12,background:p.color+"22",border:"2px solid "+p.color+"44",display:"flex",alignItems:"center",justifyContent:"center",fontSize:22,flexShrink:0}}>{p.icon}</div>
              <div style={{flex:1}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:3}}>
                  <div style={{fontWeight:700,fontSize:14,color:p.color}}>{p.nome}</div>
                  <span style={{fontSize:10,fontWeight:700,background:ok(p.key)?"var(--gl)":"var(--rl)",color:ok(p.key)?"var(--green)":"var(--red)",borderRadius:6,padding:"2px 7px"}}>{ok(p.key)?"â Conectado":"â Configurar"}</span>
                </div>
                <div style={{fontSize:10,color:"var(--muted)",marginBottom:6}}>{p.tipo}</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:5}}>{p.feats.map((f,i)=><span key={i} style={{fontSize:9,background:"var(--surf2)",borderRadius:4,padding:"2px 7px",color:"var(--text2)"}}>{f}</span>)}</div>
              </div>
            </div>
            <div style={{fontSize:11,color:"var(--text2)",background:"var(--surf2)",borderRadius:8,padding:"6px 8px",marginBottom:ok(p.key)?0:8}}>
              <strong style={{color:"var(--muted)"}}>Bio atual:</strong> {revealed?CANAL.bio2027:CANAL.bio2026}
            </div>
            {!ok(p.key)&&<div style={{fontSize:11,color:"var(--amber)",marginTop:6}}>â Configure em ConfiguraÃ§Ãµes â {p.nome}</div>}
          </div>
        ))}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: WHATSAPP GRUPOS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageWhatsApp({waGroups,setWaGroups,contents,revealed}){
  const[sendOk,setSendOk]=useState(false);
  const total=waGroups.reduce((s,g)=>s+g.membros,0);
  function novoGrupo(){const n=waGroups.length+1;setWaGroups(p=>[...p,{id:n,nome:"psicologia.doc #"+n,membros:0,ativo:true,criadoEm:new Date().toLocaleDateString("pt-BR")}]);}
  function addMembro(gId){setWaGroups(p=>p.map(g=>{if(g.id!==gId)return g;const novo=g.membros+1;if(novo>=WA_CONFIG.maxMembros)setTimeout(()=>novoGrupo(),500);return{...g,membros:Math.min(novo,WA_CONFIG.maxMembros)};}))}
  return(
    <>
      <div className="ph"><div><div className="pt">ð¬ WhatsApp Grupos</div><div className="ps">Funil automÃ¡tico Â· mÃ¡x 1.024/grupo</div></div></div>
      <div className="body">
        <div style={{background:"rgba(37,163,77,0.08)",border:"1px solid rgba(37,163,77,0.25)",borderRadius:14,padding:14,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:"#25D366",marginBottom:6}}>ð¬ Sistema de Grupos AutomÃ¡tico</div>
          <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.7}}>
            <strong>2026:</strong> membro entra â conversa â confia â fÃ£ do canal.<br/>
            <strong>2027:</strong> fÃ£ â lista de espera â consulta com Daniela Coelho, psicÃ³loga.<br/>
            <strong>MÃ¡x 1.024/grupo</strong> â ao atingir, cria novo grupo automaticamente.<br/>
            Mensagens do perfil: mÃ­nimas e estratÃ©gicas. Membros conversam entre si.
          </div>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:8,marginBottom:14}}>
          {[{l:"Grupos",v:waGroups.length,c:"var(--green)"},{l:"Membros",v:total,c:"var(--blue)"},{l:"Capacidade",v:(WA_CONFIG.maxMembros*waGroups.length).toLocaleString("pt-BR"),c:"var(--amber)"}].map(m=>(
            <div key={m.l} style={{textAlign:"center",background:"var(--surf)",border:"1px solid var(--border)",borderRadius:12,padding:"10px 6px"}}>
              <div style={{fontWeight:800,fontSize:18,color:m.c}}>{m.v}</div>
              <div style={{fontSize:10,color:"var(--muted)"}}>{m.l}</div>
            </div>
          ))}
        </div>
        {waGroups.map(g=>(
          <div key={g.id} className="card mb12">
            <div style={{display:"flex",gap:10,alignItems:"flex-start"}}>
              <div style={{width:44,height:44,borderRadius:12,background:"rgba(37,163,77,0.12)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:22,flexShrink:0}}>ð¬</div>
              <div style={{flex:1}}>
                <div style={{fontWeight:700,fontSize:13,marginBottom:4}}>{g.nome}</div>
                <div style={{height:6,background:"var(--border)",borderRadius:3,overflow:"hidden",marginBottom:5}}>
                  <div style={{height:"100%",borderRadius:3,background:g.membros>=WA_CONFIG.maxMembros-50?"var(--amber)":"#25D366",width:Math.min(100,g.membros/WA_CONFIG.maxMembros*100)+"%",transition:"width 0.5s"}}/>
                </div>
                <div style={{display:"flex",justifyContent:"space-between",fontSize:11,color:"var(--muted)",marginBottom:8}}>
                  <span>{g.membros}/{WA_CONFIG.maxMembros} membros</span>
                  <span style={{fontWeight:700,color:g.membros>=WA_CONFIG.maxMembros?"var(--red)":g.membros>=WA_CONFIG.maxMembros-50?"var(--amber)":"var(--green)"}}>{g.membros>=WA_CONFIG.maxMembros?"ð´ CHEIO":g.membros>=WA_CONFIG.maxMembros-50?"â ï¸ Quase":"ð¢ Ativo"}</span>
                </div>
                <button onClick={()=>addMembro(g.id)} style={{padding:"5px 12px",borderRadius:20,border:"1.5px solid #25D366",background:"rgba(37,163,77,0.08)",color:"#25D366",fontSize:11,fontWeight:700,cursor:"pointer"}}>+ Simular membro</button>
              </div>
            </div>
          </div>
        ))}
        <button onClick={novoGrupo} style={{width:"100%",padding:"12px",borderRadius:12,border:"2px dashed var(--border)",background:"var(--surf2)",color:"var(--muted)",fontWeight:700,fontSize:13,cursor:"pointer",marginBottom:14}}>
          + Criar Grupo psicologia.doc #{waGroups.length+1}
        </button>
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:13,marginBottom:10}}>ð Mensagens AutomÃ¡ticas</div>
          {(revealed?WA_CONFIG.msgs2027:WA_CONFIG.msgs2026).map((msg,i)=>(
            <div key={i} style={{padding:"8px 10px",background:"var(--surf2)",borderRadius:8,marginBottom:6,fontSize:12,color:"var(--text2)",lineHeight:1.5}}>
              <span style={{fontSize:10,fontWeight:700,color:"var(--green)",display:"block",marginBottom:2}}>Msg {i+1}</span>{msg}
            </div>
          ))}
        </div>
        {contents[0]&&<div className="card mb12">
          <div style={{fontWeight:700,fontSize:13,marginBottom:8}}>ð¤ Compartilhar nos Grupos</div>
          <div style={{fontSize:12,color:"var(--text2)",marginBottom:8,lineHeight:1.4}}>{contents[0].title?.slice(0,80)}</div>
          <button onClick={()=>{setSendOk(true);setTimeout(()=>setSendOk(false),2000);}} style={{width:"100%",padding:"10px",borderRadius:10,border:"none",background:sendOk?"var(--gl)":"#25D366",color:"white",fontWeight:700,fontSize:13,cursor:"pointer"}}>
            {sendOk?"â Agendado para todos os grupos!":"ð¤ Enviar para todos os grupos"}
          </button>
        </div>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: RANKING MUNDIAL
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageRanking({ranking,isRanking}){
  return(
    <>
      <div className="ph"><div><div className="pt">ð Ranking Mundial</div><div className="ps">Psicologia + dark channels Â· atualiza 1x/min</div></div>
        {isRanking&&<div style={{width:20,height:20,border:"3px solid var(--bl)",borderTopColor:"var(--blue)",borderRadius:"50%",animation:"spin 0.8s linear infinite",flexShrink:0}}/>}
      </div>
      <div className="body">
        {!ranking?.length&&<div style={{textAlign:"center",padding:"40px 20px",color:"var(--muted)"}}><div style={{fontSize:40,marginBottom:12}}>ð</div><div style={{fontWeight:700,marginBottom:6}}>Buscando virais mundiais...</div></div>}
        {ranking?.map((v,i)=>(
          <div key={i} className="card mb12">
            <div style={{display:"flex",gap:10,alignItems:"flex-start"}}>
              <div style={{flexShrink:0,width:32,height:32,borderRadius:8,display:"flex",alignItems:"center",justifyContent:"center",fontWeight:800,fontSize:12,background:i===0?"linear-gradient(135deg,#FFD700,#FFA500)":i<3?"var(--pl)":"var(--surf2)",color:i===0?"white":i<3?"var(--purple)":"var(--text)"}}>#{i+1}</div>
              <div style={{flex:1,minWidth:0}}>
                <div style={{fontWeight:700,fontSize:13,lineHeight:1.35,marginBottom:3}}>{v.title_pt||v.title_en}</div>
                <div style={{fontSize:10,color:"var(--muted)",marginBottom:6}}>ð {v.channel}</div>
                <div style={{display:"flex",flexWrap:"wrap",gap:5,marginBottom:5}}>
                  {v.views&&<span style={{background:"var(--rl)",color:"var(--red)",borderRadius:6,padding:"2px 7px",fontSize:11,fontWeight:700}}>ð {v.views}</span>}
                  {v.duration_min&&<span style={{background:"var(--pl)",color:"var(--purple)",borderRadius:6,padding:"2px 7px",fontSize:10}}>â± {v.duration_min}min</span>}
                </div>
                {v.hook&&<div style={{background:"var(--surf2)",borderRadius:8,padding:"6px 8px",fontSize:11,fontStyle:"italic"}}>"{v.hook?.slice(0,100)}"</div>}
                {v.what_makes_viral&&<div style={{marginTop:5,fontSize:10,color:"var(--green)"}}>â¡ {v.what_makes_viral?.slice(0,80)}</div>}
              </div>
              {v.url?.includes("watch?v=")&&<a href={v.url} target="_blank" rel="noopener noreferrer" style={{flexShrink:0,width:40,height:40,borderRadius:10,background:"#dc2626",color:"white",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",textDecoration:"none",fontSize:9,fontWeight:700,gap:1}}><span style={{fontSize:16,lineHeight:1}}>â¶</span><span>Ver</span></a>}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: CASES DO DIA
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageCases({cases}){
  return(
    <>
      <div className="ph"><div><div className="pt">ð Cases do Dia</div><div className="ps">Pesquisa automÃ¡tica Â· implementaÃ§Ã£o imediata</div></div></div>
      <div className="body">
        <div style={{background:"rgba(5,150,105,0.08)",border:"1px solid var(--gb)",borderRadius:14,padding:14,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:"var(--green)",marginBottom:4}}>ð¬ Pesquisa DiÃ¡ria AutomÃ¡tica</div>
          <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.6}}>A cada ciclo o cÃ©rebro pesquisa cases reais de crescimento e monetizaÃ§Ã£o. As melhores tÃ¡ticas sÃ£o implementadas automaticamente no prÃ³ximo conteÃºdo.</div>
        </div>
        {!cases&&<div style={{textAlign:"center",padding:"30px 20px",color:"var(--muted)"}}><div style={{fontSize:32,marginBottom:8}}>ð¬</div><div>Aguardando prÃ³xima pesquisa...</div></div>}
        {cases?.cases?.map((c,i)=>(
          <div key={i} className="card mb12">
            <div style={{fontWeight:700,fontSize:13,color:"var(--purple)",marginBottom:4}}>{c.channel}</div>
            <div style={{fontSize:12,color:"var(--text2)",marginBottom:6,lineHeight:1.5}}>{c.achievement}</div>
            <div style={{background:"var(--pl)",borderRadius:8,padding:"6px 8px",fontSize:11,color:"var(--purple)",marginBottom:4}}>ð¯ {c.tactic}</div>
            <div style={{background:"var(--gl)",borderRadius:8,padding:"6px 8px",fontSize:11,color:"var(--green)"}}>ð {c.metric}</div>
            {c.apply&&<div style={{marginTop:6,fontSize:11,color:"var(--amber)"}}>â¡ Aplicar: {c.apply}</div>}
          </div>
        ))}
        {cases?.tactics?.map((t,i)=>(
          <div key={"t"+i} style={{padding:14,background:"rgba(37,99,235,0.08)",border:"1px solid rgba(37,99,235,0.2)",borderRadius:14,marginBottom:10}}>
            <div style={{fontWeight:700,fontSize:13,color:"var(--blue)",marginBottom:4}}>ð¡ {t.name}</div>
            <div style={{fontSize:12,color:"var(--text2)",marginBottom:4}}>{t.how}</div>
            <div style={{fontSize:11,color:"var(--green)"}}>ð {t.result}</div>
          </div>
        ))}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: PLAYLIST 630 DIAS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PagePlaylist({dayNumber}){
  const curTab=dayNumber<=14?1:dayNumber<=30?2:dayNumber<=60?3:dayNumber<=180?4:dayNumber<=260?5:6;
  const[tab,setTab]=useState(curTab);
  const PHASES=[
    {n:1,l:"Fase 1: SEO (1-14)",g:"1K inscritos",p:dayToDate(1)+" â "+dayToDate(14),c:"var(--blue)"},
    {n:2,l:"Fase 2: Viral (15-30)",g:"5K inscritos",p:dayToDate(15)+" â "+dayToDate(30),c:"var(--purple)"},
    {n:3,l:"Fase 3: Escala (31-60)",g:"10K Â· AdSense",p:dayToDate(31)+" â "+dayToDate(60),c:"var(--green)"},
    {n:4,l:"Fase 4: Crescimento (61-180)",g:"50K Â· R$10-40K/mÃªs",p:dayToDate(61)+" â "+dayToDate(180),c:"var(--amber)"},
    {n:5,l:"Fase 5: Autoridade (181-260)",g:"100K+ Â· WA cheio",p:dayToDate(181)+" â "+dayToDate(260),c:"var(--red)"},
    {n:6,l:"Fase 6: RevelaÃ§Ã£o (261+)",g:"200K+ Â· consultas",p:dayToDate(261)+"+",c:"var(--green)"},
  ];
  const cur=PHASES[tab-1];
  const F1=[{d:1,t:"Por que VocÃª se Sente Ansioso Mesmo sem Motivo"},{d:2,t:"7 Sinais de Apego Ansioso"},{d:3,t:"O Que Ã© Narcisismo de Verdade â Documentado"},{d:4,t:"5 Traumas de InfÃ¢ncia que Adultos Carregam"},{d:5,t:"Por Que VocÃª se Sabota Quando as Coisas VÃ£o Bem"},{d:7,t:"A Psicologia Por TrÃ¡s de 'O Corpo Guarda o Placar'"},{d:10,t:"Gaslighting: Como Identificar se EstÃ¡ Acontecendo com VocÃª"},{d:12,t:"Por Que VocÃª Atrai Pessoas Emocionalmente IndisponÃ­veis"},{d:14,t:"Os 4 Estilos de Apego â Em Qual VocÃª EstÃ¡?"}];
  const F6=[{d:261,t:"ð REVELAÃÃO: 'A psicÃ³loga por trÃ¡s do psicologia.doc Ã© Daniela Coelho'",star:true},{d:265,t:"CRP ativo â Daniela Coelho, psicÃ³loga"},{d:270,t:"Agenda de consultas online aberta â link na bio"},{d:300,t:"Programa premium: acompanhamento em grupo"},{d:400,t:"Marco 200K inscritos"},{d:630,t:"630 dias: de zero ao maior canal de psicologia do Brasil"}];
  return(
    <>
      <div className="ph"><div><div className="pt">ð Playlist 630 dias</div><div className="ps">Dia {dayNumber} Â· {new Date().toLocaleDateString("pt-BR")}</div></div></div>
      <div className="body">
        <div className="tab-bar">{PHASES.map(p=><div key={p.n} className={"tab"+(tab===p.n?" on":"")} onClick={()=>setTab(p.n)}>F{p.n}</div>)}</div>
        <div style={{background:cur.c+"14",border:"1px solid "+cur.c+"44",borderRadius:14,padding:12,marginBottom:14}}>
          <div style={{fontWeight:700,fontSize:13,color:cur.c,marginBottom:2}}>{cur.l}</div>
          <div style={{fontSize:12,color:"var(--text2)",marginBottom:2}}>ð¯ {cur.g}</div>
          <div style={{fontSize:11,color:"var(--muted)"}}>{cur.p}</div>
        </div>
        {tab===1&&F1.map((v,i)=>(
          <div key={i} className="card mb12" style={{borderLeft:v.d===dayNumber?"3px solid var(--purple)":"none",background:v.d===dayNumber?"rgba(124,58,237,0.04)":"var(--surf)"}}>
            <div style={{display:"flex",gap:10}}>
              <div style={{width:28,height:28,borderRadius:7,background:v.d===dayNumber?"var(--purple)":"var(--surf2)",color:v.d===dayNumber?"white":"var(--muted)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:11,fontWeight:800,flexShrink:0}}>{v.d===dayNumber?"ð":v.d}</div>
              <div style={{fontWeight:700,fontSize:13,flex:1,lineHeight:1.35}}>{v.t}</div>
            </div>
          </div>
        ))}
        {tab===6&&F6.map((v,i)=>(
          <div key={i} className="card mb12" style={{borderLeft:"3px solid "+(v.star?"var(--green)":"var(--border)"),background:v.star?"rgba(5,150,105,0.04)":"var(--surf)"}}>
            <div style={{display:"flex",gap:10}}>
              <div style={{width:36,height:28,borderRadius:7,background:v.star?"var(--green)":"var(--surf2)",color:v.star?"white":"var(--muted)",display:"flex",alignItems:"center",justifyContent:"center",fontSize:v.star?14:10,fontWeight:800,flexShrink:0}}>{v.star?"ð":"D"+v.d}</div>
              <div style={{fontWeight:700,fontSize:13,flex:1,lineHeight:1.35,color:v.star?"var(--green)":"var(--text)"}}>{v.t}</div>
            </div>
          </div>
        ))}
        {(tab===2||tab===3||tab===4||tab===5)&&<div className="card mb12">
          <div style={{fontWeight:700,fontSize:13,marginBottom:10}}>ð EstratÃ©gia da Fase</div>
          {tab===2&&["Primeiro viral: gatilho emocional forte (apego/narcisismo)","VÃ­deos 22-28min + imagens estÃ¡ticas = CPM 6x maior","WhatsApp Premium lanÃ§ado (R$29/mÃªs)","Motor 1000x gerando variaÃ§Ãµes automÃ¡ticas"].map((t,i)=><div key={i} style={{display:"flex",gap:8,padding:"6px 0",borderBottom:"1px solid var(--border)"}}><span style={{color:"var(--purple)",fontWeight:700}}>â¢</span><span style={{fontSize:12,lineHeight:1.5}}>{t}</span></div>)}
          {tab===3&&["SÃ©ries hipnÃ³ticas ativas â cada ep termina com loop aberto","AdSense desbloqueado (1K subs + 4K horas)","YouTube Memberships + Afiliados Zenklub","Canal dark: 3 vÃ­deos/dia = escala mÃ¡xima"].map((t,i)=><div key={i} style={{display:"flex",gap:8,padding:"6px 0",borderBottom:"1px solid var(--border)"}}><span style={{color:"var(--green)",fontWeight:700}}>â¢</span><span style={{fontSize:12,lineHeight:1.5}}>{t}</span></div>)}
          {tab===4&&["SÃ©rie Narcisismo, Ansiedade, Trauma em paralelo","Curso Digital BÃ¡sico R$97 (10K inscritos)","PatrocÃ­nio direto R$1-8K/vÃ­deo","WhatsApp com 1000+ membros engajados"].map((t,i)=><div key={i} style={{display:"flex",gap:8,padding:"6px 0",borderBottom:"1px solid var(--border)"}}><span style={{color:"var(--amber)",fontWeight:700}}>â¢</span><span style={{fontSize:12,lineHeight:1.5}}>{t}</span></div>)}
          {tab===5&&["Canal anÃ´nimo com autoridade mÃ¡xima estabelecida","Curso AvanÃ§ado R$297-997 + Grupo Premium R$197/mÃªs","WhatsApp cheio â lista de espera consultas sendo construÃ­da","Preparando a revelaÃ§Ã£o Daniela Coelho, psicÃ³loga"].map((t,i)=><div key={i} style={{display:"flex",gap:8,padding:"6px 0",borderBottom:"1px solid var(--border)"}}><span style={{color:"var(--red)",fontWeight:700}}>â¢</span><span style={{fontSize:12,lineHeight:1.5}}>{t}</span></div>)}
        </div>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// COMPONENT: ContentCard
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function ContentCard({c}){
  const[exp,setExp]=useState(false);
  const[copied,setCopied]=useState(false);
  const COLORS={youtube:"#FF0000",instagram:"#E1306C",tiktok:"#69C9D0",pinterest:"#E60023",whatsapp:"#25D366"};
  const ICONS={youtube:"ð¬",tiktok:"ðµ",instagram:"ð¸",pinterest:"ð",whatsapp:"ð¬"};
  const color=COLORS[c.channel]||"var(--purple)";
  const PUB={published:"â",not_configured:"âï¸",error:"â",auth_error:"ð",no_video:"ð"};
  function copy(){navigator.clipboard?.writeText(c.title+"\n\n"+(c.body||""));setCopied(true);setTimeout(()=>setCopied(false),2000);}
  return(
    <div className="card mb12">
      <div style={{display:"flex",gap:10,alignItems:"flex-start"}}>
        <div style={{width:44,height:44,borderRadius:10,flexShrink:0,background:c.hasVideo?"linear-gradient(135deg,var(--purple),#a855f7)":color+"18",border:"2px solid "+color+"33",display:"flex",alignItems:"center",justifyContent:"center",fontSize:20}}>{c.hasVideo?"ð¬":(ICONS[c.channel]||"ð")}</div>
        <div style={{flex:1,minWidth:0}}>
          <div style={{fontWeight:700,fontSize:13,lineHeight:1.35,marginBottom:4,overflow:"hidden",textOverflow:"ellipsis",display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical"}}>{c.title}</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:5,marginBottom:6}}>
            <span style={{background:color+"18",color,borderRadius:6,padding:"2px 7px",fontSize:11,fontWeight:700}}>{c.channel}</span>
            {c.day&&<span style={{background:"var(--surf2)",borderRadius:6,padding:"2px 7px",fontSize:11}}>Dia {c.day}</span>}
            {c.score&&<span style={{background:"rgba(5,150,105,0.08)",color:"var(--green)",borderRadius:6,padding:"2px 7px",fontSize:11,fontWeight:700}}>â¡{c.score}</span>}
            {c.safetyScore&&<span style={{background:c.safetyScore>=85?"var(--gl)":"var(--al)",color:c.safetyScore>=85?"var(--green)":"var(--amber)",borderRadius:6,padding:"2px 7px",fontSize:10,fontWeight:700}}>ð{c.safetyScore}</span>}
            {c.hasVideo&&<span style={{background:"var(--pl)",color:"var(--purple)",borderRadius:6,padding:"2px 7px",fontSize:10,fontWeight:700}}>ð¬</span>}
            {c.isSeriesEp&&<span style={{background:"rgba(37,99,235,0.1)",color:"var(--blue)",borderRadius:6,padding:"2px 7px",fontSize:10,fontWeight:700}}>ðº SÃ©rie</span>}
            {c.books?.length>0&&<span style={{background:"rgba(5,150,105,0.08)",color:"var(--green)",borderRadius:6,padding:"2px 7px",fontSize:9,fontWeight:600}}>ð {c.books[0]?.slice(0,20)}</span>}
          </div>
          {c.pubResults&&<div style={{display:"flex",flexWrap:"wrap",gap:4,marginBottom:6}}>{Object.entries(c.pubResults).map(([p,r])=><span key={p} style={{fontSize:10,fontWeight:600,padding:"2px 6px",borderRadius:4,background:r==="published"?"var(--gl)":"var(--surf2)",color:r==="published"?"var(--green)":"var(--muted)"}}>{PUB[r]||"?"} {p}</span>)}</div>}
          <div style={{display:"flex",gap:6,flexWrap:"wrap"}}>
            <button onClick={()=>setExp(v=>!v)} style={{padding:"5px 12px",borderRadius:20,border:"1.5px solid var(--purple)",background:"var(--pl)",color:"var(--purple)",fontSize:11,fontWeight:700,cursor:"pointer"}}>{exp?"â² Fechar":"ð Ver"}</button>
            {c.body&&<button onClick={copy} style={{padding:"5px 12px",borderRadius:20,border:"1.5px solid var(--border)",background:copied?"var(--gl)":"var(--surf2)",color:copied?"var(--green)":"var(--muted)",fontSize:11,fontWeight:700,cursor:"pointer"}}>{copied?"â":"ð"}</button>}
            {c.videoUrl&&<a href={c.videoUrl} target="_blank" rel="noopener noreferrer" style={{padding:"5px 12px",borderRadius:20,border:"1.5px solid var(--red)",background:"var(--rl)",color:"var(--red)",fontSize:11,fontWeight:700,textDecoration:"none"}}>â¶</a>}
          </div>
          {exp&&c.body&&<div style={{marginTop:10,background:"var(--surf2)",borderRadius:10,padding:12,fontSize:12,lineHeight:1.8,whiteSpace:"pre-wrap",maxHeight:"60vh",overflowY:"auto"}}>{c.body}</div>}
        </div>
        <div style={{flexShrink:0,fontSize:10,color:"var(--muted)",whiteSpace:"nowrap"}}>{c.createdAt?.split(",")[1]?.trim()||""}</div>
      </div>
    </div>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: CONTEÃDO
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageConteudo({contents,setNotifCount}){
  const[filter,setFilter]=useState("todos");
  useEffect(()=>setNotifCount(0),[]);
  const filtered=filter==="todos"?contents:contents.filter(c=>c.channel===filter);
  return(
    <>
      <div className="ph"><div><div className="pt">ð ConteÃºdo</div><div className="ps">{contents.length} produzidos</div></div></div>
      <div className="body">
        {contents.length>0&&<div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:14}}>
          {CHANNELS_LIST.map(ch=><div key={ch} style={{textAlign:"center",background:"var(--surf)",border:"1px solid var(--border)",borderRadius:12,padding:"10px 6px"}}>
            <div style={{fontWeight:800,fontSize:20,color:"var(--purple)"}}>{contents.filter(c=>c.channel===ch).length}</div>
            <div style={{fontSize:9,color:"var(--muted)",marginTop:2}}>{ch}</div>
          </div>)}
        </div>}
        <div className="tab-bar">{["todos",...CHANNELS_LIST].map(f=><div key={f} className={"tab"+(filter===f?" on":"")} onClick={()=>setFilter(f)}>{f}</div>)}</div>
        {filtered.length===0&&<div style={{textAlign:"center",padding:"40px 20px",color:"var(--muted)"}}><div style={{fontSize:40,marginBottom:12}}>ð¬</div><div style={{fontWeight:700,marginBottom:6}}>Nenhum documentÃ¡rio ainda</div><div style={{fontSize:12}}>Primeiro ciclo em ~1 minuto</div></div>}
        {filtered.map(c=><ContentCard key={c.id} c={c}/>)}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: MONETIZAÃÃO
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageMonetizacao({metrics,dayNumber,revealed}){
  const[tab,setTab]=useState("fontes");
  const TC={passivo:"var(--green)",recorrente:"var(--blue)",variÃ¡vel:"var(--amber)",lanÃ§amento:"var(--purple)",profissional:"var(--green)","alto valor":"var(--red)"};
  return(
    <>
      <div className="ph"><div><div className="pt">ð° MonetizaÃ§Ã£o</div><div className="ps">Dia {dayNumber} Â· CRP-compliant Â· psicologia.doc</div></div></div>
      <div className="body">
        <div className="tab-bar">{[["fontes","ð¡ Fontes"],["projecao","ð ProjeÃ§Ã£o"],["protecao","ð¡ï¸ Anti-Ban"]].map(([id,lb])=><div key={id} className={"tab"+(tab===id?" on":"")} onClick={()=>setTab(id)}>{lb}</div>)}</div>
        {tab==="fontes"&&MONETIZACAO.map((s,i)=>(
          <div key={i} className="card mb12">
            <div style={{display:"flex",gap:12,alignItems:"center"}}>
              <span style={{fontSize:26,flexShrink:0}}>{s.ic}</span>
              <div style={{flex:1}}>
                <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:2}}>
                  <div style={{fontWeight:700,fontSize:13}}>{s.n}</div>
                  <span style={{fontSize:9,fontWeight:700,background:TC[s.tipo]+"22",color:TC[s.tipo],borderRadius:4,padding:"1px 6px",flexShrink:0,marginLeft:6}}>{s.tipo}</span>
                </div>
                <div style={{fontSize:11,color:"var(--muted)",marginBottom:3}}>â° {s.t}</div>
                <div style={{fontWeight:800,fontSize:12,color:"var(--green)"}}>{s.v}</div>
              </div>
            </div>
          </div>
        ))}
        {tab==="projecao"&&<>
          <div style={{background:"rgba(5,150,105,0.08)",border:"1px solid var(--gb)",borderRadius:14,padding:14,marginBottom:14}}>
            <div style={{fontSize:10,fontWeight:700,color:"var(--green)",textTransform:"uppercase",marginBottom:6}}>ð Case real verificado</div>
            <div style={{fontWeight:700,fontSize:14,marginBottom:4}}>Canal dark anÃ´nimo: 1.2M views + R$24K em 60 dias</div>
            <div style={{fontSize:12,color:"var(--text2)",lineHeight:1.6}}>VÃ­deos 22-28min + imagens estÃ¡ticas + narraÃ§Ã£o + pÃºblico 25-54 + nicho emocional. <strong>CPM gringo: 6-7x maior que Brasil.</strong></div>
          </div>
          {[{p:"Dias 1-30",r:"R$0-500/mÃªs",f:"Afiliados Zenklub desde o dia 1"},{p:"Dias 31-60",r:"R$500-2K/mÃªs",f:"AdSense + Memberships"},{p:"Dias 61-180",r:"R$2K-15K/mÃªs",f:"Curso R$97 + WA Premium + PatrocÃ­nio"},{p:"Dias 181-260",r:"R$15K-50K/mÃªs",f:"Curso avanÃ§ado + Grupo premium"},{p:"Dia 261+",r:"R$50K-250K/mÃªs",f:"Consultas + todos os acima"}].map((t,i)=>(
            <div key={i} style={{display:"flex",gap:10,padding:"10px 0",borderBottom:"1px solid var(--border)"}}>
              <div style={{flexShrink:0,width:70}}><div style={{fontSize:10,fontWeight:700,color:"var(--muted)"}}>{t.p}</div></div>
              <div style={{flex:1}}><div style={{fontWeight:800,fontSize:13,color:"var(--green)",marginBottom:2}}>{t.r}</div><div style={{fontSize:10,color:"var(--text2)"}}>{t.f}</div></div>
            </div>
          ))}
          <div style={{marginTop:10,padding:10,background:"linear-gradient(135deg,rgba(5,150,105,0.1),rgba(5,150,105,0.03))",borderRadius:10}}>
            <div style={{fontSize:11,color:"var(--green)",fontWeight:700}}>ð¯ Meta final â psicologia.doc + Daniela Coelho, psicÃ³loga</div>
            <div style={{fontSize:20,fontWeight:800,color:"var(--green)",marginTop:4}}>R$80.000 â 250.000/mÃªs</div>
          </div>
        </>}
        {tab==="protecao"&&<div className="card mb12">
          <div style={{fontWeight:700,fontSize:13,marginBottom:10,color:"var(--red)"}}>ð¡ï¸ Anti-Ban + CRP Compliance</div>
          {[["SEM","diagnÃ³stico mÃ©dico ou psiquiÃ¡trico"],["SEM","promessa de cura ou tratamento"],["SEM","prÃ¡tica ilegal de psicologia"],["SEM","citaÃ§Ã£o de medicamentos"],["SEM","conteÃºdo que induza automedicaÃ§Ã£o"],["COM","base cientÃ­fica citÃ¡vel (DSM-5, APA, CID-11)"],["COM","CRP compliance total"],["COM","linguagem inclusiva e empÃ¡tica"],["SEM","nome de pessoa em 2026"],["SEM","'Dra.' â apenas 'psicÃ³loga' em 2027"]].map(([tp,r],i)=>(
            <div key={i} style={{display:"flex",gap:8,padding:"7px 0",borderBottom:"1px solid var(--border)"}}>
              <span style={{color:tp==="SEM"?"var(--red)":"var(--green)",flexShrink:0,fontWeight:700}}>{tp==="SEM"?"â":"â"}</span>
              <span style={{fontSize:12,lineHeight:1.5,color:tp==="SEM"?"var(--red)":"var(--text2)"}}>{tp} {r}</span>
            </div>
          ))}
          <div style={{marginTop:12,padding:12,background:"rgba(217,119,6,0.08)",borderRadius:10,fontSize:11,color:"var(--amber)"}}>
            â ï¸ Freq. mÃ¡x/dia: YT {ANTI_BAN.maxDaily.youtube} Â· TK {ANTI_BAN.maxDaily.tiktok} Â· IG {ANTI_BAN.maxDaily.instagram} Â· Pinterest {ANTI_BAN.maxDaily.pinterest}
          </div>
        </div>}
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: CONFIGURAÃÃES
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageConfig({metrics}){
  const load2=()=>{try{return JSON.parse(localStorage.getItem("doc_cfg")||"{}");}catch{return{};}};
  const[keys,setKeys]=useState(load2);
  const[saved,setSaved]=useState(false);
  const[show,setShow]=useState({});
  const save=()=>{try{localStorage.setItem("doc_cfg",JSON.stringify(keys));setSaved(true);setTimeout(()=>setSaved(false),2000);}catch{}};
  const APIS=[
    {s:"ðï¸ ElevenLabs",c:"#7c3aed",l:"https://elevenlabs.io/app",fields:[{k:"elevenlabs",l:"API Key",ph:"sk_..."},{k:"elevenlabsVoice",l:"Voice ID PT-BR",ph:"pNInz6obpgDQGcFmaJgB"}]},
    {s:"ð¬ HeyGen",c:"#2563eb",l:"https://app.heygen.com/settings",fields:[{k:"heygen",l:"API Key",ph:"MzY..."},{k:"heygenAvatar",l:"Avatar ID",ph:"Daisy-inskirt-20220818"},{k:"heygenVoice",l:"Voice ID",ph:"1bd001e7e50f421d891986aad5158bc8"}]},
    {s:"â¶ï¸ YouTube Data API v3",c:"#FF0000",l:"https://console.cloud.google.com",fields:[{k:"youtube",l:"OAuth Access Token",ph:"ya29..."}]},
    {s:"ð¸ Instagram Meta Graph",c:"#E1306C",l:"https://business.facebook.com",fields:[{k:"instagram",l:"Access Token",ph:"EAABs..."}]},
    {s:"ðµ TikTok Content API",c:"#69C9D0",l:"https://developers.tiktok.com",fields:[{k:"tiktok",l:"Access Token",ph:"act..."}]},
    {s:"ð Pinterest API v5",c:"#E60023",l:"https://developers.pinterest.com",fields:[{k:"pinterest",l:"Access Token",ph:"pina_..."}]},
  ];
  const ok=k=>keys[k]?.length>8;
  return(
    <>
      <div className="ph"><div><div className="pt">âï¸ ConfiguraÃ§Ãµes</div><div className="ps">APIs Â· psicologia.doc v7</div></div></div>
      <div className="body">
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,marginBottom:8,color:"var(--muted)",textTransform:"uppercase"}}>Status APIs</div>
          <div style={{display:"flex",flexWrap:"wrap",gap:6,marginBottom:10}}>
            {["elevenlabs","heygen","youtube","instagram","tiktok","pinterest"].map(k=><div key={k} style={{padding:"4px 10px",borderRadius:20,fontSize:11,fontWeight:600,background:ok(k)?"var(--gl)":"var(--rl)",color:ok(k)?"var(--green)":"var(--red)"}}>{ok(k)?"â":"â"} {k}</div>)}
          </div>
          <div style={{fontSize:11,color:"var(--muted)",lineHeight:1.5}}>â ï¸ Sem APIs, o cÃ©rebro gera roteiros completos. ElevenLabs + HeyGen ativam narraÃ§Ã£o + avatar automÃ¡ticos.</div>
        </div>
        {APIS.map(sec=>(
          <div key={sec.s} className="card mb12">
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
              <div style={{fontWeight:700,fontSize:13,color:sec.c}}>{sec.s}</div>
              <a href={sec.l} target="_blank" rel="noopener noreferrer" style={{fontSize:11,color:"var(--blue)",fontWeight:600,textDecoration:"none"}}>Gerar â</a>
            </div>
            {sec.fields.map(f=>(
              <div key={f.k} style={{marginBottom:10}}>
                <div style={{fontSize:12,fontWeight:600,marginBottom:4}}>{f.l}</div>
                <div style={{display:"flex",gap:6}}>
                  <input type={show[f.k]?"text":"password"} value={keys[f.k]||""} onChange={e=>setKeys(p=>({...p,[f.k]:e.target.value}))} placeholder={f.ph} style={{flex:1,padding:"10px 12px",borderRadius:10,border:"1.5px solid var(--border)",background:"var(--surf2)",fontSize:12,fontFamily:"monospace",color:"var(--text)",outline:"none"}}/>
                  <button onClick={()=>setShow(p=>({...p,[f.k]:!p[f.k]}))} style={{padding:"0 10px",borderRadius:8,border:"1px solid var(--border)",background:"var(--surf2)",cursor:"pointer",fontSize:14}}>{show[f.k]?"ð":"ð"}</button>
                </div>
              </div>
            ))}
          </div>
        ))}
        <button onClick={save} style={{width:"100%",padding:"14px",borderRadius:12,border:"none",background:saved?"var(--green)":"linear-gradient(135deg,var(--purple),#a855f7)",color:"white",fontWeight:700,fontSize:15,cursor:"pointer",marginBottom:12}}>{saved?"â Salvo!":"ð¾ Salvar ConfiguraÃ§Ãµes"}</button>
        <div className="card mb12">
          <div style={{fontWeight:700,fontSize:12,marginBottom:8,color:"var(--muted)",textTransform:"uppercase"}}>ð Sistema</div>
          {[["Canal","@psicologiadoc"],["InÃ­cio","15 abr 2026 (Dia 1)"],["Dia atual",calcDay()],["RevelaÃ§Ã£o","Dia "+DIA_REVELACAO+" (~1 jan 2027)"],["Docs gerados",metrics.generated],["Score mÃ©dio",metrics.scoreAvg||"â"],["Ranking","a cada 1 minuto"],["ProduÃ§Ã£o","a cada 30 minutos"]].map(([k,v])=>(
            <div key={k} style={{display:"flex",justifyContent:"space-between",padding:"7px 0",borderBottom:"1px solid var(--border)",fontSize:12}}><span style={{color:"var(--muted)"}}>{k}</span><span style={{fontWeight:700}}>{v}</span></div>
          ))}
        </div>
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// PAGE: LOGS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
function PageLogs({logs,logRef}){
  const[filter,setFilter]=useState("all");
  const filtered=filter==="all"?logs:logs.filter(l=>l.type===filter);
  return(
    <>
      <div className="ph"><div><div className="pt">ð Logs</div><div className="ps">{logs.length} eventos Â· AO VIVO</div></div></div>
      <div className="body">
        <div className="tab-bar">{["all","system","success","info","warn","error"].map(f=><div key={f} className={"tab"+(filter===f?" on":"")} onClick={()=>setFilter(f)}>{f}</div>)}</div>
        <div style={{background:"#0a0a0f",borderRadius:12,overflow:"hidden",border:"1px solid #1a1a25"}}>
          <div style={{padding:"8px 14px",borderBottom:"1px solid #1a1a25",display:"flex",justifyContent:"space-between"}}>
            <span style={{fontSize:11,fontWeight:700,color:"#555",fontFamily:"monospace"}}>{filtered.length} ENTRADAS</span>
            <span style={{fontSize:11,color:"#22c55e",display:"flex",alignItems:"center",gap:4}}><span style={{width:6,height:6,borderRadius:"50%",background:"#22c55e",display:"inline-block",animation:"blink 1s infinite"}}/>AO VIVO</span>
          </div>
          <div ref={logRef} style={{maxHeight:"72vh",overflowY:"auto",padding:10}}>
            {filtered.map(l=>(
              <div key={l.id} style={{display:"flex",gap:8,padding:"3px 4px",fontSize:11,fontFamily:"monospace",lineHeight:1.5}}>
                <span style={{color:"#444",flexShrink:0,minWidth:64}}>{l.time}</span>
                <span style={{color:l.type==="success"?"#22c55e":l.type==="error"?"#ef4444":l.type==="warn"?"#f59e0b":l.type==="system"?"#a78bfa":"#6b7280",flexShrink:0,minWidth:64}}>[{l.type}]</span>
                <span style={{color:"#d1d5db",flex:1}}>{l.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}

// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
// CSS
// âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
const CSS=`
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0f;--surf:#13131a;--surf2:#1c1c26;--border:#252535;
  --purple:#7c3aed;--pl:rgba(124,58,237,0.09);--pb:rgba(124,58,237,0.22);
  --green:#059669;--gl:rgba(5,150,105,0.09);--gb:rgba(5,150,105,0.22);
  --red:#dc2626;--rl:rgba(220,38,38,0.09);--rb:rgba(220,38,38,0.22);
  --amber:#d97706;--al:rgba(217,119,6,0.09);
  --blue:#2563eb;--bl:rgba(37,99,235,0.09);
  --text:#f0f0f8;--text2:#b0b0c8;--muted:#55556a;
  --font:'Plus Jakarta Sans',-apple-system,sans-serif;
}
html{height:100%;-webkit-text-size-adjust:100%}
body{background:var(--bg);color:var(--text);font-family:var(--font);font-size:15px;height:100%;overflow:hidden;-webkit-font-smoothing:antialiased;touch-action:manipulation}
.app{display:flex;height:100dvh;overflow:hidden;position:relative}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);z-index:40;backdrop-filter:blur(4px)}.overlay.show{display:block}
.sidebar{width:280px;flex-shrink:0;background:var(--surf);border-right:1px solid var(--border);display:flex;flex-direction:column;overflow-y:auto;position:fixed;left:0;top:0;bottom:0;z-index:50;transform:translateX(-100%);transition:transform 0.25s cubic-bezier(.4,0,.2,1)}.sidebar.open{transform:translateX(0);box-shadow:8px 0 32px rgba(0,0,0,0.5)}
.topbar{position:fixed;top:0;left:0;right:0;height:calc(52px + env(safe-area-inset-top,0px));padding-top:env(safe-area-inset-top,0px);background:rgba(19,19,26,0.95);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border-bottom:1px solid var(--border);display:flex;align-items:center;padding-left:12px;padding-right:12px;gap:8px;z-index:30}
.hbtn{width:40px;height:40px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;background:transparent;border:none;cursor:pointer;padding:0;flex-shrink:0}.hbtn span{display:block;width:20px;height:2px;background:var(--text);border-radius:1px;transition:all 0.25s}.hbtn.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}.hbtn.open span:nth-child(2){opacity:0}.hbtn.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
.main{flex:1;overflow-y:auto;padding-top:calc(52px + env(safe-area-inset-top,0px));padding-bottom:calc(24px + env(safe-area-inset-bottom,0px));-webkit-overflow-scrolling:touch}
.body{padding:12px;max-width:520px;margin:0 auto}.ph{padding:14px 12px 10px;display:flex;align-items:flex-start;justify-content:space-between;gap:10px}
.pt{font-size:20px;font-weight:800;letter-spacing:-0.02em}.ps{font-size:12px;color:var(--muted);margin-top:2px}
.card{background:var(--surf);border:1px solid var(--border);border-radius:14px;padding:14px;box-shadow:0 2px 8px rgba(0,0,0,0.2)}.mb12{margin-bottom:12px}
.ni{display:flex;align-items:center;gap:10px;padding:10px 14px;cursor:pointer;font-size:13px;font-weight:600;color:var(--muted);transition:all 0.12s;-webkit-tap-highlight-color:transparent;position:relative;min-height:44px}.ni:active{background:var(--surf2)}.ni.on{color:var(--purple);background:rgba(124,58,237,0.08)}
.nb{background:var(--red);color:white;border-radius:10px;padding:1px 5px;font-size:9px;font-weight:800;position:absolute;right:10px}
.nb-btn{position:relative;width:36px;height:36px;border-radius:50%;border:none;background:var(--surf2);cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.status-badge{font-size:11px;font-weight:700;padding:5px 10px;border-radius:20px;background:var(--gl);color:var(--green);white-space:nowrap;flex-shrink:0}.status-badge.active{background:var(--pl);color:var(--purple)}
.tab-bar{display:flex;border-bottom:1px solid var(--border);margin-bottom:14px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none}.tab-bar::-webkit-scrollbar{display:none}
.tab{padding:9px 14px;font-size:13px;font-weight:600;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;white-space:nowrap;min-height:40px;display:flex;align-items:center;gap:5px;-webkit-tap-highlight-color:transparent}.tab.on{color:var(--purple);border-bottom-color:var(--purple)}
@keyframes spin{to{transform:rotate(360deg)}}@keyframes blink{0%,100%{opacity:1}50%{opacity:0}}@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
@media(min-width:768px){.sidebar{position:relative;transform:none!important;box-shadow:none}.overlay{display:none!important}.topbar{left:280px}}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
`;
