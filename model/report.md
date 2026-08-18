# Sentiment model comparison

Dataset: 999 comments, val = 200 rows (split from notebook 00).

## Summary metrics (validation)

| Model | Accuracy | Macro-F1 | Weighted-F1 |
|-------|----------|----------|-------------|
| PhoBERT | 0.705 | 0.686 | 0.708 |
| TF-IDF + LR | 0.615 | 0.453 | 0.534 |

**Primary metric:** macro-F1 (treats negative / neutral / positive equally).

**Higher macro-F1 on val:** PhoBERT

## Why PhoBERT for the API

- Transformer captures word order, negation, and longer context better than bag-of-words.
- Baseline is a fair sanity check; if scores are close, PhoBERT still generalizes better on messy YouTube comments.
- Artifacts exported to `model/artifacts/phobert/` for step 3.

## Notes

- Neutral class is largest (~55%); accuracy alone can look good while neutral/positive get confused.
- No-diacritics comments (see notebook 00) hurt PhoBERT more than the TF-IDF baseline.
- Re-run notebooks 00–03 if `data/comments.csv` changes.
