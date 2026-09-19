import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.schemas import AnalysisRequest, AnalysisResponse, BatchAnalysisRequest, BatchAnalysisResponse, HealthResponse
from src.models.sentiment_model import SentimentAnalyzer

app = FastAPI(title="distro-orchestra API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentAnalyzer()

@app.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalysisRequest):
    start = time.time()
    try:
        res = analyzer.analyze(req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    processing_time = time.time() - start
    return AnalysisResponse(**res, processing_time=processing_time)

@app.post("/analyze/batch", response_model=BatchAnalysisResponse)
def analyze_batch(req: BatchAnalysisRequest):
    start = time.time()
    try:
        results_raw = analyzer.analyze_batch(req.texts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    processing_time = time.time() - start
    
    results = [AnalysisResponse(**r, processing_time=processing_time/len(req.texts)) for r in results_raw]
    return BatchAnalysisResponse(
        results=results,
        total=len(results),
        processing_time=processing_time
    )

@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", version="1.0.0")
