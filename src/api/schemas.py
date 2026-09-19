from pydantic import BaseModel
from typing import List, Dict

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    probabilities: Dict[str, float]
    processing_time: float

class BatchAnalysisRequest(BaseModel):
    texts: List[str]

class BatchAnalysisResponse(BaseModel):
    results: List[AnalysisResponse]
    total: int
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    version: str
