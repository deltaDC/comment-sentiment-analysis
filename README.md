# Comment sentiment analysis

Vietnamese YouTube comments about VinFast cars, labeled `positive` / `negative` / `neutral`. Fine-tuned **PhoBERT** serves predictions through a **FastAPI** backend and an optional **Next.js** demo UI.

This repo is a learning / test project — not production-grade ML infra. The goal is a working end-to-end stack another developer can inspect, test, or rebuild without asking for extra context.

**Architecture and repo layout:** [docs/architecture/architecture.md](docs/architecture/architecture.md)  
**Model metrics and rationale:** [model/report.md](model/report.md)  
**Original assignment spec (Vietnamese):** [docs/assignment/Test-Data-System-DEV.md](docs/assignment/Test-Data-System-DEV.md)

---



## What you get


| Piece        | Description                                                                 |
| ------------ | --------------------------------------------------------------------------- |
| **Data**     | ~999 labeled comments in `data/comments.csv` (also JSON exports)            |
| **Training** | Jupyter notebooks under `model/notebooks/`                                  |
| **Model**    | PhoBERT fine-tuned with class weights → `model/artifacts/phobert_weighted/` |
| **API**      | FastAPI — `GET /health`, `POST /predict`                                    |
| **UI**       | Next.js form — paste text, see sentiment + confidence                       |
| **Compose**  | `docker compose up` runs API + UI together                                  |


> **Note:** Trained weights are **not** in git (too large). You either use the live demo, download a pre-trained bundle (see below), or train locally before running Docker.

---



## Choose your path

Pick one of three ways to work with this project. You do **not** need all three.


