# Turn Your AI Chatbot Into a Document Expert with RAG

*Add Retrieval-Augmented Generation to your chatbot so it can answer questions from your own PDFs, docs, and knowledge base — in under 50 lines of Python.*

---

## Why RAG?

Your chatbot from [Part 1](/build-ai-chatbot-30-minutes) is smart, but it only knows what GPT was trained on. What if you want it to:
- Answer questions about **your company's documentation**?
- Search through **your personal notes**?
- Be an expert on **a specific PDF or manual**?

That's where **RAG (Retrieval-Augmented Generation)** comes in. Instead of fine-tuning (expensive, slow), you feed relevant context into the prompt at query time.

**The result:** A chatbot that's an instant expert on *your* data.

## What You'll Build

An upgrade to the Part 1 chatbot that:
- ✅ Ingests PDF and text files
- ✅ Chunks and embeds documents
- ✅ Retrieves relevant context for each question
- ✅ Generates grounded answers with source citations
- ✅ Works with any document type

## Architecture (Simple Version)

```
User Question
    ↓
[1. Embed Question] → vector
    ↓
[2. Search Vector Store] → top 3 relevant chunks
    ↓
[3. Build Prompt] = system + chunks + question
    ↓
[4. Call LLM] → grounded answer with citations
```

No LangChain, no frameworks. Just Python + OpenAI + a lightweight vector store.

## Prerequisites

- Python 3.9+
- OpenAI API key (from Part 1)
- `pip install openai numpy pymupdf`

## Step 1: Document Ingestion

First, let's load and chunk documents:

```python
import fitz  # PyMuPDF
import os

def load_documents(folder_path: str) -> list[dict]:
    """Load all PDFs and text files from a folder."""
    documents = []
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            doc = fitz.open(filepath)
            text = "\n".join(page.get_text() for page in doc)
            documents.append({"text": text, "source": filename})
        elif filename.endswith('.txt') or filename.endswith('.md'):
            with open(filepath, 'r') as f:
                documents.append({"text": f.read(), "source": filename})
    return documents

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks
```

**Why chunk?** LLMs have context limits. By splitting documents into ~500-word chunks, we can retrieve only the relevant parts instead of stuffing the entire document into the prompt.

**Why overlap?** So important sentences at chunk boundaries don't get cut in half.

## Step 2: Create Embeddings

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a list of texts using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

**Cost check:** `text-embedding-3-small` costs ~$0.02 per million tokens. Embedding a 100-page PDF costs less than $0.01.

## Step 3: Build the Vector Store

No Pinecone needed. We'll use a simple in-memory store:

```python
import json

class SimpleVectorStore:
    def __init__(self):
        self.chunks = []      # original text chunks
        self.embeddings = []  # corresponding embeddings
        self.metadata = []    # source file info
    
    def add_documents(self, folder_path: str):
        """Ingest all documents from a folder."""
        docs = load_documents(folder_path)
        for doc in docs:
            chunks = chunk_text(doc["text"])
            embeddings = get_embeddings(chunks)
            for chunk, embedding in zip(chunks, embeddings):
                self.chunks.append(chunk)
                self.embeddings.append(embedding)
                self.metadata.append({"source": doc["source"]})
        print(f"Indexed {len(self.chunks)} chunks from {len(docs)} documents")
    
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Find the most relevant chunks for a query."""
        query_embedding = get_embeddings([query])[0]
        similarities = [
            cosine_similarity(query_embedding, emb)
            for emb in self.embeddings
        ]
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [
            {
                "text": self.chunks[i],
                "source": self.metadata[i]["source"],
                "score": similarities[i]
            }
            for i in top_indices
        ]
    
    def save(self, path: str):
        """Save the vector store to disk."""
        data = {
            "chunks": self.chunks,
            "embeddings": self.embeddings,
            "metadata": self.metadata
        }
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """Load the vector store from disk."""
        with open(path, 'r') as f:
            data = json.load(f)
        self.chunks = data["chunks"]
        self.embeddings = data["embeddings"]
        self.metadata = data["metadata"]
```

## Step 4: RAG-Powered Chat

Now wire it into the chatbot:

```python
def rag_chat(store: SimpleVectorStore, question: str, history: list = None) -> str:
    """Answer a question using RAG."""
    # Retrieve relevant context
    results = store.search(question, top_k=3)
    
    # Build context string
    context = "\n\n---\n\n".join(
        f"[Source: {r['source']}]\n{r['text']}" for r in results
    )
    
    # Build messages
    messages = [
        {
            "role": "system",
            "content": f"""You are a helpful assistant that answers questions based on the provided documents.
Use ONLY the context below to answer. If the context doesn't contain the answer, say so.
Always cite your sources using [Source: filename].

Context:
{context}"""
        }
    ]
    
    if history:
        messages.extend(history)
    
    messages.append({"role": "user", "content": question})
    
    # Call LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,  # Lower = more factual
        stream=True
    )
    
    # Stream response
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    
    print()  # newline
    return full_response
```

## Step 5: Put It Together

```python
def main():
    store = SimpleVectorStore()
    
    # Ingest documents (do this once)
    store.add_documents("./my_documents")
    store.save("vector_store.json")
    
    # Or load existing store
    # store.load("vector_store.json")
    
    # Chat loop
    history = []
    print("📚 RAG Chatbot ready! Ask questions about your documents.")
    print("Type 'quit' to exit.\n")
    
    while True:
        question = input("You: ").strip()
        if question.lower() in ('quit', 'exit'):
            break
        
        answer = rag_chat(store, question, history)
        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
```

## Complete File Structure

```
my-rag-chatbot/
├── app.py              # Main application
├── my_documents/       # Drop your PDFs/texts here
│   ├── manual.pdf
│   ├── notes.txt
│   └── faq.md
├── vector_store.json   # Generated embeddings (cached)
└── requirements.txt
```

**requirements.txt:**
```
openai>=1.0
numpy
pymupdf
```

## Cost Breakdown

For a typical use case (100-page document, 50 queries/day):

| Component | Cost |
|-----------|------|
| Embedding (one-time) | ~$0.01 |
| GPT-4o-mini per query | ~$0.002 |
| Daily cost (50 queries) | ~$0.10 |
| **Monthly cost** | **~$3** |

Compare that to fine-tuning ($25+ per run) or enterprise RAG platforms ($100+/month).

## Level Up: Production Tips

### 1. Better Chunking
Use semantic chunking instead of fixed-size:
```python
# Split on paragraph boundaries, headers, or sentence endings
# instead of arbitrary word counts
```

### 2. Hybrid Search
Combine vector similarity with keyword search (BM25) for better recall:
```python
# Use a library like rank_bm25 alongside embeddings
```

### 3. Re-ranking
After retrieval, re-rank results with a cross-encoder for higher precision.

### 4. Persistent Vector Store
For production, swap `SimpleVectorStore` with:
- **ChromaDB** (local, easy setup)
- **Qdrant** (self-hosted, feature-rich)
- **Pinecone** (managed, scales effortlessly)

### 5. Web Interface
Plug this into the FastAPI frontend from Part 1 — just replace the chat endpoint.

## What's Next?

In **Part 3**, we'll add:
- Multi-modal support (images + text)
- Conversation memory with RAG
- A polished web UI with file upload

---

*Found this useful? Follow [@bitale14](https://x.com/bitale14) for more practical AI tutorials.*

*Part 1: [Build an AI Chatbot in 30 Minutes](/build-ai-chatbot-30-minutes)*
