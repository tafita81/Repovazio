import { scoreContent } from "@/lib/intelligence";

export const dynamic = 'force-dynamic';

export async function GET() {
  // simulação de dados reais
  const data = [
    { views: 1000, clicks: 120 },
    { views: 500, clicks: 20 },
    { views: 2000, clicks: 300 }
  ];

  const analyzed = data.map(d => ({
    ...d,
    analysis: scoreContent(d)
  }));

  return Response.json({ analyzed });
}
