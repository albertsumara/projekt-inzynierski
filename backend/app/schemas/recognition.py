
from pydantic import BaseModel, Field


class RecognitionItem(BaseModel):
    class_id: str
    product: str
    confidence: float = Field(ge=0.0, le=1.0)


class RecognitionResponse(BaseModel):
    filename: str
    predictions: list[RecognitionItem]
