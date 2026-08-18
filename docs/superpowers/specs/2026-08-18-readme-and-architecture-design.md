# README + architecture docs

**Date:** 2026-08-18  
**Status:** approved in brainstorm; waiting user review of this file  
**Goal:** Other-dev can train, then `docker compose up -d --build`, then use UI/API — without asking. Weights stay out of git.

This is a hiring take-home for Vietnamese YouTube comment sentiment (VinFast). Author is a developer learning the stack, not an ML specialist. Docs should sound like that: honest, short, no research-paper tone.

---

## Locked decisions

| Topic | Choice |
|-------|--------|
| Language | English only |
| README role | Run + use only. Lives at **repo root**, next to `docker-compose.yml` |
| Architecture | One file: `docs/architecture/architecture.md` (not a README inside that folder) |
| Plans | Keep `docs/plan/` as build history. Do not rewrite them in this work |
| Train vs compose | Honest two-step: train on host first, then compose. Compose is not clone-and-run |
| API model | Prefer **weighted** PhoBERT (`model/artifacts/phobert_weighted/`) because labels are imbalanced. Unweighted notebook stays as comparison |
| Local-without-Docker | Out of README. Compose is how we run the stack |
| Weights in git | No. `.gitignore` already excludes artifact dirs |

`docker-compose.yml` `MODEL_PATH` is **already** `/app/model/artifacts/phobert_weighted` (changed during brainstorm). Spec does not ask to revert that.

---

## Problem this work fixes

Today a clone cannot serve the model: artifacts are gitignored, and the API image still **COPY**s `model/artifacts/phobert/` while compose expects `phobert_weighted` inside the container. README does not exist. Architecture story lives only in `docs/plan/` (partly stale: Flask vs current Next.js).

---

## Deliverables

| File | Action |
|------|--------|
| `README.md` | Create at repo root |
| `docs/architecture/architecture.md` | Create |
| `api/Dockerfile` | COPY + `ENV MODEL_PATH` → `phobert_weighted` |
| `api/config.py` | Default `MODEL_PATH` → `phobert_weighted`; `MODEL_NAME` → `"phobert_weighted"` so `/health` matches the artifact dir |

No new Docker services. No download script. No train-in-Docker. No UI changes. No notebook edits. Do not move or rewrite `docs/plan/`.

---

## `README.md` outline (runbook)

Keep it thin. Order matters: train before compose.

### 1. What this is (5–8 lines)

- Vietnamese comment sentiment on VinFast YouTube comments (`positive` / `negative` / `neutral`).
- Learning project by a developer, not an expert AI engineer.
- Fine-tuned weights are **not** in the repo (size). You train locally, then run the stack.
- Link: [Architecture](docs/architecture/architecture.md).

### 2. Need on the machine

- Docker + Docker Compose (stack).
- Host Python venv + Jupyter (train). Point at existing `requirements.txt` for notebooks; `requirements-api.txt` is image-only.
- CPU is enough, slow. GPU optional, not required.

### 3. Train (required before compose)

Notebooks under `model/notebooks/`, in order:

1. `00_data_prep_and_split.ipynb`
2. **Prefer** `01_01_train_phobert_with_weighted_data.ipynb` — class weights because the dataset is imbalanced (neutral is majority; unweighted training hugs that class).
3. `02_train_baseline.ipynb` (comparison)
4. `03_evaluate_and_compare.ipynb`

Alternative for comparison only: `01_train_phobert.ipynb` → `model/artifacts/phobert/`. The **API image does not copy that folder.**

Done when `model/artifacts/phobert_weighted/model.safetensors` exists (`api/predictor.py` refuses to load without that file).

One link to numbers: `model/report.md`.

### 4. Run stack

```bash
docker compose up -d --build
```

- UI: http://localhost:3000
- API docs: http://localhost:8000/docs

If artifacts are missing, build or API start **fails**. That is expected. Do not hide it.

### 5. Use

- UI: paste a comment → sentiment + confidence.
- API: `POST /predict` with a small curl example; `GET /health`.
- Empty / whitespace text → 400. Text longer than `MAX_TEXT_LEN` (512) → truncated, `X-Text-Truncated: true`.

### Explicitly not in README

