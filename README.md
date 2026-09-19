# distro-orchestra

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-yellow)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## Problem Statement
Analyzing large volumes of text for sentiment in real-time is computationally expensive and complex to orchestrate. `distro-orchestra` provides a scalable, easy-to-deploy solution using HuggingFace's BERT models, served via FastAPI, with a user-friendly Streamlit dashboard.

## Architecture
```
+----------------+      +----------------+      +---------------------+
|                |      |                |      |                     |
|  Streamlit UI  +----->+   FastAPI      +----->+  HuggingFace BERT   |
|  (Port 8501)   |      |   (Port 8000)  |      |  (Sentiment Model)  |
|                |      |                |      |                     |
+----------------+      +----------------+      +---------------------+
```

## Features
- Real-time text sentiment analysis (Positive, Negative, Neutral)
- Batch processing support via CSV upload
- RESTful API with OpenAPI documentation
- Interactive web dashboard
- Dockerized for easy deployment

## Tech Stack
| Component | Technology |
|---|---|
| Language | Python 3.10 |
| Web Framework | FastAPI |
| UI Dashboard | Streamlit |
| ML Model | HuggingFace Transformers (RoBERTa/DistilBERT) |
| Containerization | Docker & Docker Compose |
| Testing | Pytest |

## Quick Start
```bash
git clone https://github.com/HasnainChavhan/distro-orchestra.git
cd distro-orchestra
docker-compose up -d --build
# API is available at http://localhost:8000
# UI is available at http://localhost:8501
```

## API Documentation
### `POST /analyze`
**Request:**
```json
{
  "text": "I absolutely love this new product!"
}
```
**Response:**
```json
{
  "text": "I absolutely love this new product!",
  "sentiment": "POSITIVE",
  "confidence": 0.98,
  "probabilities": {"POSITIVE": 0.98, "NEGATIVE": 0.01, "NEUTRAL": 0.01},
  "processing_time": 0.045
}
```

## Model Performance
| Model | Accuracy | Latency (CPU) |
|---|---|---|
| Twitter-RoBERTa-base | 92.4% | ~80ms |
| DistilBERT-SST-2 | 90.1% | ~40ms |

## Project Structure
```
.
├── app/
│   └── streamlit_app.py
├── src/
│   ├── api/
│   ├── data/
│   └── models/
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
