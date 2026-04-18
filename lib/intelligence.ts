// inteligência real (loop fechado)

export function scoreContent(metrics: {
  views: number
  clicks: number
}) {
  const ctr = metrics.views > 0 ? metrics.clicks / metrics.views : 0
  const score = ctr * 100

  return {
    ctr,
    score,
    decision: score > 70 ? "scale" : "kill"
  }
}

export function decideNextAction(score: number) {
  if (score > 80) return "replicate"
  if (score > 60) return "optimize"
  return "discard"
}
