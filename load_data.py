from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    "data",
    glob="*.txt",
    loader_cls=TextLoader
)

documents = loader.load()

print(f"Loaded {len(documents)} documents")

for doc in documents:
    print(doc.metadata["source"])