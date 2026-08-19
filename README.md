# VinFast comment sentiment

Vietnamese YouTube comments about VinFast cars, labeled `positive` / `negative` / `neutral`. This is just a learning pass - not an expert AI-engineer project.

Fine-tuned weights are **not** in git (too big). Train on your machine, then run the stack.

How it is built, and structure: [docs/architecture/architecture.md](docs/architecture/architecture.md).

## For testing convenience
- You can view the deployed project by this URL: https://matgrouptest-ui-658869844900.asia-southeast1.run.app

## Need

- Docker + Docker Compose (API + UI)
- Host Python venv + Jupyter (train). Use `requirements.txt`. `requirements-api.txt` is for the API image only.
- CPU is enough, slow. GPU optional.

## 1. Train (required before compose)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook model/notebooks/
```

Run in order:

1. `00_data_prep_and_split.ipynb`
2. `01_01_train_phobert_with_weighted_data.ipynb` (prefer this for the API)
3. `02_train_baseline.ipynb`
4. `03_evaluate_and_compare.ipynb`

Prefer the weighted notebook: the dataset is imbalanced (neutral is the majority). Without class weights the model hugs that class.

Optional compare: `01_train_phobert.ipynb` writes `model/artifacts/phobert/`. The API image does **not** copy that folder.

Train is done when `model/artifacts/phobert_weighted/model.safetensors` exists. Metrics: [model/report.md](model/report.md).

## 2. Run

```bash
docker compose up -d --build
```

- UI: [http://localhost:3000](http://localhost:3000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

No weights → image build fails on `COPY`, or `/health` shows `model_loaded: false` and `/predict` returns 503. Train first.

## Use

UI: paste a comment, submit, read sentiment + confidence.

```bash
curl -s http://localhost:8000/health

curl -s http://localhost:8000/predict \
  -H 'Content-Type: application/json' \
  -d '{"text": "VF3 giá tốt, đi phố tiện"}'
```

Empty / whitespace text → `400`. Text longer than 512 chars → truncated; response header `X-Text-Truncated: true`.