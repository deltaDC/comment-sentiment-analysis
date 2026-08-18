FROM python:3.11-slim

WORKDIR /app

# ponytail: 3.11 for torch/transformers stability (host may use 3.14 for dev)
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api/ ./api/
COPY model/artifacts/phobert_weighted/ ./model/artifacts/phobert_weighted/

ENV MODEL_PATH=/app/model/artifacts/phobert_weighted
EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
