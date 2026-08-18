"""FastAPI sentiment API."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response

from api.config import LOG_LEVEL, MAX_TEXT_LEN, MODEL_NAME
from api.predictor import Predictor
from api.schemas import HealthResponse, PredictRequest, PredictResponse, Probabilities
from api.validation import INVALID_TEXT_MSG, text_has_invalid_chars

logging.basicConfig(level=LOG_LEVEL.upper())
logger = logging.getLogger(__name__)

predictor = Predictor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        predictor.load()
    except Exception:
        logger.exception("Failed to load model at startup")
    yield


app = FastAPI(title="Sentiment API", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=predictor.loaded,
        model=MODEL_NAME,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest, response: Response) -> PredictResponse:
    if not predictor.loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    text = body.text
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if text_has_invalid_chars(text):
        raise HTTPException(status_code=400, detail=INVALID_TEXT_MSG)

    truncated = False
    if len(text) > MAX_TEXT_LEN:
        text = text[:MAX_TEXT_LEN]
        truncated = True

    result = predictor.predict(text)

    if truncated:
        response.headers["X-Text-Truncated"] = "true"

    return PredictResponse(
        sentiment=result["sentiment"],
        confidence=result["confidence"],
        probabilities=Probabilities(**result["probabilities"]),
    )
