# 🛡️ SafeX Assistant

A grounded **Retrieval-Augmented Generation (RAG) chatbot** built for [SafeX Solutions](https://safexsolutions.com/). It answers only from real site content — services, cybersecurity offerings, and Trust welfare programs — and shows the exact source for every answer instead of guessing.

**🔗 Live demo:** https://huggingface.co/spaces/humi69/safex-assistant

---

## ✨ Features

- **Grounded answers, not hallucinations** — every response is retrieved from real SafeX Solutions content; if the answer isn't in the knowledge base, the bot says so instead of making something up
- **Source citations** — each answer shows exactly which document(s) it was pulled from
- **Custom-branded UI** — matches SafeX's real logo and color identity, built as a single self-contained HTML file (no framework, no build step)
- **One-Space deployment** — frontend and backend served together from a single FastAPI app, no separate hosting or CORS setup needed

## 🧠 How it works

1. SafeX Solutions website content (services, about, cybersecurity, Trust programs) is split into chunks and embedded using `sentence-transformers/all-MiniLM-L6-v2`
2. Chunks are indexed in a local **FAISS** vector store
3. On each question, the top-matching chunks are retrieved and passed to **Gemini 2.5 Flash** (via LangChain) with a strict prompt: *answer only from this context, or say you don't know*
4. The answer, its source filenames, and a confidence score are returned to the chat UI

## 🛠️ Tech stack

| Layer | Tech |
|---|---|
| Embeddings | sentence-transformers (MiniLM-L6-v2) |
| Vector store | FAISS |
| LLM | Google Gemini 2.5 Flash |
| Orchestration | LangChain |
| Backend | FastAPI |
| Frontend | Single-file HTML/CSS/JS |
| Hosting | Hugging Face Spaces (Docker) |

## 📡 API

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the chat UI |
| `/chat` | POST | `{ "question": "..." }` → grounded answer + sources + confidence |
| `/stats` | GET | Query volume, answer rate, latency, most-cited sources |
| `/api/health` | GET | Health check |

## 🚀 Running locally

```bash
pip install -r requirements.txt
# create a .env file with: GEMINI_API_KEY=your_key_here
uvicorn main:app --reload
```

Then open `http://127.0.0.1:8000` in your browser.

## ☁️ Deployment

Deployed as a single Hugging Face Space (Docker SDK). Set `GEMINI_API_KEY` under **Settings → Variables and secrets** — never commit it to the repo.

## 📂 Repo contents

- `main.py`, `chatbot.py` — FastAPI backend + RAG pipeline
- `static/index.html` — the chat UI
- `data/` — source content the bot is grounded on
- `faiss_index/` — prebuilt vector index
- `CASE_STUDY.md` — full write-up: approach, architecture decisions, debugging process, and results

## 📝 Project background

Built as an AI/ML internship prototype for SafeX Solutions — see `CASE_STUDY.md` in this repo for the complete case study.

## 👤 Author

**Huma Aslam**
GitHub: [@humaaslam46](https://github.com/humaaslam46)
