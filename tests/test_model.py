import pytest
from src.models.sentiment_model import SentimentAnalyzer

@pytest.fixture(scope="module")
def analyzer():
    return SentimentAnalyzer()

def test_analyze(analyzer):
    res = analyzer.analyze("This is great!")
    assert "sentiment" in res
    assert res["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert "confidence" in res
    assert 0 <= res["confidence"] <= 1.0

def test_analyze_batch(analyzer):
    res = analyzer.analyze_batch(["Good", "Bad"])
    assert len(res) == 2
    assert res[0]["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    assert res[1]["sentiment"] in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
