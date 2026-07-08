---
title: SafeX Assistant
emoji: 🛡️
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# SafeX Assistant

A grounded RAG chatbot for SafeX Solutions — answers only from real site content
(services, about, cybersecurity, Trust programs), with sources shown for every answer.

- **Backend:** FastAPI + FAISS + Gemini (via LangChain)
- **Frontend:** single static `index.html`, served by the same app at `/`
- **API:** `POST /chat`, `GET /stats`, `GET /api/health`

Set your `GEMINI_API_KEY` in this Space's **Settings → Variables and secrets** — do not commit it.