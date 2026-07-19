# SafeX Assistant: A Grounded RAG Chatbot for SafeX Solutions


## Internship TASK 1 — July 2026

  **Live demo:** https://huggingface.co/spaces/humi69/safex-assistant
  
  **Source:** https://huggingface.co/spaces/humi69/safex-assistant/tree/main

  ---

## 1. Problem

SafeX Solutions' website (safexsolutions.com) spans several service lines — web development,
cybersecurity, network infrastructure, cloud solutions, digital marketing, AI automation, and
creative media — plus a separate "Trust" welfare initiative (Hope Rising, Health Outreach,
Education Support). Visitors have to hunt across many pages to find answers to simple questions
("What cybersecurity services do you offer?", "What is the Trust program?"). I built an AI
assistant that answers directly from the site's real content, with sources shown for every
answer, so replies are verifiable rather than guessed.

## 2. Approach

**Architecture:** Retrieval-Augmented Generation (RAG) — the model only answers from retrieved,
real site content, and says so explicitly when it can't find something ("I couldn't find that
information in the SafeX knowledge base"), rather than hallucinating.

- **Data:** 8 pages of real SafeX content (home, about, services, contact, blog, plus four Trust
  program pages) exported into plain-text files.
- **Chunking:** `RecursiveCharacterTextSplitter`, 500-character chunks with 100-character overlap.
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (HuggingFace) — small, fast, free,
  runs on CPU, no per-embedding API cost.
- **Vector store:** FAISS, local index — no external DB needed at this scale.
- **Generation:** Google Gemini 2.5 Flash via LangChain — fast, cheap, good instruction-following.
- **Retrieval:** top-k nearest chunks per question, injected into a strict prompt that forces the
  model to answer only from context and admit when it can't.
- **Serving:** FastAPI backend with a single `/chat` endpoint (question in, grounded answer +
  cited source filenames out) plus a lightweight `/stats` endpoint and `/api/health` check.
- **Frontend:** a single self-contained `index.html` (no framework, no build step) matching
  SafeX's real brand — their actual logo (shield/chevron mark, navy-to-blue gradient) embedded
  directly in the page, white/blue/grey palette, chat bubbles with source citations under
  grounded answers.
- **Deployment:** one Hugging Face Space (Docker SDK) serving both the API and the frontend
  together — FastAPI mounts the static `index.html` at `/` after all API routes, so there's a
  single URL, no separate frontend host, and no CORS configuration needed.

## 3. Why these choices

- **RAG over fine-tuning:** far cheaper, avoids stale/hallucinated info, and updates instantly if
  site content changes — just re-run the indexing script, no retraining.
- **Small local embedding model:** no per-embedding API cost, runs fine on CPU, good enough for an
  8-document knowledge base at this scale.
- **Strict "answer only from context" prompt:** directly addresses the biggest risk of a chatbot
  on a company website — confidently wrong answers about services or pricing.
- **One Space instead of split hosting:** originally planned to split the frontend (Vercel) and
  backend (Render) because Vercel's serverless functions can't comfortably run FAISS +
  sentence-transformers + LangChain. Switched to a single Hugging Face Docker Space instead —
  same reasoning (needs a real always-on Python host), but one deployment target, one URL, zero
  CORS setup, simpler to maintain and to explain in an interview.

## 4. Debugging journey (worth showing, not hiding)

A portfolio piece is more convincing when it shows real problem-solving, not just a finished
product. Three real issues came up during this build:

1. **Missing API key on first run** — `ChatGoogleGenerativeAI` requires `GOOGLE_API_KEY` or
   `GEMINI_API_KEY` in the environment. Traced a `pydantic.ValidationError` at startup to a
   missing `.env` file, fixed by creating it from `.env.example` and setting the real key
   (locally, and later as a Hugging Face Space secret for the deployed version).
2. **Windows vs. Linux path separators** — source filenames displayed correctly locally
   (`home.txt`) but showed as `data\home.txt` once deployed to Hugging Face's Linux container.
   The FAISS index had been built on Windows, so stored source paths used backslashes;
   `os.path.basename()` only strips folders correctly using the current OS's separator. Fixed by
   normalizing backslashes to forward slashes before extracting the filename — one line, but a
   good example of an environment-dependent bug that only shows up after deployment.
3. **Unauthenticated `git push` rejected** — Hugging Face requires an access token instead of a
   password for git operations; resolved by generating a token with Write access at
   huggingface.co/settings/tokens.

## 5. Results

*(Fill in with your own testing — these are the categories worth reporting)*

- Tested with real questions spanning services, cybersecurity, and Trust programs; answered
 correctly with accurate source citations, and correctly declined out-of-scope questions
  (e.g. asking about something not on the site) instead of guessing.
- Example interaction:
  > **Q:** What are the services of SafeX?
  > **A:** SafeX Solutions specializes in: web development, network infrastructure, cloud
  > solutions, cybersecurity services, data-driven digital marketing, branding, photography,
  > videography services, AI Automation, and Creative Media Services.
  > **Sources:** home.txt, about.txt
- Most-cited source pages: [check `/stats` — likely home.txt and about.txt, since they cover
  services broadly]

## 6. Limitations & next steps

- Free-tier Hugging Face Spaces can go idle and take longer to respond after inactivity —
  reasonable tradeoff for a portfolio prototype, would need a paid tier or different host for
  production traffic.
- The "confidence" score is a simple heuristic (did retrieval + generation succeed), not a
  calibrated probability — a labeled evaluation set of correct/incorrect answers would be a
  natural next step.
- No conversation memory yet — each question is answered independently. Multi-turn context
  (e.g. "what about pricing for that?") would be a good v2 feature.
- Could add scheduled re-scraping so the knowledge base stays current without manual re-indexing
  whenever the website changes.

## 7. Stack summary

| Layer | Tech |
|---|---|
| Embeddings | sentence-transformers (MiniLM-L6-v2) |
| Vector store | FAISS |
| LLM | Gemini 2.5 Flash |
| Orchestration | LangChain |
| Backend | FastAPI |
| Frontend | Single-file HTML/CSS/JS, no framework |
| Hosting | Hugging Face Spaces (Docker) — one Space serves both frontend and API |
