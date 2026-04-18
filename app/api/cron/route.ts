import { NextResponse } from "next/server";

export async function GET() {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL}/api/pipeline`, {
      method: "POST"
    });

    const data = await res.json();

    return NextResponse.json({
      status: "cron_executed",
      pipeline: data
    });
  } catch (e) {
    return NextResponse.json({ error: true, message: e.message });
  }
}
