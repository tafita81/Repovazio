export const dynamic = 'force-dynamic';

import OpenAI from "openai";

function getClient() {
  const key = process.env.OPENAI_API_KEY;
  if (!key) return null;
  return new OpenAI({ apiKey: key });
}

export async function POST() {
  const client = getClient();

  if (!client) {
    return Response.json({
      status: "fallback",
      content: "3 ideias virais: 1) Psicologia da procrastinação 2) Viés cognitivo no dia a dia 3) Como hábitos moldam decisões",
      createdAt: new Date().toISOString()
    });
  }

  try {
    const completion = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You generate viral short-form content." },
        { role: "user", content: "Generate 3 viral content ideas about psychology." }
      ]
    });

    const result = completion.choices[0].message.content;

    return Response.json({
      status: "ok",
      content: result,
      createdAt: new Date().toISOString()
    });

  } catch {
    return Response.json({
      status: "error",
      content: "fallback content",
      createdAt: new Date().toISOString()
    });
  }
}
