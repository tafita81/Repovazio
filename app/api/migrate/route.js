export const dynamic = 'force-dynamic';
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

async function dbPost(path, body) {
  if (!SU || !SK) return { error: 'No Supabase config' };
  try {
    const r = await fetch(SU + '/rest/v1/' + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: 'return=representation' },
      body: JSON.stringify(body)
    });
    return { status: r.status, ok: r.ok };
  } catch(e) { return { error: e.message }; }
}

async function dbCheck(table) {
  if (!SU || !SK) return 404;
  try {
    const r = await fetch(SU + '/rest/v1/' + table + '?limit=1', {
      headers: { apikey: SK, Authorization: 'Bearer ' + SK }
    });
    return r.status;
  } catch { return 0; }
}

async function createTablesViaRpc() {
  // Usar o endpoint RPC do Supabase para executar SQL
  if (!SU || !SK) return { error: 'No config' };
  const sql = `
    CREATE TABLE IF NOT EXISTS whatsapp_mensagens (
      id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMPTZ DEFAULT now(),
      remetente TEXT, remetente_nome TEXT, conteudo TEXT, tipo TEXT DEFAULT 'texto',
      grupo_id TEXT, respondido BOOLEAN DEFAULT false, sentimento TEXT, topico_detectado TEXT
    );
    CREATE TABLE IF NOT EXISTS whatsapp_respostas (
      id BIGSERIAL PRIMARY KEY, timestamp TIMESTAMPTZ DEFAULT now(), mensagem_id BIGINT,
      resposta TEXT NOT NULL, modelo_ia TEXT, enviado BOOLEAN DEFAULT false,
      horario_programado TIMESTAMPTZ, motivo TEXT
    );
    CREATE TABLE IF NOT EXISTS whatsapp_membros (
      id BIGSERIAL PRIMARY KEY, phone TEXT UNIQUE, nome TEXT,
      entrada TIMESTAMPTZ DEFAULT now(), engajamento INT DEFAULT 0,
      ultima_mensagem TIMESTAMPTZ, nivel_interesse INT DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS planejamento_revelacao (
      id BIGSERIAL PRIMARY KEY, dia INT NOT NULL, fase TEXT, acao TEXT,
      executado BOOLEAN DEFAULT false, resultado TEXT, criado_em TIMESTAMPTZ DEFAULT now()
    );
  `;
  try {
    const r = await fetch(SU + '/rest/v1/rpc/exec_sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK },
      body: JSON.stringify({ query: sql })
    });
    return { rpc_status: r.status, rpc_ok: r.ok };
  } catch(e) { return { rpc_error: e.message }; }
}

export async function GET() {
  // Verificar status atual
  const checks = await Promise.all([
    dbCheck('whatsapp_mensagens'),
    dbCheck('whatsapp_respostas'),
    dbCheck('whatsapp_membros'),
    dbCheck('planejamento_revelacao'),
  ]);

  const allExist = checks.every(s => s === 200);
  if (allExist) {
    // Inserir dados do plano se a tabela existir mas estiver vazia
    const planoCheck = await fetch(SU + '/rest/v1/planejamento_revelacao?select=count', {
      headers: { apikey: SK, Authorization: 'Bearer ' + SK }
    });
    const planoData = await planoCheck.json();
    const total = planoData && planoData[0] && planoData[0].count;
    if (total === '0' || total === 0) {
      const items = [
        {dia:1,fase:'lancamento',acao:'Publicar 1o video YouTube - ativa Dia 1'},
        {dia:30,fase:'crescimento',acao:'Meta 500 subs - WhatsApp grupo ativo'},
        {dia:60,fase:'engajamento',acao:'Meta 1000 subs - solicitar AdSense'},
        {dia:90,fase:'monetizacao',acao:'Primeiros ganhos AdSense - adicionar afiliados'},
        {dia:120,fase:'expansao',acao:'Meta 5000 subs - TikTok e Instagram ativos'},
        {dia:180,fase:'consolidacao',acao:'Meta 10000 subs - curso gratuito lead magnet'},
        {dia:240,fase:'pre-revelacao',acao:'Hints sobre Daniela Coelho nos videos'},
        {dia:261,fase:'revelacao',acao:'REVELAR Daniela Coelho Psicologa - agenda consultas online'},
        {dia:270,fase:'pos-revelacao',acao:'Converter grupo WhatsApp em clientes consulta'},
        {dia:365,fase:'escala',acao:'Meta 100000 subs - canal EUA ingles'},
      ];
      await dbPost('planejamento_revelacao', items);
    }
    return Response.json({ status: 'ok', tables: checks, all_exist: true });
  }

  // Tentar criar via RPC
  const rpcResult = await createTablesViaRpc();
  return Response.json({ status: 'migrate_attempted', checks, rpc: rpcResult });
}