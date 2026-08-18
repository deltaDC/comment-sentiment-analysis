"use client";

import { FormEvent, useState } from "react";

import { INVALID_TEXT_MSG, textHasInvalidChars } from "@/lib/validation";

const MAX_LEN = 512;

type Probabilities = {
  positive: number;
  negative: number;
  neutral: number;
};

type PredictResult = {
  sentiment: string;
  confidence: number;
  probabilities: Probabilities;
};

const SENTIMENT_STYLE: Record<string, string> = {
  positive: "bg-emerald-500/15 text-emerald-400 ring-emerald-500/30",
  negative: "bg-red-500/15 text-red-400 ring-red-500/30",
  neutral: "bg-zinc-500/15 text-zinc-300 ring-zinc-500/30",
};

const BAR_COLOR: Record<string, string> = {
  positive: "bg-emerald-500",
  negative: "bg-red-500",
  neutral: "bg-zinc-400",
};

function validate(text: string): string | null {
  if (!text.trim()) return "Comment cannot be empty.";
  if (textHasInvalidChars(text)) return INVALID_TEXT_MSG;
  if (text.length > MAX_LEN) return `Comment must be at most ${MAX_LEN} characters.`;
  return null;
}

function parseApiError(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail[0]?.msg) {
    return String(detail[0].msg).replace(/^Value error,\s*/i, "");
  }
  return "Prediction failed.";
}

export function SentimentForm() {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResult | null>(null);
  const [truncated, setTruncated] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setResult(null);
    setTruncated(false);

    const validationError = validate(text);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(parseApiError(data.detail));
        return;
      }

      setResult(data);
      if (res.headers.get("X-Text-Truncated") === "true") {
        setTruncated(true);
      }
    } catch {
      setError("Could not reach the API. Try again later.");
    } finally {
      setLoading(false);
    }
  }

  const charCount = text.length;
  const nearLimit = charCount > MAX_LEN * 0.9;

  return (
    <div className="space-y-6">
      <form
        onSubmit={handleSubmit}
        className="rounded-2xl border border-[var(--border)] bg-[var(--surface-elevated)] p-6 shadow-sm"
        noValidate
      >
        <div className="flex flex-col gap-2">
          <label htmlFor="comment" className="text-sm font-medium text-[var(--text)]">
            Comment
          </label>
          <textarea
            id="comment"
            name="comment"
            rows={5}
            value={text}
            onChange={(e) => {
              const next = e.target.value;
              setText(next);
              const validationError = validate(next);
              setError(validationError);
            }}
            placeholder="VF8 pin trâu, chạy sướng"
            aria-invalid={error ? true : undefined}
            aria-describedby={error ? "comment-error" : "comment-hint"}
            className="w-full resize-y rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-[var(--text)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]/30"
          />
          <div className="flex items-center justify-between text-sm">
            <p id="comment-hint" className="text-[var(--text-muted)]">
              Letters, numbers, and . , ? ! : ; &apos; &quot; - ( ) only
            </p>
            <span
              className={
                nearLimit || charCount > MAX_LEN
                  ? "font-mono text-amber-500"
                  : "font-mono text-[var(--text-muted)]"
              }
            >
              {charCount}/{MAX_LEN}
            </span>
          </div>
          {error && (
            <p id="comment-error" role="alert" className="text-sm text-red-400">
              {error}
            </p>
          )}
        </div>

        <button
          type="submit"
          disabled={loading || !!validate(text)}
          className="mt-5 w-full rounded-xl bg-[var(--accent)] px-4 py-3 text-sm font-medium text-white transition active:scale-[0.98] hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Analyzing..." : "Analyze sentiment"}
        </button>
      </form>

      {loading && (
        <div
          className="animate-pulse space-y-4 rounded-2xl border border-[var(--border)] bg-[var(--surface-elevated)] p-6"
          aria-busy="true"
          aria-label="Loading result"
        >
          <div className="h-8 w-32 rounded-lg bg-[var(--border)]" />
          <div className="space-y-3">
            <div className="h-4 w-full rounded bg-[var(--border)]" />
            <div className="h-4 w-full rounded bg-[var(--border)]" />
            <div className="h-4 w-3/4 rounded bg-[var(--border)]" />
          </div>
        </div>
      )}

      {result && !loading && (
        <section
          className="rounded-2xl border border-[var(--border)] bg-[var(--surface-elevated)] p-6"
          aria-live="polite"
        >
          {truncated && (
            <p className="mb-4 text-sm text-amber-500">
              Input was truncated to {MAX_LEN} characters before analysis.
            </p>
          )}

          <div className="flex flex-wrap items-center gap-3">
            <span
              className={`inline-flex rounded-full px-3 py-1 text-sm font-medium capitalize ring-1 ring-inset ${SENTIMENT_STYLE[result.sentiment] ?? SENTIMENT_STYLE.neutral}`}
            >
              {result.sentiment}
            </span>
            <span className="font-mono text-2xl font-semibold text-[var(--text)]">
              {(result.confidence * 100).toFixed(0)}%
            </span>
            <span className="text-sm text-[var(--text-muted)]">confidence</span>
          </div>

          <div className="mt-6 space-y-3">
            {(["positive", "negative", "neutral"] as const).map((label) => {
              const score = result.probabilities[label];
              return (
                <div key={label} className="grid grid-cols-[80px_1fr_48px] items-center gap-3">
                  <span className="text-sm capitalize text-[var(--text-muted)]">{label}</span>
                  <div className="h-2 overflow-hidden rounded-full bg-[var(--border)]">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${BAR_COLOR[label]}`}
                      style={{ width: `${Math.round(score * 100)}%` }}
                    />
                  </div>
                  <span className="text-right font-mono text-sm text-[var(--text)]">
                    {(score * 100).toFixed(0)}%
                  </span>
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
