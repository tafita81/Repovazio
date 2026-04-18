export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const base = process.env.NEXT_PUBLIC_BASE_URL

    // 1. learning loop
    const learning = await fetch(`${base}/api/learning`).then(r => r.json())
    const topics = learning?.nextTopics || []

    // fallback seguro
    const finalTopics = topics.length
      ? topics
      : ["ansiedade moderna", "dopamina barata"]

    // 2. executar pipeline baseado no aprendizado
    const results = []

    for (const topic of finalTopics) {
      const res = await fetch(`${base}/api/pipeline`, {
        method: "POST",
        body: JSON.stringify({ topic })
      })

      results.push(await res.json())
    }

    return Response.json({
      status: "autopilot_running",
      topics: finalTopics,
      results
    })

  } catch (e: any) {
    return Response.json({ error: true, message: e.message })
  }
}
