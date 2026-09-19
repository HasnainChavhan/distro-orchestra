import os
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        except Exception:
            print("Falling back to distilbert")
            self.model = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def _map_label(self, label: str) -> str:
        label = label.upper()
        if "POS" in label: return "POSITIVE"
        if "NEG" in label: return "NEGATIVE"
        return "NEUTRAL"

    def analyze(self, text: str) -> dict:
        result = self.model(text, return_all_scores=True)[0]
        # result is a list of dicts like [{'label': 'LABEL_0', 'score': 0.1}, ...]
        probs = {}
        for r in result:
            mapped_label = self._map_label(r['label'])
            # If multiple labels map to the same (e.g. in some models), we can just take max or sum, but usually it's 1:1
            probs[mapped_label] = probs.get(mapped_label, 0) + r['score']
        
        # Ensure POSITIVE, NEGATIVE, NEUTRAL are in probs
        for l in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            if l not in probs:
                probs[l] = 0.0

        best_label = max(probs, key=probs.get)
        confidence = probs[best_label]
        
        return {
            "text": text,
            "sentiment": best_label,
            "confidence": confidence,
            "probabilities": probs
        }

    def analyze_batch(self, texts: list) -> list:
        return [self.analyze(t) for t in texts]
