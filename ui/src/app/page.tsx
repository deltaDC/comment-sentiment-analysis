import { SentimentForm } from "@/components/SentimentForm";

export default function Home() {
  return (
    <main className="min-h-[100dvh] bg-[var(--surface)] px-4 py-12 md:py-16">
      <div className="mx-auto grid max-w-2xl gap-10">
        <header className="space-y-3">
          <p className="font-mono text-sm tracking-wide text-[var(--accent)]">
            PhoBERT fine-tuned
          </p>
          <h1 className="text-4xl font-semibold tracking-tight text-[var(--text)] md:text-5xl">
            VinFast comment sentiment
          </h1>
          <p className="max-w-[65ch] text-base leading-relaxed text-[var(--text-muted)]">
            Paste a Vietnamese comment about VinFast cars. The model returns
            positive, negative, or neutral with confidence scores.
          </p>
        </header>

        <SentimentForm />

        <footer className="text-sm text-[var(--text-muted)]">
          API docs at{" "}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--accent)] underline-offset-2 hover:underline"
          >
            localhost:8000/docs
          </a>
        </footer>
      </div>
    </main>
  );
}
