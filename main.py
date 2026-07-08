import json
import os
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from chatbot import ask_question

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="SafeX RAG API")

# -------------------------
# CORS
# -------------------------
# "*" is fine for a portfolio prototype. If you want it tighter, replace with
# your real Vercel URL, e.g. ["https://safex-dashboard.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Lightweight analytics store (JSON file, no DB needed for a prototype)
# -------------------------
LOG_PATH = Path(__file__).parent / "analytics_log.json"


def _load_log():
    if LOG_PATH.exists():
        try:
            return json.loads(LOG_PATH.read_text())
        except Exception:
            return []
    return []


def _save_event(question: str, answer: str, sources: list, confidence: float, latency_ms: float):
    log = _load_log()
    log.append({
        "timestamp": time.time(),
        "question": question,
        "sources": sources,
        "confidence": confidence,
        "latency_ms": round(latency_ms, 1),
        "answered": "couldn't find" not in answer.lower(),
    })
    # keep the log bounded so the file doesn't grow forever
    log = log[-500:]
    LOG_PATH.write_text(json.dumps(log))


# -------------------------
# Request body schema
# -------------------------
class Query(BaseModel):
    question: str


# -------------------------
# Health check
# -------------------------
@app.get("/api/health")
def health():
    return {"message": "SafeX RAG API is running"}


# -------------------------
# Chat endpoint
# -------------------------
@app.post("/chat")
def chat(query: Query):
    start = time.time()
    answer, sources, confidence = ask_question(query.question)
    latency_ms = (time.time() - start) * 1000

    _save_event(query.question, answer, sources, confidence, latency_ms)

    return {
        "answer": answer,
        "sources": sources,
        "confidence": confidence,
        "latency_ms": round(latency_ms, 1),
    }


# -------------------------
# Stats endpoint — powers the dashboard panel
# -------------------------
@app.get("/stats")
def stats():
    log = _load_log()
    total = len(log)

    if total == 0:
        return {
            "total_queries": 0,
            "answered_rate": 0,
            "avg_latency_ms": 0,
            "avg_confidence": 0,
            "top_sources": [],
            "recent": [],
        }

    answered = sum(1 for e in log if e["answered"])
    avg_latency = sum(e["latency_ms"] for e in log) / total
    avg_confidence = sum(e["confidence"] for e in log) / total

    source_counts = {}
    for e in log:
        for s in e["sources"]:
            source_counts[s] = source_counts.get(s, 0) + 1
    top_sources = sorted(source_counts.items(), key=lambda x: -x[1])[:6]

    return {
        "total_queries": total,
        "answered_rate": round(answered / total * 100, 1),
        "avg_latency_ms": round(avg_latency, 1),
        "avg_confidence": round(avg_confidence, 2),
        "top_sources": [{"name": n, "count": c} for n, c in top_sources],
        "recent": [
            {"question": e["question"], "answered": e["answered"], "timestamp": e["timestamp"]}
            for e in log[-8:][::-1]
        ],
    }

# Frontend — serves static/index.html at "/".
# Must be mounted LAST so it doesn't shadow the API routes above.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