| #   | Path                                                          | Best for                                             | Training required?    |
| --- | ------------------------------------------------------------- | ---------------------------------------------------- | --------------------- |
| 1   | [Live demo](#1-live-demo-fastest)                             | Quick test, API smoke check, UI walkthrough          | No                    |
| 2   | [Google Drive bundle](#2-google-drive-bundle-pre-trained)     | Run the full stack locally without training          | No (weights included) |
| 3   | [Manual implementation](#3-manual-implementation-from-source) | Understand the pipeline, retrain, or extend the code | Yes                   |


---



## 1. Live demo (fastest)

Everything is already deployed on Google Cloud Run — UI, API, and loaded model weights.


| Service                | URL                                                                                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **UI**                 | [https://matgrouptest-ui-658869844900.asia-southeast1.run.app](https://matgrouptest-ui-658869844900.asia-southeast1.run.app)                 |
| **API docs (Swagger)** | [https://matgrouptest-api-658869844900.asia-southeast1.run.app/docs](https://matgrouptest-api-658869844900.asia-southeast1.run.app/docs)     |
| **Health check**       | [https://matgrouptest-api-658869844900.asia-southeast1.run.app/health](https://matgrouptest-api-658869844900.asia-southeast1.run.app/health) |




### Try the UI

1. Open the UI link above.
2. Paste a Vietnamese comment about VinFast (e.g. `VF3 giá tốt, đi phố tiện`).
3. Click **Analyze sentiment**.
4. Read the predicted label (`positive` / `negative` / `neutral`) and confidence scores.

Allowed characters: letters, numbers, and `. , ? ! : ; ' " - ( )`. Text longer than 512 characters is truncated server-side.

### Try the API directly

```bash
# Health — model_loaded should be true
curl -s https://matgrouptest-api-658869844900.asia-southeast1.run.app/health

# Predict
curl -s https://matgrouptest-api-658869844900.asia-southeast1.run.app/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "VF3 giá tốt, đi phố tiện"}'
```

Example response:

```json
{
  "sentiment": "positive",
  "confidence": 0.87,
  "probabilities": {
    "positive": 0.87,
    "negative": 0.05,
    "neutral": 0.08
  }
}
```

**Edge cases the API handles:**


| Input                         | Result                                              |
| ----------------------------- | --------------------------------------------------- |
| Empty or whitespace-only text | `400` — `"Text cannot be empty"`                    |
| Disallowed special characters | `400` — validation error                            |
| Text longer than 512 chars    | Truncated; response header `X-Text-Truncated: true` |
| Model not loaded (local only) | `503` — `"Model not loaded"`                        |


Use this path when you only need to verify behavior or demo the product. No clone, Docker, or GPU required.

---



## 2. Google Drive bundle (pre-trained)

Download a zip that includes **source code + trained model weights**, so you can run the stack locally **without** retraining.

> **Link:** *[(Source code + model)](https://drive.google.com/file/d/1AbIpMCgjq7carMnWSESM4YzqS-VAa1u4/view?usp=sharing)*



### What is inside the bundle

```
matgrouptest/
├── (full repo source)
└── model/artifacts/phobert_weighted/
    ├── model.safetensors      ← fine-tuned PhoBERT weights
    ├── config.json
    ├── tokenizer files
    └── ...
```

The bundle matches what the deployed API uses (`phobert_weighted`, not the unweighted comparison run).

### Steps

1. Download and unzip the archive from the Google Drive link above.
2. Open a terminal in the project root.
3. Make sure **Docker** and **Docker Compose** are installed.
4. Verify weights exist:
  ```bash
   ls model/artifacts/phobert_weighted/model.safetensors
  ```
5. Start the stack:
  ```bash
   docker compose up -d --build
  ```
6. Open locally:
  - UI: [http://localhost:3000](http://localhost:3000)
  - API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
7. Stop when done:
  ```bash
   docker compose down
  ```

If `model.safetensors` is missing, the API image build may fail on `COPY`, or `/health` will show `"model_loaded": false`.

---



## 3. Manual implementation (from source)

Full path: clone the repo, train the model on your machine, then run Docker Compose. Use this to understand the pipeline, change hyperparameters, or retrain on updated data.

### Prerequisites


| Tool                          | Used for                                              |
| ----------------------------- | ----------------------------------------------------- |
| **Git**                       | Clone / pull source                                   |
| **Python 3.10+** and **venv** | Data scripts + Jupyter training                       |
| **Docker + Docker Compose**   | Run API + UI after training                           |
| **Jupyter**                   | Training notebooks (installed via `requirements.txt`) |


**Hardware:** CPU is enough but slow for training. GPU optional and speeds up PhoBERT fine-tuning.

Two requirement files:

- `requirements.txt` — host training + data pipeline
- `requirements-api.txt` — API Docker image only (do not need to install locally for Compose)

---



### Step 0 — Get the code

**First time (clone):**

```bash
git clone https://github.com/deltaDC/comment-sentiment-analysis.git
cd comment-sentiment-analysis
```

**Already cloned (update to latest):**

```bash
cd comment-sentiment-analysis   # or your local folder name
git pull origin main
```

If you forked the repo, replace the remote URL with your fork and pull from your default branch.

---



### Step 1 — Python environment (training)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---



### Step 2 — Train the model (required before Compose)

Training runs on the **host**, not inside Docker. Notebooks stay outside Compose so you can use Jupyter, CPU/GPU, and long jobs freely.

```bash
jupyter notebook model/notebooks/
```

Run notebooks **in order**:


| Order | Notebook                                       | Purpose                                                   |
| ----- | ---------------------------------------------- | --------------------------------------------------------- |
| 1     | `00_data_prep_and_split.ipynb`                 | Load CSV, split train/val, save indices                   |
| 2     | `01_01_train_phobert_with_weighted_data.ipynb` | **Primary model** — PhoBERT + class weights (used by API) |
| 3     | `02_train_baseline.ipynb`                      | TF-IDF + logistic regression baseline                     |
| 4     | `03_evaluate_and_compare.ipynb`                | Compare models; metrics in `model/report.md`              |


**Important:**

- Prefer the **weighted** notebook (`01_01_...`). The dataset is imbalanced (~55% neutral). Without class weights the model tends to predict neutral too often.
- Optional comparison: `01_train_phobert.ipynb` writes to `model/artifacts/phobert/`. The API image does **not** copy that folder — only `phobert_weighted/`.

**Training is done when this file exists:**

```bash
ls model/artifacts/phobert_weighted/model.safetensors
```

See [model/report.md](model/report.md) for validation metrics (macro-F1 is the primary metric).

---



### Step 3 — Run API + UI

From the repo root (with weights in place):

```bash
docker compose up -d --build
```


| Service  | Local URL                                                    |
| -------- | ------------------------------------------------------------ |
| UI       | [http://localhost:3000](http://localhost:3000)               |
| API docs | [http://localhost:8000/docs](http://localhost:8000/docs)     |
| Health   | [http://localhost:8000/health](http://localhost:8000/health) |


**Verify:**

```bash
curl -s http://localhost:8000/health

curl -s http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "VF3 giá tốt, đi phố tiện"}'
```

**Stop:**

```bash
docker compose down
```

---



### Optional — Data pipeline from scratch

Labeled data is already in `data/comments.csv`. To regenerate from YouTube comments:

```bash
source .venv/bin/activate
python scripts/main.py
```

Scripts live under `scripts/` (scrape → clean → export). See [docs/plan/step-1-prepare-data-plan.md](docs/plan/step-1-prepare-data-plan.md) for details.

After changing data, re-run notebooks `00` through `03`.

---



### Optional — CLI predict (no Docker)

Quick local inference without Compose:

```bash
source .venv/bin/activate
python model/predict_cli.py "VF3 giá tốt, đi phố tiện"
```

---



## Project structure

```
.
├── api/                 # FastAPI service (POST /predict, GET /health)
├── ui/                  # Next.js demo (proxies /api/predict → API)
├── model/
│   ├── notebooks/       # Train + evaluate (Jupyter)
│   ├── artifacts/       # Weights (gitignored — train or use Drive bundle)
│   └── report.md        # Metrics summary
├── data/                # Labeled comments (CSV / JSON)
├── scripts/             # Scrape, clean, export pipeline
├── docs/
│   ├── architecture/    # How the stack fits together
│   ├── assignment/      # Original test requirements
│   └── plan/            # Step-by-step build notes
├── docker-compose.yml   # api:8000 + ui:3000
├── requirements.txt     # Host: training + notebooks
└── requirements-api.txt # API Docker image only
```

---



## Troubleshooting


| Symptom                                          | Likely cause                        | Fix                                                        |
| ------------------------------------------------ | ----------------------------------- | ---------------------------------------------------------- |
| Docker build fails on `COPY model/artifacts/...` | Weights missing                     | Train (path 3) or use Drive bundle (path 2)                |
| `/health` → `"model_loaded": false`              | Weights not in image / wrong path   | Check `model/artifacts/phobert_weighted/model.safetensors` |
| `/predict` → `503`                               | Model failed to load at startup     | Check API container logs: `docker compose logs api`        |
| UI loads but predict fails                       | API not healthy                     | Wait for healthcheck or check `docker compose ps`          |
| Training very slow                               | CPU-only                            | Expected; use GPU or reduce epochs in notebook             |
| Neutral predicted too often                      | Unweighted model or imbalanced data | Use `01_01_train_phobert_with_weighted_data.ipynb`         |


---



## Limits (read before trusting predictions)

- Trained on VinFast-style YouTube comments only; general Vietnamese is untested.
- Sarcasm and mixed sentiment are weak spots.
- Comments without diacritics hurt PhoBERT more than the TF-IDF baseline.
- Not production-hardened (auth, rate limits, monitoring, etc.).

---



## Quick reference


| Goal                     | Command / link                                                          |
| ------------------------ | ----------------------------------------------------------------------- |
| Test without setup       | [Live UI](https://matgrouptest-ui-658869844900.asia-southeast1.run.app) |
| Run locally with weights | Google Drive bundle → `docker compose up -d --build`                    |
| Clone repo               | `git clone https://github.com/deltaDC/comment-sentiment-analysis.git`   |
| Update repo              | `git pull origin main`                                                  |
| Train                    | `jupyter notebook model/notebooks/` (run 00 → 01_01 → 02 → 03)          |
| Run stack                | `docker compose up -d --build`                                          |