Mermaid, folder tree, “why FastAPI / PhoBERT / Next.js”, scrape pipeline story, metric tables. Those belong in architecture or `model/report.md`.

---

## `docs/architecture/architecture.md` outline

One page. How / structure / why. No clone-run steps.

### How we built

Host pipeline, then two containers:

```
YouTube VF comments → scripts/ → data/comments.csv
        → model/notebooks (train on host)
        → model/artifacts (gitignored)
        → api image (COPY weighted weights at build)
Browser → ui:3000 → /api/predict proxy → api:8000 → PhoBERT
```

Training stays on the host so Jupyter, CPU/GPU, and long jobs are not stuffed into Compose. Compose only serves.

Include a mermaid flowchart matching the above (data → notebooks → artifacts → api; browser → ui → api).

### Structure

Document the **current** tree, not the old Flask spec in `docs/plan/00-design-spec.md`:

| Path | Job |
|------|-----|
| `data/` | Labeled CSV/JSON |
| `scripts/` | Scrape / clean / export |
| `model/notebooks/` | Train + compare (`.ipynb` on purpose: see loss and confusion inline) |
| `model/artifacts/` | Weights, gitignored |
| `api/` | FastAPI `POST /predict`, `GET /health` |
| `ui/` | Next.js demo; server-side proxy so the browser never uses Docker-internal hostnames |
| `docs/plan/` | How it was planned (may be stale vs Next.js) |
| `docs/architecture/architecture.md` | This page |
| `docker-compose.yml` | `api` + `ui` |

### Why

- **PhoBERT** — Vietnamese tokenizer; fine-tune on a small labeled set. TF-IDF + LR baseline so BERT is a comparison, not a vibe.
- **Class weights** — labels not equal; prefer `phobert_weighted` for the API.
- **Notebooks** — training progress visible; no hidden `.py` train scripts.
- **FastAPI** — typed, OpenAPI `/docs`, small service.
- **Next.js** — optional demo UI (assignment UI was optional); proxy to FastAPI.
- **Compose** — same stack after train.
- **No weights in git** — size. Other-dev trains.

### Limits (short)

- Domain: VinFast-style comments; general Vietnamese untested.
- Sarcasm / mixed sentiment weak.
- CPU training is slow.
- Numbers live in `model/report.md`. Step-by-step build notes live in `docs/plan/`.

---

## Code alignment (must match docs)

Compose env is already:

```yaml
MODEL_PATH: /app/model/artifacts/phobert_weighted
```

Still wrong until Dockerfile + API default match:

| File | Change |
|------|--------|
| `api/Dockerfile` | `COPY model/artifacts/phobert_weighted/ ./model/artifacts/phobert_weighted/` and `ENV MODEL_PATH=/app/model/artifacts/phobert_weighted` |
| `api/config.py` | Default `MODEL_PATH` → `.../phobert_weighted`; `MODEL_NAME` → `"phobert_weighted"` |

Unweighted `model/artifacts/phobert/` stays on disk for notebook comparison. It is **not** copied into the API image.

Missing weights: Docker `COPY` fails the build, or the API starts with model not loaded (`GET /health` `model_loaded: false`, `POST /predict` 503). README states train-first. Do not add a custom error-entrypoint.

`model/config.py` and `model/predict_cli.py` already point at `phobert_weighted`. Leave them.

---

## Out of scope

- Retraining or changing notebooks
- Download / Git LFS for weights
- Local venv + `npm run dev` runbook in README
- Rewriting `docs/plan/` Flask leftovers
- Tests/CI for markdown
- Committing `model/artifacts/`

---

## Success

- Root `README.md` is enough to train (prefer weighted) then compose then open UI + API docs.
- `docs/architecture/architecture.md` answers how / folder map / why, and README links it.
- After train, `docker compose up -d --build` copies **weighted** artifacts; `MODEL_PATH` in compose, Dockerfile, and `api/config.py` is the same folder.
- Weights remain gitignored.

---

## Check

After implementation: every path named in README exists; architecture links work; the three serve-path strings are identical (`phobert_weighted`). Optional smoke only if weights already exist on this machine: `GET /health` with `model_loaded: true`. Do not invent CI.
