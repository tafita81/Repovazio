export async function GET() {
  return Response.json({
    status: "online",
    env: "production",
    build: "stable",
    time: new Date().toISOString()
  })
}
