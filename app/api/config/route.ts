export async function GET() {
  return Response.json({
    theme: { primaryColor: "#00ff88", background: "#0b0f1a" },
    widgets: { clock: true },
    texts: { title: "Dashboard" }
  });
}

export async function POST() {
  return Response.json({ ok: true });
}
