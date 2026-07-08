from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load documents
loader = DirectoryLoader(
    "data",
    glob="*.txt",
    loader_cls=TextLoader
)

documents = loader.load()

# Split documents
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Total Chunks: {len(chunks)}")

# Create embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Build FAISS vector database
vectorstore = FAISS.from_documents(
    chunks,
    embedding_model
)

# Save it
vectorstore.save_local("faiss_index")

print("✅ FAISS index created successfully!")