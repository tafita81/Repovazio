import { createClient as createSupabaseClient } from "@supabase/supabase-js";

/**
 * Cria um cliente Supabase server-side (para API routes e Server Components).
 * Usa Service Key para operações administrativas.
 * Retorna null se as variáveis de ambiente não estiverem configuradas.
 */
export function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;

  if (!url || !key) {
    console.warn(
      "[Supabase] Variáveis não configuradas: NEXT_PUBLIC_SUPABASE_URL, SUPABASE_SERVICE_KEY"
    );
    return null;
  }

  // Em serverless (Netlify/Vercel), cada invocação é isolada.
  // Criamos um novo cliente por request para evitar problemas com RLS.
  return createSupabaseClient(url, key, {
    auth: {
      persistSession: false,
      autoRefreshToken: false,
    },
  });
}
