// camada de aprendizado contínuo

export function learnFromMetrics(items: any[]) {
  return items.map(item => {
    const ctr = item.views > 0 ? item.clicks / item.views : 0

    let action = "hold"
    if (ctr > 0.15) action = "scale"
    else if (ctr > 0.08) action = "optimize"
    else action = "kill"

    return {
      ...item,
      ctr,
      action
    }
  })
}

export function generateNextTopics(items: any[]) {
  return items
    .filter(i => i.action === "scale")
    .map(i => `variação de ${i.topic || "conteúdo"}`)
}
