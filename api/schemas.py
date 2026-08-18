"""Pydantic request/response models."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from api.validation import INVALID_TEXT_MSG, text_has_invalid_chars


class PredictRequest(BaseModel):
    text: str = Field(..., examples=["VF3 giá tốt, đi phố tiện"])

    @field_validator("text")
    @classmethod
    def reject_special_chars(cls, v: str) -> str:
        if text_has_invalid_chars(v):
            raise ValueError(INVALID_TEXT_MSG)
        return v


class Probabilities(BaseModel):
    positive: float
    negative: float
    neutral: float


class PredictResponse(BaseModel):
    sentiment: str
    confidence: float
    probabilities: Probabilities


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model: str
