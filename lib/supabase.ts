import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

let supabase: any;

if (supabaseUrl && supabaseKey) {
  supabase = createClient(supabaseUrl, supabaseKey);
} else {
  // fallback compatível com chain (select → order → limit)
  supabase = {
    from: () => ({
      select: () => ({
        order: () => ({
          limit: () => ({ data: [], error: null })
        })
      }),
      insert: () => ({ data: null, error: null }),
      upsert: () => ({ data: null, error: null })
    })
  };
}

export { supabase };
