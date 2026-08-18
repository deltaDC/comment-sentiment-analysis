import { NextResponse } from "next/server";

import { INVALID_TEXT_MSG, textHasInvalidChars } from "@/lib/validation";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const text = typeof body?.text === "string" ? body.text : "";

    if (!text.trim()) {
      return NextResponse.json({ detail: "Text cannot be empty" }, { status: 400 });
    }
    if (textHasInvalidChars(text)) {
      return NextResponse.json({ detail: INVALID_TEXT_MSG }, { status: 400 });
    }

    const res = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    const response = NextResponse.json(data, { status: res.status });

    const truncated = res.headers.get("X-Text-Truncated");
    if (truncated) {
      response.headers.set("X-Text-Truncated", truncated);
    }

    return response;
  } catch {
    return NextResponse.json(
      { detail: "API unavailable. Check that the api service is running." },
      { status: 503 },
    );
  }
}
