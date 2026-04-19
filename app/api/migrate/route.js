export const dynamic = 'force-dynamic';
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

// Usar o endpoint de execução SQL do Supabase via REST API
// O Supabase expõe /rest/v1/rpc para funções SQL, mas tambem podemos usar
// a API de admin para executar DDL
async function executeSql(sql) {
  if (!SU || !SK) return { error: 'No config' };
  // Tentar via endpoint de query direto
  const projectRef = SU.replace('https://', '').replace('.supabase.co', '');
  const endpoints = [
    { url: 'https://api.supabase.com/v1/projects/' + projectRef + '/database/query', method: 'POST', body: { query: sql }, auth: 'Bearer ' + SK },
    { url: SU + '/rest/v1/rpc/sql', method: 'POST', body: { query: sql }, auth: 'Bearer ' + SK },
  ];
  for (const ep of endpoints) {
    try {
      const r = await fetch(ep.url, {
        method: ep.method,
        headers: { 'Content-Type': 'application/json', Authorization: ep.auth, apikey: SK },
        body: JSON.stringify(ep.body)
      });
      const text = await r.text();
      if (r.ok) return { ok: true, endpoint: ep.url.split('/').slice(-2).join('/'), result: text.slice(0,100) };
    } catch(e) {}
  }
  return { error: 'All endpoints failed' };
}

export async function GET() {
  const SU2 = SU || '';
  const projectRef = SU2.replace('https://', '').replace('.supabase.co', '');
  
  // Verificar quais tabelas existem
  const checks = {};
  for (const t of ['whatsapp_mensagens','whatsapp_respostas','whatsapp_membros','planejamento_revelacao']) {
    try {
      const r = await fetch(SU + '/rest/v1/' + t + '?limit=0', {
        headers: { apikey: SK, Authorization: 'Bearer ' + SK }
      });
      checks[t] = r.status;
    } catch { checks[t] = 0; }
  }

  const allExist = Object.values(checks).every(s => s === 200);
  if (allExist) {
    // Inserir plano se vazio
    try {
      const pr = await fetch(SU + '/rest/v1/planejamento_revelacao?select=count', {
        headers: { apikey: SK, Authorization: 'Bearer ' + SK, Prefer: 'count=exact' }
      });
      const count = pr.headers.get('content-range');
      if (count && count.includes('/0')) {
        const items = [
          {dia:1,fase:'lancamento',acao:'Publicar 1o video YouTube - ativa Dia 1'},
          {dia:30,fase:'crescimento',acao:'Meta 500 subs - WhatsApp grupo ativo'},
          {dia:60,fase:'engajamento',acao:'Meta 1000 subs - solicitar AdSense'},
          {dia:90,fase:'monetizacao',acao:'Primeiros ganhos AdSense - afiliados'},
          {dia:120,fase:'expansao',acao:'Meta 5000 subs - TikTok e Instagram'},
          {dia:180,fase:'consolidacao',acao:'Meta 10000 subs - curso gratuito'},
          {dia:240,fase:'pre-revelacao',acao:'Hints sobre Daniela Coelho nos videos'},
          {dia:261,fase:'revelacao',acao:'REVELAR Daniela Coelho Psicologa - agenda consultas'},
          {dia:270,fase:'pos-revelacao',acao:'Converter grupo WA em clientes consulta'},
          {dia:365,fase:'escala',acao:'Meta 100000 subs - canal EUA ingles'},
        ];
        await fetch(SU + '/rest/v1/planejamento_revelacao', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: 'return=minimal' },
          body: JSON.stringify(items)
        });
      }
    } catch {}
    return Response.json({ status: 'all_ok', checks });
  }

  // Tabelas nao existem - retornar o SQL para criar manualmente
  const sqlToRun = [
    "CREATE TABLE IF NOT EXISTS whatsapp_mensagens (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMPTZ DEFAULT now(), remetente TEXT, remetente_nome TEXT, conteudo TEXT, tipo TEXT DEFAULT 'texto', grupo_id TEXT, respondido BOOLEAN DEFAULT false, sentimento TEXT, topico_detectado TEXT);",
    "CREATE TABLE IF NOT EXISTS whatsapp_respostas (id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMPTZ DEFAULT now(), mensagem_id BIGINT, resposta TEXT NOT NULL, modelo_ia TEXT, enviado BOOLEAN DEFAULT false, horario_programado TIMESTAMPTZ, motivo TEXT);",
    "CREATE TABLE IF NOT EXISTS whatsapp_membros (id BIGSERIAL PRIMARY KEY, phone TEXT UNIQUE, nome TEXT, entrada TIMESTAMPTZ DEFAULT now(), engajamento INT DEFAULT 0, ultima_mensagem TIMESTAMPTZ, nivel_interesse INT DEFAULT 1);",
    "CREATE TABLE IF NOT EXISTS planejamento_revelacao (id BIGSERIAL PRIMARY KEY, dia INT NOT NULL, fase TEXT, acao TEXT, executado BOOLEAN DEFAULT false, resultado TEXT, criado_em TIMESTAMPTZ DEFAULT now());",
  ];

  return Response.json({
    status: 'tables_missing',
    checks,
    project_ref: projectRef,
    sql_editor_url: 'https://supabase.com/dashboard/project/' + projectRef + '/sql/new',
    sql_to_run: sqlToRun,
    message: 'Execute o SQL no Supabase SQL Editor'
  });
}