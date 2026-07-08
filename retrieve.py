from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

query = "What services does SafeX provide?"

docs = vectorstore.similarity_search(query, k=3)

print("=" * 80)

for i, doc in enumerate(docs, start=1):
    print(f"\nResult {i}")
    print("-" * 80)
    print(doc.page_content[:1000])