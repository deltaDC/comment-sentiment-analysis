# STEP 3 PLAN — MICROSERVICE API (30%)

**Criteria:** API & xử lý — code sạch, edge cases, response chuẩn.

**Output:** FastAPI service serving fine-tuned PhoBERT, packaged as Docker image.

---

## Scope

- REST API with `POST /predict` and `GET /health`.
- Load **primary model** from `model/artifacts/phobert/` (baseline stays offline for comparison report only).
- Dockerize API for reproducible deploy.
- Edge-case handling per assignment.

Out of scope: Flask UI (step 4), training scripts (step 2).

---

## Project layout

```
api/
├── main.py           # FastAPI app, routes
├── schemas.py        # Pydantic request/response models
├── predictor.py      # Model load + inference
├── config.py         # env vars, paths, limits
└── Dockerfile
```

---

## API design

### `POST /predict`

**Request:**
```json
{ "text": "VF3 giá tốt, đi phố tiện" }
```

**Response 200:**
```json
{
  "sentiment": "positive",
  "confidence": 0.91,
  "probabilities": {
    "positive": 0.91,
    "negative": 0.03,
    "neutral": 0.06
  }
}
```

- `sentiment` — argmax class label.
- `confidence` — softmax probability of predicted class.
- `probabilities` — all three classes (useful for UI/debug).

### `GET /health`

```json
{ "status": "ok", "model_loaded": true, "model": "phobert" }
```

### `GET /docs`

FastAPI auto Swagger UI (built-in).

---

## Edge cases

| Case | HTTP | Behavior |
|------|------|----------|
| Empty / whitespace `text` | 400 | `{ "detail": "Text cannot be empty" }` |
| Missing `text` field | 422 | Pydantic validation error |
| `text` not string | 422 | Pydantic validation error |
| Text > `MAX_TEXT_LEN` (512) | 200 | Truncate to 512 chars; response header `X-Text-Truncated: true` |
| Special chars, emoji, no diacritics | 200 | Pass through to model |
| Model not loaded at startup | 503 | `/health` shows `model_loaded: false`; `/predict` returns 503 |

---

## `predictor.py`

**Responsibilities:**
1. Load tokenizer + model from `MODEL_PATH` (default `/app/model/artifacts/phobert`).
2. Map label ids ↔ `positive` / `negative` / `neutral` (persist mapping from training).
3. `predict(text: str) -> dict` — tokenize, forward pass, softmax, return structured result.

**Performance notes:**
- Load model **once** at startup (`lifespan` or `@app.on_event("startup")`).
- CPU inference OK for demo; note latency in README (~100–300ms per request on CPU).

**Label id file:** save `model/artifacts/phobert/label_map.json` during training:

```json
{ "0": "negative", "1": "neutral", "2": "positive" }
```

---

## Config (`config.py` + env)

| Env var | Default | Description |
|---------|---------|-------------|
| `MODEL_PATH` | `/app/model/artifacts/phobert` | Path to HF model folder |
| `MAX_TEXT_LEN` | `512` | Max characters before truncate |
| `LOG_LEVEL` | `info` | uvicorn log level |

---

## Dockerfile — `api/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# ponytail: 3.11 for torch/transformers stability (host may use 3.14 for dev)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api/ ./api/
COPY model/artifacts/phobert/ ./model/artifacts/phobert/

ENV MODEL_PATH=/app/model/artifacts/phobert
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`requirements-api.txt`** (minimal runtime deps):
```
fastapi
uvicorn[standard]
transformers>=4.46,<5
torch
pydantic
```

Model baked into image at build time — reviewer needs no training step to run API.

---

## Local dev (without Docker)

```bash
source .venv/bin/activate
export MODEL_PATH=model/artifacts/phobert
uvicorn api.main:app --reload --port 8000
```

Test:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "VF8 pin trâu, chạy sướng"}'
```

---

## Error response format

Consistent JSON errors:

```json
{ "detail": "Text cannot be empty" }
```

No stack traces in production responses; log internally.

---

## Deliverables

| File | Description |
|------|-------------|
| `api/main.py` | FastAPI app |
| `api/schemas.py` | Pydantic models |
| `api/predictor.py` | Inference logic |
| `api/config.py` | Settings |
| `api/Dockerfile` | API container |
| `requirements-api.txt` | Runtime deps for container |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Large Docker image (~1.5GB with torch) | Document size; use `python:3.11-slim`; multi-stage if needed later |
| Slow cold start (model load) | `/health` only ready after load; note in README |
| Label id mismatch train vs API | Save `label_map.json` at train time; load in predictor |

---

## Execution order

1. Implement `predictor.py` — load artifacts, single-text inference
2. Implement `schemas.py` + `main.py` routes
3. Add edge-case handling + tests (manual curl or pytest)
4. Write `api/Dockerfile` + `requirements-api.txt`
5. Build and smoke test: `docker build -f api/Dockerfile -t sentiment-api .`
6. Hand off image/service name to step 4 compose file
