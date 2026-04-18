-- Execute este SQL no Supabase SQL Editor:
-- https://app.supabase.com -> SQL Editor

-- Tabela principal de registros (já pode existir)
CREATE TABLE IF NOT EXISTS registros (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT,
  script TEXT,
  status TEXT DEFAULT 'gerado',
  canal TEXT DEFAULT 'psicologia.doc',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  plataforma TEXT,
  score INTEGER DEFAULT 80,
  modelo TEXT,
  inovacao TEXT,
  ciclo_id BIGINT,
  memoria_usada INTEGER DEFAULT 0,
  views INTEGER DEFAULT 0,
  clicks INTEGER DEFAULT 0
);

-- Memória evolutiva do cérebro
CREATE TABLE IF NOT EXISTS cerebro_memoria (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT UNIQUE,
  score INTEGER DEFAULT 80,
  vezes_gerado INTEGER DEFAULT 1,
  estilo_vencedor TEXT,
  criado_em TIMESTAMPTZ DEFAULT NOW(),
  ultimo_ciclo TIMESTAMPTZ DEFAULT NOW()
);

-- Histórico de aprendizado diário
CREATE TABLE IF NOT EXISTS cerebro_aprendizado (
  id BIGSERIAL PRIMARY KEY,
  data TIMESTAMPTZ DEFAULT NOW(),
  total_ciclos_24h INTEGER DEFAULT 0,
  score_medio INTEGER DEFAULT 80,
  padroes_virais JSONB DEFAULT '[]',
  padroes_ruins JSONB DEFAULT '[]',
  proximos_topics JSONB DEFAULT '[]',
  tendencia TEXT DEFAULT 'estavel',
  insight TEXT,
  ajuste_tom TEXT
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_registros_created ON registros(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_registros_score ON registros(score DESC);
CREATE INDEX IF NOT EXISTS idx_memoria_score ON cerebro_memoria(score DESC);
