# STEP 2 PLAN — BUILD SENTIMENT MODEL (40%)

**Criteria:** Model & phương pháp — lựa chọn phù hợp, đánh giá kết quả, giải thích được quyết định.

**Input:** `data/comments.csv` from step 1 (`comment`, `sentiment`, …).  
**Output:** Fine-tuned PhoBERT (API model) + TF-IDF baseline (comparison) + `model/report.md`.

---

## Important: use Jupyter notebooks, not `.py`

All **training, testing, and model comparison** must be implemented as **Jupyter notebooks** (`.ipynb`) under `model/notebooks/`.

**Why:** See training progress inline — loss per epoch, validation metrics, confusion matrices, sample predictions — without digging through logs.

| Do | Don't |
|----|-------|
| `model/notebooks/01_train_phobert.ipynb` | `model/train_phobert.py` |
| Cells for EDA, train loop, eval plots | Headless scripts with print-only output |
| Export artifacts at end of notebook | Separate export script |

API inference (step 3) stays `.py` — notebooks only produce artifacts in `model/artifacts/`.

---

## Scope

Build and evaluate two approaches on the **same validation split**:

1. **Approach A — Fine-tune PhoBERT** (primary, do first) → used by API in step 3.
2. **Approach B — TF-IDF + Logistic Regression** (baseline, do later) → comparison only.

Out of scope: data collection (step 1), API/Docker (steps 3–4).

---

## Notebook layout

```
model/notebooks/
├── 00_data_prep_and_split.ipynb   # validate, EDA, stratified split
├── 01_train_phobert.ipynb         # approach A — fine-tune + export
├── 02_train_baseline.ipynb        # approach B — TF-IDF + LR + export
└── 03_evaluate_and_compare.ipynb  # both models on val set, report
```

Run in order. Each notebook should have markdown cells explaining **what** and **why** (helps assignment "giải thích được quyết định" score).

---

## Input requirements

From step 1, `data/comments.csv` must have:

| Column | Required | Notes |
|--------|----------|-------|
| `comment` | yes | Raw text |
| `sentiment` | yes | `positive` / `negative` / `neutral` |

Optional columns (`model`, `video_id`, …) used for EDA only.

Expected: **500–1,000** rows, human-reviewed labels.

---

## Environment

- Training runs on the **host venv: `.venv` = Python 3.14** (torch 2.13 supports 3.14; pin libs and smoke-test in notebook 00)
- API/Docker (step 3) can use a separate Python 3.11 image — artifacts are plain files, so the training/API version split is fine **as long as you never re-dump/load `baseline.pkl` across Python major versions** (joblib/pickle compat)
- Libraries:

```
torch
transformers>=4.46,<5    # pin 4.x — most PhoBERT guides target 4.x
datasets                 # optional — can feed Trainer from pandas instead
scikit-learn
pandas
numpy
matplotlib               # plots in notebooks
seaborn                  # confusion matrix heatmap
pyvi                     # approach B only — VN word segmentation
joblib                   # approach B export
jupyter
ipykernel
```

Write shared deps to root `requirements.txt`. Register kernel: `python -m ipykernel install --user --name=matgrouptest`.

---

## Notebook 00 — `00_data_prep_and_split.ipynb`

**Purpose:** Validate input, explore data, create shared train/val split.

**Cells (suggested):**

1. **Load & validate** — read `data/comments.csv`, assert row count 500–1k, no empty/duplicate comments.
2. **EDA** — label distribution bar chart; comment length histogram; samples per VF model.
3. **Stratified split** — 80/20, `random_state=42`, stratify on `sentiment`.
4. **Diacritics check** — measure the % of comments written without diacritics (typical for YouTube data). Report it in a markdown cell; this drives the risk decision in notebook 01.
5. **Save split** — write train/val CSVs or indices to `model/artifacts/split_indices.json`. **Warning cell: if the dataset from step 1 changes later, re-run this notebook from the top** — stale `split_indices.json` will silently corrupt training.
6. **Preview** — show 3 sample comments per label.

**Output artifacts:**
- `model/artifacts/split_indices.json` (or `train.csv` / `val.csv`)
- Inline plots visible in notebook

---

## Notebook 01 — `01_train_phobert.ipynb` (Approach A, do first)

**Purpose:** Fine-tune PhoBERT, evaluate on val set, export model.

**Cells (suggested):**

1. **Load split** — read train/val from notebook 00.
2. **Load pretrained** — `AutoTokenizer` + `AutoModelForSequenceClassification` from `vinai/phobert-base`, `num_labels=3`.
3. **Label map** — assign ids, display mapping, save `model/artifacts/phobert/label_map.json`:

   ```json
   { "0": "negative", "1": "neutral", "2": "positive" }
   ```

4. **Preprocess** — normalize whitespace; **keep Vietnamese diacritics**; tokenize with `max_length=128`.
   - **Diacritics note:** PhoBERT degrades badly on diacritic-free text. `dactriphizer` is not on PyPI (manual GitHub setup) → **skipped**. Decision driven by notebook 00's diacritics %: if high, document the expected accuracy drop and optionally try `trituenhantaoio/bert-base-vietnamese-diacritics-uncased` as a stretch; otherwise proceed as-is.
