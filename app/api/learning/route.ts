import { learnFromMetrics, generateNextTopics } from "@/lib/learning";

export const dynamic = 'force-dynamic';

export async function GET() {
  // simulação métricas
  const metrics = [
    { topic: "ansiedade", views: 1000, clicks: 200 },
    { topic: "produtividade", views: 800, clicks: 40 },
    { topic: "hábitos", views: 2000, clicks: 400 }
  ];

  const learned = learnFromMetrics(metrics);
  const nextTopics = generateNextTopics(learned);

  return Response.json({
    learned,
    nextTopics
  });
}
