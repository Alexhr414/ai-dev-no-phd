"""
RAG Chatbot - Add document expertise to your chatbot
Part 2 of "AI Development Without a PhD"
"""

import os
import fitz  # PyMuPDF
import numpy as np
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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

def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a list of texts using OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr))

class SimpleVectorStore:
    """Lightweight in-memory vector store."""
    
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.metadata = []
    
    def add(self, texts: list[str], metadata: list[dict]):
        """Add texts and their metadata to the store."""
        embeddings = get_embeddings(texts)
        self.chunks.extend(texts)
        self.embeddings.extend(embeddings)
        self.metadata.extend(metadata)
    
    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search for most relevant chunks."""
        query_embedding = get_embeddings([query])[0]
        
        # Calculate similarities
        scores = [cosine_similarity(query_embedding, emb) for emb in self.embeddings]
        
        # Get top k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        return [
            {
                "text": self.chunks[i],
                "score": scores[i],
                "source": self.metadata[i]["source"]
            }
            for i in top_indices
        ]

class RAGChatbot:
    """Chatbot with RAG capabilities."""
    
    def __init__(self, documents_folder: str, model: str = "gpt-4o-mini"):
        self.model = model
        self.vector_store = SimpleVectorStore()
        self.conversation_history = []
        
        # Load and index documents
        print(f"Loading documents from {documents_folder}...")
        documents = load_documents(documents_folder)
        
        for doc in documents:
            chunks = chunk_text(doc["text"])
            metadata = [{"source": doc["source"]} for _ in chunks]
            self.vector_store.add(chunks, metadata)
        
        print(f"Indexed {len(self.vector_store.chunks)} chunks from {len(documents)} documents.")
    
    def chat(self, user_message: str) -> str:
        """Chat with RAG-augmented context."""
        # Retrieve relevant chunks
        results = self.vector_store.search(user_message, top_k=3)
        
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[Source: {r['source']}]\n{r['text']}"
            for r in results
        ])
        
        # Build prompt with context
        system_prompt = f"""You are a helpful assistant with access to the following context:

{context}

Answer questions based on this context. If the context doesn't contain the answer, say so clearly."""
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                *self.conversation_history
            ]
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        # Show sources
        sources = set(r["source"] for r in results)
        print(f"\n[Sources consulted: {', '.join(sources)}]")
        
        return assistant_message

def main():
    """Main interactive loop."""
    print("RAG Chatbot - Part 2 of 'AI Development Without a PhD'\n")
    
    # Create sample documents folder if it doesn't exist
    docs_folder = "sample_docs"
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        print(f"Created '{docs_folder}' folder. Add some .txt, .md, or .pdf files there and restart.")
        return
    
    if not os.listdir(docs_folder):
        print(f"'{docs_folder}' folder is empty. Add some documents and restart.")
        return
    
    # Initialize chatbot
    chatbot = RAGChatbot(docs_folder)
    
    print("\nChatbot ready! Type 'exit' to quit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        
        if not user_input:
            continue
        
        response = chatbot.chat(user_input)
        print(f"\nAssistant: {response}\n")

if __name__ == "__main__":
    main()