5. **Train** — HuggingFace `Trainer`:
   - `learning_rate=2e-5`, `weight_decay=0.01`
   - `num_train_epochs=3–5`
   - `per_device_train_batch_size=8`
   - `eval_strategy="epoch"`
   - Early stopping (patience 2)
   - **`load_best_model_at_end=True`** + `metric_for_best_model="f1"` — without this, the exported model is the *last* checkpoint, not the *best*
   - **`save_total_limit=1`** — each checkpoint is ~1.4GB; limit avoids filling the disk
   - **Device note:** use MPS on Apple Silicon with a `try/except` fallback to CPU (MPS can be flaky with some transformers versions)
6. **Training curves** — plot train/val loss per epoch (matplotlib).
7. **Evaluate** — accuracy, macro-F1, per-class F1, confusion matrix heatmap on val set.
8. **Sample predictions** — show 5 correct + 5 wrong predictions (comment, true, pred).
9. **Export** — save best checkpoint to `model/artifacts/phobert/`.

> **No GPU:** markdown cell stating CPU/MPS setup. Estimate 15–45 min/epoch on CPU.

---

## Notebook 02 — `02_train_baseline.ipynb` (Approach B, do later)

**Purpose:** Train TF-IDF + Logistic Regression baseline on **same split** as notebook 01.

**Cells (suggested):**

1. **Load same split** — must use identical train/val indices from notebook 00.
2. **Preprocess** — `pyvi` word segmentation; lowercase; note diacritic-dropped comments in EDA cell.
3. **Pipeline** — `TfidfVectorizer(ngram_range=(1,2), max_features=10000)` → `LogisticRegression(multi_class="multinomial", max_iter=1000)`.
4. **Train** — fit on train set; show top TF-IDF features per class (optional, nice for report).
5. **Evaluate** — same metrics as notebook 01; confusion matrix heatmap.
6. **Sample predictions** — same format as PhoBERT notebook for easy compare.
7. **Export** — `joblib.dump` → `model/artifacts/baseline.pkl`.

---

## Notebook 03 — `03_evaluate_and_compare.ipynb`

**Purpose:** Side-by-side comparison; feed content into `model/report.md`.

**Cells (suggested):**

1. **Load both models** — PhoBERT from `model/artifacts/phobert/`, baseline from `.pkl`.
2. **Run on val set** — predictions from both on identical rows.
3. **Comparison table** — accuracy, macro-F1, weighted-F1, per-class F1.
4. **Confusion matrices** — side-by-side plots.
5. **Error analysis** — comments where models disagree; where BERT wins (negation, long text).
6. **Decision markdown** — why PhoBERT chosen for API (even if baseline close).
7. **Export report** — write summary to `model/report.md` (can `%writefile` or manual copy).

---

## Metrics & rationale

Sentiment data is usually **imbalanced** → accuracy alone misleading.

| Metric | Role |
|--------|------|
| **Macro-F1** | **Primary** — treats all 3 classes equally |
| Weighted-F1 | Secondary — weighted by class frequency |
| Per-class P/R/F1 | Show which label fails (often neutral) |
| Confusion matrix | Visualize neutral ↔ positive confusion |
| Accuracy | Easy headline number; explain why not primary |

Document in notebook 03 markdown + `model/report.md`.

---

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Small dataset (~800) → overfitting | Few epochs, weight decay, early stopping; watch val loss plot |
| PhoBERT not better than baseline | Report honestly in notebook 03; comparison is the point |
| Exporting wrong (last) checkpoint | `load_best_model_at_end=True` + `metric_for_best_model="f1"` |
| Disk full from checkpoints (~1.4GB each) | `save_total_limit=1` |
| Long CPU training | 3 epochs, batch 8, use MPS if available (fall back to CPU on error) |
| Diacritic-free YouTube comments hurt PhoBERT | Measure % in notebook 00; document drop or optional diacritics-restoration model |
| Python 3.14 + torch incompatibility | Pin `transformers<5`; smoke test in notebook 00 |
| Stale `split_indices.json` after data changes | Re-run notebook 00 whenever step 1 data changes |
| Cross-version pickle of `baseline.pkl` (3.14 train vs 3.11 API) | Re-dump `baseline.pkl` inside the API image, or train API-compatible version |
| Notebook outputs not committed | Clear outputs before git OR commit with outputs for reviewer visibility (prefer clear outputs + export artifacts) |
| Label column mismatch | Read `sentiment` column (not `label`) |

---

## Deliverables

| File | Description |
|------|-------------|
| `model/notebooks/00_data_prep_and_split.ipynb` | Validate, EDA, split |
| `model/notebooks/01_train_phobert.ipynb` | PhoBERT fine-tune + eval plots |
| `model/notebooks/02_train_baseline.ipynb` | TF-IDF + LR baseline |
| `model/notebooks/03_evaluate_and_compare.ipynb` | Comparison + error analysis |
| `model/artifacts/phobert/` | Exported HF model + `label_map.json` |
| `model/artifacts/baseline.pkl` | Exported baseline pipeline |
| `model/artifacts/split_indices.json` | Shared train/val indices |
| `model/report.md` | Summary from notebook 03 |

---

## Handoff to step 3

Step 3 API loads from `model/artifacts/phobert/` using `label_map.json`.  
Notebook 01 must save complete HF artifact folder before Docker build.  
Avoid cross-version pickle of `baseline.pkl` between the 3.14 training venv and the API image (re-dump inside the image if needed).

---

## Execution order

1. Notebook 00 — validate data, EDA, create split
2. Notebook 01 — fine-tune PhoBERT, export artifacts
3. Notebook 02 — train baseline on same split
4. Notebook 03 — compare, error analysis, write `model/report.md`
5. Confirm artifacts ready for `api/Dockerfile`
