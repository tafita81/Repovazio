import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function POST() {
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

  } catch (e) {
    return Response.json({ error: true, message: e.message });
  }
}
