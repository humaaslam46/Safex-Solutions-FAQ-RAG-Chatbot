import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load env
load_dotenv()

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

# Prompt
prompt = ChatPromptTemplate.from_template("""
You are the official AI assistant for SafeX Solutions.

Answer ONLY using the context below.

If the answer is not present in the context, say:
"I couldn't find that information in the SafeX knowledge base."

Context:
{context}

Question:
{question}
""")

def ask_question(question: str):
    """
    Runs retrieval + generation for a single question.
    Returns (answer_text, sources_list, confidence_float).
    Never raises — always returns a user-safe message on failure.
    """
    question = (question or "").strip()
    if not question:
        return "Please type a question so I can help.", [], 0.0

    try:
        docs = retriever.invoke(question)
    except Exception as e:
        return f"Sorry, I couldn't search the knowledge base right now ({type(e).__name__}).", [], 0.0

    if not docs:
        return "I couldn't find that information in the SafeX knowledge base.", [], 0.0

    context = "\n\n".join([doc.page_content for doc in docs])

    messages = prompt.format_messages(
        context=context,
        question=question
    )

    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        return f"Sorry, the AI model is unavailable right now ({type(e).__name__}). Please try again shortly.", [], 0.0

    sources = list(set([os.path.basename(doc.metadata["source"]) for doc in docs]))

    # Simple heuristic "confidence" for the dashboard: did we actually find grounded context?
    confidence = 0.9 if docs and "couldn't find" not in answer.lower() else 0.3

    return answer, sources, confidence